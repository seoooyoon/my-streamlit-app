import streamlit as st
import time
from openai import OpenAI

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="MajorPass",
    page_icon="🎓",
    layout="centered"
)

# -------------------------------------------------
# Soft Yellow Design
# -------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [data-testid="stApp"] {
    background-color: #FFF6D8;
    font-family: 'Inter', sans-serif;
    color: #1C1C1C;
}

h1 {
    font-size: 3.2rem;
    font-weight: 700;
    text-align: center;
}

.subtitle {
    text-align: center;
    color: #555;
    margin-top: -10px;
    margin-bottom: 40px;
}

.card {
    background-color: #FFFFFF;
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}

.stButton button {
    background-color: #1C1C1C;
    color: white;
    border-radius: 999px;
    padding: 10px 28px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Intro Animation (3 sec)
# -------------------------------------------------
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    intro = st.empty()
    intro.markdown("<h1>MajorPass</h1>", unsafe_allow_html=True)
    time.sleep(3)
    intro.empty()
    st.session_state.intro_done = True
    st.rerun()

# -------------------------------------------------
# Sidebar - API
# -------------------------------------------------
st.sidebar.title("API 설정")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown("<h1>MajorPass</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>전공을 커리어 자산으로 정리합니다</div>", unsafe_allow_html=True)

# -------------------------------------------------
# User Input
# -------------------------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)

major = st.text_input(
    "현재 전공 (풀네임으로 작성)",
    placeholder="예: 실내건축학과"
)

semester = st.selectbox(
    "현재 재학 학기",
    [f"{y}학년 {s}학기" for y in range(1,5) for s in [1,2]]
)

career_goal = st.text_input(
    "희망 진로 / 관심 분야",
    placeholder="예: 광고기획, 브랜드 전략, UX 기획"
)

concern = st.selectbox(
    "현재 가장 큰 고민",
    ["전과", "복수전공", "전공 유지", "진로 불안"]
)

anxiety = st.text_area(
    "불안하거나 고민되는 점",
    placeholder="취업 가능성, 전공 활용도, 졸업 이후 진로 등"
)

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Academic Status
# -------------------------------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📊 학업 현황")

major_credits = st.number_input("전공 이수 학점", min_value=0, max_value=200)
general_credits = st.number_input("교양 이수 학점", min_value=0, max_value=200)
gpa = st.number_input("전체 GPA", min_value=0.0, max_value=4.5, step=0.01)

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# OpenAI Logic
# -------------------------------------------------
def analyze(info, api_key):
    client = OpenAI(api_key=api_key)

    prompt = f"""
당신은 대학생 진로 상담 전문 코치입니다.
결정을 강요하지 말고, 판단 기준과 다음 행동을 제시하세요.

[사용자 상황]
전공: {info['major']}
현재 학기: {info['semester']}
희망 진로: {info['career']}
전공 이수 학점: {info['major_credits']}
교양 이수 학점: {info['general_credits']}
전체 GPA: {info['gpa']}
고민 유형: {info['concern']}
불안 요소: {info['anxiety']}

다음 항목으로 나누어 설명하세요:
1. 현재 상황 요약
2. 전공에서 축적된 역량
3. 희망 진로와의 연결 가능성
4. 선택지 비교 (전과 / 복수 / 유지)
5. 추천 전략
6. 다음 학기부터 할 수 있는 To-do
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )

    return res.choices[0].message.content

# -------------------------------------------------
# Run
# -------------------------------------------------
if st.button("분석 시작"):
    if not api_key:
        st.warning("API Key를 입력해주세요.")
    elif not major or not career_goal:
        st.warning("전공과 희망 진로를 모두 입력해주세요.")
    else:
        with st.spinner("당신의 전공을 커리어 자산으로 분석 중입니다..."):
            result = analyze({
                "major": major,
                "semester": semester,
                "career": career_goal,
                "major_credits": major_credits,
                "general_credits": general_credits,
                "gpa": gpa,
                "concern": concern,
                "anxiety": anxiety
            }, api_key)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("📌 MajorPass 분석 결과")
        st.markdown(result)
        st.markdown("</div>", unsafe_allow_html=True)








