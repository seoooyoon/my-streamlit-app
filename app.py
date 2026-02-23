import json
import os
import random
import re
import textwrap
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import requests
import streamlit as st

# Optional local extraction (no external key)
import trafilatura


# =========================================================
# Optional OpenAI (LLM)
# =========================================================
OPENAI_AVAILABLE = True
try:
    from openai import OpenAI
except Exception:
    OPENAI_AVAILABLE = False


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MajorPass · YONSEI Edition",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# THEME / DESIGN (Yonsei-style)
# =========================================================
YONSEI_BLUE = "#003876"   # Deep blue vibe (approx)
ACCENT = "#4F46E5"        # modern accent
MINT = "#22C55E"


def eagle_svg(color: str = YONSEI_BLUE) -> str:
    # Simple abstract eagle (original SVG) – not official Yonsei logo.
    return f"""
<svg width="54" height="54" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M8 38c10-8 18-12 24-12s14 4 24 12" stroke="{color}" stroke-width="3" stroke-linecap="round"/>
  <path d="M10 34c8-10 16-16 22-16s14 6 22 16" stroke="{color}" stroke-width="3" stroke-linecap="round" opacity="0.8"/>
  <path d="M22 28c3-6 6-10 10-10s7 4 10 10" stroke="{color}" stroke-width="3" stroke-linecap="round" opacity="0.7"/>
  <path d="M30 20c1-2 2-3 2-3s1 1 2 3" stroke="{color}" stroke-width="3" stroke-linecap="round"/>
  <circle cx="32" cy="22" r="1.5" fill="{color}"/>
</svg>
""".strip()


def inject_css() -> None:
    # Pretendard CDN (optional). If blocked, fallback fonts still work.
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

:root{
  --yonsei: #003876;
  --accent: #4F46E5;
  --mint: #22C55E;
  --bg1: #F7F8FC;
  --bg2: #EEF2FF;
  --text: #0B1220;
  --muted: rgba(11,18,32,0.62);
  --card: rgba(255,255,255,0.72);
  --card2: rgba(255,255,255,0.92);
  --border: rgba(15,23,42,0.10);
  --shadow: 0 14px 38px rgba(15,23,42,0.12);
  --radius: 18px;
}

/* background */
html, body, [data-testid="stApp"]{
  font-family: Pretendard, Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: var(--text);
}
[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(1100px 650px at 10% 12%, rgba(0,56,118,0.14), transparent 60%),
    radial-gradient(900px 550px at 85% 8%, rgba(79,70,229,0.14), transparent 60%),
    linear-gradient(180deg, var(--bg1), #FFFFFF 60%);
  position: relative;
}

/* subtle noise overlay */
[data-testid="stAppViewContainer"]::before{
  content:"";
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.08;
  mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='180' height='180' filter='url(%23n)' opacity='.35'/%3E%3C/svg%3E");
}

/* page padding */
.block-container{
  padding-top: 1.1rem;
  padding-bottom: 3rem;
  max-width: 1200px;
}

/* hide default header/footer */
header {visibility: hidden;}
footer {visibility: hidden;}

/* sidebar */
section[data-testid="stSidebar"]{
  background: rgba(255,255,255,0.75) !important;
  border-right: 1px solid var(--border);
}

/* hero */
.mp-hero{
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  background: linear-gradient(120deg, rgba(0,56,118,0.12), rgba(79,70,229,0.10));
  padding: 18px 18px;
  margin: 6px 0 18px 0;
  overflow:hidden;
  position: relative;
}
.mp-hero::after{
  content:"";
  position:absolute;
  inset:-2px;
  background: radial-gradient(600px 160px at 20% 0%, rgba(255,255,255,0.55), transparent 60%);
  pointer-events:none;
}
.mp-hero-top{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap: 12px;
}
.mp-title{
  font-weight: 800;
  letter-spacing: -0.03em;
  margin: 0;
  font-size: 2.05rem;
  animation: heroShrink 900ms ease-out both;
}
@keyframes heroShrink{
  0%{ transform: scale(1.22); opacity: 0; filter: blur(2px); }
  100%{ transform: scale(1.00); opacity: 1; filter: blur(0px); }
}
.mp-sub{
  margin-top: 6px;
  color: var(--muted);
  line-height: 1.45;
}
.mp-badges{
  display:flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content:flex-end;
}
.mp-pill{
  display:inline-flex;
  align-items:center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.80);
  font-size: 0.85rem;
  color: var(--muted);
}
.mp-eagle{
  display:flex;
  align-items:center;
  gap: 10px;
}
.mp-eagle-badge{
  width: 44px; height: 44px;
  border-radius: 14px;
  display:flex;
  align-items:center;
  justify-content:center;
  background: rgba(255,255,255,0.72);
  border: 1px solid var(--border);
}

/* cards */
.mp-card{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 16px 16px;
}
.mp-card-solid{
  background: var(--card2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 16px 16px;
}
.mp-section{
  font-size: 1.05rem;
  font-weight: 800;
  margin: 10px 0 8px 0;
  letter-spacing: -0.01em;
}
.mp-muted{ color: var(--muted); }
.mp-divider{
  height: 1px;
  background: var(--border);
  margin: 14px 0;
}

/* digest card */
.d-card{
  background: rgba(255,255,255,0.80);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px 14px;
  box-shadow: 0 12px 32px rgba(15,23,42,0.10);
}
.d-head{
  display:flex;
  justify-content:space-between;
  gap: 10px;
  align-items:flex-start;
}
.d-title{
  font-weight: 800;
  line-height: 1.25;
  font-size: 1.03rem;
}
.d-one{
  margin-top: 6px;
  color: var(--muted);
}
.d-meta{
  font-size: 0.82rem;
  color: var(--muted);
  white-space: nowrap;
}
.d-tag{
  display:inline-flex;
  padding: 6px 8px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(0,56,118,0.06);
  font-size: 0.82rem;
  margin-right: 6px;
}

/* buttons */
.stButton button, .stDownloadButton button{
  border-radius: 12px !important;
  padding: 10px 14px !important;
  font-weight: 700 !important;
}

/* dataframe */
[data-testid="stDataFrame"]{
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow: hidden;
}
</style>
""",
        unsafe_allow_html=True,
    )


inject_css()


# =========================================================
# SESSION STATE INIT
# =========================================================
def init_state() -> None:
    ss = st.session_state
    ss.setdefault("nav", "Profile")
    ss.setdefault("profile", {})
    ss.setdefault("profile_analysis", None)          # dict
    ss.setdefault("action_plan_df", None)            # DataFrame
    ss.setdefault("recommended_keywords", [])        # list[str]

    ss.setdefault("search_df", None)                 # DataFrame
    ss.setdefault("digest_result", None)             # dict {digests, overall}
    ss.setdefault("trend_df", None)                  # DataFrame
    ss.setdefault("trend_summary", None)             # str
    ss.setdefault("plan_result", None)               # dict

    ss.setdefault("chat_history", [])                # [{role, content}]
    ss.setdefault("chat_context", {"profile": None, "analysis": None, "digest": None, "trend": None, "plan": None})
    ss.setdefault("pending_user_message", None)

    ss.setdefault("rewards", [])
    ss.setdefault("achievements", {
        "first_profile": False,
        "first_digest": False,
        "first_trend": False,
        "first_plan": False,
        "chat_5": False,
        "triple_action": False,
        "night_owl": False,
        "secret_phrase": False,
    })
    ss.setdefault("events_done", set())


init_state()


# =========================================================
# UTIL
# =========================================================
def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def clean_html(s: str) -> str:
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", s).strip()


def clamp_text(s: str, max_chars: int = 3500) -> str:
    s = (s or "").strip()
    if len(s) <= max_chars:
        return s
    return s[:max_chars] + "…"


def safe_secret(key: str, default: str = "") -> str:
    try:
        return st.secrets.get(key, default)  # type: ignore[attr-defined]
    except Exception:
        return os.getenv(key, default)


def llm_enabled(openai_key: str) -> bool:
    return OPENAI_AVAILABLE and bool((openai_key or "").strip())


# =========================================================
# REWARDS (Yonsei themed)
# =========================================================
RARITY_POOL = [
    ("Common", 0.72, "🟦"),
    ("Rare", 0.22, "🟪"),
    ("Epic", 0.055, "🟨"),
    ("Secret", 0.005, "🟥"),
]

COLLECTIBLES = [
    ("Eagle Feather", "🪶"),
    ("Torch Spark", "🔥"),
    ("Book Stamp", "📘"),
    ("Shield Badge", "🛡️"),
    ("Momentum Booster", "🚀"),
    ("Focus Token", "🎯"),
    ("Insight Gem", "💎"),
]

SECRET_PHRASE = "path to pass"


def unlock(key: str) -> None:
    if key in st.session_state.achievements and not st.session_state.achievements[key]:
        st.session_state.achievements[key] = True
        st.toast(f"업적 달성: {key} 🏆", icon="🏆")


def maybe_drop_reward(event: str) -> None:
    if event in st.session_state.events_done:
        return
    st.session_state.events_done.add(event)

    # drop chance
    if random.random() > 0.45:
        return

    # rarity
    r = random.random()
    cum = 0.0
    rarity, icon = "Common", "🟦"
    for name, prob, ico in RARITY_POOL:
        cum += prob
        if r <= cum:
            rarity, icon = name, ico
            break

    n, e = random.choice(COLLECTIBLES)
    reward = {
        "name": n,
        "emoji": e,
        "rarity": rarity,
        "rarity_icon": icon,
        "ts": now_str(),
        "event": event,
    }
    st.session_state.rewards.append(reward)

    if rarity == "Secret":
        st.toast("시크릿 보상이 드랍됐어요… 👀", icon="🟥")
        st.balloons()
    else:
        st.toast(f"{e} {n} ({rarity}) 획득!", icon=icon)


def check_combo() -> None:
    done = st.session_state.events_done
    if {"profile_done", "digest_done", "trend_done"}.issubset(done):
        unlock("triple_action")


# Night owl
h = datetime.now().hour
if h >= 23 or h <= 4:
    unlock("night_owl")


# =========================================================
# NAVER APIs
# =========================================================
def naver_headers(client_id: str, client_secret: str) -> Dict[str, str]:
    return {
        "X-Naver-Client-Id": client_id.strip(),
        "X-Naver-Client-Secret": client_secret.strip(),
    }


@st.cache_data(ttl=60 * 30)
def naver_search(query: str, client_id: str, client_secret: str, category: str, display: int, sort: str) -> pd.DataFrame:
    if not query.strip():
        return pd.DataFrame()

    url = f"https://openapi.naver.com/v1/search/{category}.json"
    params = {"query": query, "display": int(display), "start": 1, "sort": sort}
    r = requests.get(url, headers=naver_headers(client_id, client_secret), params=params, timeout=15)
    r.raise_for_status()
    data = r.json()

    items = data.get("items", [])
    rows = []
    for it in items:
        rows.append({
            "Select": False,
            "Title": clean_html(it.get("title", "")),
            "Snippet": clean_html(it.get("description", "")),
            "Link": it.get("originallink") or it.get("link") or "",
            "Published": it.get("pubDate") or "",
            "Type": category,
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=60 * 60)
def naver_datalab_trend(
    client_id: str,
    client_secret: str,
    start_date: str,
    end_date: str,
    time_unit: str,
    keyword_groups: List[Dict[str, Any]],
) -> pd.DataFrame:
    url = "https://openapi.naver.com/v1/datalab/search"
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups,
    }
    r = requests.post(
        url,
        headers={**naver_headers(client_id, client_secret), "Content-Type": "application/json"},
        data=json.dumps(body, ensure_ascii=False),
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()

    results = data.get("results", [])
    if not results:
        return pd.DataFrame()

    all_periods = set()
    series = {}
    for g in results:
        name = g.get("title") or g.get("keyword") or "Group"
        series[name] = {}
        for p in g.get("data", []):
            period = p.get("period")
            ratio = p.get("ratio")
            if period is None or ratio is None:
                continue
            all_periods.add(period)
            series[name][period] = float(ratio)

    periods = sorted(all_periods)
    df = pd.DataFrame(index=periods)
    for name, m in series.items():
        df[name] = [m.get(p, None) for p in periods]
    df.index.name = "Period"
    return df


# =========================================================
# EXTRACTION (local) - "links → text"
# =========================================================
@st.cache_data(ttl=60 * 60)
def fetch_and_extract_text(url: str) -> str:
    """
    No extra API key version:
    - fetch HTML
    - trafilatura extracts main text
    """
    if not url:
        return ""
    try:
        res = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        res.raise_for_status()
        html = res.text
        extracted = trafilatura.extract(html) or ""
        extracted = re.sub(r"\n{3,}", "\n\n", extracted).strip()
        return extracted
    except Exception:
        return ""


# =========================================================
# LLM (Korean-first results, English UI allowed)
# =========================================================
def openai_client(openai_key: str) -> "OpenAI":
    return OpenAI(api_key=openai_key)


def try_parse_json(s: str) -> Optional[dict]:
    if not s:
        return None
    s = s.strip()
    try:
        return json.loads(s)
    except Exception:
        pass
    # try extract JSON block
    m = re.search(r"\{.*\}", s, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def llm_profile_analysis(profile: Dict[str, Any], openai_key: str, model: str) -> Dict[str, Any]:
    """
    한국어 결과.
    """
    client = openai_client(openai_key)

    system = (
        "너는 'MajorPass · YONSEI Edition'의 커리어/학업 코치다. "
        "대상은 연세대학교 학생. "
        "결과는 한국어로 작성하되, 섹션 제목은 짧은 영어를 섞어도 된다. "
        "과장하지 말고 현실적인 액션과 산출물을 중심으로 제안하라. "
        "반드시 JSON만 출력하라(마크다운 금지)."
    )

    schema = {
        "summary_ko": "string",
        "strengths": ["string"],
        "risks": ["string"],
        "next_focus": ["string"],
        "keyword_suggestions": ["string"],
        "action_plan": [
            {
                "priority": "High|Medium|Low",
                "action": "string",
                "deliverable": "string",
                "weeks": 1,
                "why": "string",
            }
        ],
        "tone_note": "짧게 1문장",
    }

    user = {
        "profile": profile,
        "output_schema": schema,
        "instructions": [
            "액션플랜은 6~10개",
            "deliverable(산출물)을 구체적으로",
            "연세대 학생 관점(캠퍼스/대외활동/인턴 준비 타이밍)으로 실용적으로",
        ],
    }

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
        temperature=0.5,
    )
    txt = resp.choices[0].message.content or ""
    parsed = try_parse_json(txt)
    if not parsed:
        raise ValueError("JSON 파싱 실패. 모델 출력이 JSON이 아닙니다.")
    return parsed


def llm_digest(
    selected_sources: List[Dict[str, Any]],
    openai_key: str,
    model: str,
) -> Dict[str, Any]:
    """
    selected_sources: [{Title, Link, Published, Type, ExtractedText, Snippet}]
    returns JSON:
      { digests: [...], overall: {...} }
    """
    client = openai_client(openai_key)

    system = (
        "너는 'Evidence Digest' 작성자다. "
        "입력으로 들어오는 여러 문서(기사/블로그/웹)의 텍스트를 읽고, "
        "연세대학교 학생에게 유용한 '요약본'만 제공한다. "
        "결과는 한국어 중심(영어는 1~2단어 UI 레벨만). "
        "반드시 JSON만 출력하라(마크다운 금지). "
        "너무 단정하지 말고, 근거가 약하면 confidence를 낮춰라."
    )

    schema = {
        "digests": [
            {
                "title": "string",
                "source_url": "string",
                "one_liner": "string",
                "highlights": ["string"],
                "yonsei_takeaways": ["string"],
                "next_actions": ["string"],
                "keywords": ["string"],
                "confidence": "높음|중간|낮음",
            }
        ],
        "overall": {
            "themes": ["string"],
            "recommended_queries": ["string"],
            "what_to_do_next": ["string"],
        },
    }

    # Reduce text to avoid huge tokens
    compact = []
    for s in selected_sources:
        compact.append({
            "title": s.get("Title", ""),
            "url": s.get("Link", ""),
            "published": s.get("Published", ""),
            "type": s.get("Type", ""),
            "snippet": (s.get("Snippet", "") or "")[:400],
            "text": clamp_text(s.get("ExtractedText", "") or "", 3200),
        })

    user = {
        "sources": compact,
        "output_schema": schema,
        "instructions": [
            "각 문서 요약은 한 줄(one_liner) + highlights(3~5) + takeaways(2~4) + next_actions(2~4)",
            "overall에는 공통 theme 3~6개, 추천 검색어 5~8개",
            "링크는 요약 검증용으로만(요약이 메인)",
        ],
    }

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
        ],
        temperature=0.4,
    )

    txt = resp.choices[0].message.content or ""
    parsed = try_parse_json(txt)
    if not parsed:
        raise ValueError("JSON 파싱 실패. 모델 출력이 JSON이 아닙니다.")
    return parsed


def llm_trend_interpretation(df: pd.DataFrame, openai_key: str, model: str) -> str:
    client = openai_client(openai_key)

    tail = df.tail(30).reset_index().to_dict(orient="records")

    system = (
        "너는 'Trend Pulse' 분석가다. "
        "시계열 비율 데이터에서 의미 있는 패턴(상승/하락/피크/지속)을 찾아 "
        "연세대 학생의 다음 액션(수업/프로젝트/검색어/포트폴리오)으로 연결하라. "
        "결과는 한국어로, 짧고 구조적으로."
    )
    user = {
        "data": tail,
        "format": [
            "요약(2~3줄)",
            "관찰 포인트 3개",
            "추천 액션 4개(산출물 포함)",
            "주의사항 1개(과해석 금지)",
        ],
    }
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": json.dumps(user, ensure_ascii=False)}],
        temperature=0.4,
    )
    return resp.choices[0].message.content or ""


def llm_plan_builder(context: Dict[str, Any], openai_key: str, model: str) -> Dict[str, Any]:
    client = openai_client(openai_key)

    system = (
        "너는 'Plan Builder'다. "
        "입력된 프로필/요약본/트렌드/분석을 종합해 '다음 학기 실행 로드맵'을 만든다. "
        "연세대학교 학생에게 현실적으로 실행 가능한 계획(주차별, 산출물 중심)이어야 한다. "
        "결과는 한국어 중심. 반드시 JSON만 출력."
    )

    schema = {
        "goal": "string",
        "north_star_deliverables": ["string"],
        "weekly_plan": [
            {"week": 1, "focus": "string", "deliverable": "string", "tasks": ["string"]}
        ],
        "course_activity_suggestions": [
            {"type": "Course|Project|Club|Contest|Intern", "suggestion": "string", "why": "string"}
        ],
        "risk_controls": ["string"],
        "checklist": ["string"],
    }

    payload = {"context": context, "output_schema": schema}

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
        temperature=0.45,
    )
    txt = resp.choices[0].message.content or ""
    parsed = try_parse_json(txt)
    if not parsed:
        raise ValueError("JSON 파싱 실패. 모델 출력이 JSON이 아닙니다.")
    return parsed


def llm_chat(user_message: str, history: List[Dict[str, str]], context: Dict[str, Any], openai_key: str, model: str) -> str:
    client = openai_client(openai_key)

    system = (
        "너는 'MajorPass · YONSEI Edition'의 대화 코치다. "
        "사용자의 상황에 맞춰 실전적으로 답하고, 결과는 한국어 중심으로 제공한다. "
        "가능하면 '다음 행동(액션)'을 체크리스트로 마무리하라. "
        "불필요하게 길게 쓰지 말고, 구조적(소제목/불릿)으로."
    )

    # light context
    ctx = {
        "profile": context.get("profile"),
        "analysis": context.get("analysis"),
        "digest_overall": (context.get("digest") or {}).get("overall") if isinstance(context.get("digest"), dict) else context.get("digest"),
        "trend_summary": context.get("trend"),
        "plan": context.get("plan"),
    }

    messages = [{"role": "system", "content": system}]
    messages.append({"role": "user", "content": f"컨텍스트(JSON): {json.dumps(ctx, ensure_ascii=False)}"})

    # last 8 turns
    for m in history[-8:]:
        messages.append({"role": m["role"], "content": m["content"]})

    messages.append({"role": "user", "content": user_message})

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.6,
    )
    return resp.choices[0].message.content or ""


# =========================================================
# SIDEBAR: KEYS & NAV
# =========================================================
with st.sidebar:
    st.markdown("## 🦅 MajorPass")
    st.caption("YONSEI Edition · Korean-first results")

    st.markdown("### 🔐 Keys")
    openai_key = st.text_input("OpenAI API Key", value=safe_secret("OPENAI_API_KEY"), type="password")
    model = st.text_input("Model (editable)", value=safe_secret("OPENAI_MODEL", "gpt-4o-mini"))

    st.markdown("### 🇰🇷 Naver OpenAPI")
    naver_id = st.text_input("NAVER_CLIENT_ID", value=safe_secret("NAVER_CLIENT_ID"), type="password")
    naver_secret = st.text_input("NAVER_CLIENT_SECRET", value=safe_secret("NAVER_CLIENT_SECRET"), type="password")

    st.markdown("### ⚙️ Options")
    max_digest_docs = st.slider("Digest 문서 수(최대)", 1, 6, 3, 1)
    show_extracted_text = st.toggle("디버그: 추출 본문 보기", value=False)

    st.markdown("---")

    nav = st.radio(
        "Navigation",
        ["Profile", "Evidence Digest", "Trend Pulse", "Plan Builder", "Chat Coach", "Rewards"],
        index=["Profile", "Evidence Digest", "Trend Pulse", "Plan Builder", "Chat Coach", "Rewards"].index(st.session_state.nav),
    )
    st.session_state.nav = nav

    st.markdown("---")
    st.caption("※ 학교 로고 사용은 규정/허용 범위 확인 권장\n(본 앱은 추상 독수리 아이콘을 기본 제공)")


# =========================================================
# HERO
# =========================================================
llm_ready = llm_enabled(openai_key)
naver_ready = bool(naver_id.strip() and naver_secret.strip())

st.markdown(
    f"""
<div class="mp-hero">
  <div class="mp-hero-top">
    <div class="mp-eagle">
      <div class="mp-eagle-badge">{eagle_svg()}</div>
      <div>
        <div class="mp-title">MajorPass <span style="color:{YONSEI_BLUE};">· YONSEI</span></div>
        <div class="mp-sub">전공을 커리어 자산으로 정리하는 <b>요약 중심</b> 코치 · <span style="color:{YONSEI_BLUE};font-weight:700;">Evidence → Plan → Action</span></div>
      </div>
    </div>
    <div class="mp-badges">
      <span class="mp-pill">🕒 {now_str()}</span>
      <span class="mp-pill">{'✅ LLM ON' if llm_ready else '⚪ LLM OFF'}</span>
      <span class="mp-pill">{'✅ NAVER ON' if naver_ready else '⚪ NAVER OFF'}</span>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# PAGE: PROFILE
# =========================================================
def page_profile() -> None:
    st.markdown("<div class='mp-section'>Profile</div>", unsafe_allow_html=True)
    st.caption("UI는 영어로 깔끔하게, 결과는 한국어로 명확하게. (원하면 Chat에서 더 다듬을 수 있어요)")

    with st.form("profile_form", border=False):
        c1, c2, c3 = st.columns([1.2, 1.0, 1.0])

        with c1:
            major = st.text_input("Major", value=st.session_state.profile.get("major", ""), placeholder="예: 경영학과 / 컴퓨터과학과")
            semester = st.selectbox(
                "Semester",
                options=[f"{y}학년 {s}학기" for y in range(1, 5) for s in (1, 2)],
                index=0,
            )
            plan = st.selectbox("Plan", ["본전공 유지", "복수전공 희망", "전과 희망"], index=0)

        with c2:
            gpa = st.slider("GPA (4.3)", 0.0, 4.3, float(st.session_state.profile.get("gpa", 3.5)), 0.01)
            major_credit = st.number_input("Major credits", 0, 200, int(st.session_state.profile.get("major_credit", 45)))
            liberal_credit = st.number_input("Liberal credits", 0, 200, int(st.session_state.profile.get("liberal_credit", 30)))

        with c3:
            total_required = st.number_input("Total required (editable)", 60, 200, int(st.session_state.profile.get("total_required", 130)))
            major_required = st.number_input("Major target", 0, 200, int(st.session_state.profile.get("major_required", 60)))
            liberal_required = st.number_input("Liberal target", 0, 200, int(st.session_state.profile.get("liberal_required", 30)))

        interest = st.text_area(
            "Interests / Direction (자유롭게)",
            value=st.session_state.profile.get("interest", ""),
            placeholder="예: PM, UX, 브랜딩, 데이터 분석, 콘텐츠, 전략기획…",
            height=100,
        )

        submitted = st.form_submit_button("Generate", use_container_width=True)

    if submitted:
        st.session_state.profile = {
            "major": major,
            "semester": semester,
            "plan": plan,
            "gpa": float(gpa),
            "major_credit": int(major_credit),
            "liberal_credit": int(liberal_credit),
            "total_required": int(total_required),
            "major_required": int(major_required),
            "liberal_required": int(liberal_required),
            "interest": interest,
        }

        unlock("first_profile")
        maybe_drop_reward("profile_done")

        st.session_state.chat_context["profile"] = st.session_state.profile

        # LLM analysis
        if llm_ready:
            with st.spinner("한국어 전략을 생성 중…"):
                try:
                    analysis = llm_profile_analysis(st.session_state.profile, openai_key, model)
                    st.session_state.profile_analysis = analysis
                    st.session_state.chat_context["analysis"] = analysis

                    df = pd.DataFrame(analysis.get("action_plan", []))
                    if not df.empty:
                        df = df.rename(columns={"weeks": "주(week)", "priority": "우선순위", "action": "액션", "deliverable": "산출물", "why": "이유"})
                    st.session_state.action_plan_df = df
                    st.session_state.recommended_keywords = (analysis.get("keyword_suggestions", []) or [])[:10]
                except Exception as e:
                    st.error(f"LLM 분석 오류: {e}")
                    st.session_state.profile_analysis = None
        else:
            st.info("좌측 사이드바에 OpenAI Key를 넣으면 ‘맞춤 전략(한국어)’이 생성됩니다.")

    # Display dashboard
    if st.session_state.profile:
        p = st.session_state.profile
        total_done = p["major_credit"] + p["liberal_credit"]
        total_remaining = max(0, p["total_required"] - total_done)
        major_remaining = max(0, p["major_required"] - p["major_credit"])
        lib_remaining = max(0, p["liberal_required"] - p["liberal_credit"])

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("GPA", f"{p['gpa']:.2f} / 4.30")
        k2.metric("Credits", f"{total_done}", f"-{total_remaining} 남음")
        k3.metric("Major", f"{p['major_credit']}", f"-{major_remaining} 목표까지")
        k4.metric("Liberal", f"{p['liberal_credit']}", f"-{lib_remaining} 목표까지")

        st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)

        c1, c2 = st.columns([1.15, 0.85])
        with c1:
            st.markdown("<div class='mp-card'><div class='mp-section'>Dashboard</div><div class='mp-muted'>학점 진행 상황을 한눈에.</div></div>", unsafe_allow_html=True)
            chart_df = pd.DataFrame(
                {
                    "Category": ["Total", "Major", "Liberal"],
                    "Completed": [total_done, p["major_credit"], p["liberal_credit"]],
                    "Remaining": [total_remaining, major_remaining, lib_remaining],
                }
            ).set_index("Category")
            st.bar_chart(chart_df)

        with c2:
            st.markdown("<div class='mp-card'><div class='mp-section'>Keyword Seeds</div><div class='mp-muted'>Evidence Digest / Trend에서 바로 쓰세요.</div></div>", unsafe_allow_html=True)
            kws = st.session_state.recommended_keywords or []
            if kws:
                st.write(" • ".join(kws))
            else:
                st.write("- 아직 추천 키워드가 없어요. Generate 후 자동 생성됩니다.")

        st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)

        left, right = st.columns([1.2, 0.8])
        with left:
            st.markdown("<div class='mp-card-solid'><div class='mp-section'>Summary</div></div>", unsafe_allow_html=True)
            if st.session_state.profile_analysis:
                a = st.session_state.profile_analysis
                st.write(a.get("summary_ko", ""))

                st.markdown("**Strengths**")
                st.write("\n".join([f"- {x}" for x in a.get("strengths", [])]) or "- (없음)")

                st.markdown("**Risks**")
                st.write("\n".join([f"- {x}" for x in a.get("risks", [])]) or "- (없음)")

                st.markdown("**Next Focus**")
                st.write("\n".join([f"- {x}" for x in a.get("next_focus", [])]) or "- (없음)")
            else:
                st.info("아직 분석 결과가 없어요. 상단에서 Generate를 눌러주세요.")

        with right:
            st.markdown("<div class='mp-card-solid'><div class='mp-section'>Action Plan</div><div class='mp-muted'>산출물 중심으로 설계됨</div></div>", unsafe_allow_html=True)
            df = st.session_state.action_plan_df
            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                fallback = pd.DataFrame([
                    {"우선순위": "High", "액션": "타겟 직무 1~2개 정의", "산출물": "직무 브리프 1p", "주(week)": 1, "이유": "선택지가 줄어야 실행이 쉬워져요."},
                    {"우선순위": "High", "액션": "포트폴리오 산출물 1개 만들기", "산출물": "케이스 스터디/리포트", "주(week)": 3, "이유": "말이 아니라 증거를 만들기."},
                    {"우선순위": "Medium", "액션": "Evidence Digest 3건 생성", "산출물": "요약 카드 3개", "주(week)": 1, "이유": "현실 기반 의사결정."},
                ])
                df = fallback
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "Download CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="majorpass_action_plan.csv",
                mime="text/csv",
                use_container_width=True,
            )


# =========================================================
# PAGE: EVIDENCE DIGEST
# =========================================================
def page_digest() -> None:
    st.markdown("<div class='mp-section'>Evidence Digest</div>", unsafe_allow_html=True)
    st.caption("링크를 나열하는 대신, **요약본(정리본)**만 보여주는 모드입니다. (원문 링크는 검증용으로 최소화)")

    if not naver_ready:
        st.warning("좌측에서 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 을 입력하면 사용 가능합니다.")
        return

    default_q = ""
    if st.session_state.recommended_keywords:
        default_q = st.session_state.recommended_keywords[0]
    elif st.session_state.profile:
        default_q = st.session_state.profile.get("interest", "") or st.session_state.profile.get("major", "")

    q1, q2, q3, q4 = st.columns([1.4, 0.8, 0.8, 0.8])
    with q1:
        query = st.text_input("Query", value=default_q, placeholder="예: UX 인턴, 데이터 분석, 브랜드 매니저…")
    with q2:
        category = st.selectbox("Type", ["news", "blog", "webkr"], index=0)
    with q3:
        sort = st.selectbox("Sort", ["sim", "date"], index=0)
    with q4:
        display = st.slider("Results", 5, 30, 10, 5)

    run_search = st.button("Search", use_container_width=True)

    if run_search:
        with st.spinner("Naver에서 검색 결과를 가져오는 중…"):
            try:
                df = naver_search(query=query, client_id=naver_id, client_secret=naver_secret, category=category, display=display, sort=sort)
                st.session_state.search_df = df
            except Exception as e:
                st.error(f"Naver Search 오류: {e}")

    df = st.session_state.search_df
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        st.info("검색 후, 요약하고 싶은 문서를 선택(Select)하고 Digest를 실행하세요.")
        return

    st.markdown("<div class='mp-card-solid'><div class='mp-section'>Select sources</div><div class='mp-muted'>최대 3~6개 추천(비용/속도 고려)</div></div>", unsafe_allow_html=True)

    edited = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Select": st.column_config.CheckboxColumn("Select"),
            "Link": st.column_config.LinkColumn("Link", display_text="open"),
        },
        disabled=["Title", "Snippet", "Link", "Published", "Type"],
    )
    st.session_state.search_df = edited

    selected = edited[edited["Select"] == True].head(max_digest_docs)
    if selected.empty:
        st.warning("Select 체크를 해주세요.")
        return

    digest_btn = st.button("Digest selected", use_container_width=True)

    if digest_btn:
        if not llm_ready:
            st.warning("요약본 생성은 LLM(OpenAI Key)이 필요합니다. 좌측 사이드바에 키를 입력해주세요.")
            return

        with st.spinner("원문을 추출하고 요약본을 생성 중…"):
            sources = []
            for _, row in selected.iterrows():
                url = row.get("Link", "")
                text = fetch_and_extract_text(url)
                sources.append({
                    "Title": row.get("Title", ""),
                    "Link": url,
                    "Published": row.get("Published", ""),
                    "Type": row.get("Type", ""),
                    "Snippet": row.get("Snippet", ""),
                    "ExtractedText": text,
                })

            # If extraction fails, still allow snippet-based digest
            for s in sources:
                if not s["ExtractedText"]:
                    s["ExtractedText"] = s["Snippet"]

            try:
                digest = llm_digest(sources, openai_key=openai_key, model=model)
                st.session_state.digest_result = digest

                unlock("first_digest")
                maybe_drop_reward("digest_done")
                check_combo()

                st.session_state.chat_context["digest"] = digest
            except Exception as e:
                st.error(f"Digest 생성 오류: {e}")
                st.session_state.digest_result = None

    digest = st.session_state.digest_result
    if not digest:
        return

    # Overall
    overall = digest.get("overall", {})
    st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='mp-card'><div class='mp-section'>Overall</div></div>", unsafe_allow_html=True)
    if overall:
        st.markdown("**Themes**")
        st.write("\n".join([f"- {t}" for t in overall.get("themes", [])]) or "- (없음)")
        st.markdown("**Recommended Queries**")
        st.write(" • ".join(overall.get("recommended_queries", [])) or "- (없음)")
        st.markdown("**What to do next**")
        st.write("\n".join([f"- {x}" for x in overall.get("what_to_do_next", [])]) or "- (없음)")

    # Per-doc cards
    st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='mp-section'>Digest Cards</div>", unsafe_allow_html=True)

    for d in digest.get("digests", []):
        title = d.get("title", "")
        url = d.get("source_url", "")
        one = d.get("one_liner", "")
        conf = d.get("confidence", "중간")
        keywords = d.get("keywords", [])[:6]

        tags_html = "".join([f"<span class='d-tag'>{clean_html(k)}</span>" for k in keywords])

        st.markdown(
            f"""
<div class="d-card">
  <div class="d-head">
    <div>
      <div class="d-title">{clean_html(title)}</div>
      <div class="d-one">{clean_html(one)}</div>
    </div>
    <div class="d-meta">confidence · <b>{conf}</b></div>
  </div>
  <div style="margin-top:10px;">{tags_html}</div>
</div>
""",
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("**핵심 요약**")
            st.write("\n".join([f"- {x}" for x in d.get("highlights", [])]) or "-")
            st.markdown("**연세대 학생에게 의미**")
            st.write("\n".join([f"- {x}" for x in d.get("yonsei_takeaways", [])]) or "-")
        with c2:
            st.markdown("**다음 행동(액션)**")
            st.write("\n".join([f"- {x}" for x in d.get("next_actions", [])]) or "-")
            if url:
                st.link_button("원문 보기 (검증용)", url, use_container_width=True)

        if show_extracted_text:
            with st.expander("추출 본문(디버그)", expanded=False):
                st.write(clamp_text(fetch_and_extract_text(url), 5000))


# =========================================================
# PAGE: TREND PULSE
# =========================================================
def page_trend() -> None:
    st.markdown("<div class='mp-section'>Trend Pulse</div>", unsafe_allow_html=True)
    st.caption("관심 키워드의 흐름을 보고, ‘지금 무엇을 쌓을지’를 결정합니다.")

    if not naver_ready:
        st.warning("NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 이 필요합니다.")
        return

    end = date.today()
    start = end - timedelta(days=365)

    c1, c2, c3 = st.columns([1.0, 1.0, 1.0])
    with c1:
        start_date = st.date_input("Start", value=start)
    with c2:
        end_date = st.date_input("End", value=end)
    with c3:
        time_unit = st.selectbox("Unit", ["week", "month", "date"], index=0)

    st.markdown("**Keywords (up to 5)**")
    suggested = st.session_state.recommended_keywords[:5] if st.session_state.recommended_keywords else []
    cols = st.columns(5)
    keys = []
    for i in range(5):
        default_kw = suggested[i] if i < len(suggested) else ""
        with cols[i]:
            keys.append(st.text_input(f"K{i+1}", value=default_kw, placeholder="예: UX"))

    run = st.button("Generate", use_container_width=True)

    if run:
        groups = []
        for kw in keys:
            kw = (kw or "").strip()
            if kw:
                groups.append({"groupName": kw, "keywords": [kw]})
        if not groups:
            st.warning("키워드를 1개 이상 입력해주세요.")
            return

        with st.spinner("Naver Datalab 호출 중…"):
            try:
                df = naver_datalab_trend(
                    client_id=naver_id,
                    client_secret=naver_secret,
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d"),
                    time_unit=time_unit,
                    keyword_groups=groups,
                )
                st.session_state.trend_df = df
                unlock("first_trend")
                maybe_drop_reward("trend_done")
                check_combo()
            except Exception as e:
                st.error(f"Trend 오류: {e}")
                st.session_state.trend_df = None

    df = st.session_state.trend_df
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        st.info("Generate를 눌러 그래프를 생성하세요.")
        return

    st.markdown("<div class='mp-card-solid'><div class='mp-section'>Chart</div><div class='mp-muted'>절대 검색량이 아니라 ‘상대적 신호’입니다.</div></div>", unsafe_allow_html=True)
    st.line_chart(df)

    if llm_ready:
        if st.button("Interpret", use_container_width=True):
            with st.spinner("트렌드 해석 생성 중…"):
                try:
                    summary = llm_trend_interpretation(df, openai_key, model)
                    st.session_state.trend_summary = summary
                    st.session_state.chat_context["trend"] = summary
                except Exception as e:
                    st.error(f"해석 오류: {e}")

    if st.session_state.trend_summary:
        st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='mp-card'><div class='mp-section'>Interpretation</div></div>", unsafe_allow_html=True)
        st.write(st.session_state.trend_summary)


# =========================================================
# PAGE: PLAN BUILDER
# =========================================================
def page_plan() -> None:
    st.markdown("<div class='mp-section'>Plan Builder</div>", unsafe_allow_html=True)
    st.caption("Profile + Evidence Digest + Trend를 합쳐 다음 학기 실행 로드맵을 만듭니다.")

    if not st.session_state.profile:
        st.warning("먼저 Profile에서 정보를 입력하고 Generate를 해주세요.")
        return

    if not llm_ready:
        st.warning("Plan 생성은 LLM(OpenAI Key)이 필요합니다.")
        return

    context = {
        "profile": st.session_state.profile,
        "analysis": st.session_state.profile_analysis,
        "digest": st.session_state.digest_result,
        "trend_summary": st.session_state.trend_summary,
    }

    st.markdown("<div class='mp-card-solid'><div class='mp-section'>Inputs</div><div class='mp-muted'>현재 세션에 저장된 정보로 계획을 만듭니다.</div></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Profile", "✅" if st.session_state.profile else "⚪")
    c2.metric("Digest", "✅" if st.session_state.digest_result else "⚪")
    c3.metric("Trend", "✅" if st.session_state.trend_df is not None else "⚪")

    gen = st.button("Build Plan", use_container_width=True)

    if gen:
        with st.spinner("다음 학기 로드맵 생성 중…"):
            try:
                plan = llm_plan_builder(context, openai_key, model)
                st.session_state.plan_result = plan
                unlock("first_plan")
                maybe_drop_reward("plan_done")
                st.session_state.chat_context["plan"] = plan
            except Exception as e:
                st.error(f"Plan 생성 오류: {e}")

    plan = st.session_state.plan_result
    if not plan:
        st.info("Build Plan을 눌러 계획을 생성하세요.")
        return

    st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='mp-card'><div class='mp-section'>Goal</div></div>", unsafe_allow_html=True)
    st.write(plan.get("goal", ""))

    st.markdown("**North Star Deliverables**")
    st.write("\n".join([f"- {x}" for x in plan.get("north_star_deliverables", [])]) or "-")

    # Weekly plan table
    weekly = plan.get("weekly_plan", [])
    if weekly:
        df = pd.DataFrame(weekly)
        st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='mp-card-solid'><div class='mp-section'>Weekly Plan</div><div class='mp-muted'>주차별 초점과 산출물</div></div>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Weekly Plan CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="majorpass_weekly_plan.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # Suggestions
    sug = plan.get("course_activity_suggestions", [])
    if sug:
        st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)
        st.markdown("<div class='mp-card-solid'><div class='mp-section'>Suggestions</div></div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(sug), use_container_width=True, hide_index=True)

    st.markdown("**Risk controls**")
    st.write("\n".join([f"- {x}" for x in plan.get("risk_controls", [])]) or "-")

    st.markdown("**Checklist**")
    st.write("\n".join([f"- {x}" for x in plan.get("checklist", [])]) or "-")


# =========================================================
# PAGE: CHAT COACH
# =========================================================
def page_chat() -> None:
    st.markdown("<div class='mp-section'>Chat Coach</div>", unsafe_allow_html=True)
    st.caption("버튼으로 원하는 답변 형태를 고르고, 결과는 한국어로 받는 코치 모드입니다.")

    # render history
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # quick actions
    q1, q2, q3, q4 = st.columns(4)
    if q1.button("4-week Plan", use_container_width=True):
        st.session_state.pending_user_message = "내 상황을 바탕으로 4주 실행계획을 만들어줘. 산출물 중심으로."
    if q2.button("Priorities", use_container_width=True):
        st.session_state.pending_user_message = "다음 학기 우선순위 5개를 정해줘. 각 우선순위마다 왜 중요한지 근거도 써줘."
    if q3.button("Digest → Actions", use_container_width=True):
        st.session_state.pending_user_message = "Evidence Digest 요약을 바탕으로 당장 할 수 있는 액션 6개로 바꿔줘. 산출물 포함."
    if q4.button("Portfolio Outline", use_container_width=True):
        st.session_state.pending_user_message = "내 관심사에 맞는 포트폴리오 목차를 설계해줘. 섹션별 예시 산출물도."

    user_input = st.chat_input("메시지를 입력하세요… (한국어 추천)")
    if user_input:
        st.session_state.pending_user_message = user_input

    if st.session_state.pending_user_message:
        msg = st.session_state.pending_user_message
        st.session_state.pending_user_message = None

        # secret phrase
        if SECRET_PHRASE in msg.lower():
            unlock("secret_phrase")
            maybe_drop_reward("secret_phrase")

        st.session_state.chat_history.append({"role": "user", "content": msg})
        with st.chat_message("user"):
            st.markdown(msg)

        # chat count
        user_msgs = [x for x in st.session_state.chat_history if x["role"] == "user"]
        if len(user_msgs) >= 5:
            unlock("chat_5")

        if not llm_ready:
            with st.chat_message("assistant"):
                st.info("Chat은 OpenAI Key가 필요합니다. 좌측 사이드바에 입력해주세요.")
            return

        with st.chat_message("assistant"):
            with st.spinner("생각 중…"):
                try:
                    answer = llm_chat(
                        user_message=msg,
                        history=st.session_state.chat_history[:-1],
                        context=st.session_state.chat_context,
                        openai_key=openai_key,
                        model=model,
                    )
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                    maybe_drop_reward("chat_done")
                except Exception as e:
                    st.error(f"Chat 오류: {e}")


# =========================================================
# PAGE: REWARDS
# =========================================================
def page_rewards() -> None:
    st.markdown("<div class='mp-section'>Rewards</div>", unsafe_allow_html=True)
    st.caption("귀엽지만 유치하지 않게: 깃털/횃불/책/시크릿 배지로 ‘실행’을 유도합니다.")

    st.markdown("<div class='mp-card-solid'><div class='mp-section'>Achievements</div><div class='mp-muted'>일부는 숨겨져 있어요.</div></div>", unsafe_allow_html=True)

    ach = st.session_state.achievements
    rows = []
    for k, v in ach.items():
        rows.append({"업적": k, "상태": "✅" if v else "🔒"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)

    st.markdown("<div class='mp-card-solid'><div class='mp-section'>Collectibles</div><div class='mp-muted'>행동할 때 랜덤 드랍</div></div>", unsafe_allow_html=True)
    if not st.session_state.rewards:
        st.info("아직 보상이 없어요. Profile/Digest/Trend/Plan/Chat을 사용해보세요.")
        return

    for r in reversed(st.session_state.rewards[-25:]):
        st.markdown(
            f"""
<div class="d-card" style="margin-bottom:10px;">
  <div class="d-head">
    <div>
      <div class="d-title">{r['emoji']} {r['name']} <span style="color:rgba(11,18,32,0.55);font-weight:700;">({r['rarity']})</span></div>
      <div class="d-one">{r['rarity_icon']} {r['event']} · {r['ts']}</div>
    </div>
    <div class="d-meta">{r['rarity_icon']}</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )


# =========================================================
# ROUTER
# =========================================================
if st.session_state.nav == "Profile":
    page_profile()
elif st.session_state.nav == "Evidence Digest":
    page_digest()
elif st.session_state.nav == "Trend Pulse":
    page_trend()
elif st.session_state.nav == "Plan Builder":
    page_plan()
elif st.session_state.nav == "Chat Coach":
    page_chat()
elif st.session_state.nav == "Rewards":
    page_rewards()
