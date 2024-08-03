# chatbot_service.py

from openai import OpenAI

import os
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
from models import ChatRequest, ChatResponse


phq9_questions = [
    "최근에 기분이 가라앉거나 우울한 적이 있나요?",
    "최근에 평소에 즐기던 일들에 흥미를 잃으셨나요?",
    "최근에 잠들기 어렵거나 자주 깨셨나요?",
    "최근에 평소보다 피곤하거나 기운이 없으셨나요?",
    "최근에 식욕이 줄거나 폭식하는 경향이 있었나요?",
    "최근에 자신에 대해 나쁘게 느끼셨나요?",
    "최근에 집중하기 어려운 적이 있나요?",
    "최근에 움직이거나 말하는 것이 느리다고 느끼셨나요?",
    "최근에 죽고 싶다는 생각을 하신 적이 있나요?"
]

def get_chat_response(chat_request: ChatRequest) -> ChatResponse:
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant. You only provide responses related to depression assessment or casual daily conversations. If a user asks about another topic, politely remind them that you can only discuss depression and daily life."},
        {"role": "user", "content": chat_request.message}
    ],
    max_tokens=100,
    temperature=0.5)

    bot_response = response.choices[0].message.content.strip()
    return ChatResponse(response=bot_response)

def get_score_from_intent(answer: str) -> int:
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"다음 문장이 부정(전혀 아님, 0점) ~ 긍정(매우 맞음, 3점) 중 몇 점에 속하는지 0~3으로 숫자로만 대답해: '{answer}'"}
    ],
    max_tokens=10,
    temperature=0)

    intent = response.choices[0].message.content.strip()
    try:
        score = int(intent)
    except ValueError:
        score = 0

    return score

def ask_phq9_question(question_index: int) -> str:
    if question_index < len(phq9_questions):
        return phq9_questions[question_index]
    else:
        return None