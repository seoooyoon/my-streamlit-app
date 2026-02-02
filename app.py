import streamlit as st
import requests
from collections import Counter

# 페이지 설정
st.set_page_config(page_title="🎬 나와 어울리는 영화는?", layout="wide")

# 사이드바 - API Key 입력
st.sidebar.title("🔑 TMDB 설정")
tmdb_api_key = st.sidebar.text_input("TMDB API Key를 입력하세요", type="password")

st.title("🎬 나와 어울리는 영화는?")
st.write("당신의 영화 취향에 어울리는 작품을 추천합니다 🎥✨")
st.markdown("---")

# 질문
questions = [
    {
        "question": "Q1. 시험 끝난 날, 가장 끌리는 계획?",
        "options": ["카페에서 하루 정리 ☕", "친구들과 여행 🚗", "집에서 콘텐츠 몰입 🪐", "웃긴 영상 보기 😂"]
    },
    {
        "question": "Q2. 새벽 감성, 드는 생각?",
        "options": ["관계는 왜 복잡해?", "지금 떠나고 싶다", "다른 차원의 내가 있다면?", "나만 이 시간에..."]
    },
    {
        "question": "Q3. 같이 볼 영화 장르?",
        "options": ["스토리 중심 🎞", "스케일 큰 장면 💥", "세계관 영화 ✨", "배꼽 잡는 코미디 🤣"]
    },
    {
        "question": "Q4. 과제 스트레스 회복 방식?",
        "options": ["혼자 생각", "운동", "다른 세계 도피", "친구 수다"]
    },
    {
        "question": "Q5. 인생 영화 장르?",
        "options": ["감정 성장 🌱", "도전 연속 🔥", "비밀 세계 🌌", "웃픈 전개 🤪"]
    }
]

answers = []
for i, q in enumerate(questions):
    answers.append(st.radio(q["question"], q["options"], key=f"q{i}"))
    st.write("")

st.markdown("---")

genre_map = {
    0: ("로맨스/드라마", [18, 10749]),
    1: ("액션/어드벤처", [28]),
    2: ("SF/판타지", [878, 14]),
    3: ("코미디", [35])
}

def fetch_tmdb_recommendations(genre_ids, api_key):
    """
    TMDB discover API로 인기 + 평점 높은 영화 5개를 가져옵니다.
    """
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key,
        "with_genres": ",".join(map(str, genre_ids)),
        "language": "ko-KR",
        "sort_by": "vote_average.desc",  # 평점 높은 순
        "vote_count.gte": 50            # 투표수가 50 이상
    }
    response = requests.get(url, params=params)
    return response.json().get("results", [])

if st.button("🎯 결과 보기"):
    if not tmdb_api_key:
        st.error("TMDB API Key를 입력해주세요!")
    else:
        # 장르 분석
        counts = Counter([q.index(a) for q, a in zip([[o for o in q["options"]] for q in questions], answers)])
        top_idx = counts.most_common(1)[0][0]
        genre_name, genre_id_list = genre_map[top_idx]

        st.success(f"✨ 추천 장르: **{genre_name}**")

        # TMDB 추천
        movies = fetch_tmdb_recommendations(genre_id_list, tmdb_api_key)

        st.subheader("🎬 추천 영화 TOP 5")
        for movie in movies[:5]:
            cols = st.columns([1, 3])
            with cols[0]:
                if movie.get("poster_path"):
                    st.image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}")
                else:
                    st.write("포스터 없음")

            with cols[1]:
                st.markdown(f"### {movie['title']}")
                st.write(f"⭐ 평점: {movie['vote_average']} (투표: {movie['vote_count']})")
                st.write(f"📅 개봉일: {movie.get('release_date', '정보 없음')}")
                st.write(movie.get("overview", "줄거리 없음"))
                st.caption(f"💡 이 영화를 추천하는 이유: {genre_name} 감성과 잘 맞습니다!")
            st.markdown("---")


