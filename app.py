# app.py

from flask import Flask, request, jsonify, session
from flask_session import Session
from chatbot_service import get_chat_response, get_score_from_intent, ask_phq9_question, phq9_questions
from models import ChatRequest
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/api/chatbot/chat', methods=['POST'])
def chat():
    if 'phq9_index' not in session:
        session['phq9_index'] = 0
        session['phq9_scores'] = []

    data = request.json
    if 'message' not in data:
        return jsonify({'error': 'Message field is required'}), 400

    chat_request = ChatRequest(message=data['message'])
    chat_response = get_chat_response(chat_request)

    phq9_index = session['phq9_index']
    phq9_scores = session['phq9_scores']

    if phq9_index < len(phq9_questions):
    # if phq9_index < 9:
        score = get_score_from_intent(chat_request.message)
        phq9_scores.append(score)
        session['phq9_index'] = phq9_index + 1
        session['phq9_scores'] = phq9_scores
        next_question = ask_phq9_question(phq9_index)
        return jsonify({'response': next_question, 'current_score': score, 'total_score': sum(phq9_scores)})
    else:
        total_score = sum(phq9_scores)
        session.pop('phq9_index', None)
        session.pop('phq9_scores', None)
        result = {
            'response': "PHQ-9 질문이 완료되었습니다.",
            'total_score': total_score,
            'assessment': assess_depression(total_score)
        }
        return jsonify(result)

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