import streamlit as st

from config import TRACELOOP_API_KEY
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow


load_dotenv()

Traceloop.init(
    disable_batch=True,
    api_key=TRACELOOP_API_KEY
)


def create_chain():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "回答には以下の情報も参考にしてください。参考情報: \n{info}",
            ),
            ("placeholder", "{history}"),
            ("human", "{input}"),
        ]
    )
    return prompt | ChatOpenAI(model="gpt-4o-mini", temperature=0)


if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.chain = create_chain()


@workflow(name="multimodal-history-append")
def history_append(user_input, response):
    st.session_state.history.append(HumanMessage(user_input))
    st.session_state.history.append(response)


st.title("Multimodal RAG ChatBot")
uploaded_file = st.file_uploader(
    "Upload an image", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", width=700)

user_input = st.text_input("Enter a prompt")
if st.button("Send"):
    response = st.session_state.chain.invoke(
        {
            "input": user_input,
            "history": st.session_state.history,
            "info": "ユーザーの年齢は10歳です。"
        }
    )
    history_append(user_input, response)

    for message in reversed(st.session_state.history):
        st.write(f"{message.type}: {message.content}")
