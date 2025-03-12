import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.llm = ChatOpenAI()

load_dotenv()

st.title("Multimodal RAG ChatBot")
uploaded_file = st.file_uploader(
    "Upload an image", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", width=700)

user_input = st.text_input("Enter a prompt")
if st.button("Send"):
    st.session_state.history.append(HumanMessage(user_input))
    response = st.session_state.llm.invoke(st.session_state.history)
    st.session_state.history.append(response)

    for message in reversed(st.session_state.history):
        st.write(f"{message.type}: {message.content}")
