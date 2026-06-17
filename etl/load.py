# -*- coding: utf-8 -*-
"""
load.py — MySQL 적재(Load)

data/faq.json (transform.py 산출물) 을 ev_infra 데이터베이스의 faq 테이블에 적재한다.
접속 정보는 프로젝트 루트의 .env 에서 읽는다(.env 는 git 제외).
테이블이 없으면 sql/schema.sql 의 DDL 로 생성해 두고 실행할 것.

  INSERT ... ON DUPLICATE KEY UPDATE 로 멱등(idempotent) 적재 → 재실행해도 중복 없음.

실행:
    python etl/load.py
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "data" / "faq.json"

load_dotenv(ROOT / ".env")


def get_engine():
    """.env 의 DB_* 값으로 SQLAlchemy 엔진 생성."""
    user = os.getenv("DB_USER", "root")
    pw = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME", "ev_infra")
    url = f"mysql+pymysql://{user}:{pw}@{host}:{port}/{name}?charset=utf8mb4"
    return create_engine(url)


UPSERT = text("""
    INSERT INTO faq (id, category, question, answer, modified)
    VALUES (:id, :category, :question, :answer, :modified)
    ON DUPLICATE KEY UPDATE
        category = VALUES(category),
        question = VALUES(question),
        answer   = VALUES(answer),
        modified = VALUES(modified)
""")


def main():
    with open(JSON_PATH, encoding="utf-8") as f:
        rows = json.load(f)

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(UPSERT, rows)

    print(f"적재 완료: ev_infra.faq ← {JSON_PATH} ({len(rows)}건)")


if __name__ == "__main__":
    main()
