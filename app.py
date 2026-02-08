import streamlit as st
import time
import streamlit.components.v1 as components

st.set_page_config(
    page_title="MajorPass",
    layout="wide"
)

# -----------------------------
# GLOBAL STYLE (Yellow Background)
# -----------------------------
st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background-color: #FFF6CC;
    color: #1A1A1A;
    font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif;
}

/* Remove default padding */
.block-container {
    padding-top: 2rem;
}

/* Title */
.major-title {
    font-size: 4.5rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0.5rem;
}

.major-sub {
    font-size: 1.4rem;
    text-align: center;
    opacity: 0.85;
}

/* Section title */
.section-title {
    font-size: 1.8rem;
    font-weight: 700;
    margin: 2.5rem 0 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SPLASH SCREEN
# -----------------------------
splash = st.empty()
with splash:
    st.markdown("""
    <div style="height:70vh; display:flex; flex-direction:column; justify-content:center; align-items:center;">
        <div class="major-title">MajorPass</div>
        <div class="major-sub">
            전공을 커리어 자산으로 정리합니다<br/>
            <b>Path to PASS!</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

time.sleep(3)
splash.empty()

# -----------------------------
# USER INPUT
# -----------------------------
st.markdown("<div class='section-title'>🎓 나의 현재 상황 입력</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    major = st.text_input("현재 전공 (풀네임 입력)", placeholder="예: 실내건축학과")
    semester = st.selectbox(
        "현재 학년 / 학기",
        [f"{y}학년 {s}학기" for y in range(1,5) for s in ["1", "2"]]
    )

with col2:
    major_plan = st.selectbox(
        "복수전공 / 전과 희망 여부",
        ["본전공 유지", "복수전공 희망", "전과 희망"]
    )
    gpa = st.slider("전체 GPA (4.3 만점)", 0.0, 4.3, 3.5, 0.01)

st.markdown("#### 📊 이수 학점")
c1, c2 = st.columns(2)
with c1:
    major_credit = st.number_input("전공 이수 학점", 0, 150, 45)
with c2:
    liberal_credit = st.number_input("교양 이수 학점", 0, 150, 30)

# -----------------------------
# CARD FLIP COMPONENT
# -----------------------------
def flip_card(title, content, emoji):
    components.html(f"""
    <style>
    .card-container {{
        width: 100%;
        height: 260px;
        perspective: 1000px;
        margin-bottom: 30px;
    }}
    .card {{
        width: 100%;
        height: 100%;
        position: relative;
        transition: transform 0.8s;
        transform-style: preserve-3d;
        cursor: pointer;
    }}
    .card.flip {{
        transform: rotateY(180deg);
    }}
    .card-face {{
        position: absolute;
        width: 100%;
        height: 100%;
        backface-visibility: hidden;
        border-radius: 18px;
        padding: 24px;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }}
    .card-front {{
        background: #ffffff;
        font-size: 1.6rem;
        font-weight: 700;
    }}
    .card-back {{
        background: #1A1A1A;
        color: #ffffff;
        transform: rotateY(180deg);
        font-size: 1rem;
        line-height: 1.6;
    }}
    </style>

    <div class="card-container">
        <div class="card" onclick="this.classList.toggle('flip')">
            <div class="card-face card-front">
                {emoji}<br/>{title}
            </div>
            <div class="card-face card-back">
                {content}
            </div>
        </div>
    </div>
    """, height=300)

# -----------------------------
# ANALYSIS SECTION
# -----------------------------
st.markdown("<div class='section-title'>📌 분석 결과</div>", unsafe_allow_html=True)

flip_card(
    "현재 상황 분석",
    f"""
    • 전공: {major}<br/>
    • 학기: {semester}<br/>
    • GPA: {gpa} / 4.3<br/>
    • 전공 학점 {major_credit}학점 이수<br/>
    <br/>
    👉 전공 기반은 이미 형성 단계에 있으며,
    방향성만 명확히 잡으면 강점으로 발전 가능
    """,
    "📊"
)

flip_card(
    "전공 기반 커리어 로드맵",
    f"""
    1️⃣ 전공 역량 정제 (포트폴리오 중심)<br/>
    2️⃣ 광고·브랜드 공간 사례 분석<br/>
    3️⃣ 제일기획 / 이노션 스타일 리서치<br/>
    <br/>
    👉 공간 + 브랜드 스토리텔링 융합 전략
    """,
    "🧭"
)

flip_card(
    "추천 To-Do List",
    """
    ✅ 브랜드 팝업스토어 분석 프로젝트<br/>
    ✅ 공간 × 광고 레퍼런스 아카이빙<br/>
    ✅ UX / 브랜드 전략 기초 학습<br/>
    <br/>
    🎯 ‘전공 = 결과물’로 증명하기
    """,
    "📝"
)

st.markdown("---")
st.markdown("✨ **MajorPass는 전공을 선택이 아닌 ‘자산’으로 바꾸는 도구입니다.**")

# -----------------------------
# NEXT IDEAS
# -----------------------------
st.markdown("""
### 🚀 다음 단계로 발전시킬 수 있는 기능
- 결과 카드 **PDF / 이미지 저장**
- 제일기획·이노션 **직무별 맞춤 카드**
- 졸업 시점 기준 **타임라인 시각화**
- 포트폴리오 체크리스트 자동 생성
""")

