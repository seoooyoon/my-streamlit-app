import streamlit as st
from openai import OpenAI

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="MajorPass",
    page_icon="🎓",
    layout="wide"
)

# -------------------------------------------------
# High-End CSS (Agency Style)
# -------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [data-testid="stApp"] {
    background-color: #0B0B0B;
    font-family: 'Inter', sans-serif;
    color: #FFFFFF;
}

section[data-testid="stSidebar"] {
    background-color: #0E0E0E;
}

h1 {
    font-size: 3rem;
    font-weight: 700;
    letter-spacing: -1px;
}

.subtitle {
    color: #B5B5B5;
    font-size: 1.1rem;
    margin-bottom: 40px;
}

.card {
    background: linear-gradient(145deg, #111111, #0C0C0C);
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}

.card-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 12px;
}

.card-desc {
    color: #CFCFCF;
    line-height: 1.6;
}

.stButton button {
    background: white;
    color: black;
    border-radius: 999px;
    padding: 10px 26px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton button:hover {
    transform: translateY(-1px);
    background: #EAEAEA;
}

.stTabs [data-baseweb="tab"] {
    font-size: 0.95rem;
    color: #999999;
}

.stTabs [aria-selected="true"] {
    color: white;
}

hr {
    border: none;
    border-top: 1px solid #222;
    margin: 40px 0;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Sidebar - API
# -------------------------------------------------
st.sidebar.title("API 설정")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

st.sidebar.markdown("---")
st.sidebar.markdown("""
**MajorPass**  
전공을 커리어 자산으로
""")

# -------------------------------------------------
# Yonsei Colleges (Main Campus)
# -------------------------------------------------
yonsei = {
    "문과대학": ["국어국문학과","영어영문학과","사학과","철학과","심리학과"],
    "상경대학": ["경제학부","응용통계학과"],
    "경영대학": ["경영학과"],
    "이과대학": ["수학과","물리학과","화학과","지구시스템과학과"],
    "공과대학": ["건축공학과","기계공학부","전기전자공학부","산업공학과"],
    "생활과학대학": ["실내건축학과","의류환경학과","식품영양학과"],
    "사회과학대학": ["정치외교학과","행정학과","언론홍보영상학부"],
    "의과대학": ["의예과"],
    "간호대학": ["간호학과"],
    "약학대학": ["약학과"],
    "언더우드국제대학": ["UIC"]
}

# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown("<h1>MajorPass</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Your major is not a limit. It’s a material.</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Input Section
# -------------------------------------------------
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    college = st.selectbox("단과대", yonsei.keys())
    major = st.selectbox("전공", yonsei[college])
    year = st.selectbox("학년", ["1학년","2학년","3학년","4학년"])
    goal = st.text_input("희망 진로", placeholder="광고, 브랜딩, UX, 콘텐츠 기획")
    concern = st.selectbox("고민 유형", ["전과","복수전공","전공 유지","진로 불안"])
    anxiety = st.text_area("불안 요소", placeholder="취업, 전공 활용도, 졸업 시기")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# OpenAI Function
# -------------------------------------------------
def analyze(info, api_key):
    client = OpenAI(api_key=api_key)

    prompt = f"""
당신은 광고회사 전략팀 출신의 대학생 진로 코치입니다.
톤은 차분하고 설득력 있게, 정보는 구조적으로 제시하세요.

[사용자 정보]
전공: {info['major']}
단과대: {info['college']}
학년: {info['year']}
희망 진로: {info['goal']}
고민: {info['concern']}
불안: {info['anxiety']}

아래 항목별로 나눠서 작성하세요.
### Situation
### Major as Asset
### Choice Comparison
### Recommended Strategy
### Next Actions
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.6
    )

    return res.choices[0].message.content

# -------------------------------------------------
# Run
# -------------------------------------------------
if st.button("분석 시작"):
    if not api_key:
        st.warning("API Key를 입력해주세요.")
    else:
        with st.spinner("Strategic thinking in progress..."):
            output = analyze({
                "college": college,
                "major": major,
                "year": year,
                "goal": goal,
                "concern": concern,
                "anxiety": anxiety
            }, api_key)

        sections = output.split("###")

        tabs = st.tabs(["Situation","Asset","Comparison","Strategy","Actions"])

        for tab, sec in zip(tabs, sections[1:]):
            with tab:
                st.markdown(f"<div class='card'><div class='card-desc'>{sec.strip()}</div></div>", unsafe_allow_html=True)






