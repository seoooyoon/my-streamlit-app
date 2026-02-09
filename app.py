import re
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
# CARD COMPONENT (내용이 모두 보이도록: 높이 자동 추정 + 스크롤 최소화)
# -----------------------------
if "card_seq" not in st.session_state:
    st.session_state.card_seq = 0

def _estimate_height_from_html(html_str: str) -> int:
    """
    카드 뒷면 텍스트가 길어도 '최대한' 잘 보이도록 iframe height를 넉넉히 추정합니다.
    (Streamlit components iframe은 완전한 자동 리사이즈가 제한적이라, 추정치로 해결)
    """
    plain = re.sub(r"<[^>]*>", "", html_str or "")
    plain = re.sub(r"\s+", " ", plain).strip()
    # 대략 45~55자 = 1줄로 가정하여 줄 수 추정
    approx_lines = max(10, len(plain) // 52)
    height = 260 + approx_lines * 22
    return max(520, min(height, 1100))

def flip_card(title, content, emoji):
    st.session_state.card_seq += 1
    key = st.session_state.card_seq
    iframe_h = _estimate_height_from_html(content)

    components.html(f"""
    <style>
    .card-container-{key} {{
        width: 100%;
        perspective: 1200px;
        margin-bottom: 40px;
    }}

    /* 높이를 '고정'하지 않고, JS가 front/back 중 큰 높이로 맞춥니다 */
    .card-{key} {{
        width: 100%;
        position: relative;
        transition: transform 0.8s;
        transform-style: preserve-3d;
        cursor: pointer;
    }}
    .card-{key}.flip {{
        transform: rotateY(180deg);
    }}

    .card-face-{key} {{
        position: absolute;
        inset: 0;
        backface-visibility: hidden;
        border-radius: 18px;
        padding: 28px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        box-sizing: border-box;
    }}

    .card-front-{key} {{
        background: #ffffff;
        font-size: 1.6rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
    }}

    .card-back-{key} {{
        background: #1A1A1A;
        color: #ffffff;
        transform: rotateY(180deg);
        font-size: 1.02rem;
        line-height: 1.9;

        /* ✅ 스크롤을 없애고(또는 최소화하고), 줄글이 자연스럽게 이어지도록 */
        overflow: visible;
        word-break: keep-all;
        white-space: normal;
    }}

    /* 줄글 가독성: 문단 간격 */
    .card-back-{key} p {{
        margin: 0 0 1rem 0;
    }}
    .card-back-{key} p:last-child {{
        margin-bottom: 0;
    }}
    </style>

    <div class="card-container-{key}" id="container-{key}">
        <div class="card-{key}" id="card-{key}">
            <div class="card-face-{key} card-front-{key}" id="front-{key}">
                {emoji}<br/>{title}
            </div>
            <div class="card-face-{key} card-back-{key}" id="back-{key}">
                {content}
            </div>
        </div>
    </div>

    <script>
      (function() {{
        const container = document.getElementById("container-{key}");
        const card = document.getElementById("card-{key}");
        const front = document.getElementById("front-{key}");
        const back  = document.getElementById("back-{key}");

        function syncHeights() {{
          // 앞/뒤 내용 중 더 큰 높이를 기준으로 카드 높이를 맞춥니다.
          const frontH = front.scrollHeight;
          const backH  = back.scrollHeight;
          const H = Math.max(frontH, backH);

          container.style.height = (H) + "px";
          card.style.height = (H) + "px";
          front.style.height = (H) + "px";
          back.style.height  = (H) + "px";
        }}

        // 초기 렌더/폰트 로딩/레이아웃 안정화 타이밍 대응
        window.addEventListener("load", syncHeights);
        setTimeout(syncHeights, 30);
        setTimeout(syncHeights, 200);

        // 클릭 시 flip + 높이 재정렬
        card.addEventListener("click", () => {{
          card.classList.toggle("flip");
          setTimeout(syncHeights, 60);
        }});

        // 혹시 iframe 폭이 변할 때(반응형)도 대응
        window.addEventListener("resize", () => {{
          setTimeout(syncHeights, 60);
        }});
      }})();
    </script>
    """, height=iframe_h)

# -----------------------------
# RESULT
# -----------------------------
if analyze:

    flip_card(
        "현재 상태 진단",
        f"""
        <p>
        지금 당신은 <b>{major}</b> 전공을 이수 중이며, 현재 학적 기준으로 <b>{semester}</b>에 해당합니다.
        이 시점은 “전공을 계속 가져갈지/확장할지/바꿀지” 같은 큰 결정을 서둘러 내리기보다,
        지금까지의 선택과 경험이 어떤 방향성을 만들고 있는지 <b>하나의 서사로 정리</b>하는 것이 특히 중요한 구간입니다.
        </p>

        <p>
        또한 GPA <b>{gpa}</b>는 분명 의미 있는 지표이지만, 지금 단계에서는 성적 그 자체보다
        “내가 무엇을 잘하고, 어떤 방식으로 성장했으며, 무엇을 더 쌓아야 하는가”를 설명할 수 있는
        <b>근거</b>로 쓰일 때 훨씬 강해집니다. 즉, 성적은 결론이 아니라
        당신의 학습 방식과 역량 축적을 보여주는 <b>데이터</b>가 되는 것이죠.
        </p>

        <p>
        특히 당신이 적어준 관심 분야인 <b>{interest}</b>는 단순한 “흥미 목록”이 아니라,
        앞으로의 과목 선택, 프로젝트 참여, 대외활동, 포트폴리오 구성까지 연결되는
        <b>핵심 나침반</b>이 됩니다. 지금은 이 관심사가 “전공과 어떻게 연결되는지”,
        그리고 “어떤 형태의 결과물(프로젝트/리서치/콘텐츠/인턴 등)”로 증명될 수 있는지를
        구체화하기 시작하기 좋은 시점입니다.
        </p>

        <p>
        정리하면, 지금의 목표는 완벽한 결정을 내리는 것이 아니라
        “내가 가진 재료(전공 경험/성적/활동/관심사)를 한 장의 지도처럼 펼쳐두는 것”입니다.
        그 지도가 선명해질수록 다음 선택은 훨씬 덜 불안해집니다.
        </p>
        """,
        "📊"
    )

    flip_card(
        "전공 기반 전략 방향",
        f"""
        <p>
        현재까지 전공 이수 학점은 <b>{major_credit}학점</b>, 교양 이수 학점은 <b>{liberal_credit}학점</b>입니다.
        이 숫자는 단순히 “얼마나 들었는가”의 문제가 아니라, 당신이 이미 투자한 시간과 노력,
        그리고 그 과정에서 얻은 개념/기술/사고방식이 어느 정도 축적되었는지를 보여줍니다.
        </p>

        <p>
        당신이 선택한 전공 계획 <b>{plan}</b>은 제도 선택처럼 보이지만,
        실제로는 “지금까지의 전공 경험을 커리어 관점에서 어떻게 활용할 것인가”라는
        <b>전략 문제</b>에 가깝습니다. 본전공을 유지하든, 복수전공을 하든, 전과를 하든
        핵심은 하나입니다. <b>설명 가능한 성장 경로</b>로 이어지느냐입니다.
        </p>

        <p>
        예를 들어, 전공에서 배운 핵심 역량(분석력/문제정의/실험/리서치/설계/글쓰기/커뮤니케이션 등)을
        관심 분야(<b>{interest}</b>)가 요구하는 역량과 연결해보세요.
        “전공에서 A를 배웠고, 그 과정에서 B를 해봤으며, 그래서 관심 분야에서 C를 할 수 있다”처럼
        <b>이야기의 다리</b>가 생기면 선택의 부담이 줄어듭니다.
        </p>

        <p>
        중요한 건 전공을 바꾸는지 여부보다, 기존 전공에서 이미 확보한 자산을
        다음 선택에서도 낭비하지 않고 <b>재사용</b>하는 방식입니다.
        지금까지의 전공 경험을 “버릴 것/가질 것”으로 나누기보다,
        “어떤 형태로 재포장하면 가치가 커지는가”로 접근하면 전략이 훨씬 유연해집니다.
        </p>
        """,
        "🧭"
    )

    flip_card(
        "다음 학기 전략적 포인트",
        f"""
        <p>
        다음 학기의 핵심 목표는 ‘결정’이 아니라 <b>정리</b>입니다.
        정리가 잘 되면 결정은 자연스럽게 따라오고, 정리가 안 된 상태에서 내린 결정은
        작은 변수에도 쉽게 흔들립니다. 그래서 다음 학기는
        “내가 어떤 학생(또는 예비 직무인)인지”를 더 명확히 만드는 학기로 설계하는 게 좋습니다.
        </p>

        <p>
        먼저, 지금까지 수강한 전공 과목/프로젝트/과제/활동을 떠올려
        ① 무엇을 했는지(행동), ② 무엇이 어려웠는지(문제), ③ 어떻게 해결했는지(전략),
        ④ 무엇이 남았는지(성과/배움) 형태로 3~5개만이라도 정리해보세요.
        이때 관심 분야인 <b>{interest}</b>와 연결되는 키워드가 어디에 있었는지를 표시하면
        “나는 이쪽으로 가면 설명이 잘 된다”는 감각이 생깁니다.
        </p>

        <p>
        그다음, 다음 학기에는 ‘강의 선택’도 중요하지만,
        그 강의가 끝났을 때 남는 산출물이 무엇인지가 더 중요합니다.
        보고서/기획서/리서치 결과/프로토타입/데이터 분석 리포트/포트폴리오 글 등
        <b>증거물</b>이 남는 과목과 활동을 우선순위로 두면,
        선택의 결과가 “말”이 아니라 “자료”로 남게 됩니다.
        </p>

        <p>
        마지막으로, 지금 느끼는 불안은 아주 자연스러운 신호입니다.
        다만 그 불안을 ‘결정’으로 잠재우려 하면 더 커질 수 있고,
        ‘정리’로 다루면 빠르게 작아집니다. 다음 학기엔
        “내가 어떤 선택을 해도 설명할 수 있는 상태”를 만드는 데 집중해보세요.
        그 상태가 만들어지면 전공 유지/복수전공/전과 중
        어떤 선택이 가장 자연스럽게 이어지는지 스스로 보이기 시작할 것입니다.
        </p>
        """,
        "📝"
    )

    st.markdown("---")
    st.markdown(
        "✨ **MajorPass는 선택을 대신하지 않습니다. 대신, 선택을 덜 불안하게 만듭니다.**"
    )
