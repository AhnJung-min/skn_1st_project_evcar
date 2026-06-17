# snk_1st_project_evcar

전기차/교통 인프라 공공데이터 수집 → MySQL 적재 → Streamlit 시각화 팀 프로젝트.
공용 데이터베이스 이름은 **`ev_infra`** 로 통일한다. 각 팀원은 자신이 수집한
데이터셋을 같은 DB의 별도 테이블로 적재하고, 대시보드 페이지를 구성한다.

## 프로젝트 구조

```
project/
├── data/                   # 원본/정제 데이터 (정제본만 커밋, *_raw.json 은 제외)
│   ├── faq.json            #  └ FAQ 정제본
│   └── faq.csv
├── etl/
│   ├── extract.py          # 수집(Extract)   — [안정민] FAQ 스크래핑
│   ├── transform.py        # 정제(Transform) — 분류 분리·날짜 정규화
│   ├── load.py             # 적재(Load)      — ev_infra.faq 로 적재
│   └── extract_ev_charger.py  # (참고) 환경공단 전기차 충전소 API 수집 샘플
├── sql/
│   └── schema.sql          # ev_infra DDL (팀원별 테이블을 여기에 추가)
├── app/
│   └── dashboard.py        # Streamlit 대시보드 (DB→json 폴백)
├── .env.example            # DB 접속 정보 템플릿 (.env 로 복사해 사용)
├── .gitignore
└── requirements.txt
```

## 빠른 시작

```bash
# 1) 의존성
pip install -r requirements.txt

# 2) DB 접속 정보 설정
cp .env.example .env        # 값 채우기 (DB_PASSWORD 등)

# 3) 테이블 생성
mysql -u root -p < sql/schema.sql

# 4) ETL 파이프라인 (FAQ 기준)
python etl/extract.py       # data/faq_raw.json
python etl/transform.py     # data/faq.json, data/faq.csv
python etl/load.py          # ev_infra.faq 적재

# 5) 대시보드
streamlit run app/dashboard.py
```

> DB 접속이 안 되면 대시보드는 `data/faq.json` 으로 자동 폴백하므로
> MySQL 없이도 화면 확인이 가능하다.

## 팀원 작업 가이드 (충돌 방지)

공용 저장소이므로 같은 파일을 여러 명이 고치면 충돌이 난다. 아래 규칙을 따른다.

1. **테이블**: `sql/schema.sql` 의 "팀원 추가 영역"에 본인 테이블 `CREATE TABLE` 추가.
2. **ETL**: 본인 데이터셋 이름을 붙인 파일로 추가
   (예: `etl/extract_<dataset>.py`, `etl/load_<dataset>.py`).
   공용 `extract.py / transform.py / load.py` 는 FAQ 전용이므로 수정하지 말 것.
3. **대시보드**: `app/pages/` 폴더를 만들고 본인 페이지를 추가
   (예: `app/pages/2_충전소.py`) — Streamlit 멀티페이지로 자동 인식된다.
4. **데이터**: 정제본만 `data/` 에 커밋, 대용량 원본(`*_raw.json`)은 커밋 금지.

## 담당

| 담당 | 데이터셋 | 테이블 | 진행 |
|---|---|---|---|
| 안정민 | 교통안전공단 FAQ | `faq` | 수집·정제·적재·대시보드 ✅ |
| (팀원) | (충전소 등) | (추가) | - |
