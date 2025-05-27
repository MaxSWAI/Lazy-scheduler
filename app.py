from flask import Flask, render_template, request
import google.generativeai as genai # Gemini 라이브러리 임포트
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)

# Gemini API 키 설정
# .env 파일에 GEMINI_API_KEY가 설정되어 있는지 확인하세요.
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')  # 사용자 설문 페이지

@app.route('/generate', methods=['POST'])
def generate():
    print("generate 함수 호출됨")  # 콘솔 로그 확인용

    # 사용자가 입력한 설문 내용 수집
    q1 = request.form.get('q1')
    q2 = request.form.get('q2')
    q3 = request.form.get('q3')

    # Gemini 프롬프트 구성
    # Gemini의 프롬프트 구조는 OpenAI의 Chat Completion과 약간 다릅니다.
    prompt = f"""
    당신은 사용자의 목표 달성을 돕는 똑똑한 일정 플래너입니다.

    다음은 사용자의 일정 계획을 돕기 위한 질문과 답변이다.

    1. 최근에 하고 싶었던 일은? -> {q1}
    2. 3개월 이내 달성하고 싶은 목표는? -> {q2}
    3. 계속 미루고 있었던 일은? -> {q3}

    이 정보를 바탕으로 사용자가 이번 주에 시작할 수 있는 계획을 한글로 구체적으로 3가지 제안해줘.
    각 제안은 '제목: 내용' 형식으로 작성해줘.
    """

    try:
        # Gemini 모델 초기화
        # 'gemini-pro', 'gemini-1.5-pro-latest' 등 다양한 Gemini 모델을 선택할 수 있습니다.
        model = genai.GenerativeModel('gemini-pro')

        # Gemini를 사용하여 콘텐츠 생성
        # 'gemini-pro'의 경우 직접 텍스트 생성이 일반적입니다.
        # 더 복잡한 대화 흐름의 경우 model.start_chat() 사용을 고려하세요.
        response = model.generate_content(prompt)
        ai_plan = response.text
    except Exception as e:
        ai_plan = f"AI 추천 중 오류가 발생했습니다: {str(e)}"

    return render_template('plan.html', plan=ai_plan)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
