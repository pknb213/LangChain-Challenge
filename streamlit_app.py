import json
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import ChatPromptTemplate

st.title("QuizGPT")

# --- API key 입력 및 세션 저장 ---
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if api_key:
    st.session_state['openai_api_key'] = api_key

# 세션 상태 초기화
if 'quiz_started' not in st.session_state:
    st.session_state['quiz_started'] = False
if 'questions' not in st.session_state:
    st.session_state['questions'] = []

# --- 사이드바 설정 ---
st.sidebar.markdown('[Git Hub Link](https://github.com/pknb213/LangChain-Challenge)')
difficulty = st.sidebar.selectbox("Select Difficulty", ["Easy", "Medium", "Hard"])
num_questions = 3

if st.sidebar.button("Start Quiz"):
    if 'openai_api_key' not in st.session_state:
        st.error("Please enter your OpenAI API Key.")
    else:
        # 퀴즈 시작 상태 저장
        st.session_state['quiz_started'] = True

        # 함수 호출 스펙: 여러 문제를 배열로 반환
        function_spec = {
            "name": "generate_quiz",
            "description": "Generate multiple Pokémon quiz questions with solutions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "questions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "equation": {"type": "string", "description": "Quiz Pokémon"},
                                "solution": {"type": "string", "description": "Answer"},
                            },
                            "required": ["equation", "solution"],
                        },
                    },
                },
                "required": ["questions"],
            },
        }

        # 한 번의 프롬프트로 문제 생성 요청
        system_prompt = ("""
            "Please produce {num} {difficulty} level questions in Korean." 
            "Be sure to elaborate so that the correct answer always refers to only one Pokémon.
            "Ensure each question is unique and not based on any example. "
        """)
        human_template = (
            "Please produce {num} {difficulty} level questions in Korean. "
            "Return the result as a JSON object conforming to the function schema."
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_template),
        ]).format(num=num_questions, difficulty=difficulty)

        # 모델 바인딩 및 호출
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            openai_api_key=st.session_state['openai_api_key'],
            streaming=False,
            callbacks=[StreamingStdOutCallbackHandler()],
        ).bind(function_call={"name": "generate_quiz"}, functions=[function_spec])

        response = llm.invoke(prompt)
        payload = response.additional_kwargs['function_call']['arguments']
        quiz_data = json.loads(payload)
        st.session_state['questions'] = quiz_data['questions']

# --- 퀴즈 화면 ---
if st.session_state['quiz_started']:
    st.subheader("Quiz Questions")
    user_answers = []

    for idx, q in enumerate(st.session_state['questions'], start=1):
        st.write(f"**Q{idx}.** {q['equation']}")
        ans = st.text_input(f"Your answer for Q{idx}", key=f"answer_{idx}")
        user_answers.append(ans)

    if st.button("Submit Answers"):
        correct_answers = [q['solution'] for q in st.session_state['questions']]
        st.write(correct_answers)
        score = sum(1 for i, a in enumerate(user_answers) if a.strip() == correct_answers[i])
        st.write(f"Your score: **{score} / {len(correct_answers)}**")
        if score == len(correct_answers):
            st.balloons()
            st.success("🎉 만점입니다!")
        else:
            st.warning("다시 도전해 보세요! Please select 'Start Quiz' btn.")
