from flask import Flask, render_template, request
import openai
import os

app = Flask(__name__)

# OPENAI API 키 설정
openai.api_key = os.environ.get("OPENAI_API_KEY")  # Render에서 환경변수로 설정

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
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        ai_plan = response['choices'][0]['message']['content']
    except Exception as e:
        ai_plan = f"AI 추천 중 오류가 발생했습니다: {str(e)}"

    return render_template('plan.html', plan=ai_plan)
