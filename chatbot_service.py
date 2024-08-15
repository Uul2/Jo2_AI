# from openai import OpenAI

# import os
# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
# from models import ChatRequest, ChatResponse


# phq9_questions = [
#     "최근에 기분이 가라앉거나 우울한 적이 있나요?",
#     "최근에 평소에 즐기던 일들에 흥미를 잃으셨나요?",
#     "최근에 잠들기 어렵거나 자주 깨셨나요?",
#     "최근에 평소보다 피곤하거나 기운이 없으셨나요?",
#     "최근에 식욕이 줄거나 폭식하는 경향이 있었나요?",
#     "최근에 자신에 대해 나쁘게 느끼셨나요?",
#     "최근에 집중하기 어려운 적이 있나요?",
#     "최근에 움직이거나 말하는 것이 느리다고 느끼셨나요?",
#     "최근에 죽고 싶다는 생각을 하신 적이 있나요?"
# ]

# def get_chat_response(chat_request: ChatRequest) -> ChatResponse:
#     response = client.chat.completions.create(model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant. You only provide responses related to depression assessment or casual daily conversations. If a user asks about another topic, politely remind them that you can only discuss depression and daily life."},
#         {"role": "user", "content": chat_request.message}
#     ],
#     max_tokens=100,
#     temperature=0.5)

#     bot_response = response.choices[0].message.content.strip()
#     return ChatResponse(response=bot_response)

# def get_score_from_intent(answer: str) -> int:
#     response = client.chat.completions.create(model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": f"다음 문장이 부정(전혀 아님, 0점) ~ 긍정(매우 맞음, 3점) 중 몇 점에 속하는지 0~3으로 숫자로만 대답해 : '{answer}'"}
#     ],
#     max_tokens=10,
#     temperature=0)

#     intent = response.choices[0].message.content.strip()
#     try:
#         score = int(intent)
#     except ValueError:
#         score = 0

#     return score

# def ask_phq9_question(question_index: int) -> str:
#     if question_index < len(phq9_questions):
#         return phq9_questions[question_index]
#     else:
#         return None

# def evaluate_overall_depression(chat_history) -> dict:
#     response = client.chat.completions.create(model="gpt-3.5-turbo",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant. Evaluate the overall depression level (out of 10) and mental state based on the following conversation history:"},
#         {"role": "user", "content": "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])}
#     ],
#     max_tokens=100,
#     temperature=0.5)

#     overall_assessment = response.choices[0].message.content.strip()
#     return {'assessment': overall_assessment}

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
import librosa
import torch
import numpy as np
from openspeech.models import MODEL_REGISTRY
from openspeech.tokenizers import TOKENIZER_REGISTRY
from omegaconf import OmegaConf
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from models import ChatRequest, ChatResponse

# OpenAI API 키 설정

# PHQ-9 질문 목록
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
        {"role": "user", "content": f"다음 문장이 부정(전혀 아님, 0점) ~ 긍정(매우 맞음, 3점) 중 몇 점에 속하는지 0~3으로 숫자로만 대답해 : '{answer}'"}
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

def evaluate_overall_depression(chat_history) -> dict:
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Evaluate the overall depression level (out of 10) and mental state based on the following conversation history:"},
        {"role": "user", "content": "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])}
    ],
    max_tokens=100,
    temperature=0.5)

    overall_assessment = response.choices[0].message.content.strip()
    return {'assessment': overall_assessment}

def summarize_depression_analysis(text: str) -> str:
    """우울증 점수 및 분석을 요약하는 함수"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Summarize the following depression analysis in 300 characters or less: '{text}'"}
        ],
        max_tokens=100,
        temperature=0.5
    )

    summary = response.choices[0].message['content'].strip()
    return summary

# 음성 인식 설정
audio_config = {
    "name": "melspectogram",
    "sample_rate": 16000,
    "frame_length": 20.0,
    "frame_shift": 10.0,
    "del_silence": False,
    "num_mels": 80,
    "apply_spec_augment": True,
    "apply_noise_augment": False,
    "apply_time_stretch_augment": False,
    "apply_joining_augment": False,
}

infer_config = {
    "use_cuda": torch.cuda.is_available(),
    "checkpoint_path": "./models/multi_head_las.ckpt",
}

model_config = {
    "model_name": "listen_attend_spell_with_multi_head",
    "num_encoder_layers": 3,
    "num_decoder_layers": 2,
    "hidden_state_dim": 512,
    "encoder_dropout_p": 0.3,
    "encoder_bidirectional": True,
    "rnn_type": "lstm",
    "joint_ctc_attention": False,
    "max_length": 128,
    "num_attention_heads": 4,
    "decoder_dropout_p": 0.2,
    "decoder_attn_mechanism": "multi-head",
    "teacher_forcing_ratio": 1.0,
    "optimizer": "adam",
}

tokenizer_config = {
    "sos_token": "<sos>",
    "eos_token": "<eos>",
    "pad_token": "<pad>",
    "blank_token": "<blank>",
    "encoding": "utf-8",
    "unit": "kspon_character",
    "vocab_path": "./aihub_labels.csv",
}

# 설정 파일 생성
configs = OmegaConf.create({
    "audio": audio_config,
    "infer": infer_config,
    "model": model_config,
    "tokenizer": tokenizer_config,
})

# 토크나이저 및 모델 초기화
tokenizer = TOKENIZER_REGISTRY[configs.tokenizer.unit](configs)
model = MODEL_REGISTRY[configs.model.model_name].load_from_checkpoint(
    configs.infer.checkpoint_path, configs=configs, tokenizer=tokenizer)
model.to(torch.device("cuda" if configs.infer.use_cuda else "cpu"))

def transform_input(signal):
    """오디오 신호를 멜스펙트로그램으로 변환"""
    melspectrogram = librosa.feature.melspectrogram(
        y=signal, sr=configs.audio.sample_rate, n_mels=configs.audio.num_mels,
        n_fft=512, hop_length=160)
    melspectrogram = librosa.power_to_db(melspectrogram, ref=np.max)
    melspectrogram -= melspectrogram.mean()
    melspectrogram /= np.std(melspectrogram)
    return torch.FloatTensor(melspectrogram).transpose(0, 1)

def parse_audio(filepath):
    """오디오 파일을 파싱하여 멜스펙트로그램으로 변환"""
    signal, sr = librosa.load(filepath, sr=None)
    signal = librosa.resample(signal, orig_sr=sr, target_sr=16000)
    return transform_input(signal).to(torch.device("cuda" if configs.infer.use_cuda else "cpu"))

def inference(feature):
    """모델을 사용하여 추론 수행"""
    model.eval()
    with torch.no_grad():
        outputs = model(feature.unsqueeze(0), torch.tensor([feature.shape[0]]))
    return tokenizer.decode(outputs["predictions"].cpu().detach().numpy())[0]

def correct_text(text, device):
    """음성 인식된 텍스트를 문법적으로나 의미적으로 교정합니다."""
    model_name = "t5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    if torch.cuda.is_available() and device == "cuda":
        model = model.to("cuda")

    nlp = pipeline("text2text-generation", model=model, tokenizer=tokenizer, device=0 if torch.cuda.is_available() and device == "cuda" else -1)
    corrected_text = nlp(f"correct: {text}", max_new_tokens=50)

    return corrected_text[0]['generated_text']

def send_to_openai_chat(text):
    """OpenAI API에 텍스트를 보내고 응답을 받음"""
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": text}
    ])
    chat_response = response.choices[0].message.content.strip()
    print("ChatGPT Response:", chat_response)
    return chat_response

def upload_and_predict(filepath):
    """오디오 파일을 업로드하고 모델을 사용해 추론 후 교정 및 OpenAI API로 전송"""
    feature = parse_audio(filepath)
    prediction = inference(feature)
    print("Original Prediction:", prediction)

    # 교정된 텍스트 출력
    corrected_text = correct_text(prediction, device="cuda")
    print("Corrected Text:", corrected_text)

    # 교정된 텍스트를 OpenAI API로 전송
    chat_response = send_to_openai_chat(corrected_text)

    return chat_response