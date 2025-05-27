from flask import Flask, render_template, request
import google.generativeai as genai
import os
from dotenv import load_dotenv
import locale
from notion_client import Client # Notion 클라이언트 임포트
import re # 정규표현식 모듈 임포트 (AI 생성 텍스트 파싱용)

# .env 파일에서 환경변수 로드
load_dotenv()

# Flask 앱 초기화
app = Flask(__name__)

# 한국어 로케일 설정
try:
    locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')  # Linux 기반
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'ko_KR')  # macOS 기반
    except locale.Error:
        locale.setlocale(locale.LC_ALL, '')  # 시스템 기본값

# Gemini API 키 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Notion API 설정
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

notion = None
# Notion 토큰이 설정되어 있으면 Notion 클라이언트 초기화
if NOTION_TOKEN:
    try:
        notion = Client(auth=NOTION_TOKEN)
        print("Notion 클라이언트 초기화 성공")
    except Exception as e:
        print(f"Notion 클라이언트 초기화 중 오류 발생: {e}")
else:
    print("WARNING: NOTION_TOKEN 환경 변수가 설정되지 않았습니다. Notion 연동이 비활성화됩니다.")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    print("generate 함수 호출됨")

    q1 = request.form.get('q1')
    q2 = request.form.get('q2')
    q3 = request.form.get('q3')

    prompt = f"""
    다음은 사용자의 일정 계획을 돕기 위한 질문과 답변입니다.

    1. 최근에 하고 싶었던 일은? -> {q1}
    2. 3개월 이내 달성하고 싶은 목표는? -> {q2}
    3. 계속 미루고 있었던 일은? -> {q3}

    이 정보를 바탕으로 사용자가 이번 주에 시작할 수 있는 계획을 한국어로 구체적으로 3가지 제안해주세요.
    각 제안은 '제목: 내용' 형식으로 작성해주세요.
    """

    ai_plan = ""
    try:
        model = genai.GenerativeModel('gemini-pro') # 또는 'gemini-1.5-flash-latest' 등
        response = model.generate_content(prompt)
        ai_plan = response.text
    except Exception as e:
        ai_plan = f"AI 추천 중 오류가 발생했습니다: {str(e)}"
        print(f"Gemini API 호출 오류: {e}")

    # AI가 생성한 계획을 Notion에 추가 시도
    notion_status_message = ""
    # notion 클라이언트가 초기화되었고, 데이터베이스 ID가 있으며, AI 플랜에 오류가 없을 경우에만 Notion 연동 시도
    if notion and NOTION_DATABASE_ID and "오류가 발생했습니다" not in ai_plan:
        try:
            # 정규표현식을 사용하여 AI가 생성한 텍스트에서 '제목: ... 내용: ...' 패턴을 찾습니다.
            # re.DOTALL은 .이 줄바꿈 문자까지 포함하도록 합니다.
            # (?=(?:제목:|$))는 다음 '제목:'이 오거나 문자열의 끝까지 매칭되도록 합니다.
            plans_parsed = re.findall(r'제목:\s*(.*?)\s*내용:\s*(.*?)(?=(?:제목:|$))', ai_plan, re.DOTALL)

            if not plans_parsed: # 파싱된 계획이 없으면 오류 메시지 출력
                notion_status_message = "\n\nNotion 연동 실패: AI 응답에서 계획을 파싱할 수 없습니다."
                print("Notion 연동 실패: AI 응답에서 계획을 파싱할 수 없습니다.")
            else:
                for title, content in plans_parsed:
                    # Notion 데이터베이스에 페이지 생성
                    print(f"Notion에 추가 시도 - 제목: {title.strip()}, 내용: {content.strip()[:50]}...") # 내용 일부만 출력
                    notion.pages.create(
                        parent={"database_id": NOTION_DATABASE_ID},
                        properties={
                            "제목": { # Notion 데이터베이스의 '제목' 속성 이름과 정확히 일치해야 합니다. (대소문자, 띄어쓰기)
                                "title": [
                                    {
                                        "text": {"content": title.strip()}
                                    }
                                ]
                            },
                            "내용": { # Notion 데이터베이스의 '내용' 속성 이름과 정확히 일치해야 합니다. (대소문자, 띄어쓰기)
                                "rich_text": [
                                    {
                                        "text": {"content": content.strip()}
                                    }
                                ]
                            }
                        }
                    )
                notion_status_message = "\n\nNotion에 일정이 성공적으로 추가되었습니다."
                print("Notion에 일정 추가 성공")

        except Exception as e:
            notion_status_message = f"\n\nNotion 연동 중 오류 발생: {str(e)}. Notion API 키, DB ID, 권한을 확인해주세요."
            print(f"Notion 연동 오류: {e}")
    elif not NOTION_TOKEN or not NOTION_DATABASE_ID:
        notion_status_message = "\n\nNotion 연동 비활성화: .env 파일에 NOTION_TOKEN 또는 NOTION_DATABASE_ID가 설정되지 않았습니다."
        print("Notion 연동 비활성화: .env 파일에 NOTION_TOKEN 또는 NOTION_DATABASE_ID가 설정되지 않았습니다.")

    final_plan_output = ai_plan + notion_status_message
    return render_template('plan.html', plan=final_plan_output)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
