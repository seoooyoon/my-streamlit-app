import streamlit as st
import openai

# -------------------------------------------------
# 페이지 설정
# -------------------------------------------------
st.set_page_config(
    page_title="MajorPass",
    page_icon="🎓",
    layout="centered"
)

# -------------------------------------------------
# 커스텀 CSS (블랙 배경 + 화이트 도트)
# -------------------------------------------------
st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background-color: #0f0f0f;
    background-image: radial-gradient(#ffffff 0.6px, transparent 0.6px);
    background-size: 22px 22px;
    color: #ffffff;
}

h1, h2, h3, h4, h5, h6, p, label, div {
    color: #ffffff !important;
}

[data-testid="stSidebar"] {
    background-color: #111111;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div {
    background-color: #1c1c1c;
    color: white;
}

.stButton button {
    background-color: white;
    color: black;
    border-radius: 8px;
    font-weight: 600;
}

.stButton button:hover {
    background-color: #dddddd;
    color: black;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 사이드바 - API Key 입력
# -------------------------------------------------
st.sidebar.title("🔑 API 설정")
api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    help="세션 동안만 사용됩니다."
)

if api_key:
    openai.api_key = api_key

st.sidebar.markdown("---")
st.sidebar.markdown("**MajorPass**  \n전공을 커리어 자산으로")

# -------------------------------------------------
# 연세대학교 본캠퍼스 단과대 / 학과 데이터
# -------------------------------------------------
yonsei_departments = {
    "문과대학": ["국어국문학과", "영어영문학과", "사학과", "철학과"],
    "사회과학대학": ["정치외교학과", "행정학과", "사회학과", "언론홍보영상학부"],
    "경영대학": ["경영학과"],
    "이과대학": ["수학과", "물리학과", "화학과"],
    "공과대학": ["건축공학과", "전기전자공학부", "기계공학부"],
    "생활과학대학": ["의류환경학과", "실내건축학과"],
    "교육과학대학": ["교육학과"],
    "언더우드국제대학": ["UIC"]
}

# -------------------------------------------------
# 메인 UI
# -------------------------------------------------
st.title("🎓 MajorPass")
st.subheader("Path to Pass")
st.markdown("""
전과를 해야 할지,  
복수전공을 해야 할지,  
아니면 전공을 유지한 채 진로를 바꿀 수 있을지.

MajorPass는 **결정을 대신하지 않습니다.**  
대신, **판단 기준과 다음 행동**을 제공합니다.
""")

st.divider()

# -------------------------------------------------
# 사용자 입력
# -------------------------------------------------
st.header("📝 나의 상황")

college = st.selectbox(
    "단과대학 선택 (연세대 본캠퍼스)",
    list(yonsei_departments.keys())
)

department = st.selectbox(
    "전공 선택",
    yonsei_departments[college]
)

year = st.selectbox(
    "현재 학년",
    ["1학년", "2학년", "3학년", "4학년"]
)

career_goal = st.text_input(
    "희망 진로 / 관심 분야",
    placeholder="예: 광고, 브랜딩, UX, 콘텐츠 기획"
)

concern_type = st.selectbox(
    "현재 가장 큰 고민",
    ["전과", "복수전공", "전공 유지", "진로 불안"]
)

anxiety = st.text_area(
    "불안하거나 걱정되는 점",
    placeholder="예: 취업 가능성, 전공 활용도, 졸업 시기"
)

# -------------------------------------------------
# AI 함수
# -------------------------------------------------
def get_majorpass_advice(info):
    prompt = f"""
당신은 대학생 진로 상담 전문 AI 코치입니다.
목표는 전공을 '버릴지 말지'가 아니라,
전공을 커리어 자산으로 전환하는 방법을 제시하는 것입니다.

[사용자 정보]
- 학교: 연세대학교 본캠퍼스
- 단과대: {info['college']}
- 전공: {info['department']}
- 학년: {info['year']}
- 희망 진로: {info['career']}
- 고민 유형: {info['concern']}
- 불안 요소: {info['anxiety']}

다음 순서로 답변하세요:

1. 사용자의 현재 상황 요약 + 공감
2. 현재 전공에서 얻은 핵심 역량 정리
3. 해당 역량을 희망 진로 관점에서 재해석
4. 전과 / 복수전공 / 전공 유지 비교 (현실 기준)
5. 전공을 커리어 자산으로 활용하는 전략
6. 지금부터 할 수 있는 단계별 To-do

결정을 강요하지 말고,
판단 기준과 선택의 근거를 제시하세요.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 현실적이고 공감 능력이 높은 진로 코치다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# -------------------------------------------------
# 실행 버튼
# -------------------------------------------------
if st.button("🚀 MajorPass 분석 시작"):
    if not api_key:
        st.warning("사이드바에 OpenAI API Key를 입력해주세요.")
    elif not career_goal:
        st.warning("희망 진로를 입력해주세요.")
    else:
        user_data = {
            "college": college,
            "department": department,
            "year": year,
            "career": career_goal,
            "concern": concern_type,
            "anxiety": anxiety
        }

        with st.spinner("전공을 커리어 자산으로 분석 중입니다..."):
            result = get_majorpass_advice(user_data)

        st.divider()
        st.header("📊 MajorPass 결과")
        st.markdown(result)
        st.success("결정은 당신의 몫입니다. MajorPass는 기준을 제공합니다.")





