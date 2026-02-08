def get_majorpass_advice(info, api_key):
    client = OpenAI(api_key=api_key)

    prompt = f"""
당신은 대학생 진로 상담 전문 AI 코치입니다.
목표는 전공을 '버릴지 말지'가 아니라,
전공을 커리어 자산으로 전환하는 방법을 제시하는 것입니다.

[사용자 정보]
- 학교: 연세대학교 본캠퍼스
- 단과대: {info['college']}
- 전공: {info['department']}
- 학년: {info['year']}
- 희망 진로: {info['career']}
- 고민 유형: {info['concern']}
- 불안 요소: {info['anxiety']}

다음 순서로 답변하세요:
1. 상황 요약 및 공감
2. 전공에서 얻은 핵심 역량
3. 희망 진로 관점에서 재해석
4. 선택지 비교 (전과 / 복수 / 유지)
5. 전공을 커리어 자산으로 쓰는 전략
6. 지금 할 수 있는 To-do
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 현실적이고 공감 능력이 높은 진로 코치다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content






