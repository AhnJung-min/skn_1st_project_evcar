import os
import csv
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 1. .env 파일에서 DB 접속 정보(아이디, 비번 등)를 로드합니다.
load_dotenv()


def get_db_engine():
    """MySQL 데이터베이스와 안전하게 연결 통로를 만드는 함수"""
    return create_engine(
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )


def main():
    print("🔄 [1단계: 데이터 전처리 시작] 회원님 스타일의 텍스트 정제 및 비율 계산을 시작합니다...")

    final_data_list = []
    general_data = {}

    # [일반 자동차 파일 읽기]
    with open(r'C:/SKN_AI/skn_1st_project_evcar/data/general_num.csv', mode='r', encoding='cp949') as f:
        reader = csv.reader(f)
        next(reader)  # 헤더 1줄 건너뛰기
        next(reader)  # 헤더 2줄 건너뛰기

        for row in reader:
            if not row or len(row) < 4:
                continue

            연월 = row[0].strip()
            지역 = row[1].strip()

            # 천 단위 쉼표 때문에 쪼개진 마지막 두 조각을 결합하여 중복 없는 진짜 총계를 구합니다.
            try:
                진짜총계str = row[-2].strip() + row[-1].strip()
                진짜총계 = int(진짜총계str)
            except ValueError:
                try:
                    진짜총계 = int(row[-1].strip())
                except:
                    진짜총계 = 0

            key = (연월, 지역)
            general_data[key] = general_data.get(key, 0) + 진짜총계

    # [전기차 파일 읽기]
    with open(r'C:/SKN_AI/skn_1st_project_evcar/data/ev_num.csv', mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)

        for row in reader:
            if not row:
                continue
            연월 = row[0][:7].strip()

            for idx in range(1, len(row)):
                지역 = headers[idx].strip()
                val = row[idx]

                if val.strip():
                    clean_val = val.replace(',', '').strip()
                    if clean_val.isdigit():
                        전기차대수 = int(clean_val)

                        if (연월, 지역) in general_data:
                            전체자동차대수 = general_data[(연월, 지역)]

                            # ⭐ [핵심 추가] total_cars 대비 ev_cars의 비율을 계산합니다 (소수점 둘째 자리까지)
                            if 전체자동차대수 > 0:
                                전기차비율 = round((전기차대수 / 전체자동차대수) * 100, 2)
                            else:
                                전기차비율 = 0.0

                            final_data_list.append({
                                'base_month': 연월,
                                'region': 지역,
                                'total_cars': 전체자동차대수,
                                'ev_cars': 전기차대수,
                                'ev_ratio': 전기차비율  # 👈 DB 테이블에 비율 컬럼 추가!
                            })

    print("🤝 [2단계: 데이터 병합 완료] 비율 계산이 포함된 청정 데이터가 조립되었습니다.")
    print("🚀 [3단계: DB 적재] MySQL 'car_ev_status' 테이블에 적재를 시작합니다...")

    df_final = pd.DataFrame(final_data_list)
    engine = get_db_engine()

    # 'replace' 옵션으로 기존 구조를 깔끔하게 밀어버리고 ev_ratio 컬럼이 포함된 새 테이블을 만듭니다.
    df_final.to_sql('car_ev_status', con=engine, if_exists='replace', index=False)

    print("\n⭐ [복원 및 비율 계산 완료] 상위 데이터 미리보기:")
    # 보기 편하게 소수점 뒤에 %를 붙인 가독성용 출력 포맷 설정 (실제 DB에는 순수 숫자만 들어갑니다)
    print(df_final.head(10))
    print("\n🎉 총 자동차 대수 대비 전기차 비율(ev_ratio)까지 완벽하게 적재되었습니다!")


if __name__ == "__main__":
    main()