from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일에서 환경 변수 불러오기
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)

# OpenAI 클라이언트 설정
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    q1 = request.form.get('q1')
    q2 = request.form.get('q2')
    q3 = request.form.get('q3')

    prompt = f"""
다음은 사용자의 일정 계획을 돕기 위한 질문과 답변이다.

1. 최근에 하고 싶었던 일은? -> {q1}
2. 3개월 이내 달성하고 싶은 목표는? -> {q2}
3. 계속 미루고 있었던 일은? -> {q3}

이 정보를 바탕으로 사용자가 이번 주에 시작할 수 있는 계획을 한글로 구체적으로 3가지 제안해줘.
각 제안은 '제목: 내용' 형식으로 작성해줘.
"""

    try:
        # 새로운 방식 사용
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 사용자의 목표 달성을 돕는 똑똑한 일정 플래너입니다."},
                {"role": "user", "content": prompt}
            ]
        )
        ai_plan = response.choices[0].message.content
    except Exception as e:
        ai_plan = f"AI 추천 중 오류가 발생했습니다: {str(e)}"

    return render_template('plan.html', plan=ai_plan)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
