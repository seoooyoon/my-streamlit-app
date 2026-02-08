import streamlit as st
import time
from openai import OpenAI

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(
    page_title="MajorPass",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------
# CSS (Black & White / Flip Card)
# ----------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
    background-color: #000000;
    color: #ffffff;
}

a, label, span {
    color: #ffffff !important;
}

/* Splash */
.splash {
    height: 90vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    animation: fadeout 3s forwards;
}

@keyframes fadeout {
    0% {opacity: 1;}
    70% {opacity: 1;}
    100% {opacity: 0; display:none;}
}

.title {
    font-size: 5.5rem;
    font-weight: 800;
    letter-spacing: -2px;
}

.subtitle {
    font-size: 1.8rem;
    margin-top: 12px;
}

.tagline {
    font-size: 1.2rem;
    margin-top: 6px;
    opacity: 0.7;
}

/* Flip Card */
.flip-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 40px;
    margin-top: 40px;
}

.flip-card {
    background-color: transparent;
    width: 100%;
    height: 280px;
    perspective: 1000px;
}

.flip-inner {
    position: relative;
    width: 100%;
    height: 100%;
    transition: transform 0.8s;
    transform-style: preserve-3d;
}

.flip-card:hover .flip-inner {
    transform: rotateY(180deg) scale(1.05);
}

.flip-front, .flip-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 32px;
    box-shadow: 0 20px 50px rgba(255,255,255,0.08);
}

.flip-front {
    background: #ffffff;
    color: #000000;
    font-size: 1.4rem;
    font-weight: 700;
    text-align: center;
}

.flip-back {
    background: #111111;
    color: #ffffff;
    transform: rotateY(180deg);
    border-radius: 24px;
    overflow-y: auto;
    font-size: 0.95rem;
    line-height: 1.6;
}

/* Inputs */
input, textarea, select {
    background-color: #111 !important;
    color: #fff !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# Splash Screen
# ----------------------------------
if "splash_done" not in st.session_state:
    st.session_state.splash_done = False

if not st.session_state.splash_done:
    st.markdown("""
    <div class="splash">
        <div class="title">MajorPass</div>
        <div class="subtitle">전공을 커리어 자산으로 정리합니다</div>
        <div class="tagline">Path to PASS!</div>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(3)
    st.session_state.splash_done = True
    st.rerun()

# ----------------------------------
# Sidebar
# ----------------------------------
st.sidebar.title("API 설정")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# ----------------------------------
# User Input
# ----------------------------------
st.markdown("## 현재 나의 상황")

col1, col2 = st.columns(2)

with col1:
    major = st.text_input("현재 전공 (풀네임)", placeholder="예: 실내건축학과")
    semester = st.selectbox(
        "재학 학기",
        [f"{y}학년 {s}학기" for y in range(1,5) for s in ["1","2"]]
    )
    career_interest = st.text_input("관심 진로 분야", placeholder="광고기획 / BX / UX / AX")

with col2:
    major_credit = st.number_input("전공 이수 학점", 0, 200, 60)
    liberal_credit = st.number_input("교양 이수 학점", 0, 200, 40)
    gpa = st.slider("전체 GPA", 0.0, 4.5, 3.5, 0.1)

change_major = st.radio(
    "전공 계획",
    ["본전공 유지", "복수전공 희망", "전과 희망", "아직 고민 중"]
)

analyze = st.button("MajorPass 분석 시작", use_container_width=True)

# ----------------------------------
# OpenAI Function (New API)
# ----------------------------------
def analyze_majorpass(data):
    client = OpenAI(api_key=openai_api_key)

    prompt = f"""
    사용자의 전공과 학업 상태를 기반으로
    전공을 커리어 자산으로 재해석하라.

    1. 현재 상태 진단
    2. 전공에서 이미 확보한 커리어 자산
    3. 광고/AX 분야 연결 전략
    4. 연세대학교 본캠퍼스 기준 추천 학과 (실제 학과명)

    사용자 정보:
    전공: {data['major']}
    학기: {data['semester']}
    전공 학점: {data['major_credit']}
    교양 학점: {data['liberal_credit']}
    GPA: {data['gpa']}
    관심 진로: {data['career_interest']}
    전공 계획: {data['change_major']}
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 커리어 전략 컨설턴트다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return res.choices[0].message.content.split("\n\n")

# ----------------------------------
# Result
# ----------------------------------
if analyze:
    if not openai_api_key:
        st.error("API Key를 입력해주세요.")
    else:
        with st.spinner("전공을 커리어 자산으로 변환 중..."):
            sections = analyze_majorpass({
                "major": major,
                "semester": semester,
                "major_credit": major_credit,
                "liberal_credit": liberal_credit,
                "gpa": gpa,
                "career_interest": career_interest,
                "change_major": change_major
            })

        titles = [
            "현재 상태 진단",
            "전공 커리어 자산",
            "광고/AX 연결 전략",
            "연세대 추천 학과"
        ]

        st.markdown("## 분석 결과")
        st.markdown('<div class="flip-grid">', unsafe_allow_html=True)

        for t, c in zip(titles, sections):
            st.markdown(f"""
            <div class="flip-card">
              <div class="flip-inner">
                <div class="flip-front">{t}</div>
                <div class="flip-back">{c}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)










