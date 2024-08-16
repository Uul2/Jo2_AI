from flask import Flask, request, jsonify, session, send_file
from flask_session import Session
from chatbot_service import get_chat_response, get_score_from_intent, ask_phq9_question, phq9_questions, evaluate_overall_depression, upload_and_predict, summarize_depression_analysis
import os
import datetime
import requests
import pyttsx3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=10)  # 세션 타임아웃 10분 설정
Session(app)

TARGET_SERVER_URL = 'https://example.com/receive_data'  # 데이터를 전송할 대상 서버의 URL
WAVE_OUTPUT_FILENAME = "./audio/record.wav"  # 클라이언트로부터 받은 오디오 파일 저장 경로
TTS_OUTPUT_FILENAME = "./audio/response.mp3"  # TTS로 생성된 음성 파일 저장 경로

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/api/chatbot/start', methods=['POST'])
def start_chat():
    data = request.json
    if 'user_id' not in data:
        return jsonify({'error': 'User ID is required'}), 400

    session.clear()  # 이전 세션을 지우고 새 세션을 시작
    session['user_id'] = data['user_id']  # 사용자의 ID 저장
    session['phq9_index'] = 0
    session['phq9_scores'] = []
    session['completed_phq9'] = False
    session['chat_history'] = []  # 채팅 내역 초기화
    return jsonify({'message': '새로운 세션이 시작되었습니다.', 'user_id': session['user_id']})

def process_chat_message(message):
    """메시지(텍스트 또는 음성 변환 텍스트)를 처리하는 함수"""
    if 'phq9_index' not in session:
        return {'error': '세션이 만료되었거나 유효하지 않습니다. 새로운 세션을 시작하세요.'}, 403

    session['chat_history'].append({'role': 'user', 'content': message})  # 채팅 내역에 추가

    if not session['completed_phq9']:
        phq9_index = session['phq9_index']
        phq9_scores = session['phq9_scores']

        score = get_score_from_intent(message)
        phq9_scores.append(score)
        session['phq9_index'] = phq9_index + 1
        session['phq9_scores'] = phq9_scores

        if phq9_index < len(phq9_questions):
            next_question = ask_phq9_question(phq9_index)
            session['chat_history'].append({'role': 'assistant', 'content': next_question})  # 채팅 내역에 추가
            return {'response': next_question, 'current_score': score, 'total_score': sum(phq9_scores)}, 200
        else:
            total_score = sum(phq9_scores)
            session['completed_phq9'] = True
            result = {
                'response': "PHQ-9 질문이 완료되었습니다. 이제 일상적인 대화를 나눌 수 있습니다.",
                'total_score': total_score,
                'assessment': assess_depression(total_score)
            }
            session['chat_history'].append({'role': 'assistant', 'content': result['response']})  # 채팅 내역에 추가
            return result, 200
    else:
        chat_response = get_chat_response(message)
        session['chat_history'].append({'role': 'assistant', 'content': chat_response})  # 챗봇 응답 추가
        return {'response': chat_response}, 200

@app.route('/api/chatbot/chat', methods=['POST'])
def chat():
    data = request.json
    if 'message' not in data:
        return jsonify({'error': 'Message field is required'}), 400

    result, status_code = process_chat_message(data['message'])
    return jsonify(result), status_code

@app.route('/api/chatbot/voice', methods=['POST'])
def voice_chat():
    """클라이언트로부터 음성 파일을 받아 처리하고 OpenAI API로 전송 후, 응답을 음성 파일로 반환"""
    if 'file' not in request.files:
        return jsonify({'error': 'Audio file is required'}), 400

    # 음성 파일 저장
    audio_file = request.files['file']
    audio_file.save(WAVE_OUTPUT_FILENAME)

    # 음성 인식 및 텍스트 추론 수행
    corrected_text = upload_and_predict(WAVE_OUTPUT_FILENAME)

    result, status_code = process_chat_message(corrected_text)
    
    if status_code == 200:
        # TTS 변환
        tts_engine = pyttsx3.init()
        tts_engine.save_to_file(result['response'], TTS_OUTPUT_FILENAME)
        tts_engine.runAndWait()

        # 음성 파일 반환
        return send_file(TTS_OUTPUT_FILENAME, mimetype='audio/mp3')

    return jsonify(result), status_code

@app.route('/api/chatbot/end', methods=['POST'])
def end_chat():
    chat_history = session.get('chat_history', [])
    overall_assessment = evaluate_overall_depression(chat_history)

    data_to_send = {
        'user_id': session.get('user_id'),  # 세션에 저장된 사용자 ID
        'session_id': session.sid,
        'overall_assessment': overall_assessment,
        'chat_history': chat_history
    }

    # 다른 서버로 데이터 전송
    response = requests.post(TARGET_SERVER_URL, json=data_to_send)

    session.clear()  # 세션 데이터를 삭제하여 세션을 종료합니다.
    return jsonify({'response': '채팅이 종료되었습니다. 세션이 종료되었습니다.', 'server_response': response.json()})

@app.route('/api/chatbot/analyze', methods=['POST'])
def analyze_depression_trend():
    """우울증 점수와 분석을 받아 요약된 분석을 생성"""
    data = request.json
    if 'text' not in data:
        return jsonify({'error': 'Text field is required'}), 400

    summary = summarize_depression_analysis(data['text'])
    return jsonify({'summary': summary})

def assess_depression(total_score: int) -> str:
    if total_score < 5:
        return "우울증이 없는 상태입니다."
    elif total_score < 10:
        return "경미한 우울증이 의심됩니다."
    elif total_score < 15:
        return "중간 정도의 우울증이 의심됩니다."
    else:
        return "심한 우울증이 의심됩니다."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)