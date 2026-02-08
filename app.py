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
# SPLASH
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
# ANALYSIS BUTTON
# -----------------------------
st.markdown("<br/>", unsafe_allow_html=True)
analyze = st.button("🔍 분석 결과 확인하기", use_container_width=True)

# -----------------------------
# LOGIC
# -----------------------------
def diagnose_status(gpa, plan):
    # ⭐ 수정됨: 메시지 구체화
    if gpa >= 3.8:
        grade_msg = (
            "현재 GPA는 상위권에 해당합니다.<br/>"
            "성적 자체가 하나의 경쟁력이 될 수 있는 구간으로, "
            "전공 심화·연구·대외활동 확장이 매우 유리합니다."
        )
    elif gpa >= 3.3:
        grade_msg = (
            "성적은 안정적인 편이지만, 앞으로의 선택에 따라 가치가 달라질 수 있습니다.<br/>"
            "성적 관리와 함께 ‘무엇을 남길 것인가’를 병행 설계하는 시점입니다."
        )
    else:
        grade_msg = (
            "현재 성적은 전략적 관리가 필요한 구간입니다.<br/>"
            "모든 과목을 끌어올리기보다는, 핵심 과목과 결과물 중심으로 집중하는 것이 효과적입니다."
        )

    if plan == "본전공 유지":
        plan_msg = (
            "본전공을 유지하는 선택은 ‘깊이’가 핵심입니다.<br/>"
            "전공 내 세부 트랙, 진로 연결 가능 분야를 명확히 하고 "
            "수업·프로젝트·포트폴리오를 하나의 스토리로 묶는 전략이 적합합니다."
        )
    elif plan == "복수전공 희망":
        plan_msg = (
            "복수전공은 ‘조합의 논리’가 중요합니다.<br/>"
            "현재 전공에서 이미 확보한 역량이 무엇인지 정리한 뒤, "
            "이를 확장·보완할 수 있는 전공을 선택해야 시너지가 발생합니다."
        )
    else:
        plan_msg = (
            "전과를 고려한다면, 지금까지의 전공을 ‘버리지 않는 전략’이 필요합니다.<br/>"
            "기존 전공에서 축적한 지식·툴·사고방식을 "
            "새 전공에서 어떻게 재활용할 수 있는지 정의하는 것이 핵심입니다."
        )

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
# RESULT
# -----------------------------
if analyze:
    grade_msg, plan_msg = diagnose_status(gpa, plan)

    st.markdown("<div class='section-title'>📌 맞춤 분석 결과</div>", unsafe_allow_html=True)

    # ⭐ 수정됨: 내용 대폭 확장
    flip_card(
        "현재 상태 진단",
        f"""
        <b>전공:</b> {major}<br/>
        <b>현재 학기:</b> {semester}<br/>
        <b>GPA:</b> {gpa} / 4.3<br/><br/>
        {grade_msg}<br/><br/>
        지금 단계에서는 ‘잘하고 있는 것’과 ‘더 가져가야 할 것’을 
        구분해 정리하는 작업이 특히 중요합니다.
        """,
        "📊"
    )

    flip_card(
        "전공 기반 전략 방향",
        f"""
        <b>전공 이수 학점:</b> {major_credit}학점<br/>
        <b>교양 이수 학점:</b> {liberal_credit}학점<br/><br/>
        {plan_msg}<br/><br/>
        전공 선택은 ‘전공명’보다 
        <b>전공을 통해 설명할 수 있는 나의 역량</b>이 핵심입니다.
        """,
        "🧭"
    )

    flip_card(
        "다음 학기 To-Do List",
        """
        ✅ 지금까지 들은 전공 수업을 기능/역량 기준으로 재분류<br/>
        ✅ 성적이 잘 나온 과목과 결과물을 중심으로 핵심 스토리 정리<br/>
        ✅ 전공 선택지별 (유지/복수/전과) 리스크와 기회 비교<br/><br/>
        🎯 목표는 ‘결정을 미루지 않을 수 있는 판단 기준 만들기’입니다.
        """,
        "📝"
    )

    st.markdown("---")
    st.markdown("✨ **MajorPass는 ‘정답’을 주지 않고, 지금의 상태에서 가장 합리적인 선택 기준을 설계하도록 돕습니다.**")
