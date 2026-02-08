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
    major = st.text_input("현재 전공", placeholder="예: 실내건축학과")
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
# LOGIC
# -----------------------------
def diagnose_status(gpa, plan):
    if gpa >= 3.8:
        grade_msg = """
        현재 성적은 **상위권에 속하는 안정적인 상태**입니다.<br/>
        선택지의 폭이 넓고, 전공 심화·확장·전환 모두 시도 가능한 구간입니다.<br/>
        다만 성적에만 의존하기보다, **‘어떤 방향으로 쓸 것인가’**를 정리해야
        성적의 가치가 커집니다.
        """
    elif gpa >= 3.3:
        grade_msg = """
        성적은 **평균 이상으로 안정적이지만, 전략에 따라 격차가 벌어지는 구간**입니다.<br/>
        무작정 유지하기보다, 남은 학기 동안 **선택과 집중이 필요한 시점**입니다.<br/>
        전공 내에서의 강점 포인트를 명확히 만들지 않으면
        성적이 평범하게 소비될 가능성도 있습니다.
        """
    else:
        grade_msg = """
        현재 성적은 **향후 설계에 따라 충분히 만회 가능한 구간**입니다.<br/>
        지금 중요한 것은 과거 성적보다,
        **앞으로 어떤 구조로 학기를 쌓을 것인지**입니다.<br/>
        전략적인 과목 선택과 결과물 중심의 접근이 필요합니다.
        """

    if plan == "본전공 유지":
        plan_msg = """
        전공을 유지한다면 핵심은 **‘얼마나 깊이 파고들었는지’**입니다.<br/>
        단순 이수보다, 전공 안에서의 전문 영역·관심 축을 명확히 해야 합니다.<br/>
        → 전공 결과물, 프로젝트, 리서치 경험을
        하나의 스토리로 연결하는 전략이 적합합니다.
        """
    elif plan == "복수전공 희망":
        plan_msg = """
        복수전공을 고려한다면,
        두 전공이 **어디에서 연결되고 어디에서 갈라지는지**를 먼저 정리해야 합니다.<br/>
        단순히 ‘유리해 보이는 조합’보다,
        현재 전공에서 이미 쌓은 자산을
        확장할 수 있는 선택이 중요합니다.
        """
    else:
        plan_msg = """
        전과를 염두에 둔다면,
        지금 전공에서 얻은 경험을 **어떻게 이전할 것인지**가 핵심입니다.<br/>
        완전히 새로 시작하는 것이 아니라,
        기존 전공을 ‘배경 자산’으로 활용하는 전략이 필요합니다.
        """

    return grade_msg, plan_msg

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
    """, height=300)

# -----------------------------
# RESULT
# -----------------------------
if analyze:
    grade_msg, plan_msg = diagnose_status(gpa, plan)

    st.markdown("<div class='section-title'>📌 맞춤 분석 결과</div>", unsafe_allow_html=True)

    flip_card(
        "현재 상태 종합 진단",
        f"""
        <b>전공</b>: {major}<br/>
        <b>현재 학기</b>: {semester}<br/>
        <b>GPA</b>: {gpa} / 4.3<br/><br/>
        {grade_msg}
        """,
        "📊"
    )

    flip_card(
        "전공 기반 전략 해석",
        f"""
        <b>전공 이수</b>: {major_credit}학점<br/>
        <b>교양 이수</b>: {liberal_credit}학점<br/><br/>
        {plan_msg}
        """,
        "🧭"
    )

    flip_card(
        "다음 학기 실행 로드맵",
        """
        <b>1️⃣ 전공 핵심 정리</b><br/>
        지금까지 들은 전공 과목을
        ‘나에게 남은 것’ 기준으로 정리하세요.<br/><br/>

        <b>2️⃣ 결과물 중심 설계</b><br/>
        성적보다 설명 가능한 결과물을
        의도적으로 만들어야 합니다.<br/><br/>

        <b>3️⃣ 선택지 비교</b><br/>
        유지 / 확장 / 전환 중
        가장 리스크가 낮은 방향부터 검토하세요.
        """,
        "📝"
    )

    st.markdown("---")
    st.markdown("✨ **MajorPass는 정답 대신, 지금 상황에서 합리적인 판단 기준을 제공합니다.**")

---

원하면 다음 단계로  
- 카드 **4~5장으로 쪼개기**
- 결과를 **GPT 응답 기반으로 더 개인화**
- 결과 PDF 저장 기능  

이 중에서 어디까지 갈지 같이 설계해줄게.

