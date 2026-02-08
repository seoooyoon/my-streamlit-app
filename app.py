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
# SPLASH SCREEN
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
        "현재 전공 (풀네임)",
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
# ANALYSIS BUTTON
# -----------------------------
st.markdown("<br/>", unsafe_allow_html=True)
analyze = st.button("🔍 분석 결과 확인하기", use_container_width=True)

# -----------------------------
# ANALYSIS LOGIC (디테일 강화)
# -----------------------------
def diagnose_status(gpa, major_credit, plan):
    # 성적 분석
    if gpa >= 3.8:
        grade_msg = """
        현재 성적은 상위권에 해당하며,  
        **선택의 폭이 넓은 상태**입니다.  
        학점 관리보다 ‘어디에 집중할 것인가’가 더 중요해지는 시점입니다.
        """
    elif gpa >= 3.3:
        grade_msg = """
        성적은 안정적인 편이지만,  
        **전공 내 포지셔닝 전략이 필요한 구간**입니다.  
        전공 수업 중 강점 과목을 명확히 구분하는 것이 중요합니다.
        """
    else:
        grade_msg = """
        성적 관리가 향후 선택에 직접적인 영향을 줄 수 있습니다.  
        다음 학기에는 **선택과 집중 전략**이 반드시 필요합니다.
        """

    # 전공 계획 분석
    if plan == "본전공 유지":
        plan_msg = """
        현재 전공을 중심으로  
        **전문성을 깊게 쌓는 전략**이 적합합니다.  
        전공 수업 + 결과물 + 경험이 하나의 스토리로 연결되어야 합니다.
        """
    elif plan == "복수전공 희망":
        plan_msg = """
        두 전공이 어떻게 연결되는지가 핵심입니다.  
        단순 병행이 아니라  
        **기존 전공을 확장하는 방향의 복수전공**을 설계해야 합니다.
        """
    else:
        plan_msg = """
        전과 이후를 대비해  
        현재 전공에서 이미 확보한  
        **기술·사고방식·결과물을 명확히 정리**해두는 것이 중요합니다.
        """

    # 학점 기반 조언
    credit_msg = f"""
    현재까지 전공 {major_credit}학점, 교양 {liberal_credit}학점을 이수했습니다.  
    이는 전공 이해도가 형성되기 시작하는 단계로,  
    **지금부터의 선택이 커리어 방향에 큰 영향을 미칩니다.**
    """

    return grade_msg, plan_msg, credit_msg

# -----------------------------
# CARD FLIP COMPONENT
# -----------------------------
def flip_card(title, content, emoji):
    components.html(f"""
    <style>
    .card-container {{
        width: 100%;
        height: 300px;
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
        padding: 28px;
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
        line-height: 1.7;
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
    """, height=330)

# -----------------------------
# RESULT (버튼 클릭 시)
# -----------------------------
if analyze:
    grade_msg, plan_msg, credit_msg = diagnose_status(gpa, major_credit, plan)

    st.markdown("<div class='section-title'>📌 맞춤 분석 결과</div>", unsafe_allow_html=True)

    flip_card(
        "현재 상태 종합 진단",
        f"""
        전공: {major}<br/>
        학기: {semester}<br/>
        GPA: {gpa} / 4.3<br/><br/>
        {grade_msg}
        """,
        "📊"
    )

    flip_card(
        "전공 계획에 따른 전략",
        f"""
        {plan_msg}<br/><br/>
        {credit_msg}
        """,
        "🧭"
    )

    flip_card(
        "다음 학기 실행 To-Do",
        """
        ✅ 전공 핵심 과목 3개 선정 및 정리<br/>
        ✅ 지금까지의 전공 결과물 구조화<br/>
        ✅ 전공 선택지별 시나리오 비교<br/><br/>
        🎯 “지금 할 수 있는 것”부터 명확히 실행하세요
        """,
        "📝"
    )

    st.markdown("---")
    st.markdown("✨ **MajorPass는 선택을 대신하지 않고, 판단 기준을 제공합니다.**")
