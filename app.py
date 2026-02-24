import json
import os
import random
import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

import trafilatura  # 본문 추출 (키 필요 없음)

# Optional OpenAI (LLM)
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

YONSEI_BLUE = "#003876"


# =========================================================
# SVG: Eagle (abstract / not official logo)
# =========================================================
def eagle_svg(color: str = YONSEI_BLUE) -> str:
    return f"""
<svg width="54" height="54" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="eagle">
  <path d="M8 38c10-8 18-12 24-12s14 4 24 12" stroke="{color}" stroke-width="3" stroke-linecap="round"/>
  <path d="M10 34c8-10 16-16 22-16s14 6 22 16" stroke="{color}" stroke-width="3" stroke-linecap="round" opacity="0.8"/>
  <path d="M22 28c3-6 6-10 10-10s7 4 10 10" stroke="{color}" stroke-width="3" stroke-linecap="round" opacity="0.7"/>
  <path d="M30 20c1-2 2-3 2-3s1 1 2 3" stroke="{color}" stroke-width="3" stroke-linecap="round"/>
  <circle cx="32" cy="22" r="1.5" fill="{color}"/>
</svg>
""".strip()


# =========================================================
# CSS — White background + premium glass cards + fix hero clipping
# =========================================================
def inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

:root{
  --bg: #FFFFFF;
  --bg2: #F7F8FC;
  --text: #0B1220;
  --muted: rgba(11,18,32,0.62);
  --card: rgba(255,255,255,0.72);
  --card2: rgba(255,255,255,0.92);
  --border: rgba(15,23,42,0.10);
  --shadow: 0 14px 38px rgba(15,23,42,0.12);
  --radius: 18px;
  --yonsei: #003876;
  --accent: #4F46E5;
  --mint: #22C55E;
}

/* background */
html, body, [data-testid="stApp"]{
  font-family: Pretendard, Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: var(--text);
}
[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(1100px 650px at 12% 12%, rgba(0,56,118,0.12), transparent 60%),
    radial-gradient(900px 550px at 88% 10%, rgba(79,70,229,0.12), transparent 60%),
    linear-gradient(180deg, var(--bg2), var(--bg) 60%);
  position: relative;
}

/* subtle noise overlay */
[data-testid="stAppViewContainer"]::before{
  content:"";
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.06;
  mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='https://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='180' height='180' filter='url(%23n)' opacity='.35'/%3E%3C/svg%3E");
}

/* ✅ extra top padding to prevent hero clipping */
.block-container{
  padding-top: 1.65rem;
  padding-bottom: 3rem;
  max-width: 1200px;
}

/* hide default footer */
footer {visibility: hidden;}

/* sidebar */
section[data-testid="stSidebar"]{
  background: rgba(255,255,255,0.70) !important;
  border-right: 1px solid var(--border);
  backdrop-filter: blur(10px);
}

/* ✅ add margin-top to hero */
.mp-hero{
  margin-top: 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  background: linear-gradient(120deg, rgba(0,56,118,0.10), rgba(79,70,229,0.08));
  padding: 18px 18px;
  margin-bottom: 18px;
  overflow:hidden;
  position: relative;
}
.mp-hero::after{
  content:"";
  position:absolute;
  inset:-2px;
  background: radial-gradient(600px 160px at 20% 0%, rgba(255,255,255,0.62), transparent 60%);
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
  animation: heroIn 900ms ease-out both;
}
@keyframes heroIn{
  0%{ transform: translateY(6px) scale(1.02); opacity: 0; filter: blur(2px); }
  100%{ transform: translateY(0) scale(1.00); opacity: 1; filter: blur(0px); }
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
  background: rgba(255,255,255,0.78);
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

/* section */
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

/* cards */
.mp-card{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 16px 16px;
  backdrop-filter: blur(10px);
}
.mp-card-solid{
  background: var(--card2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 16px 16px;
  backdrop-filter: blur(10px);
}

/* digest card */
.d-card{
  background: rgba(255,255,255,0.86);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px 14px;
  box-shadow: 0 12px 32px rgba(15,23,42,0.10);
  backdrop-filter: blur(10px);
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

/* dataframe */
[data-testid="stDataFrame"]{
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow: hidden;
}

/* buttons */
.stButton button, .stDownloadButton button{
  border-radius: 12px !important;
  padding: 10px 14px !important;
  font-weight: 700 !important;
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
    ss.setdefault("profile", {})
    ss.setdefault("profile_analysis", None)
    ss.setdefault("action_plan_df", None)
    ss.setdefault("recommended_keywords", [])

    ss.setdefault("search_df", None)
    ss.setdefault("digest_result", None)
    ss.setdefault("trend_df", None)
    ss.setdefault("trend_summary", None)
    ss.setdefault("plan_result", None)

    ss.setdefault("chat_history", [])
    ss.setdefault("chat_context", {"profile": None, "analysis": None, "digest": None, "trend": None, "plan": None})

    ss.setdefault("achievements", {"chat_5": False, "secret_phrase": False})

    ss.setdefault("xp", 0)
    ss.setdefault("growth_stage", 0)
    ss.setdefault("growth_log", [])
    ss.setdefault("roadmap_todos", [])
    ss.setdefault("todos_seeded", False)


init_state()


# =========================================================
# HELPERS
# =========================================================
def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", text).strip()


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
# REWARDS / ACHIEVEMENTS
# =========================================================
def _unlock(key: str) -> None:
    if key in st.session_state.achievements and not st.session_state.achievements[key]:
        st.session_state.achievements[key] = True
        st.toast(f"Unlocked: {key}", icon="🏆")


def award_xp(points: int, reason: str) -> None:
    ss = st.session_state
    ss.xp += max(0, int(points))
    ss.growth_log.append({"ts": now_str(), "reason": reason, "points": int(points)})
    ss.growth_stage = _current_stage_from_xp(ss.xp)


def _maybe_drop_reward(event: str) -> None:
    points_map = {
        "profile_done": 8,
        "digest_done": 10,
        "trend_done": 8,
        "plan_done": 12,
        "chat_done": 2,
        "secret_phrase_used": 3,
        "todo_added": 2,
    }
    award_xp(points_map.get(event, 2), reason=event)


# =========================================================
# GROWTH STAGES (XP thresholds)
# =========================================================
GROWTH_STAGES = [
    {"name": "Baby", "min_xp": 0, "desc": "작은 행동부터 시작해요.", "emoji": "👶"},
    {"name": "Kid", "min_xp": 25, "desc": "조금씩 습관이 잡히는 구간!", "emoji": "🧒"},
    {"name": "Student", "min_xp": 60, "desc": "산출물이 쌓이기 시작해요.", "emoji": "🧑‍🎓"},
    {"name": "Adult", "min_xp": 100, "desc": "학기 계획을 견고하게 만드는 단계.", "emoji": "🧑"},
    {"name": "Pro", "min_xp": 150, "desc": "완성 단계. 결과물을 지원/제출로 연결!", "emoji": "🧑‍💼"},
]


def _current_stage_from_xp(xp: int) -> int:
    stage = 0
    for i, stg in enumerate(GROWTH_STAGES):
        if xp >= stg["min_xp"]:
            stage = i
    return stage


# =========================================================
# NAVER APIs
# =========================================================
def naver_headers(client_id: str, client_secret: str) -> Dict[str, str]:
    return {"X-Naver-Client-Id": client_id.strip(), "X-Naver-Client-Secret": client_secret.strip()}


@st.cache_data(ttl=60 * 30)
def naver_search(query: str, client_id: str, client_secret: str, category: str = "news", display: int = 10, sort: str = "sim") -> pd.DataFrame:
    if not query.strip():
        return pd.DataFrame()
    url = f"https://openapi.naver.com/v1/search/{category}.json"
    params = {"query": query, "display": int(display), "start": 1, "sort": sort}
    res = requests.get(url, headers=naver_headers(client_id, client_secret), params=params, timeout=15)
    res.raise_for_status()
    data = res.json()
    items = data.get("items", [])
    rows = []
    for it in items:
        rows.append(
            {
                "Select": False,
                "Title": clean_html(it.get("title", "")),
                "Snippet": clean_html(it.get("description", "")),
                "Link": it.get("originallink") or it.get("link") or "",
                "Published": it.get("pubDate") or "",
                "Type": category,
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(ttl=60 * 60)
def naver_datalab_trend(client_id: str, client_secret: str, start_date: str, end_date: str, time_unit: str, keyword_groups: List[Dict[str, Any]]) -> pd.DataFrame:
    url = "https://openapi.naver.com/v1/datalab/search"
    body = {"startDate": start_date, "endDate": end_date, "timeUnit": time_unit, "keywordGroups": keyword_groups}
    res = requests.post(
        url,
        headers={**naver_headers(client_id, client_secret), "Content-Type": "application/json"},
        data=json.dumps(body, ensure_ascii=False),
        timeout=20,
    )
    res.raise_for_status()
    data = res.json()
    results = data.get("results", [])
    if not results:
        return pd.DataFrame()

    all_periods = set()
    series: Dict[str, Dict[str, float]] = {}
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
# EXTRACTION (no key)
# =========================================================
@st.cache_data(ttl=60 * 60)
def fetch_and_extract_text(url: str) -> str:
    if not url:
        return ""
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        extracted = trafilatura.extract(r.text) or ""
        extracted = re.sub(r"\n{3,}", "\n\n", extracted).strip()
        return extracted
    except Exception:
        return ""


# =========================================================
# LLM
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
    m = re.search(r"\{.*\}", s, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def llm_profile_analysis(profile: Dict[str, Any], openai_key: str, model: str) -> Dict[str, Any]:
    client = openai_client(openai_key)
    system = (
        "너는 'MajorPass · YONSEI Edition'의 커리어/학업 코치다. "
        "대상은 대학교 학생. 결과는 한국어로 작성하라. "
        "실행 가능한 액션과 산출물을 중심으로 제안하라. "
        "반드시 JSON만 출력(마크다운 금지)."
    )
    schema = {
        "summary_ko": "string",
        "strengths": ["string"],
        "risks": ["string"],
        "next_focus": ["string"],
        "keyword_suggestions": ["string"],
        "action_plan": [
            {"priority": "High|Medium|Low", "action": "string", "deliverable": "string", "weeks": 1, "why": "string"}
        ],
    }
    payload = {"profile": profile, "output_schema": schema}
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
        temperature=0.5,
    )
    parsed = try_parse_json(resp.choices[0].message.content or "")
    if not parsed:
        raise ValueError("JSON 파싱 실패")
    return parsed


def llm_digest(selected_sources: List[Dict[str, Any]], openai_key: str, model: str) -> Dict[str, Any]:
    client = openai_client(openai_key)
    system = (
        "너는 'Evidence Digest' 작성자다. 여러 문서 텍스트를 읽고 "
        "사용자에게 링크 나열이 아니라 정리본만 제공한다. "
        "결과는 한국어로, 근거가 약하면 confidence를 낮춰라. "
        "반드시 JSON만 출력(마크다운 금지)."
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
        "overall": {"themes": ["string"], "recommended_queries": ["string"], "what_to_do_next": ["string"]},
    }

    compact = []
    for s in selected_sources:
        compact.append(
            {
                "title": s.get("Title", ""),
                "url": s.get("Link", ""),
                "published": s.get("Published", ""),
                "type": s.get("Type", ""),
                "snippet": (s.get("Snippet", "") or "")[:400],
                "text": clamp_text(s.get("ExtractedText", "") or "", 3200),
            }
        )
    payload = {"sources": compact, "output_schema": schema}
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
        temperature=0.4,
    )
    parsed = try_parse_json(resp.choices[0].message.content or "")
    if not parsed:
        raise ValueError("JSON 파싱 실패")
    return parsed


def llm_trend_interpretation(df: pd.DataFrame, openai_key: str, model: str) -> str:
    client = openai_client(openai_key)
    tail = df.tail(30).reset_index().to_dict(orient="records")
    system = (
        "너는 'Trend Pulse' 분석가다. 시계열 비율 데이터에서 패턴을 찾아 "
        "다음 행동(수업/프로젝트/검색어/포트폴리오)으로 연결하라. "
        "결과는 한국어로, 짧고 구조적으로."
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": json.dumps({"data": tail}, ensure_ascii=False)}],
        temperature=0.4,
    )
    return resp.choices[0].message.content or ""


def llm_plan_builder(context: Dict[str, Any], openai_key: str, model: str) -> Dict[str, Any]:
    client = openai_client(openai_key)
    system = (
        "너는 'Plan Builder'다. 프로필/요약/트렌드/분석을 종합해 다음 학기 실행 로드맵을 만든다. "
        "주차별, 산출물 중심. 결과는 한국어. 반드시 JSON만 출력."
    )
    schema = {
        "goal": "string",
        "north_star_deliverables": ["string"],
        "weekly_plan": [{"week": 1, "focus": "string", "deliverable": "string", "tasks": ["string"]}],
        "risk_controls": ["string"],
        "checklist": ["string"],
    }
    payload = {"context": context, "output_schema": schema}
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
        temperature=0.45,
    )
    parsed = try_parse_json(resp.choices[0].message.content or "")
    if not parsed:
        raise ValueError("JSON 파싱 실패")
    return parsed


def llm_chat(*, openai_key: str, model: str, history: List[Dict[str, str]], context: Dict[str, Any], user_message: str) -> str:
    client = openai_client(openai_key)
    system = (
        "너는 'MajorPass · YONSEI Edition'의 대화 코치다. "
        "항상 한국어로 답하라. 구조적으로(짧은 소제목/불릿) 쓰고 "
        "마지막에 '다음 행동' 체크리스트로 마무리하라."
    )
    ctx = {
        "profile": context.get("profile"),
        "analysis": context.get("analysis"),
        "digest_overall": (context.get("digest") or {}).get("overall") if isinstance(context.get("digest"), dict) else context.get("digest"),
        "trend_summary": context.get("trend"),
        "plan": context.get("plan"),
    }
    messages = [{"role": "system", "content": system}]
    messages.append({"role": "user", "content": f"컨텍스트(JSON): {json.dumps(ctx, ensure_ascii=False)}"})
    for m in history[-10:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_message})
    resp = client.chat.completions.create(model=model, messages=messages, temperature=0.6)
    return resp.choices[0].message.content or ""


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 🔐 Keys")
    openai_key = st.text_input("OpenAI API Key", value=safe_secret("OPENAI_API_KEY"), type="password")
    model = st.text_input("Model", value=safe_secret("OPENAI_MODEL", "gpt-4o-mini"))

    st.markdown("## 🇰🇷 Naver OpenAPI")
    naver_id = st.text_input("NAVER_CLIENT_ID", value=safe_secret("NAVER_CLIENT_ID"), type="password")
    naver_secret = st.text_input("NAVER_CLIENT_SECRET", value=safe_secret("NAVER_CLIENT_SECRET"), type="password")

    st.markdown("## ⚙️ Options")
    max_digest_docs = st.slider("Digest sources", 1, 6, 3, 1)
    show_extracted_text = st.toggle("Debug: show extracted text", value=False)

    st.markdown("---")
    st.caption("Streamlit Cloud Settings → Secrets에 키를 등록하면 됩니다.")


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
        <div class="mp-sub">Evidence → Plan → Action</div>
      </div>
    </div>
    <div class="mp-badges">
      <span class="mp-pill">🕒 {now_str()}</span>
      <span class="mp-pill">{'✅ LLM' if llm_ready else '⚪ LLM'}</span>
      <span class="mp-pill">{'✅ NAVER' if naver_ready else '⚪ NAVER'}</span>
      <span class="mp-pill">🪙 XP {st.session_state.xp}</span>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# =========================================================
# Growth todos seeding
# =========================================================
def seed_todos_if_needed() -> None:
    ss = st.session_state
    if ss.todos_seeded and ss.roadmap_todos:
        return

    todos = []
    tid = 1

    df = ss.action_plan_df
    if isinstance(df, pd.DataFrame) and not df.empty:
        for _, r in df.head(10).iterrows():
            action = str(r.get("액션", "")).strip()
            deliverable = str(r.get("산출물", "")).strip()
            pr = str(r.get("우선순위", "Medium")).strip().lower()
            points = 14 if "high" in pr else (10 if "medium" in pr else 8)
            task = action if action else "로드맵 액션"
            if deliverable and deliverable != "nan":
                task = f"{task} → 산출물: {deliverable}"
            todos.append({"id": tid, "task": task, "done": False, "points": points, "source": "Action Plan"})
            tid += 1

    if not todos:
        base = [
            ("타겟 직무 1개를 1페이지로 정리하기", 12),
            ("포트폴리오 산출물 1개 초안 만들기", 14),
            ("Evidence Digest 2건 생성하기", 10),
            ("트렌드 키워드 2개 비교 후 결론 5줄 작성", 10),
        ]
        for t, p in base:
            todos.append({"id": tid, "task": t, "done": False, "points": p, "source": "Starter"})
            tid += 1

    ss.roadmap_todos = todos
    ss.todos_seeded = True


# =========================================================
# MAIN TABS
# =========================================================
tab_profile, tab_digest, tab_trend, tab_plan, tab_chat, tab_growth = st.tabs(
    ["Profile", "Evidence Digest", "Trend Pulse", "Plan Builder", "Chat", "Growth Rewards"]
)

# (기타 탭들은 이전 코드와 동일하게 유지되어야 하므로, 아래는 생략 없이 그대로)
# ---------------------------------------------------------
# TAB 1: PROFILE
# ---------------------------------------------------------
with tab_profile:
    st.markdown("<div class='mp-section'>Profile</div>", unsafe_allow_html=True)

    with st.form("profile_form", border=False):
        c1, c2, c3 = st.columns([1.2, 1.0, 1.0])

        with c1:
            major = st.text_input("Major", value=st.session_state.profile.get("major", ""), placeholder="예: 경영학과 / 컴퓨터과학과")
            semester = st.selectbox("Semester", options=[f"{y}학년 {s}학기" for y in range(1, 5) for s in (1, 2)], index=0)
            plan = st.selectbox("Plan", ["본전공 유지", "복수전공 희망", "전과 희망"], index=0)

        with c2:
            gpa = st.slider("GPA (4.3)", 0.0, 4.3, float(st.session_state.profile.get("gpa", 3.5)), 0.01)
            major_credit = st.number_input("Major credits", 0, 200, int(st.session_state.profile.get("major_credit", 45)))
            liberal_credit = st.number_input("Liberal credits", 0, 200, int(st.session_state.profile.get("liberal_credit", 30)))

        with c3:
            total_required = st.number_input("Total required", 60, 200, int(st.session_state.profile.get("total_required", 130)))
            major_required = st.number_input("Major target", 0, 200, int(st.session_state.profile.get("major_required", 60)))
            liberal_required = st.number_input("Liberal target", 0, 200, int(st.session_state.profile.get("liberal_required", 30)))

        interest = st.text_area(
            "Interests / Direction",
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
        st.session_state.chat_context["profile"] = st.session_state.profile
        _maybe_drop_reward("profile_done")

        if llm_ready:
            with st.spinner("분석 생성 중…"):
                try:
                    analysis = llm_profile_analysis(st.session_state.profile, openai_key, model)
                    st.session_state.profile_analysis = analysis
                    st.session_state.chat_context["analysis"] = analysis

                    df = pd.DataFrame(analysis.get("action_plan", []))
                    if not df.empty:
                        df = df.rename(columns={"weeks": "주(week)", "priority": "우선순위", "action": "액션", "deliverable": "산출물", "why": "이유"})
                    st.session_state.action_plan_df = df
                    st.session_state.recommended_keywords = (analysis.get("keyword_suggestions", []) or [])[:10]

                    st.session_state.todos_seeded = False
                except Exception as e:
                    st.error(f"LLM 분석 오류: {e}")
                    st.session_state.profile_analysis = None
        else:
            st.info("OpenAI Key를 넣으면 맞춤 분석이 생성됩니다.")

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
            st.markdown("<div class='mp-card'><div class='mp-section'>Dashboard</div><div class='mp-muted'>학점 진행 상황</div></div>", unsafe_allow_html=True)
            chart_df = pd.DataFrame(
                {"Category": ["Total", "Major", "Liberal"],
                 "Completed": [total_done, p["major_credit"], p["liberal_credit"]],
                 "Remaining": [total_remaining, major_remaining, lib_remaining]}
            ).set_index("Category")
            st.bar_chart(chart_df)

        with c2:
            st.markdown("<div class='mp-card'><div class='mp-section'>Keyword Seeds</div><div class='mp-muted'>Digest/Trend에 바로 사용</div></div>", unsafe_allow_html=True)
            kws = st.session_state.recommended_keywords or []
            st.write(" • ".join(kws) if kws else "-")

        st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)

        left, right = st.columns([1.2, 0.8])
        with left:
            st.markdown("<div class='mp-card-solid'><div class='mp-section'>Summary</div></div>", unsafe_allow_html=True)
            if st.session_state.profile_analysis:
                a = st.session_state.profile_analysis
                st.write(a.get("summary_ko", ""))
                st.markdown("**Strengths**")
                st.write("\n".join([f"- {x}" for x in a.get("strengths", [])]) or "-")
                st.markdown("**Risks**")
                st.write("\n".join([f"- {x}" for x in a.get("risks", [])]) or "-")
                st.markdown("**Next Focus**")
                st.write("\n".join([f"- {x}" for x in a.get("next_focus", [])]) or "-")

        with right:
            st.markdown("<div class='mp-card-solid'><div class='mp-section'>Action Plan</div><div class='mp-muted'>산출물 중심</div></div>", unsafe_allow_html=True)
            df = st.session_state.action_plan_df
            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                st.info("Generate 후 Action Plan이 생성됩니다.")
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button(
                    "Download CSV",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name="majorpass_action_plan.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

# ---------------------------------------------------------
# TAB 2: EVIDENCE DIGEST
# ---------------------------------------------------------
with tab_digest:
    st.markdown("<div class='mp-section'>Evidence Digest</div>", unsafe_allow_html=True)

    if not (naver_id.strip() and naver_secret.strip()):
        st.warning("NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 이 필요합니다.")
    else:
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

        if st.button("Search", use_container_width=True):
            with st.spinner("검색 중…"):
                try:
                    df = naver_search(query=query, client_id=naver_id, client_secret=naver_secret, category=category, display=display, sort=sort)
                    st.session_state.search_df = df
                except Exception as e:
                    st.error(f"Naver Search 오류: {e}")

        df = st.session_state.search_df
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            st.info("검색 후, 요약할 문서를 Select로 체크하고 Digest를 실행하세요.")
        else:
            st.markdown("<div class='mp-card-solid'><div class='mp-section'>Select sources</div><div class='mp-muted'>최대 3~6개 추천</div></div>", unsafe_allow_html=True)

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
            else:
                if st.button("Digest selected", use_container_width=True):
                    if not llm_ready:
                        st.warning("OpenAI Key가 필요합니다.")
                    else:
                        with st.spinner("본문 추출 + 요약 생성 중…"):
                            sources = []
                            for _, row in selected.iterrows():
                                url = row.get("Link", "")
                                text = fetch_and_extract_text(url)
                                sources.append(
                                    {
                                        "Title": row.get("Title", ""),
                                        "Link": url,
                                        "Published": row.get("Published", ""),
                                        "Type": row.get("Type", ""),
                                        "Snippet": row.get("Snippet", ""),
                                        "ExtractedText": text or row.get("Snippet", ""),
                                    }
                                )

                            try:
                                digest = llm_digest(sources, openai_key=openai_key, model=model)
                                st.session_state.digest_result = digest
                                st.session_state.chat_context["digest"] = digest
                                _maybe_drop_reward("digest_done")
                            except Exception as e:
                                st.error(f"Digest 생성 오류: {e}")
                                st.session_state.digest_result = None

            digest = st.session_state.digest_result
            if digest:
                overall = digest.get("overall", {})
                st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)
                st.markdown("<div class='mp-card'><div class='mp-section'>Overall</div></div>", unsafe_allow_html=True)
                st.markdown("**Themes**")
                st.write("\n".join([f"- {t}" for t in overall.get("themes", [])]) or "-")
                st.markdown("**Recommended Queries**")
                st.write(" • ".join(overall.get("recommended_queries", [])) or "-")
                st.markdown("**What to do next**")
                st.write("\n".join([f"- {x}" for x in overall.get("what_to_do_next", [])]) or "-")

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
                        st.markdown("**사용자에게 의미**")
                        st.write("\n".join([f"- {x}" for x in d.get("yonsei_takeaways", [])]) or "-")
                    with c2:
                        st.markdown("**다음 행동(액션)**")
                        st.write("\n".join([f"- {x}" for x in d.get("next_actions", [])]) or "-")
                        if url:
                            st.link_button("원문 보기", url, use_container_width=True)

                    if show_extracted_text and url:
                        with st.expander("Extracted text (debug)", expanded=False):
                            st.write(clamp_text(fetch_and_extract_text(url), 5000))

# ---------------------------------------------------------
# TAB 3: TREND PULSE
# ---------------------------------------------------------
with tab_trend:
    st.markdown("<div class='mp-section'>Trend Pulse</div>", unsafe_allow_html=True)

    if not (naver_id.strip() and naver_secret.strip()):
        st.warning("NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 이 필요합니다.")
    else:
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

        if st.button("Generate", use_container_width=True):
            groups = []
            for kw in keys:
                kw = (kw or "").strip()
                if kw:
                    groups.append({"groupName": kw, "keywords": [kw]})
            if not groups:
                st.warning("키워드를 1개 이상 입력해주세요.")
            else:
                with st.spinner("Datalab 호출 중…"):
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
                        _maybe_drop_reward("trend_done")
                    except Exception as e:
                        st.error(f"Trend 오류: {e}")
                        st.session_state.trend_df = None

        df = st.session_state.trend_df
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            st.info("Generate를 눌러 그래프를 생성하세요.")
        else:
            st.markdown("<div class='mp-card-solid'><div class='mp-section'>Chart</div><div class='mp-muted'>상대적 신호</div></div>", unsafe_allow_html=True)
            st.line_chart(df)

            if llm_enabled(openai_key) and st.button("Interpret", use_container_width=True):
                with st.spinner("해석 생성 중…"):
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

# ---------------------------------------------------------
# TAB 4: PLAN BUILDER
# ---------------------------------------------------------
with tab_plan:
    st.markdown("<div class='mp-section'>Plan Builder</div>", unsafe_allow_html=True)

    if not st.session_state.profile:
        st.warning("먼저 Profile에서 Generate를 해주세요.")
    elif not llm_enabled(openai_key):
        st.warning("OpenAI Key가 필요합니다.")
    else:
        context = {
            "profile": st.session_state.profile,
            "analysis": st.session_state.profile_analysis,
            "digest": st.session_state.digest_result,
            "trend_summary": st.session_state.trend_summary,
        }

        st.markdown("<div class='mp-card-solid'><div class='mp-section'>Inputs</div><div class='mp-muted'>현재 세션 데이터로 계획 생성</div></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Profile", "✅" if st.session_state.profile else "⚪")
        c2.metric("Digest", "✅" if st.session_state.digest_result else "⚪")
        c3.metric("Trend", "✅" if st.session_state.trend_df is not None else "⚪")

        if st.button("Build Plan", use_container_width=True):
            with st.spinner("로드맵 생성 중…"):
                try:
                    plan = llm_plan_builder(context, openai_key, model)
                    st.session_state.plan_result = plan
                    st.session_state.chat_context["plan"] = plan
                    _maybe_drop_reward("plan_done")
                    st.session_state.todos_seeded = False
                except Exception as e:
                    st.error(f"Plan 생성 오류: {e}")

        plan = st.session_state.plan_result
        if not plan:
            st.info("Build Plan을 눌러 계획을 생성하세요.")
        else:
            st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)
            st.markdown("<div class='mp-card'><div class='mp-section'>Goal</div></div>", unsafe_allow_html=True)
            st.write(plan.get("goal", ""))

            st.markdown("**North Star Deliverables**")
            st.write("\n".join([f"- {x}" for x in plan.get("north_star_deliverables", [])]) or "-")

            weekly = plan.get("weekly_plan", [])
            if weekly:
                df = pd.DataFrame(weekly)
                st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)
                st.markdown("<div class='mp-card-solid'><div class='mp-section'>Weekly Plan</div><div class='mp-muted'>주차별 초점/산출물</div></div>", unsafe_allow_html=True)
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button(
                    "Download Weekly Plan CSV",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name="majorpass_weekly_plan.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            st.markdown("**Risk controls**")
            st.write("\n".join([f"- {x}" for x in plan.get("risk_controls", [])]) or "-")
            st.markdown("**Checklist**")
            st.write("\n".join([f"- {x}" for x in plan.get("checklist", [])]) or "-")

# ---------------------------------------------------------
# TAB 5: CHAT
# ---------------------------------------------------------
with tab_chat:
    st.markdown("<div class='mp-section'>Chat</div>", unsafe_allow_html=True)

    SECRET_PHRASE = "path to pass"

    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    quick1, quick2, quick3, quick4 = st.columns(4)
    if quick1.button("🧩 Build a 4-week plan", use_container_width=True):
        st.session_state.chat_history.append({"role": "user", "content": "Build a 4-week plan from my current situation. Make it deliverable-driven."})
    if quick2.button("📌 Prioritize next semester", use_container_width=True):
        st.session_state.chat_history.append({"role": "user", "content": "What should I prioritize next semester? Give 5 priorities and what evidence supports them."})
    if quick3.button("🔎 Turn evidence into actions", use_container_width=True):
        st.session_state.chat_history.append({"role": "user", "content": "Turn my evidence summary into 6 concrete actions and deliverables."})
    if quick4.button("🧠 Portfolio structure", use_container_width=True):
        st.session_state.chat_history.append({"role": "user", "content": "Design a portfolio structure that matches my interests. Give sections and example artifacts."})

    user_input = st.chat_input("Ask anything…")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
        last_user = st.session_state.chat_history[-1]["content"]

        if SECRET_PHRASE in last_user.lower():
            _unlock("secret_phrase")
            _maybe_drop_reward("secret_phrase_used")

        user_msgs = [m for m in st.session_state.chat_history if m["role"] == "user"]
        if len(user_msgs) >= 5:
            _unlock("chat_5")

        if llm_enabled(openai_key):
            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    try:
                        answer = llm_chat(
                            openai_key=openai_key,
                            model=model,
                            history=st.session_state.chat_history[:-1],
                            context=st.session_state.chat_context,
                            user_message=last_user,
                        )
                        st.markdown(answer)
                        st.session_state.chat_history.append({"role": "assistant", "content": answer})
                        _maybe_drop_reward("chat_done")
                    except Exception as e:
                        st.error(f"Chat error: {e}")
        else:
            with st.chat_message("assistant"):
                st.info("OpenAI API Key를 입력하면 Chat이 동작합니다.")

# ---------------------------------------------------------
# TAB 6: GROWTH REWARDS (✅ Emoji only change)
# ---------------------------------------------------------
with tab_growth:
    st.markdown("<div class='mp-section'>Growth Rewards</div>", unsafe_allow_html=True)

    seed_todos_if_needed()

    ss = st.session_state
    ss.growth_stage = _current_stage_from_xp(ss.xp)
    stage_idx = ss.growth_stage
    stage = GROWTH_STAGES[stage_idx]

    if stage_idx < len(GROWTH_STAGES) - 1:
        next_min = GROWTH_STAGES[stage_idx + 1]["min_xp"]
        cur_min = stage["min_xp"]
        denom = max(1, next_min - cur_min)
        prog = (ss.xp - cur_min) / denom
        prog = max(0.0, min(1.0, float(prog)))
        next_label = f"Next: {GROWTH_STAGES[stage_idx+1]['name']} ({next_min} XP)"
    else:
        prog = 1.0
        next_label = "Max stage reached"

    top_left, top_right = st.columns([1.2, 0.8])
    with top_left:
        st.markdown("<div class='mp-card-solid'>", unsafe_allow_html=True)
        st.markdown("<div class='mp-section'>My Little Pass</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='mp-muted'>Stage: <b>{stage['name']}</b> · XP: <b>{ss.xp}</b></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-top:10px; color:rgba(11,18,32,0.72);'>{stage['desc']}</div>", unsafe_allow_html=True)
        st.progress(prog, text=next_label)
        st.markdown("</div>", unsafe_allow_html=True)

    with top_right:
        # ✅ Only change: show emoji instead of SVG
        st.markdown("<div class='mp-card-solid' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:84px; line-height:1.0; margin-top:10px;'>{stage['emoji']}</div>", unsafe_allow_html=True)
        st.markdown("<div class='mp-muted' style='margin-top:8px;'>Character</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)

    st.markdown("<div class='mp-card'><div class='mp-section'>Roadmap To-Do</div><div class='mp-muted'>완료할 때마다 XP가 올라가요</div></div>", unsafe_allow_html=True)

    before = {t["id"]: bool(t["done"]) for t in ss.roadmap_todos}
    df = pd.DataFrame(ss.roadmap_todos)

    edited = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "done": st.column_config.CheckboxColumn("Done"),
            "task": st.column_config.TextColumn("Task", width="large"),
            "points": st.column_config.NumberColumn("XP", width="small"),
            "source": st.column_config.TextColumn("Source", width="small"),
        },
        disabled=["id", "task", "points", "source"],
    )

    after = {int(r["id"]): bool(r["done"]) for _, r in edited.iterrows()}
    newly_done = [tid for tid in after if after[tid] and not before.get(tid, False)]
    ss.roadmap_todos = edited.to_dict(orient="records")

    for tid in newly_done:
        row = edited[edited["id"] == tid].iloc[0]
        award_xp(int(row["points"]), reason=f"todo_completed:{tid}")
        st.toast(f"+{int(row['points'])} XP (To-Do 완료)", icon="🪙")

    st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='mp-section'>Add your own task</div>", unsafe_allow_html=True)

    a1, a2, a3 = st.columns([1.6, 0.6, 0.6])
    with a1:
        new_task = st.text_input("New task", placeholder="예: 이번 주 안에 포트폴리오 초안 1개 완성")
    with a2:
        new_points = st.selectbox("XP", [6, 8, 10, 12, 14], index=2)
    with a3:
        add = st.button("Add", use_container_width=True)

    if add and new_task.strip():
        next_id = int(max([t["id"] for t in ss.roadmap_todos], default=0) + 1)
        ss.roadmap_todos.append({"id": next_id, "task": new_task.strip(), "done": False, "points": int(new_points), "source": "My plan"})
        _maybe_drop_reward("todo_added")
        st.success("To-Do가 추가됐어요!")

    all_done = all(bool(t["done"]) for t in ss.roadmap_todos) if ss.roadmap_todos else False
    if all_done:
        st.success("🎉 로드맵 To-Do를 전부 완료했어요! (완성)")
        if not any(x.get("reason") == "roadmap_complete_bonus" for x in ss.growth_log):
            award_xp(25, "roadmap_complete_bonus")
            st.balloons()

    st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='mp-card-solid'><div class='mp-section'>Reward Log</div><div class='mp-muted'>최근 기록</div></div>", unsafe_allow_html=True)
    if ss.growth_log:
        log_df = pd.DataFrame(ss.growth_log[-20:])[["ts", "reason", "points"]].iloc[::-1]
        st.dataframe(log_df, use_container_width=True, hide_index=True)
    else:
        st.info("아직 기록이 없어요. To-Do를 체크해보세요.")
