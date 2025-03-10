import streamlit as st
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

st.title("Multimodal RAG ChatBot")
uploaded_file = st.file_uploader(
    "Upload an image", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", width=700)

user_input = st.text_input("Enter a prompt")
if st.button("Send"):
    llm = ChatOpenAI()
    response = llm.invoke(user_input)
    st.write(f"bot: {response.content}")
    st.write(f"human: {user_input}")
