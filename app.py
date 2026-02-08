import streamlit as st
import time
from openai import OpenAI

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(
    page_title="MajorPass",
    layout="wide"
)

# ----------------------------------
# Global Style (Readable Modern)
# ----------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
    background-color: #F6F6F4;
    color: #111111;
}

h1, h2, h3 {
    color: #111111;
}

.card {
    background: white;
    padding: 32px;
    border-radius: 20px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.06);
    margin-bottom: 24px;
}

/* Splash */
.splash {
    height: 90vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

/* Flip Cards */
.flip-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 36px;
}

.flip-card {
    perspective: 1000px;
}

.flip-inner {
    position: relative;
    width: 100%;
    height: 280px;
    transition: transform 0.8s;
    transform-style: preserve-3d;
}

.flip-card:hover .flip-inner {
    transform: rotateY(180deg);
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
    padding: 28px;
    text-align: center;
}

.flip-front {
    background: #111111;
    color: white;
    font-weight: 700;
    font-size: 1.2rem;
}

.flip-back {
    background: white;
    color: #111111;
    transform: rotateY(180deg);
    border-radius: 20px;
    font-size: 0.95rem;
    line-height: 1.6;
    overflow-y: auto;
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
        <h1 style="font-size:5.5rem;font-weight:800;">MajorPass</h1>
        <p style="font-size:1.6rem;">전공을 커리어 자산으로 정리합니다</p>
        <p style="opacity:0.6;">Path to PASS!</p>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(3)
    st.session_state.splash_done = True
    st.rerun()

# ----------------------------------
# Sidebar
# ----------------------------------
st.sidebar.title("설정")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# ----------------------------------
# User Input
# ----------------------------------
st.markdown("## 현재 나의 상황")

st.markdown('<div class="card">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    major = st.text_input("현재 전공 (풀네임)")
    semester = st.selectbox(
        "재학 학기",
        [f"{y}학년 {s}학기" for y in range(1,5) for s in ["1","2"]]
    )
    career = st.text_input("관심 진로 분야")

with col2:
    major_credit = st.number_input("전공 이수 학점", 0, 200, 60)
    liberal_credit = st.number_input("교양 이수 학점", 0, 200, 40)
    gpa = st.slider("전체 GPA", 0.0, 4.5, 3.5, 0.1)

plan = st.radio(
    "전공 계획",
    ["본전공 유지", "복수전공 희망", "전과 희망", "아직 고민 중"]
)

st.markdown('</div>', unsafe_allow_html=True)

analyze = st.button("MajorPass 분석 시작", use_container_width=True)

# ----------------------------------
# OpenAI Analysis
# ----------------------------------
def analyze_majorpass():
    client = OpenAI(api_key=api_key)

    prompt = f"""
    사용자의 전공과 학업 상태를 분석하여
    전공을 커리어 자산 관점에서 재해석하라.

    1. 현재 상태 진단
    2. 전공에서 이미 확보한 커리어 자산
    3. 광고/AX 분야 연결 전략
    4. 연세대학교 본캠퍼스 기준 추천 학과

    전공: {major}
    학기: {semester}
    전공 학점: {major_credit}
    교양 학점: {liberal_credit}
    GPA: {gpa}
    관심 진로: {career}
    전공 계획: {plan}
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 대학생 커리어 전략 컨설턴트다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return res.choices[0].message.content.split("\n\n")

# ----------------------------------
# Result
# ----------------------------------
if analyze:
    if not api_key:
        st.error("OpenAI API Key를 입력해주세요.")
    else:
        with st.spinner("전공을 커리어 자산으로 재정리 중..."):
            sections = analyze_majorpass()

        titles = [
            "현재 상태 진단",
            "전공 커리어 자산",
            "광고 / AX 연결 전략",
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

        # Input Summary
        summary = f"""
전공: {major}
학기: {semester}
전공 학점: {major_credit}
교양 학점: {liberal_credit}
GPA: {gpa}
관심 진로: {career}
전공 계획: {plan}
"""

        st.markdown("## 이 결과를 만든 입력값")
        st.markdown(f"<div class='card'><pre>{summary}</pre></div>", unsafe_allow_html=True)

        # Download
        st.download_button(
            label="📄 결과 텍스트 저장",
            data="\n\n".join(sections),
            file_name="MajorPass_Result.txt",
            mime="text/plain"
        )

