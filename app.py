# MajorPass (Yonsei Edition)
# - 캠퍼스 공지/학사일정: 연세대 홈페이지(공식 페이지) 기반으로 화면에 표시
# - 수강편람(수강편람조회): underwood1.yonsei.ac.kr (연세 포털 수강편람 뷰어)에서 "가능하면" 불러오기 시도 + 실패 시 사용자 안내/대체 경로 제공
# - 분석 결과: (선택) OpenAI API로 개인화된 결과 생성 (키 없으면 기존 템플릿으로 폴백)
#
# 참고(공식 페이지 예시)
# - 학사일정(신촌): https://www.yonsei.ac.kr/sc/373/subview.do
# - Campus Life Notice(영문): https://www.yonsei.ac.kr/en_sc/1854/subview.do
# - 수강편람 뷰어(포털 연동): https://underwood1.yonsei.ac.kr/com/lgin/SsoCtr/initExtPageWork.do?link=handbList&locale=ko
#
# requirements.txt 예:
# streamlit
# requests
# beautifulsoup4
# openai

import re
import json
import datetime as dt
from typing import List, Dict, Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="MajorPass", layout="wide")

# -----------------------------
# CONST (Yonsei sources)
# -----------------------------
YONSEI_NOTICE_URL = "https://www.yonsei.ac.kr/en_sc/1854/subview.do"  # Campus Life > Notice (ENG)
YONSEI_ACAD_CAL_URL = "https://www.yonsei.ac.kr/sc/373/subview.do"   # 학사일정(신촌·국제)
YONSEI_HANDBOOK_URL = "https://underwood1.yonsei.ac.kr/com/lgin/SsoCtr/initExtPageWork.do?link=handbList&locale=ko"  # 수강편람조회(포털 연동)

DEFAULT_UA = {
    "User-Agent": "Mozilla/5.0 (MajorPass; Streamlit) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari"
}

KST = dt.timezone(dt.timedelta(hours=9))

# -----------------------------
# SIDEBAR – API KEY & DATA SETTINGS
# -----------------------------
with st.sidebar:
    st.markdown("## 🔑 API 설정")

    # 1) OpenAI key: 사용자 입력 or st.secrets
    api_key_input = st.text_input(
        "OpenAI API Key",
        type="password",
        help="개인화 분석 고도화에 사용됩니다. (로컬/배포에서는 st.secrets 사용 권장)"
    )
    openai_api_key = api_key_input or st.secrets.get("OPENAI_API_KEY", "")

    st.markdown("---")
    st.markdown("## 🏫 연세대 데이터")
    use_yonsei_notice = st.checkbox("캠퍼스 공지 가져오기", value=True)
    use_yonsei_calendar = st.checkbox("학사일정 가져오기", value=True)
    use_yonsei_handbook = st.checkbox("수강편람(과목) 불러오기 시도", value=True)

    st.caption("※ 수강편람은 포털 연동 페이지라 일부 환경에서 자동 수집이 실패할 수 있어요. 실패하면 안내/대체 입력으로 폴백합니다.")

    st.markdown("---")
    st.markdown("""
    **MajorPass는**
    입력된 정보를 저장하거나 외부로 전송하지 않습니다.  
    (단, OpenAI API를 사용할 경우 입력 내용이 API 요청으로 전달됩니다.)
    """)

# -----------------------------
# HTTP helpers
# -----------------------------
def _http_get(url: str, timeout: int = 15) -> str:
    r = requests.get(url, headers=DEFAULT_UA, timeout=timeout)
    r.raise_for_status()
    # 일부 사이트 EUC-KR 가능성 대비(대부분 UTF-8이지만)
    if r.encoding is None:
        r.encoding = "utf-8"
    return r.text

# -----------------------------
# Yonsei: Notice fetch (ENG Campus Life Notice)
# -----------------------------
@st.cache_data(ttl=60 * 30)
def fetch_yonsei_notices(limit: int = 7) -> List[Dict[str, str]]:
    """
    Yonsei Campus Life Notice(영문) 리스트 파싱.
    페이지 구조 변경에 대비해 'Date YYYY.MM.DD' 패턴 기반으로 추출합니다.
    """
    html = _http_get(YONSEI_NOTICE_URL)
    soup = BeautifulSoup(html, "html.parser")

    items: List[Dict[str, str]] = []

    # 텍스트 패턴 기반 추출(가장 안정적)
    # 예: "70 26-1 Freshmen Songdo Dorm. Application Schedule 조회수 ... Date 2026.01.16 ..."
    for a in soup.select("a"):
        text = " ".join(a.get_text(" ", strip=True).split())
        if "Date" in text:
            m = re.search(r"Date\s*(\d{4}\.\d{2}\.\d{2})", text)
            if not m:
                continue
            date = m.group(1)
            # 제목은 Date 앞부분에서 번호/조회수 등 제거
            title = re.sub(r"^\d+\s*", "", text)
            title = re.sub(r"조회수.*$", "", title).strip()
            title = re.sub(r"\s*Date\s*\d{4}\.\d{2}\.\d{2}.*$", "", title).strip()

            href = a.get("href") or ""
            if href.startswith("/"):
                href = "https://www.yonsei.ac.kr" + href

            # 너무 짧거나 메뉴 링크 같은 것 제외
            if len(title) < 8:
                continue

            items.append({"title": title, "date": date, "url": href})

    # 중복 제거(제목+날짜)
    uniq = {}
    for it in items:
        key = (it["title"], it["date"])
        uniq[key] = it

    out = list(uniq.values())
    # 최신순(문자열 YYYY.MM.DD는 정렬 가능)
    out.sort(key=lambda x: x["date"], reverse=True)
    return out[:limit]

# -----------------------------
# Yonsei: Academic calendar fetch (KOR)
# -----------------------------
MONTH_MAP = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

@st.cache_data(ttl=60 * 60)
def fetch_yonsei_academic_calendar_upcoming(days_ahead: int = 45) -> List[Dict[str, str]]:
    """
    연세대 학사일정 페이지(신촌·국제)에서 '다가오는 일정'만 뽑아서 반환.
    페이지가 월별 섹션 + 날짜/요일/내용으로 구성되어 있어,
    텍스트를 줄 단위로 훑으며 Month context를 기억하는 방식으로 파싱합니다.
    """
    html = _http_get(YONSEI_ACAD_CAL_URL)
    soup = BeautifulSoup(html, "html.parser")

    text = soup.get_text("\n", strip=True)
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

    # "2026년 1학기" 같은 현재 년도 힌트 찾기(없으면 올해 기준)
    # 페이지 본문에 2026-1학기 같은 문자열이 다수 존재하므로 regex로 연도 추정
    year_guess = None
    m_year = re.search(r"(20\d{2})-?[12]학기", text)
    if m_year:
        year_guess = int(m_year.group(1))
    else:
        year_guess = dt.datetime.now(KST).year

    today = dt.datetime.now(KST).date()
    end = today + dt.timedelta(days=days_ahead)

    current_month = None
    events: List[Tuple[dt.date, str]] = []

    # 라인에서 Month 이름이 단독으로 등장하거나, "2월 February"처럼 함께 등장
    for ln in lines:
        # month 감지
        for month_name, month_num in MONTH_MAP.items():
            if month_name in ln:
                current_month = month_num
                break

        if current_month is None:
            continue

        # 날짜 라인 패턴: "03 (Tue) 개강" 또는 "05 (Thu) ~ 09 (Mon) 수강신청 확인 및 변경"
        # 1) 범위
        m_rng = re.search(
            r"^(\d{1,2})\s*\(\w{3}\)\s*~\s*(\d{1,2})\s*\(\w{3}\)\s*(.+)$",
            ln
        )
        if m_rng:
            d1 = int(m_rng.group(1))
            d2 = int(m_rng.group(2))
            desc = m_rng.group(3).strip()
            try:
                start_date = dt.date(year_guess, current_month, d1)
                end_date = dt.date(year_guess, current_month, d2)
                # 기간은 시작일 기준으로 표시하되, 설명에 기간 남김
                if today <= end_date and start_date <= end:
                    events.append((start_date, f"{start_date.strftime('%m/%d')}~{end_date.strftime('%m/%d')} · {desc}"))
            except ValueError:
                pass
            continue

        # 2) 단일 날짜
        m_one = re.search(r"^(\d{1,2})\s*\(\w{3}\)\s*(.+)$", ln)
        if m_one:
            d = int(m_one.group(1))
            desc = m_one.group(2).strip()
            try:
                date_obj = dt.date(year_guess, current_month, d)
                if today <= date_obj <= end:
                    events.append((date_obj, f"{date_obj.strftime('%m/%d')} · {desc}"))
            except ValueError:
                pass

    # 날짜순 정렬 + 중복 제거
    events.sort(key=lambda x: x[0])
    uniq = {}
    for d, desc in events:
        uniq[(d.isoformat(), desc)] = {"date": d.isoformat(), "desc": desc}
    return list(uniq.values())

# -----------------------------
# Yonsei: Handbook (Course catalogue) "best-effort" fetch
# -----------------------------
def _try_extract_json_from_html(html: str) -> Optional[dict]:
    """
    수강편람 뷰어가 HTML 안에 JSON을 심어두는 케이스가 있어(사이트 개편/환경별),
    script 태그/전역변수 형태의 JSON을 최대한 찾아봅니다.
    """
    # 1) <script> ... = {...}; 형태
    candidates = re.findall(r"(\{.*?\})", html, flags=re.DOTALL)
    for c in candidates:
        c = c.strip()
        if len(c) < 200:
            continue
        try:
            obj = json.loads(c)
            if isinstance(obj, dict):
                return obj
        except Exception:
            continue

    # 2) __NEXT_DATA__ 류
    m = re.search(r'id="__NEXT_DATA__"\s*type="application/json"\s*>(.*?)</script>', html, flags=re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            return None

    return None

@st.cache_data(ttl=60 * 30)
def fetch_yonsei_handbook_courses_best_effort(
    year: int,
    semester: int,
    keyword: str,
    limit: int = 20
) -> Dict[str, object]:
    """
    ⚠️ 포털 연동 페이지라 자동 조회가 환경에 따라 실패할 수 있습니다.
    - 성공하면: courses 리스트 반환
    - 실패하면: ok=False + 안내 메시지 반환
    """
    try:
        html = _http_get(YONSEI_HANDBOOK_URL, timeout=15)
    except Exception as e:
        return {
            "ok": False,
            "message": f"수강편람 페이지 접근 실패: {e}",
            "courses": []
        }

    # 페이지가 JS 렌더링/iframe일 수 있어, 단순 파싱 실패 가능
    # 그래도 'keyword'가 HTML에 직접 들어있으면 간단히 긁어봄
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text(" ", strip=True)

    # (1) JSON 내장 추출 시도
    obj = _try_extract_json_from_html(html)
    if obj and keyword:
        # 구조가 확정적이지 않아, 문자열 전체를 덤프 탐색하는 방식(최후의 수단)
        blob = json.dumps(obj, ensure_ascii=False)
        if keyword.lower() in blob.lower():
            # 검색어가 있다는 정도만 확인 가능 → 실제 코스 리스트 구조가 환경별로 달라
            # 여기서는 사용자에게 포털에서 직접 조회 링크를 제공
            return {
                "ok": False,
                "message": "수강편람 데이터 구조를 자동 파싱하기 어려워요(포털 페이지 구조/권한/세션 영향). 아래 '대체 입력'을 사용하거나 포털에서 검색 결과를 붙여넣어 주세요.",
                "courses": []
            }

    # (2) HTML에 코스 테이블이 직접 있는 경우(드묾) 탐색
    # 테이블에서 keyword 포함 row 찾기
    if keyword:
        courses = []
        for tr in soup.select("tr"):
            row_text = tr.get_text(" ", strip=True)
            if keyword.lower() in row_text.lower() and len(row_text) > 20:
                courses.append({"raw": row_text})
            if len(courses) >= limit:
                break
        if courses:
            return {"ok": True, "message": "수강편람(부분) 추출 성공", "courses": courses}

    # (3) 실패 폴백
    return {
        "ok": False,
        "message": (
            "수강편람은 연세포털 연동(세션/JS 렌더링/권한) 때문에 이 앱에서 자동으로 "
            "과목 리스트를 안정적으로 가져오기 어려울 수 있어요. "
            "아래 '대체 입력(과목명/코드 붙여넣기)'을 사용하면 분석에 반영할게요."
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
            else:
                for n in notices:
                    st.markdown(
                        f"- **{n['title']}**  <span class='badge'>{n['date']}</span>\n"
                        f"  \n  ↗ {n['url']}",
                        unsafe_allow_html=True
                    )
        except Exception as e:
            st.error(f"공지 불러오기 실패: {e}")
            st.write(YONSEI_NOTICE_URL)
    else:
        st.caption("사이드바에서 '캠퍼스 공지 가져오기'를 켜면 표시됩니다.")

with tab2:
    if use_yonsei_calendar:
        try:
            upcoming = fetch_yonsei_academic_calendar_upcoming(days_ahead=60)
            if not upcoming:
                st.info("가까운 학사일정을 찾지 못했어요.")
            else:
                for ev in upcoming[:18]:
                    st.markdown(f"- {ev['desc']}")
            st.caption(f"출처: {YONSEI_ACAD_CAL_URL}")
        except Exception as e:
            st.error(f"학사일정 불러오기 실패: {e}")
            st.write(YONSEI_ACAD_CAL_URL)
    else:
        st.caption("사이드바에서 '학사일정 가져오기'를 켜면 표시됩니다.")

with tab3:
    st.markdown("**자동 불러오기(가능하면):** 연도/학기/키워드로 과목을 찾아 분석에 반영합니다.")
    c_year, c_sem, c_kw = st.columns([1, 1, 2])
    with c_year:
        course_year = st.number_input("연도", min_value=2020, max_value=2030, value=dt.datetime.now(KST).year)
    with c_sem:
        course_sem = st.selectbox("학기", [1, 2], index=0)
    with c_kw:
        course_kw = st.text_input("과목 키워드(예: 데이터, 심리, AI, 글쓰기, 경영 등)", value="")

    handbook_result = {"ok": False, "message": "아직 조회 전", "courses": []}
    if use_yonsei_handbook and course_kw.strip():
        with st.spinner("수강편람에서 과목을 찾아보는 중..."):
            handbook_result = fetch_yonsei_handbook_courses_best_effort(
                year=int(course_year),
                semester=int(course_sem),
                keyword=course_kw.strip(),
                limit=20
            )
        if handbook_result["ok"] and handbook_result["courses"]:
            st.success("과목(부분) 추출 성공")
            for c in handbook_result["courses"]:
                st.write("• " + c.get("raw", ""))
        else:
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
# OpenAI personalization (optional)
# -----------------------------
def build_context_snippets() -> Dict[str, str]:
    snippets = {}

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

    # handbook/courses
    handbook_lines = []
    if pasted_courses.strip():
        handbook_lines.append(pasted_courses.strip())

    if use_yonsei_handbook and course_kw.strip():
        # 이미 tab3에서 조회했을 수도 있지만, 여기서는 "가벼운 컨텍스트"로만 사용
        # (캐시로 재호출 비용 낮음)
        hr = fetch_yonsei_handbook_courses_best_effort(int(course_year), int(course_sem), course_kw.strip(), limit=12)
        if hr.get("ok") and hr.get("courses"):
            handbook_lines.append("\n".join(["• " + c.get("raw", "") for c in hr["courses"][:8]]))

    if handbook_lines:
        snippets["courses"] = "\n\n".join(handbook_lines)

    return snippets

def openai_generate_html_cards(user_profile: Dict[str, str], campus_ctx: Dict[str, str]) -> Dict[str, str]:
    """
    OpenAI key가 있으면 카드 3개를 HTML 문단 형태로 생성.
    실패/키 없음이면 호출 측에서 폴백.
    """
    from openai import OpenAI

    client = OpenAI(api_key=openai_api_key)

    # 모델명은 배포 환경에 맞게 조정 가능 (예: gpt-4.1-mini / gpt-5-mini 등)
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

    user = {
        "user_profile": user_profile,
        "campus_context": campus_ctx,
        "instructions": {
            "card1": "현재 상태 진단(서사 정리 + 리스크/강점)",
            "card2": "전공 기반 전략 방향(전공자산→관심사 연결 + 추천 액션 3개)",
            "card3": "다음 학기/다음 4주 전략(구체 체크리스트 + 공지/학사일정 반영)",
        },
    }

    resp = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
        temperature=0.6,
    )

    content = resp.choices[0].message.content or ""
    # JSON 파싱
    try:
        data = json.loads(content)
        for k in ["card1_html", "card2_html", "card3_html"]:
            if k not in data or not isinstance(data[k], str):
                raise ValueError("bad schema")
        return data
    except Exception:
        # 모델이 JSON을 깨먹는 경우 최소한의 복구
        return {
            "card1_html": f"<p>모델 출력 파싱에 실패했어요. 아래 내용을 참고해 다시 시도해 주세요.</p><p>{content}</p>",
            "card2_html": "<p>카드2 생성 실패</p>",
            "card3_html": "<p>카드3 생성 실패</p>",
        }

# -----------------------------
# RESULT
# -----------------------------
if analyze:
    profile = {
        "major": major,
        "semester": semester,
        "plan": plan,
        "gpa": gpa,
        "major_credit": major_credit,
        "liberal_credit": liberal_credit,
        "interest": interest,
        "course_year": int(course_year),
        "course_semester": int(course_sem),
        "course_keyword": course_kw.strip(),
    }
    campus_ctx = build_context_snippets()

    # 1) OpenAI로 개인화 시도
    cards = None
    if openai_api_key:
        with st.spinner("개인화 분석 생성 중 (OpenAI)..."):
            cards = openai_generate_html_cards(profile, campus_ctx)

    # 2) 폴백(키 없거나 실패)
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
                <p><b>다음 액션(3개)</b><br/>1) 전공 과목/과제 3개를 STAR(상황-과제-행동-결과)로 정리<br/>
                2) 관심 분야와 연결되는 역량 키워드 5개 뽑기<br/>
                3) 산출물(보고서/기획서/분석리포트/프로토타입)이 남는 활동 1개 착수</p>
            """,
            "card3_html": f"""
                <p>다음 4주 목표는 ‘결정’보다 <b>정리</b>입니다. 정리가 되면 선택이 덜 불안해집니다.</p>
                <p><b>체크리스트</b><br/>
                - 이번 주: 관심 분야를 2~3개로 좁히고, 각 분야에 필요한 역량/증거물 정의<br/>
                - 2주차: 포트폴리오로 남길 1개 산출물 주제 확정(과제/프로젝트/리서치/콘텐츠)<br/>
                - 3~4주차: 결과물 1차 버전 + 피드백 1회</p>
                <p>※ 학사일정/공지 탭을 참고해 마감·변경·신청 기간을 놓치지 않게 캘린더에 박아두세요.</p>
            """,
        }

    # (선택) 캠퍼스 컨텍스트를 카드에 살짝 덧붙이기(공지/학사일정이 있으면)
    if campus_ctx.get("calendar"):
        cards["card3_html"] += f"<p><b>다가오는 학사일정(요약)</b><br/>{campus_ctx['calendar'].replace(chr(10), '<br/>')}</p>"
    if campus_ctx.get("notices"):
        cards["card1_html"] += f"<p><b>최근 공지(요약)</b><br/>{campus_ctx['notices'].replace(chr(10), '<br/>')}</p>"
    if campus_ctx.get("courses"):
        cards["card2_html"] += f"<p><b>과목 힌트(사용자 제공/부분 추출)</b><br/>{campus_ctx['courses'].replace(chr(10), '<br/>')}</p>"

    flip_card("현재 상태 진단", cards["card1_html"], "📊")
    flip_card("전공 기반 전략 방향", cards["card2_html"], "🧭")
    flip_card("다음 학기/4주 전략", cards["card3_html"], "📝")

    st.markdown("---")
    st.markdown("✨ **MajorPass는 선택을 대신하지 않습니다. 대신, 선택을 덜 불안하게 만듭니다.**")

    # 디버그/투명성: 어떤 컨텍스트가 반영됐는지
    with st.expander("🔎 분석에 반영된 캠퍼스 데이터(요약) 보기"):
        if campus_ctx:
            for k, v in campus_ctx.items():
                st.markdown(f"**{k}**")
                st.code(v)
        else:
            st.caption("반영된 캠퍼스 데이터가 없습니다.")
