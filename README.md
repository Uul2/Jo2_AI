# 🧠 우울증 상담 챗봇 API

이 프로젝트는 PHQ-9 기반 우울증 평가 및 상담을 제공하는 챗봇 API입니다. OpenAI의 GPT-3.5를 사용하여 우울증 평가, 일상 대화, 음성 인식, 그리고 텍스트 분석 기능을 지원합니다.

## 📚 목차
- [기능](#-기능)
- [설치](#-설치)
- [사용 방법](#-사용-방법)
- [API 엔드포인트](#-api-엔드포인트)
- [기여하기](#-기여하기)
- [라이선스](#-라이선스)

## 💡 기능
- **PHQ-9 우울증 평가**: 사용자와의 대화를 통해 PHQ-9 질문에 답변을 받고, 이를 바탕으로 우울증 점수를 계산합니다.
- **일상 대화**: PHQ-9 질문이 완료된 후, 사용자는 일상적인 대화를 나눌 수 있습니다.
- **음성 인식**: 사용자의 음성을 텍스트로 변환하고, 이를 분석하여 응답을 제공합니다.
- **우울증 추이 분석 요약**: 클라이언트로부터 받은 우울증 점수와 분석 내용을 300자 이내로 요약합니다.

## 🚀 설치
이 프로젝트를 로컬 환경에 설치하려면 다음 단계를 따르세요:

1. **리포지토리 클론**
   ```bash
   git clone https://github.com/username/repository-name.git
   cd repository-name
필요한 패키지 설치

bash
코드 복사
pip install -r requirements.txt
환경 변수 설정
.env 파일을 생성하여 OpenAI API 키를 설정하세요:

makefile
코드 복사
OPENAI_API_KEY=your-openai-api-key
🛠 사용 방법
서버 실행
서버를 실행하려면 다음 명령어를 사용하세요:

bash
코드 복사
python app.py
서버가 실행되면 API는 http://localhost:5000에서 요청을 받을 준비가 됩니다.

📑 API 엔드포인트
1. 시작하기 (Start Chat)
URL: /api/chatbot/start
Method: POST
설명: 새로운 상담 세션을 시작합니다.
Request Body:
json
코드 복사
{
  "user_id": "string"
}
Response:
json
코드 복사
{
  "message": "새로운 세션이 시작되었습니다.",
  "user_id": "string"
}
2. 메시지 채팅 (Chat)
URL: /api/chatbot/chat
Method: POST
설명: 사용자 메시지를 처리하고, PHQ-9 질문이나 일반 대화에 응답합니다.
Request Body:
json
코드 복사
{
  "message": "string"
}
Response:
json
코드 복사
{
  "response": "string",
  "current_score": "number",
  "total_score": "number"
}
3. 음성 채팅 (Voice Chat)
URL: /api/chatbot/voice
Method: POST
설명: 클라이언트로부터 음성 파일을 받아, 텍스트로 변환 후 처리합니다.
Request Form Data:
file: 사용자가 보낸 음성 파일
Response:
json
코드 복사
{
  "response": "string",
  "current_score": "number",
  "total_score": "number"
}
4. 채팅 종료 (End Chat)
URL: /api/chatbot/end
Method: POST
설명: 현재 상담 세션을 종료하고, 대화 내역을 분석하여 외부 서버로 전송합니다.
Response:
json
코드 복사
{
  "response": "채팅이 종료되었습니다. 세션이 종료되었습니다.",
  "server_response": {}
}
5. 우울증 분석 요약 (Analyze Depression Trend)
URL: /api/chatbot/analyze
Method: POST
설명: 클라이언트로부터 제공된 우울증 점수 및 분석 텍스트를 요약합니다.
Request Body:
json
코드 복사
{
  "text": "string"
}
Response:
json
코드 복사
{
  "summary": "string"
}
🤝 기여하기
기여를 환영합니다! 버그 리포트, 기능 제안, 풀 리퀘스트 등을 통해 프로젝트에 기여할 수 있습니다.

📝 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.

go
코드 복사

이 문서 내용을 `README.md` 파일로 저장하여 프로젝트의 루트 디렉토리에 추가하시면 깃허브에 업로드할 때 자동으로 프로젝트 설명에 포함됩니다.





