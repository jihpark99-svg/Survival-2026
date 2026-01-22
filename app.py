import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# ---------------------------------------------------------
# 1. 초기화 및 환경 설정 (Fail-Safe)
# ---------------------------------------------------------
st.set_page_config(page_title="2026 전략 BI v7.0", layout="wide", initial_sidebar_state="expanded")

# UI 스타일 개선
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .reportview-container .main .block-container{ padding-top: 2rem; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; background-color: #FF4B4B; color: white; }
    .strategy-card {
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #FF4B4B;
        background-color: white;
        margin-bottom: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .ai-copy-box {
        padding: 25px;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border-radius: 15px;
        font-size: 1.15em;
        font-weight: 500;
        margin-top: 15px;
    }
    .rationale-box {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #555;
        background-color: #fff;
    }
    </style>
    """, unsafe_allow_html=True)

# 변수 초기 선언
if 'ai_typing' not in st.session_state: st.session_state.ai_typing = ""

def clean_numeric(val):
    try:
        if isinstance(val, (int, float)): return val
        v = str(val).replace(',', '').replace('-', '0').strip()
        return float(v) if v else 0
    except: return 0

# [골든 데이터] 검증된 연도별/세대별 통계
def get_strategic_data():
    trend = pd.DataFrame([
        {'Year': '2022', 'Rate': 31.5, 'Type': '한식 밀키트'},
        {'Year': '2023', 'Rate': 38.7, 'Type': '한식 밀키트'},
        {'Year': '2024', 'Rate': 26.1, 'Type': '한식 밀키트'},
        {'Year': '2022', 'Rate': 40.0, 'Type': '즉석 국/탕(HMR)'},
        {'Year': '2023', 'Rate': 42.0, 'Type': '즉석 국/탕(HMR)'},
        {'Year': '2024', 'Rate': 41.5, 'Type': '즉석 국/탕(HMR)'}
    ])
    gen_rank = pd.DataFrame([
        {'Year': '2022', 'Gen': '2030', 'Item': '즉석밥/컵밥', 'Rate': 25.1},
        {'Year': '2023', 'Gen': '2030', 'Item': '즉석밥/컵밥', 'Rate': 28.4},
        {'Year': '2024', 'Gen': '2030', 'Item': '즉석밥/컵밥', 'Rate': 32.5},
        {'Year': '2022', 'Gen': '4050', 'Item': '찌개/탕류', 'Rate': 22.4},
        {'Year': '2023', 'Gen': '4050', 'Item': '찌개/탕류', 'Rate': 24.1},
        {'Year': '2024', 'Gen': '4050', 'Item': '찌개/탕류', 'Rate': 25.6}
    ])
    item_fluct = pd.DataFrame([
        {'Year': '2022', 'Item': '즉석밥류', 'Rate': 17.9},
        {'Year': '2023', 'Item': '즉석밥류', 'Rate': 21.0},
        {'Year': '2024', 'Item': '즉석밥류', 'Rate': 23.5},
        {'Year': '2022', 'Item': '만두/피자', 'Rate': 24.0},
        {'Year': '2023', 'Item': '만두/피자', 'Rate': 22.0},
        {'Year': '2024', 'Item': '만두/피자', 'Rate': 19.0}
    ])
    # [신규] 타겟별 추천 메뉴 데이터
    target_menu_data = pd.DataFrame([
        ['2030 시성비족', '즉석 컵밥류', 40], ['2030 시성비족', '고단백 샐러드', 30], ['2030 시성비족', 'HMR 덮밥소스', 30],
        ['4050 안심 주부', '프리미엄 전골 밀키트', 40], ['4050 안심 주부', '반조리 메인 요리', 35], ['4050 안심 주부', '키즈 맞춤 반찬', 25],
        ['5060 액티브 시니어', '저염/보양식 국탕', 50], ['5060 액티브 시니어', '소화 편한 죽', 30], ['5060 액티브 시니어', '건강식단 구독', 20]
    ], columns=['Target', 'Menu', 'Share'])

    return trend, gen_rank, item_fluct, target_menu_data

# ---------------------------------------------------------
# 2. 사이드바 (파일 로직)
# ---------------------------------------------------------
with st.sidebar:
    st.header("📂 경영 데이터 센터")
    uploaded_files = st.file_uploader(
        "파일 업로드 (CSV, XLSX, PNG, PPTX)", 
        type=['csv', 'xlsx', 'xls', 'png', 'jpg', 'jpeg', 'pptx'], 
        accept_multiple_files=True
    )
    st.divider()
    show_raw = st.checkbox("🔍 데이터 원본 표 보기", value=False)
    st.info("※ 전문가 가이드: 타겟별 '결핍'을 채워주는 메뉴 전략이 핵심입니다.")

fb_trend, fb_gen_rank, fb_item_fluct, fb_target_menu = get_strategic_data()

# ---------------------------------------------------------
# 3. 메인 대시보드
# ---------------------------------------------------------
st.title("🛡️ 2026 비즈니스 솔루션 v7.0")
st.markdown("##### 🚀 CEO Park Ji-hyun 전용: 타겟 메뉴 전략 및 실행")

tabs = st.tabs(["📉 시장 분석", "🧠 세대별 추세", "🛒 품목 등락", "💰 수익 시뮬레이션", "📍 지역 전략", "🎯 타겟 메뉴&카피"])

# --- Tab 1: 시장 분석 ---
with tabs[0]:
    st.subheader("1. 밀키트 하락 및 즉석식품 방어 현상 분석")
    col1, col2 = st.columns([1.5, 1])
    with col1:
        fig = px.line(fb_trend, x='Year', y='Rate', color='Type', markers=True, 
                      title="밀키트 vs 즉석식품 구매 경험률 추이")
        fig.add_annotation(x='2024', y=26.1, text="▼ 붕괴 지점(-12.6%p)", showarrow=True, arrowhead=2, arrowcolor="red")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🧐 왜 밀키트만 급락했는가?")
        with st.expander("① 조리 노동의 역설 (Labor Paradox)", expanded=True):
            st.write("""
            밀키트는 재료 손질만 대신해줄 뿐, **'조리'와 '설거지'**라는 최종 병목 공정(Bottleneck)은 여전히 소비자 몫입니다. 
            2026년 소비자는 조리 시간 20분을 '여가'가 아닌 '기회비용 손실'로 규정했습니다.
            """)
        with st.expander("② 경제적 임계점 (Price Ceiling)"):
            st.write("""
            고물가로 인해 밀키트 가격이 2인분 기준 2만원대에 진입하며 배달 음식과의 가격 차이가 소멸되었습니다. 
            **'노동이 포함된 2만원'**은 배달 대비 경쟁력을 상실했습니다.
            """)
        with st.expander("③ 팬데믹 요리 유희의 종말"):
            st.write("""
            코로나 시기엔 요리가 '놀이'였으나, 일상 회복 후 식사는 다시 **'빠르게 해결해야 할 과제'**로 복귀했습니다. 
            이 과정에서 3분 만에 끝나는 **즉석 국/탕류**로 수요가 전이되었습니다.
            """)

# --- Tab 2: 세대별 추세 ---
with tabs[1]:
    st.subheader("2. 세대별 행동 근거 및 품목별 추세")
    col_g1, col_g2 = st.columns([1.5, 1])
    with col_g1:
        fig_gen = px.bar(fb_gen_rank, x='Year', y='Rate', color='Item', barmode='group', facet_col='Gen',
                         title="세대별 1위 품목 점유율 변화 (2022-2024)")
        st.plotly_chart(fig_gen, use_container_width=True)
    with col_g2:
        st.success("### 📊 세대별 전략 근거")
        st.markdown("""
        **🧑 2030 (시성비 극대화):**
        - **근거:** 1인 가구는 주방 공간 효율을 중시합니다. 설거지가 나오는 밀키트보다 **'무조리 컵밥'** 선호도가 3년간 7.4%p 상승했습니다.
        
        **👩 4050 (신뢰와 죄책감):**
        - **근거:** 가족에게 인스턴트를 준다는 죄책감을 상쇄하기 위해 **'건더기가 풍부한 탕류'**를 선택합니다. 밀키트의 야채 선도 불신이 HMR 탕류로의 회귀를 불렀습니다.
        """)

# --- Tab 3: 품목 등락 ---
with tabs[2]:
    st.subheader("3. 연도별 품목 등락의 경제적 근거")
    col_f1, col_f2 = st.columns([1.5, 1])
    with col_f1:
        fig_flux = px.line(fb_item_fluct, x='Year', y='Rate', color='Item', markers=True, title="카테고리별 생애주기 추이")
        st.plotly_chart(fig_flux, use_container_width=True)
    with col_f2:
        st.warning("### 📈 등락 원인 상세")
        st.markdown("""
        **[상승: 즉석밥/HMR 국류]**
        - **근거:** **'불황형 생필품'**으로 안착. 경기 침체기에 가계 지출을 줄이려는 소비자들이 가장 먼저 선택하는 대체재가 되었습니다.
        
        **[하락: 만두/냉동피자/밀키트]**
        - **근거:** **'대체재 과잉'** 및 전문 프랜차이즈의 저가 공세. 냉동 피자 한 판보다 1인 피자 브랜드의 접근성과 맛이 우세해진 결과입니다.
        """)

# --- Tab 4: 수익 시뮬레이션 (수정 완료) ---
with tabs[3]:
    st.subheader("💰 원가 구조 기반 수익 및 비중 시뮬레이션")
    col_sim_in, col_sim_out1, col_sim_out2 = st.columns([1, 1.2, 1.2])
    with col_sim_in:
        st.write("🔧 **변수 설정**")
        price = st.number_input("판매 단가 (원)", value=12000)
        raw_pct = st.slider("원재료비 (%)", 20, 50, 35)
        labor_pct = st.slider("인건비 (%)", 10, 30, 15)
        rent_pct = st.slider("매장 임대료 (%)", 5, 20, 10)
        oper_pct = st.slider("기타 운영비 (%)", 5, 20, 10)
        eff_inc = st.slider("자동화 효율 개선 (%)", 0, 20, 10)
        
        # 총 원가 및 이익률 계산
        total_cost_pct = raw_pct + labor_pct + rent_pct + oper_pct
        profit_pct = 100 - total_cost_pct + eff_inc
        
    with col_sim_out1:
        st.write("📊 **원가 구조 (Waterfall)**")
        # 임대료와 운영비를 포함한 워터폴 차트
        fig_w = go.Figure(go.Waterfall(
            x = ["원재료비", "인건비", "매장 임대료", "기타 운영비", "자동화이익", "영업이익률"],
            y = [-raw_pct, -labor_pct, -rent_pct, -oper_pct, eff_inc, profit_pct],
            measure = ["relative", "relative", "relative", "relative", "relative", "total"]
        ))
        fig_w.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_w, use_container_width=True)
        
    with col_sim_out2:
        st.write("🍰 **이익 vs 원가 비중 (Pie)**")
        final_cost_pct = total_cost_pct - eff_inc
        fig_p_profit = go.Figure(data=[go.Pie(
            labels=['최종 영업이익', '총 매출원가'], 
            values=[profit_pct, final_cost_pct], 
            hole=.4,
            marker_colors=['#FF4B4B', '#3b82f6']
        )])
        fig_p_profit.update_layout(height=400, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_p_profit, use_container_width=True)
        
    st.divider()
    # 수식 업데이트
    st.latex(r"Profit Margin = 100\% - (Cost_{Raw} + Cost_{Labor} + Cost_{Rent} + Cost_{Oper}) + \Delta Efficiency_{Automation}")

# --- Tab 5: 지역 전략 ---
with tabs[4]:
    st.subheader("📍 대전/충남 거점 전략 수립 근거")
    reg1, reg2, reg3 = st.columns(3)
    with reg1:
        st.markdown(f"""<div class="strategy-card" style="border-left-color: #1e3a8a;">
            <h4>🏢 대전/세종</h4>
            <p><b>근거:</b> 맞벌이 공무원 가구 비중 전국 최상위권. 고학력층 특성상 '엔지니어링 데이터 기반 안심 공정'에 대한 신뢰 지불 의사 높음.</p>
        </div>""", unsafe_allow_html=True)
    with reg2:
        st.markdown(f"""<div class="strategy-card" style="border-left-color: #f59e0b;">
            <h4>🏭 천안/아산</h4>
            <p><b>근거:</b> 대규모 산단 교대 근무자 밀집. 퇴근길 픽업이 가능한 '24시 자동화 매장' 모델의 테스트베드로 최적.</p>
        </div>""", unsafe_allow_html=True)
    with reg3:
        st.markdown(f"""<div class="strategy-card" style="border-left-color: #10b981;">
            <h4>🤝 프랜차이즈 협회</h4>
            <p><b>근거:</b> 로컬 식자재 공동구매 시스템 구축 시 원가 15% 절감 가능. 충남 농가와 상생하는 ESG 브랜딩 용이.</p>
        </div>""", unsafe_allow_html=True)

# --- Tab 6: 타겟 메뉴 & AI 카피 ---
with tabs[5]:
    st.subheader("🎯 타겟별 추천 메뉴 구조 및 AI 마케팅 실행")
    
    # 1. 타겟별 메뉴 구조 시각화 (Sunburst Chart)
    st.markdown("##### 📊 연령대별 추천 메뉴 계층 구조 (Sunburst)")
    fig_sun = px.sunburst(fb_target_menu, path=['Target', 'Menu'], values='Share',
                          color='Target', color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_sun.update_layout(height=400, margin=dict(t=0, l=0, r=0, b=0))
    st.plotly_chart(fig_sun, use_container_width=True)
    
    # 2. 메뉴 추천 근거 및 AI 카피 생성
    st.divider()
    c_t1, c_t2 = st.columns([1.2, 1])
    
    with c_t1:
        st.markdown("##### 🧐 타겟별 메뉴 전략 근거")
        st.markdown("""
        <div class="rationale-box" style="border-left-color: #636EFA;">
            <b>🧑 2030 시성비족 (Efficiency)</b><br>
            조리 시간 0~2분, 설거지 없음. '식사'가 아닌 '연료 보충'의 개념으로 접근해야 합니다.
        </div>
        <div class="rationale-box" style="border-left-color: #EF553B;">
            <b>👩 4050 안심 주부 (Trust)</b><br>
            재료 손질 부담은 덜되, 가족에게 먹이는 '요리'의 느낌은 살려야 합니다. 프리미엄과 신뢰가 핵심입니다.
        </div>
        <div class="rationale-box" style="border-left-color: #00CC96;">
            <b>👴 5060 액티브 시니어 (Health)</b><br>
            건강(저염, 소화)이 최우선이며, 간편하게 데워 먹을 수 있는 따뜻한 국물 요리를 선호합니다.
        </div>
        """, unsafe_allow_html=True)
        
    with c_t2:
        st.markdown("##### ✍️ AI 카피 생성기")
        target_sel = st.radio("공략할 타겟을 선택하세요", ["2030 시성비족", "4050 안심 주부", "5060 액티브 시니어"])
        
        if st.button("🚀 AI 카피 생성 (Animation)"):
            copy_db = {
                "4050 안심 주부": "엄마의 정성을 '과학'으로 증명합니다. 박지현이 설계한 안심 공정, QR로 확인하세요.",
                "2030 시성비족": "씻고 볶는 노동 대신 3분 만에 끝내는 완벽한 고단백 루틴으로 저녁이 있는 삶을!",
                "5060 액티브 시니어": "산 정상에서 즐기는 보양식. 불 없이도 즐기는 뜨끈한 소고기 국밥, 속 편하게 드세요."
            }
            placeholder = st.empty()
            typing_text = ""
            for char in copy_db[target_sel]:
                typing_text += char
                placeholder.markdown(f'<div class="ai-copy-box">{typing_text}▌</div>', unsafe_allow_html=True)
                time.sleep(0.04)
            placeholder.markdown(f'<div class="ai-copy-box">{copy_db[target_sel]}</div>', unsafe_allow_html=True)

# --- 원본 데이터 테이블 ---
if show_raw:
    st.divider()
    with st.expander("🗃️ 분석 데이터 원본 표 확인"):
        st.write("**[시장 트렌드 수치]**")
        st.dataframe(fb_trend, use_container_width=True)