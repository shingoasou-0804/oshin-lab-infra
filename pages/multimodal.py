import base64
from operator import itemgetter

import streamlit as st
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from traceloop.sdk import Traceloop
from traceloop.sdk.decorators import workflow

from config import TRACELOOP_API_KEY

Traceloop.init(disable_batch=True, api_key=TRACELOOP_API_KEY)


@workflow(name="get-image-description")
def get_image_description(image_data: str):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "human",
                [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    }
                ],
            ),
        ]
    )
    chain = prompt | ChatOpenAI(model="gpt-4o-mini") | StrOutputParser()
    return chain.invoke({"image_data": image_data})


def create_message(dic: dict):
    image_data = dic["image"]
    if image_data:
        return [
            (
                "human",
                [
                    {"type": "text", "text": dic["input"]},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    },
                ],
            )
        ]
    return [("human", dic["input"])]


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def create_chain():
    vectorstore = Chroma(
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
        persist_directory="data",
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "回答には以下の情報も参考にしてください。参考情報：\n{info}",
            ),
            ("placeholder", "{history}"),
            ("placeholder", "{message}"),
        ]
    )
    return (
        {
            "message": create_message,
            "info": itemgetter("input") | retriever | format_docs,
            "history": itemgetter("history"),
        }
        | prompt
        | ChatOpenAI(model="gpt-4o-mini", temperature=0)
    )


if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.chain = create_chain()


@workflow(name="multimodal-history-append")
def history_append(user_input, response):
    st.session_state.history.append(HumanMessage(user_input))
    st.session_state.history.append(response)


st.title("Multimodal RAG ChatBot")
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", width=700)

user_input = st.text_input("Enter a prompt")
if st.button("Send"):
    image_data = None
    image_description = ""
    if uploaded_file is not None:
        image_data = base64.b64encode(uploaded_file.read()).decode("utf-8")
        image_description = get_image_description(image_data)
    response = st.session_state.chain.invoke(
        {
            "input": user_input + image_description,
            "history": st.session_state.history,
            "image": image_data,
        }
    )
    history_append(user_input, response)

    for message in reversed(st.session_state.history):
        st.write(f"{message.type}: {message.content}")
