import streamlit as st
import time
from openai import OpenAI

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="MajorPass",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CSS 스타일
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;600;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Pretendard', sans-serif;
    background-color: #FFF6D6;
}

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
    font-size: 5rem;
    font-weight: 800;
    letter-spacing: -2px;
}

.subtitle {
    font-size: 1.6rem;
    margin-top: 12px;
}

.tagline {
    font-size: 1.2rem;
    margin-top: 6px;
    opacity: 0.8;
}

.card {
    background: white;
    border-radius: 18px;
    padding: 28px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.08);
    height: 100%;
}

.card h3 {
    margin-top: 0;
}

.swiper {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 스플래시 화면
# -----------------------------
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

# -----------------------------
# 사이드바 (API 키)
# -----------------------------
st.sidebar.title("🔑 API 설정")
openai_api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    help="결과 분석에 사용됩니다"
)

# -----------------------------
# 메인 입력 섹션
# -----------------------------
st.markdown("## 🧭 나의 현재 상황 입력")

col1, col2 = st.columns(2)

with col1:
    major = st.text_input("현재 전공 (풀네임으로 작성)", placeholder="예: 실내건축학과")
    semester = st.selectbox(
        "현재 학년 / 학기",
        [f"{y}학년 {s}학기" for y in range(1,5) for s in ["1","2"]]
    )
    career_interest = st.text_input(
        "관심 진로 분야",
        placeholder="예: 광고기획, 브랜드 전략, UX, AX"
    )

with col2:
    major_credit = st.number_input("전공 이수 학점", 0, 200, 60)
    liberal_credit = st.number_input("교양 이수 학점", 0, 200, 40)
    gpa = st.slider("전체 GPA", 0.0, 4.5, 3.5, 0.1)

change_major = st.radio(
    "복수전공 / 전과 희망 여부",
    ["아직 고민 중", "복수전공 희망", "전과 희망"]
)

# -----------------------------
# 분석 버튼
# -----------------------------
st.markdown("---")
analyze = st.button("🚀 MajorPass 분석 시작", use_container_width=True)

# -----------------------------
# OpenAI 분석 함수 (신규 API)
# -----------------------------
def get_majorpass_advice(data):
    client = OpenAI(api_key=openai_api_key)

    prompt = f"""
    사용자의 정보를 바탕으로 전공을 커리어 자산으로 재해석하고
    광고/AX/브랜드 전략 관점에서 분석해줘.

    [사용자 정보]
    전공: {data['major']}
    학기: {data['semester']}
    전공 학점: {data['major_credit']}
    교양 학점: {data['liberal_credit']}
    GPA: {data['gpa']}
    관심 진로: {data['career_interest']}
    전과/복수전공: {data['change_major']}

    아래 4개 섹션으로 나눠서 답변:
    1. 현재 상태 진단
    2. 전공에서 이미 확보한 커리어 자산
    3. 광고/AX로 연결되는 구체적 포인트
    4. 연세대 본캠퍼스 기준 추천 학과 (구체적 학과명)
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 커리어 전략 컨설턴트다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content

# -----------------------------
# 결과 출력 (카드 슬라이드)
# -----------------------------
if analyze:
    if not openai_api_key:
        st.error("OpenAI API Key를 입력해주세요.")
    else:
        with st.spinner("MajorPass가 커리어 자산을 정리 중입니다..."):
            result = get_majorpass_advice({
                "major": major,
                "semester": semester,
                "major_credit": major_credit,
                "liberal_credit": liberal_credit,
                "gpa": gpa,
                "career_interest": career_interest,
                "change_major": change_major
            })

        sections = result.split("\n\n")

        st.markdown("## 📊 분석 결과")

        st.markdown('<div class="swiper">', unsafe_allow_html=True)
        for sec in sections:
            st.markdown(f"""
            <div class="card">
                <h3>{sec.splitlines()[0]}</h3>
                <p>{"<br>".join(sec.splitlines()[1:])}</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)









