import streamlit as st
import time
from openai import OpenAI

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="MajorPass",
    layout="wide"
)

# -------------------------------------------------
# Global Style (Soft Yellow + Readable)
# -------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
    background-color: #FFF6D8;
    color: #1A1A1A;
}

/* Splash */
.splash {
    height: 90vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

/* Card (input & summary) */
.card {
    background: #FFFFFF;
    padding: 32px;
    border-radius: 20px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.08);
    margin-bottom: 28px;
}

/* Flip Cards (Click-based) */
.flip-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 36px;
    margin-top: 30px;
}

.flip-wrapper input {
    display: none;
}

.flip-card {
    width: 100%;
    height: 300px;
    perspective: 1200px;
}

.flip-inner {
    position: relative;
    width: 100%;
    height: 100%;
    transition: transform 0.7s;
    transform-style: preserve-3d;
}

.flip-wrapper input:checked + .flip-card .flip-inner {
    transform: rotateY(180deg);
}

.flip-front, .flip-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    border-radius: 18px;
    padding: 28px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.flip-front {
    background: #FFFFFF;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 1.25rem;
    font-weight: 700;
    cursor: pointer;
}

.flip-back {
    background: #FFFFFF;
    transform: rotateY(180deg);
    font-size: 0.95rem;
    line-height: 1.6;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Splash Screen
# -------------------------------------------------
if "splash_done" not in st.session_state:
    st.session_state.splash_done = False

if not st.session_state.splash_done:
    st.markdown("""
    <div class="splash">
        <h1 style="font-size:5.8rem;font-weight:800;">MajorPass</h1>
        <p style="font-size:1.6rem;">전공을 커리어 자산으로 정리합니다</p>
        <p style="opacity:0.6;">Path to PASS!</p>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(3)
    st.session_state.splash_done = True
    st.rerun()

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
st.sidebar.title("🔑 설정")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# -------------------------------------------------
# User Input
# -------------------------------------------------
st.markdown("## ✍️ 현재 나의 상황")

st.markdown('<div class="card">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    major = st.text_input("현재 전공 (풀네임)")
    semester = st.selectbox(
        "재학 학기",
        [f"{y}학년 {s}학기" for y in range(1,5) for s in ["1","2"]]
    )
    career = st.text_input("관심 진로 분야 (예: 광고기획, BX, UX)")

with col2:
    major_credit = st.number_input("전공 이수 학점", 0, 200, 60)
    liberal_credit = st.number_input("교양 이수 학점", 0, 200, 40)
    gpa = st.slider("전체 GPA (4.3 만점)", 0.0, 4.3, 3.6, 0.1)

plan = st.radio(
    "전공 계획",
    ["본전공 유지", "복수전공 희망", "전과 희망", "아직 고민 중"]
)

st.markdown('</div>', unsafe_allow_html=True)

analyze = st.button("🚀 MajorPass 분석 시작", use_container_width=True)

# -------------------------------------------------
# OpenAI Analysis
# -------------------------------------------------
def analyze_majorpass():
    client = OpenAI(api_key=api_key)

    prompt = f"""
    사용자의 정보를 바탕으로 전공을 커리어 자산 관점에서 분석하라.

    반드시 아래 3개 섹션으로 나누어 작성하라.
    각 섹션은 줄글 + 불릿 혼합.

    1. 현재 상황 분석 (공감 포함)
    2. 전공 계획에 따른 현실적인 로드맵
    3. 지금부터 하면 좋은 대학생활 To-Do 리스트

    사용자 정보:
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
            {"role": "system", "content": "너는 대학생 진로 상담 전문 코치다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return res.choices[0].message.content.split("\n\n")

# -------------------------------------------------
# Result
# -------------------------------------------------
if analyze:
    if not api_key:
        st.error("OpenAI API Key를 입력해주세요.")
    else:
        with st.spinner("🧠 전공을 커리어 자산으로 해석 중..."):
            sections = analyze_majorpass()

        titles = [
            "🧠 현재 상황 분석",
            "🛠️ 전공 계획별 로드맵",
            "✅ 대학생활 To-Do List"
        ]

        st.markdown("## 📊 분석 결과")
        st.markdown('<div class="flip-grid">', unsafe_allow_html=True)

        for i, (title, content) in enumerate(zip(titles, sections)):
            st.markdown(f"""
            <div class="flip-wrapper">
                <input type="checkbox" id="flip{i}">
                <label for="flip{i}">
                    <div class="flip-card">
                        <div class="flip-inner">
                            <div class="flip-front">{title}<br><br>👉 클릭해서 보기</div>
                            <div class="flip-back">{content}</div>
                        </div>
                    </div>
                </label>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Input Summary
        st.markdown("## 🔍 이 결과를 만든 입력값")
        st.markdown(f"""
        <div class="card">
        <b>전공:</b> {major}<br>
        <b>학기:</b> {semester}<br>
        <b>전공 / 교양 학점:</b> {major_credit} / {liberal_credit}<br>
        <b>GPA:</b> {gpa} / 4.3<br>
        <b>관심 진로:</b> {career}<br>
        <b>전공 계획:</b> {plan}
        </div>
        """, unsafe_allow_html=True)

        # Download
        st.download_button(
            "📄 결과 텍스트 저장",
            data="\n\n".join(sections),
            file_name="MajorPass_Result.txt",
            mime="text/plain"
        )

