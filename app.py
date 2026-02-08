import streamlit as st
import openai
import os

# OpenAI 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# -------------------------------
# AI 응답 함수
# -------------------------------
def generate_majorpass_response(user_info):
    prompt = f"""
당신은 대학생 진로 상담 전문 AI이자,
'전공을 커리어 자산으로 변환하는 코치'입니다.

[사용자 정보]
- 전공: {user_info['major']}
- 학년: {user_info['year']}
- 희망 진로: {user_info['career']}
- 고민 유형: {user_info['concern']}
- 불안 요소: {user_info['anxiety']}

아래 순서로 답변해주세요.

1. 사용자의 상황 요약 (공감 중심)
2. 현재 전공을 희망 진로에 맞게 재해석한 강점
3. 전과 / 복수전공 / 전공 유지+커리어 전환 비교
4. 전공을 ‘커리어 자산’으로 쓰는 전략
5. 지금 당장 할 수 있는 To-do 로드맵 (단계별)

결정을 강요하지 말고, 판단 기준을 제시해주세요.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 따뜻하지만 현실적인 진로 코치다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content


# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="MajorPass", page_icon="🎓", layout="centered")

st.title("🎓 MajorPass")
st.subheader("Path to Pass — 전공을 커리어 자산으로")

st.markdown("""
**MajorPass는 제가 실제로 겪은 고민에서 출발한 앱입니다.**

- 실내건축학과 재학  
- 광고 분야 진로 희망  
- 전과를 해야 할지, 전공을 버려야 할지 고민  
- 그리고 깨달았습니다.  
👉 *전공은 바꾸지 않아도, 다르게 쓸 수 있다는 것.*

MajorPass는  
**전공을 ‘문제’가 아니라 ‘자산’으로 바꾸는 AI 진로 상담 앱**입니다.
""")

st.divider()

# -------------------------------
# 사용자 입력
# -------------------------------
st.header("📝 나의 상황 입력")

major = st.text_input("현재 전공", placeholder="예: 실내건축학과")
year = st.selectbox("학년", ["1학년", "2학년", "3학년", "4학년"])
career = st.text_input("희망 진로 / 관심 분야", placeholder="예: 광고, 공간 브랜딩, UX")
concern = st.selectbox(
    "현재 가장 큰 고민",
    ["전과", "복수전공", "전공 유지", "진로 불안"]
)
anxiety = st.text_area(
    "불안하거나 걱정되는 점",
    placeholder="예: 취업 가능성, 포트폴리오, 늦어질 졸업"
)

# -------------------------------
# 실행 버튼
# -------------------------------
if st.button("🔍 MajorPass 분석 시작"):
    if not major or not career:
        st.warning("전공과 희망 진로는 꼭 입력해주세요.")
    else:
        user_info = {
            "major": major,
            "year": year,
            "career": career,
            "concern": concern,
            "anxiety": anxiety
        }

        with st.spinner("AI가 전공을 커리어 자산으로 변환 중입니다..."):
            result = generate_majorpass_response(user_info)

        st.divider()
        st.header("📊 MajorPass 결과 리포트")
        st.markdown(result)

        st.success("✔️ 결정은 당신의 몫입니다. MajorPass는 기준을 제공합니다.")




