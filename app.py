# MajorPass (Yonsei Edition) - FIXED: bs4 의존성 제거 버전
# ✅ 핵심 수정:
# - BeautifulSoup(bs4) 사용을 전부 제거했습니다.
# - 연세대 공지/학사일정은 requests + 정규식 기반 "베스트 에포트" 파서로 표시합니다.
# - 수강편람은 포털/세션/JS 렌더링 이슈가 많아 자동 크롤링은 불안정 → "직접 붙여넣기"를 기본으로,
#   그래도 페이지 접근이 되면 키워드 존재 여부 정도만 체크합니다.
#
# requirements.txt (최소)
# streamlit
# requests
# openai   # (개인화 기능 쓸 때만 필요. 없으면 자동 폴백)

import re
import json
import datetime as dt
from typing import List, Dict, Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components
import requests

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="MajorPass", layout="wide")

# -----------------------------
# CONST (Yonsei sources)
# -----------------------------
YONSEI_NOTICE_URL = "https://www.yonsei.ac.kr/en_sc/1854/subview.do"  # Campus Life > Notice (ENG)
YONSEI_ACAD_CAL_URL = "https://www.yonsei.ac.kr/sc/373/subview.do"   # 학사일정(신촌·국제)
YONSEI_HANDBOOK_URL = "https://underwood1.yonsei.ac.kr/com/lgin/SsoCtr/initExtPageWork.do?link=handbList&locale=ko"  # 수강편람(포털)

DEFAULT_UA = {
    "User-Agent": "Mozilla/5.0 (MajorPass; Streamlit) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari"
}

KST = dt.timezone(dt.timedelta(hours=9))

# -----------------------------
# SIDEBAR – API KEY & DATA SETTINGS
# -----------------------------
with st.sidebar:
    st.markdown("## 🔑 API 설정")

    api_key_input = st.text_input(
        "OpenAI API Key",
        type="password",
        help="개인화 분석 고도화에 사용됩니다. (배포에서는 st.secrets 사용 권장)"
    )
    openai_api_key = api_key_input or st.secrets.get("OPENAI_API_KEY", "")

    st.markdown("---")
    st.markdown("## 🏫 연세대 데이터")
    use_yonsei_notice = st.checkbox("캠퍼스 공지 가져오기", value=True)
    use_yonsei_calendar = st.checkbox("학사일정 가져오기", value=True)
    use_yonsei_handbook = st.checkbox("수강편람(과목) 불러오기 시도", value=True)

    st.caption("※ 수강편람은 포털 연동 페이지라 자동 수집이 실패할 수 있어요. 실패 시 '대체 입력'으로 폴백합니다.")

    st.markdown("---")
    st.markdown("""
    **MajorPass는**
    입력된 정보를 저장하지 않습니다.  
    (단, OpenAI API를 사용할 경우 입력 내용이 API 요청으로 전달됩니다.)
    """)

# -----------------------------
# HTTP helpers
# -----------------------------
def _http_get(url: str, timeout: int = 15) -> str:
    r = requests.get(url, headers=DEFAULT_UA, timeout=timeout)
    r.raise_for_status()
    if r.encoding is None:
        r.encoding = "utf-8"
    return r.text

def _strip_tags(html: str) -> str:
    """HTML 태그 제거(가벼운 파서)"""
    html = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", html)
    html = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", html)
    html = re.sub(r"(?s)<[^>]+>", " ", html)
    html = html.replace("&nbsp;", " ").replace("&amp;", "&")
    html = re.sub(r"\s+", " ", html).strip()
    return html

# -----------------------------
# Yonsei: Notice fetch (regex based)
# -----------------------------
@st.cache_data(ttl=60 * 30)
def fetch_yonsei_notices(limit: int = 10) -> List[Dict[str, str]]:
    """
    Yonsei Campus Life Notice(영문) 페이지에서
    Date YYYY.MM.DD 패턴을 기반으로 제목을 베스트-에포트로 추출합니다.
    """
    html = _http_get(YONSEI_NOTICE_URL)

    # 링크 href도 함께 추출해보기
    # 패턴: <a ... href="..."> ... Date 2026.01.16 ...
    # (페이지 구조 바뀌어도 Date 패턴이 있으면 어느 정도 잡히도록)
    items: List[Dict[str, str]] = []

    # a태그 블록 단위로 잡아서 Date 있는 것만 필터
    for m in re.finditer(r"(?is)<a[^>]+href=\"([^\"]+)\"[^>]*>(.*?)</a>", html):
        href = m.group(1)
        inner = m.group(2)

        # Date 추출
        dm = re.search(r"Date\s*(\d{4}\.\d{2}\.\d{2})", inner)
        if not dm:
            continue
        date = dm.group(1)

        title = _strip_tags(inner)
        # "조회수" 같은 꼬리 제거 시도
        title = re.sub(r"조회수.*$", "", title).strip()
        title = re.sub(r"\s*Date\s*\d{4}\.\d{2}\.\d{2}.*$", "", title).strip()
        title = re.sub(r"^\d+\s*", "", title).strip()

        if len(title) < 8:
            continue

        if href.startswith("/"):
            href = "https://www.yonsei.ac.kr" + href

        items.append({"title": title, "date": date, "url": href})

    # 중복 제거(제목+날짜)
    uniq = {}
    for it in items:
        uniq[(it["title"], it["date"])] = it

    out = list(uniq.values())
    out.sort(key=lambda x: x["date"], reverse=True)
    return out[:limit]

# -----------------------------
# Yonsei: Academic calendar (regex based)
# -----------------------------
MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

@st.cache_data(ttl=60 * 60)
def fetch_yonsei_academic_calendar_upcoming(days_ahead: int = 60) -> List[Dict[str, str]]:
    """
    연세대 학사일정 페이지를 텍스트로 만든 뒤,
    Month 컨텍스트 + 날짜 라인을 regex로 훑어서 다가오는 일정만 추출합니다.
    """
    html = _http_get(YONSEI_ACAD_CAL_URL)
    text = _strip_tags(html)

    # 연도 추정
    year_guess = None
    m_year = re.search(r"(20\d{2})\s*[-–]?\s*[12]\s*학기", text)
    if m_year:
        year_guess = int(m_year.group(1))
    else:
        year_guess = dt.datetime.now(KST).year

    today = dt.datetime.now(KST).date()
    end = today + dt.timedelta(days=days_ahead)

    # Month 구간을 대략적으로 쪼개기: Month 이름 기준으로 split
    # split 결과에서 month를 알 수 있도록 finditer로 위치 추적
    month_positions = []
    for name, num in MONTH_MAP.items():
        for mm in re.finditer(rf"\b{name}\b", text):
            month_positions.append((mm.start(), num))
    month_positions.sort()

    # month_positions가 없으면 포기
    if not month_positions:
        return []

    # 각 month chunk 만들기
    chunks = []
    for i, (pos, month_num) in enumerate(month_positions):
        nxt = month_positions[i + 1][0] if i + 1 < len(month_positions) else len(text)
        chunks.append((month_num, text[pos:nxt]))

    events: List[Tuple[dt.date, str]] = []

    # 날짜 패턴 1: "03 (Tue) 개강" 형태가 텍스트에서 괄호 제거되며 "03 Tue 개강"처럼 될 수 있어
    # 그래서 좀 더 유연하게:
    # - 범위: 05 ~ 09 수강신청 ...
    # - 단일: 03 개강 ...
    range_pat = re.compile(r"\b(\d{1,2})\s*~\s*(\d{1,2})\s+([^0-9]{2,80})")
    one_pat   = re.compile(r"\b(\d{1,2})\s+([^0-9]{2,80})")

    for month_num, chunk in chunks:
        # 범위 먼저
        for rm in range_pat.finditer(chunk):
            d1, d2, desc = int(rm.group(1)), int(rm.group(2)), rm.group(3).strip()
            # 너무 일반 텍스트 오탐 제거
            if len(desc) < 2:
                continue
            try:
                start_date = dt.date(year_guess, month_num, d1)
                end_date = dt.date(year_guess, month_num, d2)
                if today <= end_date and start_date <= end:
                    events.append((start_date, f"{start_date.strftime('%m/%d')}~{end_date.strftime('%m/%d')} · {desc}"))
            except ValueError:
                pass

        # 단일 날짜
        for om in one_pat.finditer(chunk):
            d, desc = int(om.group(1)), om.group(2).strip()
            if len(desc) < 2:
                continue
            # 범위 패턴에 잡힌 것과 겹칠 수 있어 간단 방지
            if "~" in desc:
                continue
            try:
                date_obj = dt.date(year_guess, month_num, d)
                if today <= date_obj <= end:
                    events.append((date_obj, f"{date_obj.strftime('%m/%d')} · {desc}"))
            except ValueError:
                pass

    events.sort(key=lambda x: x[0])

    # 중복 제거
    uniq = {}
    for d, desc in events:
        uniq[(d.isoformat(), desc)] = {"date": d.isoformat(), "desc": desc}
    return list(uniq.values())

# -----------------------------
# Yonsei: Handbook best-effort (no bs4)
# -----------------------------
@st.cache_data(ttl=60 * 30)
def fetch_yonsei_handbook_courses_best_effort(year: int, semester: int, keyword: str, limit: int = 20) -> Dict[str, object]:
    """
    포털 연동/JS 렌더링 문제로 '자동 과목 리스트'는 보장 불가.
    - 페이지 접근만 확인 + keyword가 HTML(원문)에 있는지 정도로 힌트 제공.
    """
    if not keyword:
        return {"ok": False, "message": "키워드가 비어있어요.", "courses": []}
    try:
        html = _http_get(YONSEI_HANDBOOK_URL, timeout=15)
    except Exception as e:
        return {"ok": False, "message": f"수강편람 접근 실패: {e}", "courses": []}

    # 키워드가 원문에 포함되면 '가능성'만 알려주기
    found = keyword.lower() in html.lower()

    if found:
        return {
            "ok": False,
            "message": (
                "수강편람 페이지에는 접근했지만, 과목 데이터는 포털 세션/JS로 렌더링되어 "
                "이 앱에서 안정적으로 파싱하기 어렵습니다. "
                "포털에서 검색한 결과를 아래 '대체 입력'에 붙여넣어 주세요."
            ),
            "courses": []
        }
    else:
        return {
            "ok": False,
            "message": (
                "수강편람 자동 파싱은 어려워요(포털/세션/JS). "
                "포털에서 검색 결과를 '대체 입력'에 붙여넣어 주면 분석에 반영할게요."
            ),
            "courses": []
        }

# -----------------------------
# GLOBAL STYLE
# -----------------------------
st.markdown(
    """
<style>
html, body, [data-testid="stApp"] {
    background-color: #FFF6CC;
    color: #1A1A1A;
    font-family: 'Pretendard', 'Apple SD Gothic Neo', sans-serif;
}
.block-container { padding-top: 2rem; }
@keyframes fadeOut { 0% { opacity: 1; } 70% { opacity: 1; } 100% { opacity: 0; visibility: hidden; } }
.splash {
    height: 70vh; display: flex; flex-direction: column;
    justify-content: center; align-items: center;
    animation: fadeOut 3s forwards;
}
.major-title { font-size: 4.8rem; font-weight: 800; text-align: center; }
.major-sub { font-size: 1.4rem; text-align: center; margin-top: 0.5rem; }
.section-title { font-size: 1.8rem; font-weight: 700; margin: 3rem 0 1.2rem 0; }
.badge { display: inline-block; padding: .25rem .6rem; border-radius: 999px; background: #fff; border: 1px solid rgba(0,0,0,.08); font-size: .85rem; }
.small { font-size: .92rem; opacity: .9; }
</style>
""",
    unsafe_allow_html=True
)

# -----------------------------
# SPLASH
# -----------------------------
st.markdown(
    """
<div class="splash">
    <div class="major-title">MajorPass</div>
    <div class="major-sub">
        전공을 커리어 자산으로 정리합니다<br/>
        <b>Path to PASS!</b>
    </div>
</div>
""",
    unsafe_allow_html=True
)

# -----------------------------
# CAMPUS INFO (Yonsei) – top area
# -----------------------------
st.markdown("<div class='section-title'>🏫 연세대 캠퍼스 인포</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📌 공지", "🗓️ 학사일정(다가오는)", "📚 수강편람(과목)"])

with tab1:
    if use_yonsei_notice:
        try:
            notices = fetch_yonsei_notices(limit=10)
            if not notices:
                st.info("공지 데이터를 찾지 못했어요. (페이지 구조 변경/일시적 오류 가능)")
                st.caption(YONSEI_NOTICE_URL)
            else:
                for n in notices:
                    st.markdown(
                        f"- **{n['title']}**  <span class='badge'>{n['date']}</span>\n"
                        f"  \n  ↗ {n['url']}",
                        unsafe_allow_html=True
                    )
                st.caption(f"출처: {YONSEI_NOTICE_URL}")
        except Exception as e:
            st.error(f"공지 불러오기 실패: {e}")
            st.caption(YONSEI_NOTICE_URL)
    else:
        st.caption("사이드바에서 '캠퍼스 공지 가져오기'를 켜면 표시됩니다.")

with tab2:
    if use_yonsei_calendar:
        try:
            upcoming = fetch_yonsei_academic_calendar_upcoming(days_ahead=60)
            if not upcoming:
                st.info("가까운 학사일정을 찾지 못했어요. (페이지 구조 변경/일시적 오류 가능)")
                st.caption(YONSEI_ACAD_CAL_URL)
            else:
                for ev in upcoming[:18]:
                    st.markdown(f"- {ev['desc']}")
                st.caption(f"출처: {YONSEI_ACAD_CAL_URL}")
        except Exception as e:
            st.error(f"학사일정 불러오기 실패: {e}")
            st.caption(YONSEI_ACAD_CAL_URL)
    else:
        st.caption("사이드바에서 '학사일정 가져오기'를 켜면 표시됩니다.")

with tab3:
    st.markdown("**자동 불러오기(베스트 에포트):** 수강편람은 자동 파싱이 불안정합니다. 대신 붙여넣기를 권장해요.")
    c_year, c_sem, c_kw = st.columns([1, 1, 2])
    with c_year:
        course_year = st.number_input("연도", min_value=2020, max_value=2030, value=dt.datetime.now(KST).year)
    with c_sem:
        course_sem = st.selectbox("학기", [1, 2], index=0)
    with c_kw:
        course_kw = st.text_input("과목 키워드(예: 데이터, 심리, AI, 글쓰기, 경영 등)", value="")

    if use_yonsei_handbook and course_kw.strip():
        with st.spinner("수강편람 접근/확인 중..."):
            handbook_result = fetch_yonsei_handbook_courses_best_effort(
                year=int(course_year),
                semester=int(course_sem),
                keyword=course_kw.strip(),
                limit=20
            )
        st.warning(handbook_result["message"])
        st.markdown("포털 수강편람 직접 열기:")
        st.write(YONSEI_HANDBOOK_URL)

    st.markdown("---")
    st.markdown("**대체 입력(권장):** 포털 검색 결과를 아래에 붙여넣으면 분석에 반영합니다.")
    pasted_courses = st.text_area(
        "과목명/코드/강의시간 등(여러 줄 가능)",
        placeholder="예)\nECO1234 미시경제학\nSTA2101 통계학입문\nUICxxxx ...",
        height=140
    )

# -----------------------------
# USER INPUT
# -----------------------------
st.markdown("<div class='section-title'>🎓 나의 현재 상황</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    major = st.text_input("현재 전공 (풀네임 입력)")
    semester = st.selectbox("현재 학년 / 학기", [f"{y}학년 {s}학기" for y in range(1, 5) for s in ["1", "2"]])
with col2:
    plan = st.selectbox("전공 계획", ["본전공 유지", "복수전공 희망", "전과 희망"])
    gpa = st.slider("전체 GPA (4.3 만점)", 0.0, 4.3, 3.5, 0.01)

st.markdown("#### 📊 이수 학점 현황")
c1, c2 = st.columns(2)
with c1:
    major_credit = st.number_input("전공 이수 학점", 0, 150, 45)
with c2:
    liberal_credit = st.number_input("교양 이수 학점", 0, 150, 30)

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
# CARD COMPONENT
# -----------------------------
if "card_seq" not in st.session_state:
    st.session_state.card_seq = 0

def _estimate_height_from_html(html_str: str) -> int:
    plain = re.sub(r"<[^>]*>", "", html_str or "")
    plain = re.sub(r"\s+", " ", plain).strip()
    approx_lines = max(10, len(plain) // 52)
    height = 260 + approx_lines * 22
    return max(520, min(height, 1200))

def flip_card(title, content, emoji):
    st.session_state.card_seq += 1
    key = st.session_state.card_seq
    iframe_h = _estimate_height_from_html(content)

    components.html(
        f"""
    <style>
    .card-container-{key} {{
        width: 100%;
        perspective: 1200px;
        margin-bottom: 40px;
    }}
    .card-{key} {{
        width: 100%;
        position: relative;
        transition: transform 0.8s;
        transform-style: preserve-3d;
        cursor: pointer;
    }}
    .card-{key}.flip {{ transform: rotateY(180deg); }}
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
        overflow: visible;
        word-break: keep-all;
        white-space: normal;
    }}
    .card-back-{key} p {{ margin: 0 0 1rem 0; }}
    .card-back-{key} p:last-child {{ margin-bottom: 0; }}
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
          const frontH = front.scrollHeight;
          const backH  = back.scrollHeight;
          const H = Math.max(frontH, backH);
          container.style.height = (H) + "px";
          card.style.height = (H) + "px";
          front.style.height = (H) + "px";
          back.style.height  = (H) + "px";
        }}

        window.addEventListener("load", syncHeights);
        setTimeout(syncHeights, 30);
        setTimeout(syncHeights, 200);

        card.addEventListener("click", () => {{
          card.classList.toggle("flip");
          setTimeout(syncHeights, 60);
        }});

        window.addEventListener("resize", () => {{
          setTimeout(syncHeights, 60);
        }});
      }})();
    </script>
    """,
        height=iframe_h,
    )

# -----------------------------
# OpenAI personalization (optional) - safe import
# -----------------------------
def build_context_snippets(course_kw: str, course_year: int, course_sem: int, pasted_courses: str) -> Dict[str, str]:
    snippets: Dict[str, str] = {}

    if use_yonsei_notice:
        try:
            ns = fetch_yonsei_notices(limit=6)
            if ns:
                snippets["notices"] = "\n".join([f"- {n['date']} | {n['title']}" for n in ns])
        except Exception:
            pass

    if use_yonsei_calendar:
        try:
            cal = fetch_yonsei_academic_calendar_upcoming(days_ahead=45)
            if cal:
                snippets["calendar"] = "\n".join([f"- {e['desc']}" for e in cal[:10]])
        except Exception:
            pass

    # courses context (paste가 1순위)
    lines = []
    if pasted_courses.strip():
        lines.append(pasted_courses.strip())
    if use_yonsei_handbook and course_kw.strip():
        hr = fetch_yonsei_handbook_courses_best_effort(course_year, course_sem, course_kw.strip(), limit=12)
        # 실제 과목 리스트는 못 받지만, 안내문/키워드 여부 정도는 참고
        lines.append(f"[수강편람 자동 조회 상태] {hr.get('message','')}")
    if lines:
        snippets["courses"] = "\n\n".join(lines)

    return snippets

def openai_generate_html_cards(user_profile: Dict[str, object], campus_ctx: Dict[str, str], api_key: str) -> Optional[Dict[str, str]]:
    """
    openai 패키지가 없거나 키가 없으면 None
    """
    if not api_key:
        return None
    try:
        from openai import OpenAI
    except Exception:
        return None

    client = OpenAI(api_key=api_key)
    model_name = st.secrets.get("OPENAI_MODEL", "gpt-4.1-mini")

    system = (
        "너는 연세대학교 학부생 타깃의 진로/전공 전략 코치다. "
        "사용자 프로필(전공/학기/GPA/학점/관심사/전공계획)과 연세대 공지/학사일정/과목 힌트를 참고해 "
        "실행 가능한 조언을 '짧고 선명한 문단 3~5개'로 정리한다. "
        "반드시 과장 없이, 사용자가 다음 2~4주 안에 할 수 있는 행동을 포함한다. "
        "출력은 아래 JSON 스키마만 준수한다: "
        "{'card1_html': str, 'card2_html': str, 'card3_html': str} "
        "각 값은 <p>...</p> 문단들로만 구성한다."
    )

    payload = {
        "user_profile": user_profile,
        "campus_context": campus_ctx,
        "instructions": {
            "card1": "현재 상태 진단(서사 정리 + 리스크/강점)",
            "card2": "전공 기반 전략 방향(전공자산→관심사 연결 + 추천 액션 3개)",
            "card3": "다음 학기/다음 4주 전략(구체 체크리스트 + 공지/학사일정 반영)",
        },
    }

    try:
        resp = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            temperature=0.6,
        )
        content = resp.choices[0].message.content or ""
        data = json.loads(content)
        for k in ["card1_html", "card2_html", "card3_html"]:
            if k not in data or not isinstance(data[k], str):
                return None
        return data
    except Exception:
        return None

# -----------------------------
# RESULT
# -----------------------------
if analyze:
    profile = {
        "major": major,
        "semester": semester,
        "plan": plan,
        "gpa": float(gpa),
        "major_credit": int(major_credit),
        "liberal_credit": int(liberal_credit),
        "interest": interest,
        "course_year": int(course_year),
        "course_semester": int(course_sem),
        "course_keyword": course_kw.strip(),
    }
    campus_ctx = build_context_snippets(course_kw, int(course_year), int(course_sem), pasted_courses)

    cards = openai_generate_html_cards(profile, campus_ctx, openai_api_key)

    # 폴백
    if not cards:
        cards = {
            "card1_html": f"""
                <p>지금 당신은 <b>{major}</b> 전공을 이수 중이며, 현재 <b>{semester}</b>에 해당합니다.</p>
                <p>GPA <b>{gpa}</b>는 지표이지만, 더 중요한 건 ‘무엇을 했고 어떤 역량을 쌓았는지’를 설명하는 서사입니다.</p>
                <p>관심 분야(<b>{interest}</b>)를 다음 학기 과목/프로젝트/활동의 기준으로 삼아, 산출물이 남는 선택을 우선해보세요.</p>
            """,
            "card2_html": f"""
                <p>전공 {major_credit}학점, 교양 {liberal_credit}학점은 ‘이미 확보한 자산’입니다.</p>
                <p>전공 계획 <b>{plan}</b>은 제도 선택이 아니라, 전공자산을 커리어 언어로 바꾸는 전략입니다.</p>
                <p><b>다음 액션(3개)</b><br/>
                1) 전공 과목/과제 3개를 STAR(상황-과제-행동-결과)로 정리<br/>
                2) 관심 분야와 연결되는 역량 키워드 5개 뽑기<br/>
                3) 산출물(보고서/기획서/분석리포트/프로토타입)이 남는 활동 1개 착수</p>
            """,
            "card3_html": f"""
                <p>다음 4주 목표는 ‘결정’보다 <b>정리</b>입니다. 정리가 되면 선택이 덜 불안해집니다.</p>
                <p><b>체크리스트</b><br/>
                - 이번 주: 관심 분야를 2~3개로 좁히고, 각 분야에 필요한 역량/증거물 정의<br/>
                - 2주차: 포트폴리오로 남길 1개 산출물 주제 확정(과제/프로젝트/리서치/콘텐츠)<br/>
                - 3~4주차: 결과물 1차 버전 + 피드백 1회</p>
                <p class="small">※ 상단 '캠퍼스 인포' 탭에서 공지/학사일정/수강편람 링크를 참고해 마감일을 캘린더에 박아두세요.</p>
            """,
        }

    # 캠퍼스 컨텍스트를 카드에 덧붙이기(있을 때만)
    if campus_ctx.get("calendar"):
        cards["card3_html"] += f"<p><b>다가오는 학사일정(요약)</b><br/>{campus_ctx['calendar'].replace(chr(10), '<br/>')}</p>"
    if campus_ctx.get("notices"):
        cards["card1_html"] += f"<p><b>최근 공지(요약)</b><br/>{campus_ctx['notices'].replace(chr(10), '<br/>')}</p>"
    if campus_ctx.get("courses"):
        cards["card2_html"] += f"<p><b>과목/수강 힌트</b><br/>{campus_ctx['courses'].replace(chr(10), '<br/>')}</p>"

    flip_card("현재 상태 진단", cards["card1_html"], "📊")
    flip_card("전공 기반 전략 방향", cards["card2_html"], "🧭")
    flip_card("다음 학기/4주 전략", cards["card3_html"], "📝")

    st.markdown("---")
    st.markdown("✨ **MajorPass는 선택을 대신하지 않습니다. 대신, 선택을 덜 불안하게 만듭니다.**")
