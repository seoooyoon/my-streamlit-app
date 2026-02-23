import json
import os
import re
from datetime import datetime
from typing import Dict, List

import pandas as pd
import requests
import streamlit as st

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="MajorPass · YONSEI",
    page_icon="🦅",
    layout="wide",
)

# =========================================================
# CLEAN WHITE UI
# =========================================================
st.markdown("""
<style>
body, [data-testid="stApp"] {
    background-color: #FFFFFF;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.mp-section {
    font-size: 1.2rem;
    font-weight: 700;
    margin-top: 20px;
}

.mp-card {
    background: #F8FAFC;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #E2E8F0;
    margin-bottom: 20px;
}

.metric-box {
    background: #F1F5F9;
    padding: 16px;
    border-radius: 12px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_context" not in st.session_state:
    st.session_state.chat_context = {}

if "xp" not in st.session_state:
    st.session_state.xp = 0

if "growth_stage" not in st.session_state:
    st.session_state.growth_stage = 0

if "todos" not in st.session_state:
    st.session_state.todos = [
        {"task": "Define 1 target role clearly", "done": False},
        {"task": "Create 1 portfolio deliverable", "done": False},
        {"task": "Generate 2 Evidence Digests", "done": False},
    ]

# =========================================================
# SIMPLE CHARACTER GROWTH
# =========================================================
CHARACTERS = ["👶", "🧒", "🧑", "🧑‍🎓", "🧑‍💼"]

def update_growth():
    completed = sum(1 for t in st.session_state.todos if t["done"])
    st.session_state.xp = completed * 10
    stage = min(completed, len(CHARACTERS)-1)
    st.session_state.growth_stage = stage

# =========================================================
# TABS
# =========================================================
tab_profile, tab_chat, tab_growth = st.tabs(
    ["Profile", "Chat", "Growth Rewards"]
)

# =========================================================
# TAB 1: PROFILE
# =========================================================
with tab_profile:

    st.markdown("<div class='mp-section'>Profile</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        major = st.text_input("Major")
        semester = st.selectbox("Semester", ["1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"])

    with col2:
        gpa = st.slider("GPA", 0.0, 4.3, 3.5)
        interest = st.text_area("Interest / Career Direction")

    if st.button("Generate Strategy", use_container_width=True):

        st.markdown("<div class='mp-card'>", unsafe_allow_html=True)
        st.markdown("### 전략 요약")

        st.write(f"""
현재 전공은 **{major}**, 학기는 **{semester}**입니다.  
관심 분야는 **{interest}**이며, GPA는 **{gpa:.2f}**입니다.

다음 단계는:
1. 관심 분야와 전공 연결 구조 정리
2. 산출물 1개 제작
3. 학기 중 증명 가능한 결과 만들기
""")

        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# TAB 2: CHAT
# =========================================================
with tab_chat:
    st.markdown("<div class='mp-section'>Chat</div>", unsafe_allow_html=True)

    SECRET_PHRASE = "path to pass"

    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    quick1, quick2, quick3, quick4 = st.columns(4)
    if quick1.button("🧩 Build a 4-week plan", use_container_width=True):
        st.session_state.chat_history.append({"role": "user", "content": "Build a 4-week plan from my current situation."})
    if quick2.button("📌 Prioritize next semester", use_container_width=True):
        st.session_state.chat_history.append({"role": "user", "content": "What should I prioritize next semester?"})
    if quick3.button("🔎 Turn evidence into actions", use_container_width=True):
        st.session_state.chat_history.append({"role": "user", "content": "Turn my evidence summary into actions."})
    if quick4.button("🧠 Portfolio structure", use_container_width=True):
        st.session_state.chat_history.append({"role": "user", "content": "Design a portfolio structure."})

    user_input = st.chat_input("Ask anything...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
        last = st.session_state.chat_history[-1]["content"]

        if SECRET_PHRASE in last.lower():
            st.toast("Secret unlocked 🎉")

        with st.chat_message("assistant"):
            response = f"""
좋은 질문이에요.

현재 상황을 기반으로 보면:

- 가장 중요한 것은 산출물 제작입니다.
- 실행 단위로 쪼개서 4주 계획을 만드는 것이 좋습니다.
- Evidence → 실행 → 포트폴리오 구조로 연결하세요.

다음 행동:
1. 이번 주 안에 1개 결과물 초안
2. 관심 직무 JD 3개 분석
3. 포트폴리오 구조 설계
"""
            st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

# =========================================================
# TAB 3: GROWTH REWARDS
# =========================================================
with tab_growth:

    st.markdown("<div class='mp-section'>Growth Rewards</div>", unsafe_allow_html=True)

    update_growth()

    st.markdown(f"""
<div class="mp-card" style="text-align:center;">
    <div style="font-size:3rem;">{CHARACTERS[st.session_state.growth_stage]}</div>
    <div style="margin-top:10px;">XP: {st.session_state.xp}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("### Roadmap To-Do")

    for i, todo in enumerate(st.session_state.todos):
        done = st.checkbox(todo["task"], value=todo["done"], key=f"todo_{i}")
        st.session_state.todos[i]["done"] = done

    if all(t["done"] for t in st.session_state.todos):
        st.success("🎉 You completed your roadmap! Character fully grown.")
