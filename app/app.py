import os
import csv
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================================
# 📊 1. 회원님이 직접 작성하신 데이터 정제 및 계산 로직 (백엔드)
# ==========================================================

# 데이터를 저장할 주머니
general_monthly_total = {}
ev_monthly_total = {}

# [일반 자동차 파일 읽기]
with open(r'C:/SKN_AI/skn_1st_project_evcar/data/general_num.csv', mode='r', encoding='cp949') as f:
    reader = csv.reader(f)
    next(reader)
    next(reader)
    for row in reader:
        if not row or len(row) < 4:
            continue
        연월 = row[0].strip()
        행의총합 = 0
        for val in row[3:]:
            if val.strip():
                clean_val = val.replace(',', '').strip()
                if clean_val.isdigit():
                    행의총합 += int(clean_val)
        general_monthly_total[연월] = general_monthly_total.get(연월, 0) + 행의총합

# [전기차 파일 읽기]
with open(r'C:/SKN_AI/skn_1st_project_evcar/data/ev_num.csv', mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if not row:
            continue
        연월 = row[0][:7].strip()
        행의총합 = 0
        for val in row[1:]:
            if val.strip():
                clean_val = val.replace(',', '').strip()
                if clean_val.isdigit():
                    행의총합 += int(clean_val)
        ev_monthly_total[연월] = 행의총합

# 가이드라인에 명시된 타겟 기간 설정
target_months = ['2024-08', '2024-09', '2024-10', '2024-11', '2024-12', '2025-01', '2025-02']

# 시각화를 위해 회원님의 결과를 데이터프레임(표) 형태로 변환합니다.
display_rows = []
for month in target_months:
    total_car = general_monthly_total.get(month, 0)
    total_ev = ev_monthly_total.get(month, 0)

    if total_car > 0:
        비중 = round((total_ev / total_car) * 100, 2)
    else:
        비중 = 0.0

    display_rows.append({
        '연월': month,
        '총 자동차 대수 (A)': total_car,
        '총 전기차 대수 (B)': total_ev,
        '전기차 비중 (%)': 비중
    })

df_result = pd.DataFrame(display_rows)

# ==========================================================
# 🎨 2. 가이드라인 맞춤형 Streamlit 화면 구현 (프론트엔드)
# ==========================================================
st.set_page_config(page_title="대한민국 전기차 비중 트렌드", layout="wide")

st.title("📊 대한민국 전기차 비중 트렌드 분석")
st.markdown("회원님이 정제하신 텍스트 데이터를 기반으로 가이드라인 대시보드를 생성합니다.")
st.hr()

# 가이드라인 구조 1: 상세 데이터 표 (엑셀 스타일)
st.subheader("📋 연월별 상세 데이터")

# 원본 표 모양을 그대로 유지하기 위해 가독성 포맷을 적용하여 화면에 띄웁니다.
df_formatted = df_result.copy()
df_formatted['총 자동차 대수 (A)'] = df_formatted['총 자동차 대수 (A)'].map('{:,}대'.format)
df_formatted['총 전기차 대수 (B)'] = df_formatted['총 전기차 대수 (B)'].map('{:,}대'.format)
df_formatted['전기차 비중 (%)'] = df_formatted['전기차 비중 (%)'].map('{:.2f}%'.format)

st.dataframe(df_formatted, use_container_width=True)
st.hr()

# 가이드라인 구조 2: 트렌드 선 그래프 (Line Chart)
st.subheader("📈 전기차 비중 (B/A) 변화 추이 그래프")

fig = px.line(
    df_result,
    x='연월',
    y='전기차 비중 (%)',
    markers=True,
    text='전기차 비중 (%)',
    title="대한민국 전기차 비중 트렌드 변화"
)
fig.update_traces(textposition="top center", line_color="#FF4B4B", line_width=3)
fig.update_layout(xaxis_title="기준 연월", yaxis_title="비중 (%)")

st.plotly_chart(fig, use_container_width=True)

st.success("★ 대한민국 전기차 비중 트렌드 분석 대시보드가 성공적으로 렌더링되었습니다! ★")