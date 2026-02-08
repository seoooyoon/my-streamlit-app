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
    major = st.text_input("현재 전공 (풀네임 입력)")
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
# BUTTON
# -----------------------------
st.markdown("<br/>", unsafe_allow_html=True)
analyze = st.button("🔍 분석 결과 확인하기", use_container_width=True)

# -----------------------------
# CARD COMPONENT
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
        text-align: left;
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }}
    .card-front {{
        background: #ffffff;
        font-size: 1.6rem;
        font-weight: 700;
        text-align: center;
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
    """, height=340)

# -----------------------------
# RESULT
# -----------------------------
if analyze:

    flip_card(
        "현재 상태 진단",
        f"""
        현재 당신은 <b>{major}</b> 전공을 이수 중이며, {semester}에 해당합니다.
        지금까지의 학업 흐름과 성적(GPA {gpa})을 종합적으로 보면,
        단순히 ‘잘하고 있다 / 부족하다’로 나누기보다는
        앞으로의 선택에 따라 학업 성과의 의미가 크게 달라질 수 있는 시점에 있습니다.<br/><br/>

        특히 이 시기는 성적 자체보다도,
        지금까지 어떤 전공 과목을 통해 무엇을 배웠고
        그 결과가 어떤 형태로 남아 있는지를 정리하는 것이 중요해집니다.
        같은 GPA라도 이를 설명할 수 있는 언어와 구조가 있다면
        전공은 충분히 강점으로 전환될 수 있습니다.
        """,
        "📊"
    )

    flip_card(
        "전공 기반 전략 방향",
        f"""
        현재까지 전공 이수 학점은 {major_credit}학점,
        교양 이수 학점은 {liberal_credit}학점으로,
        이미 전공의 기본 골격은 상당 부분 형성된 상태입니다.<br/><br/>

        전공 계획으로 선택한 ‘{plan}’ 방향은
        단순한 선택지가 아니라 앞으로의 시간과 노력을 어디에 집중할 것인지에 대한 선언에 가깝습니다.
        이 선택이 의미 있으려면,
        지금까지 쌓아온 전공 경험이 다음 단계에서도
        어떻게 활용될 수 있는지에 대한 연결 논리가 필요합니다.<br/><br/>

        전공은 바꾸거나 늘릴 수 있지만,
        지금까지 투자한 시간과 경험을 자산으로 전환할 수 있는지 여부가
        향후 만족도를 크게 좌우하게 됩니다.
        """,
        "🧭"
    )

    flip_card(
        "다음 학기 전략적 포인트",
        """
        다음 학기는 새로운 선택을 하기 전에
        ‘정리의 학기’로 설정하는 것이 효과적입니다.
        지금까지 수강한 전공 과목을 나열하는 것이 아니라,
        각 과목이 어떤 역량을 길러주었는지,
        그리고 그 역량이 어떤 방향으로 확장될 수 있는지를
        하나의 흐름으로 정리해보는 과정이 필요합니다.<br/><br/>

        이 과정을 거치면,
        전공 유지·복수전공·전과 중 어떤 선택을 하더라도
        더 이상 막연한 불안이 아닌,
        비교 가능한 기준을 가지고 판단할 수 있게 됩니다.
        다음 학기의 목표는 ‘결정을 내리는 것’이 아니라,
        언제든 결정할 수 있는 상태를 만드는 것입니다.
        """,
        "📝"
    )

    st.markdown("---")
    st.markdown(
        "✨ **MajorPass는 선택을 대신하지 않습니다. 대신, 선택을 덜 불안하게 만듭니다.**"
    )
