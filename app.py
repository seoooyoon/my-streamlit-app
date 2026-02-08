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
    입력된 정보를 저장하거나 외부로 전송하지 않습니다.
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

# ⭐️ 관심사 입력 복구
interest = st.text_area(
    "💡 현재 관심 분야 / 진로 방향 (자유롭게 작성)",
    placeholder="예: 기획, 콘텐츠 제작, 브랜딩, UX, 데이터 분석 등",
    height=100
)

# -----------------------------
# BUTTON
# -----------------------------
st.markdown("<br/>", unsafe_allow_html=True)
analyze = st.button("🔍 분석 결과 확인하기", use_container_width=True)

# -----------------------------
# CARD COMPONENT (가독성 개선)
# -----------------------------
def flip_card(title, content, emoji):
    components.html(f"""
    <style>
    .card-container {{
        width: 100%;
        height: 360px;
        perspective: 1200px;
        margin-bottom: 40px;
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
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }}
    .card-front {{
        background: #ffffff;
        font-size: 1.6rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }}
    .card-back {{
        background: #1A1A1A;
        color: #ffffff;
        transform: rotateY(180deg);
        font-size: 1rem;
        line-height: 1.75;
        overflow-y: auto;
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
    """, height=400)

# -----------------------------
# RESULT
# -----------------------------
if analyze:

    flip_card(
        "현재 상태 진단",
        f"""
        현재 당신은 <b>{major}</b> 전공을 이수 중이며, {semester}에 해당합니다.<br/><br/>

        GPA {gpa} 기준으로 볼 때, 지금은 성적 자체보다도
        ‘지금까지 어떤 선택을 해왔고, 앞으로 무엇을 남길 수 있는가’를
        정리하는 것이 더 중요한 시점입니다.<br/><br/>

        특히 관심 분야로 작성한 <b>{interest}</b>는
        향후 전공 선택이나 확장 방향을 판단하는 데 중요한 힌트가 됩니다.
        """,
        "📊"
    )

    flip_card(
        "전공 기반 전략 방향",
        f"""
        현재까지 전공 이수 학점은 {major_credit}학점,
        교양 이수 학점은 {liberal_credit}학점입니다.<br/><br/>

        선택한 전공 계획인 <b>{plan}</b>은
        단순히 제도를 선택하는 문제가 아니라,
        지금까지 쌓아온 전공 경험을 어떻게 활용할 것인가의 문제입니다.<br/><br/>

        중요한 것은 전공을 바꾸는지 여부보다,
        기존 전공에서 이미 확보한 역량을
        다음 선택에서도 설명 가능하게 만드는 전략입니다.
        """,
        "🧭"
    )

    flip_card(
        "다음 학기 전략적 포인트",
        f"""
        다음 학기의 핵심 목표는 ‘결정’이 아니라 ‘정리’입니다.<br/><br/>

        지금까지 수강한 전공 과목과 활동을
        관심 분야인 <b>{interest}</b>와 연결해 정리해보세요.
        그 과정에서 전공 유지, 복수전공, 전과 중
        어떤 선택이 가장 자연스럽게 이어지는지 보이기 시작할 것입니다.<br/><br/>

        불안한 상태에서 내린 결정은 쉽게 흔들리지만,
        정리된 상태에서의 선택은 훨씬 단단합니다.
        """,
        "📝"
    )

    st.markdown("---")
    st.markdown(
        "✨ **MajorPass는 선택을 대신하지 않습니다. 대신, 선택을 덜 불안하게 만듭니다.**"
    )
