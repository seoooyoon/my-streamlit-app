import streamlit as st
import streamlit.components.v1 as components

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="MajorPass",
    layout="wide"
)

# -----------------------------
# SIDEBAR – API KEY
# -----------------------------
with st.sidebar:
    st.markdown("## 🔑 API 설정")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="향후 개인 맞춤 분석 고도화를 위해 사용됩니다."
    )
    st.markdown("---")
    st.markdown("""
    **MajorPass는**
    입력된 정보를 외부에 저장하지 않습니다.
    """)

# -----------------------------
# GLOBAL STYLE
# -----------------------------
st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background-color: #FFF6CC;
    color: #1A1A1A;
    font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif;
}

.block-container {
    padding-top: 2rem;
}

/* Splash Animation */
@keyframes fadeOut {
    0% { opacity: 1; }
    70% { opacity: 1; }
    100% { opacity: 0; visibility: hidden; }
}

.splash {
    height: 70vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    animation: fadeOut 3s forwards;
}

.major-title {
    font-size: 4.8rem;
    font-weight: 800;
    text-align: center;
}

.major-sub {
    font-size: 1.4rem;
    text-align: center;
    margin-top: 0.5rem;
}

.section-title {
    font-size: 1.8rem;
    font-weight: 700;
    margin: 3rem 0 1.2rem 0;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SPLASH SCREEN (CSS FADE-OUT)
# -----------------------------
st.markdown("""
<div class="splash">
    <div class="major-title">MajorPass</div>
    <div class="major-sub">
        전공을 커리어 자산으로 정리합니다<br/>
        <b>Path to PASS!</b>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# USER INPUT
# -----------------------------
st.markdown("<div class='section-title'>🎓 나의 현재 상황</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    major = st.text_input(
        "현재 전공 (풀네임 입력)",
        placeholder="예: 실내건축학과"
    )
    semester = st.selectbox(
        "현재 학년 / 학기",
        [f"{y}학년 {s}학기" for y in range(1, 5) for s in ["1", "2"]]
    )

with col2:
    plan = st.selectbox(
        "전공 계획",
        ["본전공 유지", "복수전공 희망", "전과 희망"]
    )
    gpa = st.slider("전체 GPA (4.3 만점)", 0.0, 4.3, 3.5, 0.01)

st.markdown("#### 📊 이수 학점 현황")
c1, c2 = st.columns(2)
with c1:
    major_credit = st.number_input("전공 이수 학점", 0, 150, 45)
with c2:
    liberal_credit = st.number_input("교양 이수 학점", 0, 150, 30)

# -----------------------------
# ANALYSIS BUTTON (FLOW 핵심)
# -----------------------------
st.markdown("<br/>", unsafe_allow_html=True)
analyze = st.button("🔍 분석 결과 확인하기", use_container_width=True)

# -----------------------------
# LOGIC
# -----------------------------
def diagnose_status(gpa, plan):
    if gpa >= 3.8:
        grade_msg = "성적 측면에서 매우 안정적인 상태입니다."
    elif gpa >= 3.3:
        grade_msg = "성적은 무난하지만, 방향성이 중요해지는 구간입니다."
    else:
        grade_msg = "앞으로의 학기 전략 설계가 특히 중요합니다."

    if plan == "본전공 유지":
        plan_msg = "현재 전공을 깊이 있게 확장하는 전략이 적합합니다."
    elif plan == "복수전공 희망":
        plan_msg = "기존 전공과의 연결 지점을 고려한 선택이 중요합니다."
    else:
        plan_msg = "전환 이후 활용 가능한 기존 전공 자산을 정리하는 것이 핵심입니다."

    return grade_msg, plan_msg

# -----------------------------
# CARD FLIP COMPONENT (유지)
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
# RESULT (버튼 눌렀을 때만)
# -----------------------------
if analyze:
    grade_msg, plan_msg = diagnose_status(gpa, plan)

    st.markdown("<div class='section-title'>📌 맞춤 분석 결과</div>", unsafe_allow_html=True)

    flip_card(
        "현재 상태 진단",
        f"""
        전공: {major}<br/>
        현재 학기: {semester}<br/>
        GPA: {gpa} / 4.3<br/><br/>
        {grade_msg}
        """,
        "📊"
    )

    flip_card(
        "전공 기반 전략 방향",
        f"""
        전공 이수 학점: {major_credit}학점<br/>
        교양 이수 학점: {liberal_credit}학점<br/><br/>
        {plan_msg}
        """,
        "🧭"
    )

    flip_card(
        "다음 학기 To-Do List",
        """
        ✅ 전공 핵심 수업 정리<br/>
        ✅ 현재까지의 전공 결과물 구조화<br/>
        ✅ 선택지별 리스크 비교<br/><br/>
        🎯 지금 할 수 있는 것부터 정리하세요
        """,
        "📝"
    )

    st.markdown("---")
    st.markdown("✨ **MajorPass는 ‘정답’을 주지 않고, 지금의 상태에 맞는 판단 기준을 제공합니다.**")

