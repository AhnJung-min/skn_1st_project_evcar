# -*- coding: utf-8 -*-
"""
extract.py — 데이터 수집(Extract)

담당: 안정민 / 데이터셋: 한국교통안전공단 일반분야 FAQ

웹 게시판(서버 렌더링)을 페이지 단위로 긁어 원본을 data/faq_raw.json 으로 저장한다.
정제는 transform.py 가 맡는다. 외부 의존성은 requests 뿐.

실행:
    python etl/extract.py                 # 전체 수집 → data/faq_raw.json
    python etl/extract.py --max-pages 2   # 앞 2페이지만(테스트)
"""

import argparse
import html
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_PATH = DATA_DIR / "faq_raw.json"

BASE_URL = "https://main.kotsa.or.kr/portal/bbs/faq_list.do"
DEFAULT_PARAMS = {"menuCode": "04010000", "cateCode": "", "sechCdtn": "0", "sechKywd": ""}
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0 Safari/537.36"}

# 한 FAQ 항목(<li>) 단위로 질문/답변/수정일 추출
ITEM_RE = re.compile(
    r"fnc_setSearchCnt\('(?P<id>\d+)'\)"
    r".*?질문</span>\s*(?P<title>.*?)</a>"
    r".*?답변</span>\s*<pre>(?P<answer>.*?)</pre>"
    r"(?:.*?마지막 수정일\s*(?P<date>\d{4}-\d{2}-\d{2}))?",
    re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")


def _clean(text: str) -> str:
    text = TAG_RE.sub("", text)
    text = html.unescape(text).replace("\xa0", " ")
    return "\n".join(ln.rstrip() for ln in text.splitlines()).strip()


def _parse_page(htmltext: str):
    rows = []
    for m in ITEM_RE.finditer(htmltext):
        rows.append({
            "id": m.group("id"),
            "title": _clean(m.group("title")),   # 정제 전 원본 제목([분류] 포함)
            "answer": _clean(m.group("answer")),
            "modified": m.group("date") or "",
        })
    return rows


def fetch_faq(max_pages=None, delay=0.5):
    session = requests.Session()
    rows, seen, page = [], set(), 1
    while not (max_pages and page > max_pages):
        params = dict(DEFAULT_PARAMS, pageNumb=str(page))
        try:
            resp = session.get(f"{BASE_URL}?{urlencode(params)}", headers=HEADERS,
                               verify=False, timeout=20)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[!] {page}페이지 실패: {e}", file=sys.stderr)
            break

        items = _parse_page(resp.content.decode("utf-8", errors="replace"))
        new = [it for it in items if it["id"] not in seen]
        if not new:
            break
        for it in new:
            seen.add(it["id"])
        rows.extend(new)
        print(f"[+] {page}페이지: {len(new)}건 (누적 {len(rows)})")
        page += 1
        time.sleep(delay)
    return rows


def main():
    ap = argparse.ArgumentParser(description="FAQ 수집(Extract)")
    ap.add_argument("--max-pages", type=int, default=None)
    args = ap.parse_args()

    rows = fetch_faq(max_pages=args.max_pages)
    DATA_DIR.mkdir(exist_ok=True)
    with open(RAW_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"\n원본 저장: {RAW_PATH} ({len(rows)}건)")


if __name__ == "__main__":
    main()
