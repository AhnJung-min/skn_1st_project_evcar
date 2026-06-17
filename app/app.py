import os
import csv
import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="대한민국 전기차 비중 트렌드", layout="wide")

# ==========================================================
# 📊 1. 데이터 정제 및 계산 로직
# ==========================================================
general_monthly_total = {}
ev_monthly_total = {}

# [일반 자동차]
with open(r'C:/SKN_AI/skn_1st_project_evcar/data/general_num.csv', mode='r', encoding='cp949') as f:
    reader = csv.reader(f)
    next(reader);
    next(reader)
    for row in reader:
        if not row or len(row) < 4: continue
        연월 = row[0].strip()
        try:
            진짜총계 = int(row[-2].strip() + row[-1].strip())
        except:
            진짜총계 = int(row[-1].strip()) if row[-1].strip().isdigit() else 0
        general_monthly_total[연월] = general_monthly_total.get(연월, 0) + 진짜총계

# [전기차]
with open(r'C:/SKN_AI/skn_1st_project_evcar/data/ev_num.csv', mode='r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if not row: continue
        연월 = row[0][:7].strip()
        행의총합 = sum(int(v.replace(',', '').strip()) for v in row[1:] if v.strip().replace(',', '').isdigit())
        ev_monthly_total[연월] = 행의총합

target_months = ['2024-08', '2024-09', '2024-10', '2024-11', '2024-12', '2025-01', '2025-02']
df_result = pd.DataFrame([
    {'연월': m, '총 자동차 대수 (A)': general_monthly_total.get(m, 0), '총 전기차 대수 (B)': ev_monthly_total.get(m, 0),
     '전기차 비중 (%)': round((ev_monthly_total.get(m, 0) / general_monthly_total.get(m, 0)) * 100,
                         2) if general_monthly_total.get(m, 0) > 0 else 0}
    for m in target_months
])

# ==========================================================
# 🎨 2. 화면 구현 (그래프를 탭 밖으로 분리)
# ==========================================================

# 💡 [버튼형 디자인 CSS]
st.markdown("""
<style>
    /* 라디오 버튼의 전체 레이아웃을 버튼 박스처럼 구성 */
    div.stRadio > div {
        flex-direction: row;
        gap: 15px;
        justify-content: center;
        margin-bottom: 30px;
    }

    /* 각 버튼의 기본 디자인 */
    div.stRadio label {
        background-color: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 50px; /* 둥근 캡슐 형태 */
        padding: 10px 30px;
        color: #666;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    /* 선택된 버튼 디자인 */
    div.stRadio [data-baseweb="radio"] div:has(input:checked) + label {
        background-color: #FF4B4B !important;
        border-color: #FF4B4B !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 10px rgba(255, 75, 75, 0.3);
    }

    /* 마우스 올렸을 때 효과 */
    div.stRadio label:hover {
        border-color: #FF4B4B;
        color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)

# 기존 st.title 대신 아래 코드를 사용하세요
st.markdown("<h1 style='text-align: ; font-size: 2.2rem; margin-bottom: 20px;'>📊 전국 전기차 비중 트렌드 분석</h1>", unsafe_allow_html=True)
st.divider()

# 기간 선택 (탭 대신 라디오 버튼을 사용하여 탭 밖에서 제어)
month_labels = [f"{m.split('-')[0]}년 {int(m.split('-')[1])}월" for m in target_months]
selected_label = st.radio("기간 선택", month_labels, label_visibility="collapsed")
i = month_labels.index(selected_label)
selected_data = df_result[df_result['연월'] == target_months[i]].iloc[0]

st.write("")  # 간격

# 컬럼 나누기 (그래프를 탭 밖으로 빼서 3의 비율을 온전히 가져감)
left_col, right_col = st.columns([1, 3])

with left_col:
    card_style = "background-color: #ffffff; padding: 25px; border-radius: 15px; border-left: 8px solid; box-shadow: 3px 3px 15px rgba(0,0,0,0.05); margin-bottom: 20px;"
    st.markdown(f"""
    <div style="{card_style} border-color: #00CC96;">
        <p style="font-size: 0.95rem; font-weight: 600; color: #888; margin-bottom: 5px;">🚗 총 자동차 등록 대수</p>
        <p style="font-size: 2.0rem; font-weight: 800; color: #222;">{int(selected_data['총 자동차 대수 (A)']):,} <span style="font-size: 1.1rem; color: #6c757d;">대</span></p>
    </div>
    <div style="{card_style} border-color: #ffbc00;">
        <p style="font-size: 0.95rem; font-weight: 600; color: #888; margin-bottom: 5px;">⚡ 총 전기차 등록 대수</p>
        <p style="font-size: 2.0rem; font-weight: 800; color: #222;">{int(selected_data['총 전기차 대수 (B)']):,} <span style="font-size: 1.1rem; color: #6c757d;">대</span></p>
    </div>
    <div style="{card_style} border-color: #FF4B4B;">
        <p style="font-size: 0.95rem; font-weight: 600; color: #888; margin-bottom: 5px;">📈 전기차 비중</p>
        <p style="font-size: 2.0rem; font-weight: 800; color: #222;">{selected_data['전기차 비중 (%)']:.2f} <span style="font-size: 1.1rem; color: #6c757d;">%</span></p>
    </div>
    """, unsafe_allow_html=True)

with right_col:
    df_chart = df_result.copy()
    df_chart['is_selected'] = df_chart['연월'] == target_months[i]

    fig = px.line(df_chart, x='연월', y='전기차 비중 (%)', title="📈 대한민국 전기차 비중 트렌드 변화 추이")
    fig.update_traces(line=dict(color='#FF4B4B', width=3))
    fig.add_scatter(x=df_chart['연월'], y=df_chart['전기차 비중 (%)'], mode='markers+text',
                    text=df_chart['전기차 비중 (%)'].map('{:.2f}%'.format), textposition='top center',
                    marker=dict(size=df_chart['is_selected'].map({True: 16, False: 7}),
                                color=df_chart['is_selected'].map({True: '#C0392B', False: '#FF8A8A'}),
                                line=dict(width=2, color='#FFFFFF')), showlegend=False)

    fig.update_layout(height=450, margin=dict(t=50, b=20, l=20, r=20),
                      transition=dict(duration=400, easing="cubic-in-out"))
    # 이제 그래프가 탭 영향을 받지 않으므로 절대로 깨지지 않습니다.
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("📋 연월별 상세 데이터 (전체 기간)")
df_formatted = df_result.copy()
df_formatted['연월'] = df_formatted['연월'].apply(lambda x: f"{x.split('-')[0]}년 {int(x.split('-')[1])}월")
df_formatted['총 자동차 대수 (A)'] = df_formatted['총 자동차 대수 (A)'].map('{:,}대'.format)
df_formatted['총 전기차 대수 (B)'] = df_formatted['총 전기차 대수 (B)'].map('{:,}대'.format)
df_formatted['전기차 비중 (%)'] = df_formatted['전기차 비중 (%)'].map('{:.2f}%'.format)
st.dataframe(df_formatted, use_container_width=True)
st.success("데이터 시각화 대시보드가 성공적으로 렌더링되었습니다!")

st.divider()
st.subheader("🚗 신규 자동차 시장의 전기차 전환율 분석")

# 1. 증감분 계산 (신규 유입 데이터)
df_diff = df_result.copy()
df_diff['일반차 증가'] = df_diff['총 자동차 대수 (A)'].diff()
df_diff['전기차 증가'] = df_diff['총 전기차 대수 (B)'].diff()

# 2. 전기차 전환율 계산 (전기차 증가 / 일반차 증가)
# *주의: 일반차 증가가 0이면 무한대 방지를 위해 예외처리 필요
df_diff['전기차 전환율 (%)'] = (df_diff['전기차 증가'] / df_diff['일반차 증가']) * 100

# 3. 시각화: 신규 시장에서의 영향력 보여주기
fig_conv = px.area(
    df_diff.dropna(),
    x='연월',
    y='전기차 전환율 (%)',
    title="📈 매월 신규 자동차 유입 중 전기차 비중 (%)",
    color_discrete_sequence=['#FF4B4B']
)
fig_conv.update_layout(height=350, margin=dict(t=50, b=20, l=20, r=20))
st.plotly_chart(fig_conv, use_container_width=True)

# 4. 분석 결과 해석 출력
st.info("""
**🔍 데이터 인사이트:**
신규로 등록되는 전체 자동차 대수 중 전기차가 차지하는 비율을 분석했습니다. 
이 수치가 상승하고 있다면, 시장의 무게중심이 내연기관에서 전기차로 빠르게 이동하고 있음을 의미합니다.
""")