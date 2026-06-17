# -*- coding: utf-8 -*-
"""
transform.py — 정제·정규화(Transform)

data/faq_raw.json (extract.py 산출물) 을 읽어
  - 제목에서 [분류] 를 떼어 category / question 으로 분리
  - 수정일 문자열 → 'YYYY-MM-DD' (없으면 None)
  - 공백 정리
정제 결과를 data/faq.json, data/faq.csv 로 저장한다.

실행:
    python etl/transform.py
"""

import csv
import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_PATH = DATA_DIR / "faq_raw.json"
JSON_PATH = DATA_DIR / "faq.json"
CSV_PATH = DATA_DIR / "faq.csv"

CATE_RE = re.compile(r"^\s*\[(?P<cate>[^\]]+)\]\s*(?P<q>.*)$", re.DOTALL)
COLUMNS = ["id", "category", "question", "answer", "modified"]


def transform(rows):
    out = []
    for r in rows:
        title = (r.get("title") or "").strip()
        category, question = "", title
        m = CATE_RE.match(title)
        if m:
            category = m.group("cate").strip()
            question = m.group("q").strip()
        out.append({
            "id": int(r["id"]),
            "category": category,
            "question": question,
            "answer": (r.get("answer") or "").strip(),
            "modified": r.get("modified") or None,
        })
    return out


def main():
    with open(RAW_PATH, encoding="utf-8") as f:
        rows = json.load(f)

    cleaned = transform(rows)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for row in cleaned:
            w.writerow(row)

    print(f"정제 완료: {JSON_PATH}, {CSV_PATH} ({len(cleaned)}건)")


if __name__ == "__main__":
    main()
