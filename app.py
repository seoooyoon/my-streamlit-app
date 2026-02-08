import streamlit as st
import time

# ----------------------
# 기본 설정
# ----------------------
st.set_page_config(
    page_title="Major: Path to Pass",
    layout="wide"
)

# ----------------------
# 전체 배경 & 카드 스타일
# ----------------------
st.markdown("""
<style>
body {
    background-color: #FFF8CC;
}

.stApp {
    background-color: #FFF8CC;
}

/* 타이틀 페이드 */
.fade-title {
    text-align: center;
    font-size: 48px;
    font-weight: 800;
    margin-top: 200px;
    animation: fadeOut 3s forwards;
}

@keyframes fadeOut {
    0% { opacity: 1; }
    70% { opacity: 1; }
    100% { opacity: 0; }
}

/* 카드 컨테이너 */
.card-container {
    perspective: 1200px;
    width: 100%;
    height: 320px;
    margin-bottom: 40px;
}

/* 카드 */
.card {
    width: 100%;
    height: 100%;
    background-color: transparent;
    position: relative;
    transform-style: preserve-3d;
    transition: transform 0.8s;
    cursor: pointer;
}

/* 뒤집힘 */
.card.flipped {
    transform: rotateY(180deg);
}

/* 카드 앞/뒤 공통 */
.card-face {
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 20px;
    padding: 30px;
    box-sizing: border-box;
    backface-visibility: hidden;
    overflow-y: auto;
    word-break: keep-all;
    line-height: 1.7;
}

/* 앞면 */
.card-front {
    background-color: #111;
    color: #FFF;
    font-size: 22px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* 뒷면 */
.card-back {
    background-color: #1C1C1C;
    color: #F2F2F2;
    transform: rotateY(180deg);
    font-size: 16px;
}

/* 스크롤바 정리 */
.card-face::-webkit-scrollbar {
    width: 6px;
}
.card-face::-webkit-scrollbar-thumb {
    background-color: #666;
    border-radius: 3px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------
# 세션 상태
# ----------------------
if "show_main" not in st.session_state:
    st.session_state.show_main = False

if "show_result" not in st.session_state:
    st.session_state.show_result = False

# ----------------------
# 인트로 화면
# ----------------------
if not st.session_state.show_main:
    st.markdown("""
    <div class="fade-title">
        Major : Path to Pass
    </div>
    """, unsafe_allow_html=True)
    time.sleep(3)
    st.session_state.show_main = True
    st.experimental_rerun()

# ----------------------
# 메인 화면
# ----------------------
st.title("🎓 나의 전공 선택을 정리하는 시간")

st.markdown("### 나의 현재 상황")

current_status = st.text_area(
    "지금 나의 고민과 상황을 자유롭게 적어주세요",
    height=120
)

interest = st.text_input(
    "현재 가장 관심 있는 분야 (예: 브랜딩, 공간, 콘텐츠, UX 등)"
)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🔍 분석 결과 확인하기"):
    st.session_state.show_result = True

# ----------------------
# 분석 결과
# ----------------------
if st.session_state.show_result:

    st.markdown("---")
    st.subheader("📌 맞춤 분석 결과")

    result_text = """
이번 학기 당신에게 가장 중요한 키워드는 ‘결정’이 아니라 ‘정리’입니다.  
아직 명확한 진로가 보이지 않는 상태는 실패가 아니라, 오히려 매우 건강한 과정에 가깝습니다.  
지금까지 수강한 전공 과목과 프로젝트, 그리고 자연스럽게 흥미가 갔던 주제를 차분히 돌아볼 필요가 있습니다.  
특히 당신이 반복해서 관심을 보인 영역은 단순한 호기심이 아니라 방향성이 될 가능성이 큽니다.  

전공을 유지할지, 복수전공을 할지, 혹은 전과를 고려할지는 감정이 아닌 구조로 판단해야 합니다.  
현재 전공에서 ‘버티고 있는 이유’와 ‘재미를 느낀 순간’을 분리해서 생각해보는 것이 중요합니다.  
만약 과제의 결과보다 기획 과정이나 컨셉 설정에서 더 큰 만족을 느꼈다면, 이는 강력한 힌트입니다.  

관심 분야와 전공이 완전히 일치하지 않더라도 문제는 없습니다.  
요즘 산업은 하나의 전공보다는 전공 간의 연결 능력을 더 높게 평가합니다.  
지금 당신에게 필요한 것은 선택을 서두르는 용기가 아니라, 연결을 설계하는 시야입니다.  

정리된 상태에서 내린 선택은 흔들리지 않습니다.  
반대로 불안한 상태에서의 결정은 언제든 번복될 가능성이 큽니다.  
이번 학기는 답을 찾기보다, 스스로에 대한 이해도를 높이는 시간으로 설정해보세요.  
그 과정이 끝나면, 다음 선택은 생각보다 자연스럽게 이어질 것입니다.
"""

    # 카드 1
    st.markdown(f"""
    <div class="card-container" onclick="this.querySelector('.card').classList.toggle('flipped')">
        <div class="card">
            <div class="card-face card-front">
                📍 지금 당신에게 가장 중요한 한 가지
            </div>
            <div class="card-face card-back">
                {result_text}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 카드 2
    st.markdown("""
    <div class="card-container" onclick="this.querySelector('.card').classList.toggle('flipped')">
        <div class="card">
            <div class="card-face card-front">
                🔎 다음 단계에서 해보면 좋은 것
            </div>
            <div class="card-face card-back">
                ✔ 관심 분야와 연결되는 과제 기록 정리하기<br><br>
                ✔ 전공 수업 중 가장 몰입했던 순간 적어보기<br><br>
                ✔ 복수전공/연계전공 커리큘럼 비교해보기<br><br>
                ✔ ‘잘한 결과’보다 ‘재밌었던 과정’ 기준으로 정리하기
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.success("✨ 이 분석은 ‘결정’을 강요하지 않습니다. 당신이 흔들리지 않도록 돕기 위한 정리입니다.")

