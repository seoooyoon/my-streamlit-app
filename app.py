import json
import os
import random
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st

# Optional: OpenAI integration (recommended)
OPENAI_AVAILABLE = True
try:
    from openai import OpenAI
except Exception:
    OPENAI_AVAILABLE = False


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MajorPass",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

KST = ZoneInfo("Asia/Seoul")


# =========================================================
# DESIGN (CLEAN + MODERN)
# =========================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

:root{
  --bg1: #F7F8FC;
  --bg2: #EEF2FF;
  --text: #0B1220;
  --muted: #5B6475;
  --card: rgba(255,255,255,0.72);
  --card2: rgba(255,255,255,0.92);
  --border: rgba(15,23,42,0.10);
  --shadow: 0 10px 30px rgba(15,23,42,0.12);
  --accent: #4F46E5;
  --accent2: #22C55E;
  --warn: #F59E0B;
  --danger: #EF4444;
  --radius: 18px;
}

html, body, [data-testid="stApp"]{
  background: radial-gradient(1200px 700px at 15% 10%, var(--bg2), transparent 60%),
              radial-gradient(1000px 600px at 85% 5%, #E0F2FE, transparent 60%),
              linear-gradient(180deg, var(--bg1), #FFFFFF 60%);
  color: var(--text);
  font-family: Inter, Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

/* Layout breathing room */
.block-container{
  padding-top: 1.2rem;
  padding-bottom: 3rem;
  max-width: 1200px;
}

/* Sidebar styling */
section[data-testid="stSidebar"]{
  background: rgba(255,255,255,0.65) !important;
  border-right: 1px solid var(--border);
}

/* Remove Streamlit footer */
footer {visibility: hidden;}
header {visibility: hidden;}

/* Hero */
.mp-hero{
  background: linear-gradient(120deg, rgba(79,70,229,0.10), rgba(34,197,94,0.10));
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 22px 22px;
  margin: 8px 0 18px 0;
}
.mp-hero-top{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 12px;
}
.mp-title{
  font-size: 2.0rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0;
}
.mp-sub{
  color: var(--muted);
  margin-top: 6px;
  line-height: 1.5;
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
  background: rgba(255,255,255,0.75);
  font-size: 0.85rem;
  color: var(--muted);
}

/* Card */
.mp-card{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 18px 18px;
}
.mp-card-solid{
  background: var(--card2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 18px 18px;
}
.mp-card h3{
  margin: 0 0 8px 0;
}
.mp-muted{ color: var(--muted); }

/* Section title */
.mp-section{
  font-size: 1.1rem;
  font-weight: 800;
  margin: 12px 0 10px 0;
  letter-spacing: -0.01em;
}

/* Tiny divider */
.mp-divider{
  height: 1px;
  background: var(--border);
  margin: 14px 0;
}

/* Reward chips */
.mp-reward{
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding: 12px 12px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.65);
}
.mp-reward .name{
  font-weight: 800;
}
.mp-reward .meta{
  color: var(--muted);
  font-size: 0.85rem;
}

/* Dataframe border rounding */
[data-testid="stDataFrame"]{
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow: hidden;
}

/* Buttons */
.stButton button{
  border-radius: 12px !important;
  padding: 10px 14px !important;
  font-weight: 700 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# HELPERS
# =========================================================
def _clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", text).strip()


def _safe_secret(key: str) -> Optional[str]:
    try:
        return st.secrets.get(key)  # type: ignore[attr-defined]
    except Exception:
        return None


def _now_kst() -> datetime:
    return datetime.now(KST)


# -----------------------------
# Rewards (random + secret)
# -----------------------------
RARITY_POOL = [
    ("Common", 0.72, "🟦"),
    ("Rare", 0.22, "🟪"),
    ("Epic", 0.055, "🟨"),
    ("Secret", 0.005, "🟥"),
]

COLLECTIBLES = [
    ("Insight Gem", "💎"),
    ("Roadmap Sticker", "🗺️"),
    ("Focus Token", "🎯"),
    ("Courage Badge", "🛡️"),
    ("Curiosity Spark", "✨"),
    ("Portfolio Seed", "🌱"),
    ("Momentum Booster", "🚀"),
]

ACHIEVEMENTS = {
    "first_analysis": {"title": "First Pass", "hint": "Run your first analysis."},
    "first_search": {"title": "Evidence Hunter", "hint": "Run your first Naver search."},
    "first_trend": {"title": "Trend Explorer", "hint": "Generate your first trend chart."},
    "chat_5": {"title": "Conversation Warm-up", "hint": "Send 5 chat messages."},
    "triple_action": {"title": "Momentum", "hint": "Do analysis + search + trend in one session."},
    "night_owl": {"title": "Night Owl", "hint": "Use the app late at night."},
    "secret_phrase": {"title": "Hidden Door", "hint": "Say the secret phrase."},
}


def _init_state() -> None:
    st.session_state.setdefault("profile", {})
    st.session_state.setdefault("analysis_json", None)
    st.session_state.setdefault("action_plan_df", None)
    st.session_state.setdefault("recommended_keywords", [])
    st.session_state.setdefault("search_df", None)
    st.session_state.setdefault("trend_df", None)
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("chat_context", {"profile": None, "analysis": None, "evidence": None, "trends": None})
    st.session_state.setdefault("rewards", [])
    st.session_state.setdefault("achievements", {k: False for k in ACHIEVEMENTS.keys()})
    st.session_state.setdefault("events_done", set())


def _unlock(achievement_key: str) -> None:
    if achievement_key in st.session_state.achievements and not st.session_state.achievements[achievement_key]:
        st.session_state.achievements[achievement_key] = True
        st.toast(f"Achievement unlocked: {ACHIEVEMENTS[achievement_key]['title']} 🎉", icon="🏆")


def _maybe_drop_reward(event: str) -> None:
    # Avoid spamming: each event only once per run
    if event in st.session_state.events_done:
        return
    st.session_state.events_done.add(event)

    # Small chance to drop collectible per meaningful action
    if random.random() > 0.45:
        return

    # Choose rarity
    r = random.random()
    cum = 0.0
    rarity, icon = "Common", "🟦"
    for name, prob, ico in RARITY_POOL:
        cum += prob
        if r <= cum:
            rarity, icon = name, ico
            break

    collectible_name, collectible_emoji = random.choice(COLLECTIBLES)
    reward = {
        "name": collectible_name,
        "emoji": collectible_emoji,
        "rarity": rarity,
        "rarity_icon": icon,
        "ts": _now_kst().strftime("%Y-%m-%d %H:%M"),
        "event": event,
    }
    st.session_state.rewards.append(reward)

    if rarity == "Secret":
        st.toast("A *Secret* collectible dropped… 👀", icon="🟥")
        st.balloons()
    else:
        st.toast(f"Collectible dropped: {collectible_emoji} {collectible_name} ({rarity})", icon=icon)


def _check_combo_achievement() -> None:
    # triple_action: analysis + search + trend all done in session
    done = st.session_state.events_done
    if {"analysis_done", "search_done", "trend_done"}.issubset(done):
        _unlock("triple_action")


# =========================================================
# NAVER API (Search + Datalab)
# =========================================================
def _naver_headers(client_id: str, client_secret: str) -> Dict[str, str]:
    return {
        "X-Naver-Client-Id": client_id.strip(),
        "X-Naver-Client-Secret": client_secret.strip(),
    }


@st.cache_data(ttl=60 * 30)
def naver_search(
    query: str,
    client_id: str,
    client_secret: str,
    category: str = "news",
    display: int = 10,
    start: int = 1,
    sort: str = "sim",
) -> pd.DataFrame:
    """
    Naver Search API:
    - News: https://openapi.naver.com/v1/search/news.json
    - Blog: https://openapi.naver.com/v1/search/blog.json
    - Web documents: https://openapi.naver.com/v1/search/webkr.json
    """
    if not query.strip():
        return pd.DataFrame()

    url = f"https://openapi.naver.com/v1/search/{category}.json"
    params = {"query": query, "display": int(display), "start": int(start), "sort": sort}
    res = requests.get(url, headers=_naver_headers(client_id, client_secret), params=params, timeout=15)
    res.raise_for_status()
    data = res.json()

    items = data.get("items", [])
    rows = []
    for it in items:
        title = _clean_html(it.get("title", ""))
        desc = _clean_html(it.get("description", ""))
        link = it.get("originallink") or it.get("link") or ""
        pub = it.get("pubDate") or ""
        rows.append(
            {
                "Title": title,
                "Published": pub,
                "Link": link,
                "Snippet": desc,
                "Type": category,
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(ttl=60 * 60)
def naver_datalab_trend(
    client_id: str,
    client_secret: str,
    start_date: str,
    end_date: str,
    time_unit: str,
    keyword_groups: List[Dict[str, Any]],
    device: Optional[str] = None,
    gender: Optional[str] = None,
    ages: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Naver Datalab (Search Trend):
    POST https://openapi.naver.com/v1/datalab/search
    """
    url = "https://openapi.naver.com/v1/datalab/search"
    body: Dict[str, Any] = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups,
    }
    if device:
        body["device"] = device
    if gender:
        body["gender"] = gender
    if ages:
        body["ages"] = ages

    res = requests.post(
        url,
        headers={**_naver_headers(client_id, client_secret), "Content-Type": "application/json"},
        data=json.dumps(body),
        timeout=20,
    )
    res.raise_for_status()
    data = res.json()

    # Normalize results to a single dataframe: index=period, columns=groupName
    results = data.get("results", [])
    if not results:
        return pd.DataFrame()

    all_periods = set()
    series_map: Dict[str, Dict[str, float]] = {}
    for group in results:
        name = group.get("title") or group.get("keyword") or "Group"
        points = group.get("data", [])
        series_map[name] = {}
        for p in points:
            period = p.get("period")
            ratio = p.get("ratio")
            if period is None or ratio is None:
                continue
            all_periods.add(period)
            series_map[name][period] = float(ratio)

    periods = sorted(all_periods)
    df = pd.DataFrame(index=periods)
    for name, m in series_map.items():
        df[name] = [m.get(p, None) for p in periods]
    df.index.name = "Period"
    return df


# =========================================================
# OPENAI (Analysis + Chat)
# =========================================================
def _openai_client(api_key: str) -> "OpenAI":
    # OpenAI python library supports api_key=... or env var OPENAI_API_KEY
    return OpenAI(api_key=api_key)


def _llm_enabled(openai_key: str) -> bool:
    return OPENAI_AVAILABLE and bool(openai_key.strip())


def llm_generate_analysis_json(profile: Dict[str, Any], openai_key: str, model: str) -> Dict[str, Any]:
    """
    Returns a JSON object with:
      - narrative (string)
      - strengths (list)
      - risks (list)
      - next_semester_focus (list)
      - action_plan (list of objects)
      - keyword_suggestions (list)
    """
    client = _openai_client(openai_key)

    developer_msg = (
        "You are MajorPass, a career-oriented academic advisor. "
        "Write concise, practical guidance. "
        "All output MUST be in English. "
        "Be realistic, not overly generic. "
        "Return ONLY valid JSON (no markdown)."
    )

    user_msg = {
        "profile": profile,
        "task": (
            "Generate a structured career/semester strategy for the student. "
            "Make it actionable and evidence-driven. "
            "The action_plan should contain 6-10 items with fields: "
            "priority (High/Medium/Low), action, deliverable, timeframe_weeks (int), and why_it_matters."
        ),
        "output_schema": {
            "narrative": "string",
            "strengths": ["string"],
            "risks": ["string"],
            "next_semester_focus": ["string"],
            "action_plan": [
                {
                    "priority": "High|Medium|Low",
                    "action": "string",
                    "deliverable": "string",
                    "timeframe_weeks": 1,
                    "why_it_matters": "string",
                }
            ],
            "keyword_suggestions": ["string"],
        },
    }

    resp = client.responses.create(
        model=model,
        input=[
            {"role": "developer", "content": developer_msg},
            {"role": "user", "content": json.dumps(user_msg, ensure_ascii=False)},
        ],
        text={"format": {"type": "json_object", "verbosity": "low"}},
        temperature=0.4,
    )

    raw = resp.output_text
    parsed = json.loads(raw)
    return parsed


def llm_chat(
    openai_key: str,
    model: str,
    history: List[Dict[str, str]],
    context: Dict[str, Any],
    user_message: str,
) -> str:
    client = _openai_client(openai_key)

    developer_msg = (
        "You are MajorPass, a helpful and structured assistant. "
        "All responses must be in English. "
        "Prefer bullet points, short sections, and concrete next steps. "
        "If evidence/trends exist, cite them as 'From your evidence:' without external URLs. "
        "Do not mention policies. Be friendly and concise."
    )

    # Light context pack (keep short)
    context_pack = {
        "profile": context.get("profile"),
        "analysis": context.get("analysis"),
        "evidence_summary": context.get("evidence"),
        "trends_summary": context.get("trends"),
    }

    messages: List[Dict[str, str]] = [{"role": "developer", "content": developer_msg}]
    messages.append({"role": "user", "content": f"Context JSON:\n{json.dumps(context_pack, ensure_ascii=False)}"})

    # Add short history (last ~10 turns)
    for m in history[-10:]:
        messages.append({"role": m["role"], "content": m["content"]})

    messages.append({"role": "user", "content": user_message})

    resp = client.responses.create(
        model=model,
        input=messages,
        temperature=0.6,
    )
    return resp.output_text


# =========================================================
# APP UI
# =========================================================
_init_state()

# -----------------------------
# SIDEBAR (Keys + Settings)
# -----------------------------
with st.sidebar:
    st.markdown("## 🔐 Keys & Settings")
    st.caption("Tip: Use `.streamlit/secrets.toml` in deployment (recommended).")

    # OpenAI
    openai_key_default = _safe_secret("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    openai_key = st.text_input("OpenAI API Key", value=openai_key_default, type="password")

    # Naver
    naver_id_default = _safe_secret("NAVER_CLIENT_ID") or os.getenv("NAVER_CLIENT_ID", "")
    naver_secret_default = _safe_secret("NAVER_CLIENT_SECRET") or os.getenv("NAVER_CLIENT_SECRET", "")

    st.markdown("### 🇰🇷 Naver APIs")
    naver_client_id = st.text_input("Naver Client ID", value=naver_id_default, type="password")
    naver_client_secret = st.text_input("Naver Client Secret", value=naver_secret_default, type="password")

    st.markdown("### 🤖 Model")
    model = st.selectbox(
        "OpenAI model",
        options=["gpt-5.2", "gpt-4.1", "gpt-4o"],
        index=0,
        help="If you don't have access to a model, choose another.",
    )

    st.markdown("---")
    st.markdown("### Privacy")
    st.caption(
        "MajorPass does **not** store your inputs in a database.\n\n"
        "When you click **Analyze / Search / Trends / Chat**, your data is sent only to the APIs you enabled (OpenAI / Naver)."
    )

    st.markdown("---")
    st.page_link("https://developers.naver.com/", label="Open Naver Developers ↗", icon="🔗")
    st.page_link("https://developers.openai.com/api/docs", label="Open OpenAI Docs ↗", icon="🔗")


# -----------------------------
# HERO
# -----------------------------
llm_ready = _llm_enabled(openai_key)
naver_ready = bool(naver_client_id.strip() and naver_client_secret.strip())
now = _now_kst()

st.markdown(
    f"""
<div class="mp-hero">
  <div class="mp-hero-top">
    <div>
      <div class="mp-title">MajorPass</div>
      <div class="mp-sub">Turn your major into a career asset — <b>Path to PASS</b>.</div>
    </div>
    <div class="mp-badges">
      <span class="mp-pill">🕒 KST {now.strftime("%Y-%m-%d %H:%M")}</span>
      <span class="mp-pill">{'✅ LLM Ready' if llm_ready else '⚪ LLM Off'}</span>
      <span class="mp-pill">{'✅ Naver Ready' if naver_ready else '⚪ Naver Off'}</span>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

if now.hour >= 23 or now.hour <= 4:
    _unlock("night_owl")


# -----------------------------
# TABS
# -----------------------------
tab_profile, tab_evidence, tab_trends, tab_chat, tab_rewards = st.tabs(
    ["🎓 Profile", "🧾 Evidence (Naver Search)", "📈 Trends (Datalab)", "💬 Chat", "🎁 Rewards"]
)

# =========================================================
# TAB 1: PROFILE
# =========================================================
with tab_profile:
    st.markdown("<div class='mp-section'>Your profile</div>", unsafe_allow_html=True)

    with st.form("profile_form", border=False):
        c1, c2, c3 = st.columns([1.2, 1.1, 1.1])

        with c1:
            major = st.text_input("Current major (full name)", value=st.session_state.profile.get("major", ""))
            semester = st.selectbox(
                "Current year / semester",
                options=[f"Year {y} · Semester {s}" for y in range(1, 5) for s in (1, 2)],
                index=0,
            )
            plan = st.selectbox(
                "Major plan",
                options=["Keep current major", "Double major", "Transfer to another major"],
                index=0,
            )

        with c2:
            gpa = st.slider("Overall GPA (out of 4.3)", 0.0, 4.3, float(st.session_state.profile.get("gpa", 3.5)), 0.01)
            major_credit = st.number_input("Major credits completed", 0, 200, int(st.session_state.profile.get("major_credit", 45)))
            liberal_credit = st.number_input("Liberal arts credits completed", 0, 200, int(st.session_state.profile.get("liberal_credit", 30)))

        with c3:
            total_required = st.number_input("Total credits required (editable)", 60, 200, int(st.session_state.profile.get("total_required", 130)))
            major_required = st.number_input("Major credits target (editable)", 0, 200, int(st.session_state.profile.get("major_required", 60)))
            liberal_required = st.number_input("Liberal arts target (editable)", 0, 200, int(st.session_state.profile.get("liberal_required", 30)))

        interest = st.text_area(
            "Interests / career direction (free text)",
            value=st.session_state.profile.get("interest", ""),
            placeholder="Example: product management, UX, branding, data analysis, content creation…",
            height=100,
        )

        submitted = st.form_submit_button("✨ Generate strategy", use_container_width=True)

    # Save profile to state
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

        # Basic achievements + rewards
        _unlock("first_analysis")
        _maybe_drop_reward("analysis_done")
        _check_combo_achievement()

        # Optional LLM analysis
        if llm_ready:
            with st.spinner("Generating an evidence-driven strategy…"):
                try:
                    analysis_json = llm_generate_analysis_json(st.session_state.profile, openai_key, model=model)
                    st.session_state.analysis_json = analysis_json

                    # Build action plan DF
                    ap = analysis_json.get("action_plan", [])
                    df = pd.DataFrame(ap)
                    if not df.empty:
                        # Normalize columns
                        df = df.rename(
                            columns={
                                "timeframe_weeks": "Weeks",
                                "why_it_matters": "Why",
                                "deliverable": "Deliverable",
                                "priority": "Priority",
                                "action": "Action",
                            }
                        )
                    st.session_state.action_plan_df = df

                    # Keywords
                    kws = analysis_json.get("keyword_suggestions", []) or []
                    st.session_state.recommended_keywords = kws[:10]

                    # Put into chat context
                    st.session_state.chat_context["profile"] = st.session_state.profile
                    st.session_state.chat_context["analysis"] = analysis_json

                except Exception as e:
                    st.error(f"LLM error: {e}")
                    st.session_state.analysis_json = None
        else:
            st.session_state.analysis_json = None

    # -----------------------------
    # Dashboard view (metrics + charts + plan)
    # -----------------------------
    if st.session_state.profile:
        prof = st.session_state.profile
        total_done = prof["major_credit"] + prof["liberal_credit"]
        total_remaining = max(0, prof["total_required"] - total_done)
        major_remaining = max(0, prof["major_required"] - prof["major_credit"])
        liberal_remaining = max(0, prof["liberal_required"] - prof["liberal_credit"])

        # KPIs
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("GPA", f"{prof['gpa']:.2f} / 4.30")
        k2.metric("Credits done", f"{total_done}", f"-{total_remaining} remaining")
        k3.metric("Major credits", f"{prof['major_credit']}", f"-{major_remaining} to target")
        k4.metric("Liberal credits", f"{prof['liberal_credit']}", f"-{liberal_remaining} to target")

        st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)

        # Charts
        c1, c2 = st.columns([1.1, 0.9])
        with c1:
            st.markdown("<div class='mp-card'><h3>📊 Credit progress</h3><div class='mp-muted'>A quick visual of completion vs remaining.</div></div>", unsafe_allow_html=True)
            chart_df = pd.DataFrame(
                {
                    "Category": ["Total", "Major (target)", "Liberal (target)"],
                    "Completed": [total_done, prof["major_credit"], prof["liberal_credit"]],
                    "Remaining": [total_remaining, major_remaining, liberal_remaining],
                }
            ).set_index("Category")
            st.bar_chart(chart_df)

        with c2:
            st.markdown("<div class='mp-card'><h3>🧠 Skill signal (quick heuristic)</h3><div class='mp-muted'>Based on keywords in your interests.</div></div>", unsafe_allow_html=True)

            interest_text = (prof.get("interest") or "").lower()
            skill_map = {
                "Strategy": ["strategy", "planning", "pm", "product", "growth", "biz", "business", "기획"],
                "Design/UX": ["ux", "ui", "design", "prototype", "figma", "브랜딩", "디자인"],
                "Data": ["data", "analytics", "sql", "python", "statistics", "분석", "데이터"],
                "Writing": ["writing", "content", "copy", "blog", "콘텐츠", "글쓰기"],
                "Communication": ["presentation", "team", "collaboration", "커뮤니케이션", "협업"],
            }
            scores = {}
            for skill, keys in skill_map.items():
                score = 1
                for kw in keys:
                    if kw in interest_text:
                        score += 1
                scores[skill] = min(score, 5)

            skill_df = pd.DataFrame({"Score (1-5)": scores}).T
            st.bar_chart(skill_df)

        st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)

        # Strategy + Action plan (table)
        left, right = st.columns([1.2, 0.8])

        with left:
            st.markdown("<div class='mp-card-solid'><h3>🧭 Strategy summary</h3></div>", unsafe_allow_html=True)

            if st.session_state.analysis_json:
                narrative = st.session_state.analysis_json.get("narrative", "")
                strengths = st.session_state.analysis_json.get("strengths", [])
                risks = st.session_state.analysis_json.get("risks", [])
                focus = st.session_state.analysis_json.get("next_semester_focus", [])

                st.write(narrative)
                st.markdown("**Strengths**")
                st.write("\n".join([f"- {s}" for s in strengths]) if strengths else "- (Not provided)")
                st.markdown("**Risks / gaps**")
                st.write("\n".join([f"- {r}" for r in risks]) if risks else "- (Not provided)")
                st.markdown("**Next semester focus**")
                st.write("\n".join([f"- {f}" for f in focus]) if focus else "- (Not provided)")
            else:
                st.info(
                    "Add an OpenAI API key in the sidebar to generate a personalized strategy.\n\n"
                    "For now, here’s a simple default approach:\n"
                    "- Choose 1–2 portfolio-ready deliverables\n"
                    "- Align courses to outcomes (report, prototype, case study)\n"
                    "- Validate interest via evidence (search + trends)\n"
                )

        with right:
            st.markdown("<div class='mp-card-solid'><h3>✅ Action plan</h3><div class='mp-muted'>Exportable, portfolio-oriented tasks.</div></div>", unsafe_allow_html=True)

            df = st.session_state.action_plan_df
            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                # fallback plan
                fallback = pd.DataFrame(
                    [
                        {"Priority": "High", "Action": "Pick 1 target role", "Deliverable": "1-page role brief", "Weeks": 1, "Why": "Focus beats optionality."},
                        {"Priority": "High", "Action": "Build 1 portfolio artifact", "Deliverable": "Case study / report", "Weeks": 3, "Why": "Evidence matters."},
                        {"Priority": "Medium", "Action": "Run 2 keyword searches", "Deliverable": "Source table + summary", "Weeks": 1, "Why": "Ground decisions in reality."},
                        {"Priority": "Medium", "Action": "Do a small project", "Deliverable": "Prototype / analysis notebook", "Weeks": 4, "Why": "Skills become visible."},
                        {"Priority": "Low", "Action": "Update resume weekly", "Deliverable": "v1 → v4", "Weeks": 4, "Why": "Iterate fast, reduce anxiety."},
                    ]
                )
                df = fallback

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
            )

            st.download_button(
                "⬇️ Download action plan (CSV)",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="majorpass_action_plan.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # Keyword suggestions
        if st.session_state.recommended_keywords:
            st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)
            st.markdown("<div class='mp-card'><h3>🔎 Suggested keywords</h3><div class='mp-muted'>Use these in Naver Search + Trends tabs.</div></div>", unsafe_allow_html=True)
            st.write(" • ".join(st.session_state.recommended_keywords))


# =========================================================
# TAB 2: EVIDENCE (NAVER SEARCH)
# =========================================================
with tab_evidence:
    st.markdown("<div class='mp-section'>Evidence search</div>", unsafe_allow_html=True)
    st.caption("Get real-world signals (news/blog/web). Turn results into a table, export, and summarize.")

    if not naver_ready:
        st.warning("Add Naver Client ID/Secret in the sidebar to use this tab.")
    else:
        default_query = ""
        if st.session_state.profile:
            default_query = st.session_state.profile.get("interest", "") or st.session_state.profile.get("major", "")
        if st.session_state.recommended_keywords:
            default_query = st.session_state.recommended_keywords[0]

        qcol1, qcol2, qcol3, qcol4 = st.columns([1.4, 0.9, 0.8, 0.9])
        with qcol1:
            query = st.text_input("Search query", value=default_query, placeholder="Try: 'UX internship', 'data analyst', 'brand strategist' …")
        with qcol2:
            category = st.selectbox("Type", ["news", "blog", "webkr"], index=0)
        with qcol3:
            sort = st.selectbox("Sort", ["sim", "date"], index=0)
        with qcol4:
            display = st.slider("Results", 5, 50, 10, 5)

        run = st.button("🧾 Run Naver Search", use_container_width=True)

        if run:
            with st.spinner("Fetching results from Naver…"):
                try:
                    df = naver_search(
                        query=query,
                        client_id=naver_client_id,
                        client_secret=naver_client_secret,
                        category=category,
                        display=display,
                        start=1,
                        sort=sort,
                    )
                    st.session_state.search_df = df
                    _unlock("first_search")
                    _maybe_drop_reward("search_done")
                    _check_combo_achievement()
                except Exception as e:
                    st.error(f"Naver Search error: {e}")

        df = st.session_state.search_df
        if isinstance(df, pd.DataFrame) and not df.empty:
            st.markdown("<div class='mp-card-solid'><h3>Results</h3><div class='mp-muted'>Click links directly in the table.</div></div>", unsafe_allow_html=True)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Link": st.column_config.LinkColumn("Link", display_text="open"),
                },
            )

            st.download_button(
                "⬇️ Download results (CSV)",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="majorpass_naver_search.csv",
                mime="text/csv",
                use_container_width=True,
            )

            # Summarize
            if llm_ready:
                summarize = st.button("🧠 Summarize results in English (LLM)", use_container_width=True)
                if summarize:
                    with st.spinner("Summarizing…"):
                        try:
                            sample = df.head(15).to_dict(orient="records")
                            # Keep summary prompt short
                            prompt = (
                                "Summarize these search results into:\n"
                                "1) 5 key themes\n"
                                "2) 3 actionable insights for career/semester planning\n"
                                "3) 5 follow-up search queries\n\n"
                                f"DATA:\n{json.dumps(sample, ensure_ascii=False)}"
                            )
                            client = _openai_client(openai_key)
                            resp = client.responses.create(
                                model=model,
                                input=[
                                    {"role": "developer", "content": "You summarize evidence clearly. Output in English."},
                                    {"role": "user", "content": prompt},
                                ],
                                temperature=0.4,
                            )
                            summary = resp.output_text
                            st.session_state.chat_context["evidence"] = summary
                            st.success("Summary added to chat context ✅")
                            st.markdown(summary)

                            _maybe_drop_reward("evidence_summary_done")
                        except Exception as e:
                            st.error(f"LLM summary error: {e}")
            else:
                st.info("Add an OpenAI API key to summarize results automatically.")


# =========================================================
# TAB 3: TRENDS (NAVER DATALAB)
# =========================================================
with tab_trends:
    st.markdown("<div class='mp-section'>Trend signals</div>", unsafe_allow_html=True)
    st.caption("Visualize interest over time with Naver Datalab Search Trend.")

    if not naver_ready:
        st.warning("Add Naver Client ID/Secret in the sidebar to use this tab.")
    else:
        # Defaults
        end = date.today()
        start = end - timedelta(days=365)

        colA, colB, colC = st.columns([1.1, 1.0, 1.2])
        with colA:
            start_date = st.date_input("Start date", value=start)
        with colB:
            end_date = st.date_input("End date", value=end)
        with colC:
            time_unit = st.selectbox("Time unit", ["week", "month", "date"], index=0)

        st.markdown("**Keywords (up to 5 groups)**")
        kcols = st.columns(5)
        suggested = st.session_state.recommended_keywords[:5] if st.session_state.recommended_keywords else []
        keys = []
        for i in range(5):
            default_kw = suggested[i] if i < len(suggested) else ""
            with kcols[i]:
                keys.append(st.text_input(f"Keyword {i+1}", value=default_kw, placeholder="e.g. UX"))

        run_trend = st.button("📈 Generate trend chart", use_container_width=True)

        if run_trend:
            groups = []
            for kw in keys:
                kw = (kw or "").strip()
                if not kw:
                    continue
                groups.append({"groupName": kw, "keywords": [kw]})

            if not groups:
                st.warning("Please enter at least one keyword.")
            else:
                with st.spinner("Calling Naver Datalab…"):
                    try:
                        df = naver_datalab_trend(
                            client_id=naver_client_id,
                            client_secret=naver_client_secret,
                            start_date=start_date.strftime("%Y-%m-%d"),
                            end_date=end_date.strftime("%Y-%m-%d"),
                            time_unit=time_unit,
                            keyword_groups=groups,
                        )
                        st.session_state.trend_df = df
                        _unlock("first_trend")
                        _maybe_drop_reward("trend_done")
                        _check_combo_achievement()
                    except Exception as e:
                        st.error(f"Datalab error: {e}")

        df = st.session_state.trend_df
        if isinstance(df, pd.DataFrame) and not df.empty:
            st.markdown("<div class='mp-card-solid'><h3>Trend chart</h3><div class='mp-muted'>Ratios are relative signals, not absolute search volume.</div></div>", unsafe_allow_html=True)
            st.line_chart(df)

            # Optional LLM interpretation
            if llm_ready:
                interpret = st.button("🧠 Interpret the trend (LLM)", use_container_width=True)
                if interpret:
                    with st.spinner("Interpreting trend…"):
                        try:
                            sample = df.tail(30).reset_index().to_dict(orient="records")
                            prompt = (
                                "Interpret the trend data:\n"
                                "- Identify peaks and sustained growth/decline\n"
                                "- Suggest what to do next (courses/projects/search keywords)\n"
                                "- Keep it concise and practical\n\n"
                                f"DATA:\n{json.dumps(sample, ensure_ascii=False)}"
                            )
                            client = _openai_client(openai_key)
                            resp = client.responses.create(
                                model=model,
                                input=[
                                    {"role": "developer", "content": "You are a career analyst. Output in English."},
                                    {"role": "user", "content": prompt},
                                ],
                                temperature=0.4,
                            )
                            trend_summary = resp.output_text
                            st.session_state.chat_context["trends"] = trend_summary
                            st.success("Trend interpretation added to chat context ✅")
                            st.markdown(trend_summary)

                            _maybe_drop_reward("trend_summary_done")
                        except Exception as e:
                            st.error(f"LLM interpretation error: {e}")
            else:
                st.info("Add an OpenAI API key to generate an interpretation automatically.")


# =========================================================
# TAB 4: CHAT
# =========================================================
with tab_chat:
    st.markdown("<div class='mp-section'>Chat</div>", unsafe_allow_html=True)
    st.caption("Ask follow-ups. Your profile, strategy, evidence summary, and trend summary can be used as context.")

    # Secret phrase achievement (hidden)
    SECRET_PHRASE = "path to pass"

    # Render history
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

    user_input = st.chat_input("Ask anything… (English recommended, but any language is okay)")

    # If quick buttons created a user message, process it once
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Process if last message is user and not yet answered
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
        last_user = st.session_state.chat_history[-1]["content"]

        # Secret phrase check (do not reveal)
        if SECRET_PHRASE in last_user.lower():
            _unlock("secret_phrase")
            _maybe_drop_reward("secret_phrase_used")

        # Chat count achievement
        user_msgs = [m for m in st.session_state.chat_history if m["role"] == "user"]
        if len(user_msgs) >= 5:
            _unlock("chat_5")

        if llm_ready:
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
                st.info(
                    "Add an OpenAI API key in the sidebar to enable chat.\n\n"
                    "Meanwhile, try these tabs:\n"
                    "- Evidence (Naver Search) for real-world signals\n"
                    "- Trends (Datalab) for time-series signals\n"
                )


# =========================================================
# TAB 5: REWARDS
# =========================================================
with tab_rewards:
    st.markdown("<div class='mp-section'>Rewards</div>", unsafe_allow_html=True)
    st.caption("A playful layer to keep momentum. (Session-based: resets when you refresh or redeploy.)")

    # Achievements
    st.markdown("<div class='mp-card-solid'><h3>🏆 Achievements</h3><div class='mp-muted'>Some are hidden.</div></div>", unsafe_allow_html=True)
    ach_cols = st.columns(2)
    ach_items = list(ACHIEVEMENTS.items())
    for i, (k, meta) in enumerate(ach_items):
        col = ach_cols[i % 2]
        unlocked = st.session_state.achievements.get(k, False)
        title = meta["title"] if unlocked else "???"
        hint = meta["hint"] if unlocked else "Keep exploring."
        with col:
            st.markdown(
                f"""
<div class="mp-reward">
  <div>
    <div class="name">{'✅' if unlocked else '🔒'} {title}</div>
    <div class="meta">{hint}</div>
  </div>
  <div style="font-size:1.3rem;">{'🏆' if unlocked else '🕳️'}</div>
</div>
""",
                unsafe_allow_html=True,
            )

    st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)

    # Collectibles
    st.markdown("<div class='mp-card-solid'><h3>🎁 Collectibles</h3><div class='mp-muted'>Random drops from actions.</div></div>", unsafe_allow_html=True)
    rewards = st.session_state.rewards
    if not rewards:
        st.info("No collectibles yet. Run analysis, search, trends, and chat to get drops.")
    else:
        # Show newest first
        for r in reversed(rewards[-20:]):
            st.markdown(
                f"""
<div class="mp-reward" style="margin-bottom:10px;">
  <div>
    <div class="name">{r['emoji']} {r['name']} <span style="color:#6B7280;font-weight:700;">({r['rarity']})</span></div>
    <div class="meta">{r['rarity_icon']} {r['event']} · {r['ts']}</div>
  </div>
  <div style="font-size:1.4rem;">{r['rarity_icon']}</div>
</div>
""",
                unsafe_allow_html=True,
            )

    st.markdown("<div class='mp-divider'></div>", unsafe_allow_html=True)
    st.button("♻️ (Session) I’ll try to unlock more", use_container_width=True)
