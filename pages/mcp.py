import asyncio
import json
import os
import streamlit as st
from tenacity import retry, stop_after_attempt, wait_exponential

from dotenv import load_dotenv
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import AIMessage, HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv()


@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
async def invoke_chat_model(chat_model, messages, tools):
    return await chat_model.bind_tools(tools).ainvoke(messages)


async def main():
    st.title("Bedrock chat with MCP tools")

    if "message" not in st.session_state:
        st.session_state.messages = []
    messages = st.session_state.messages

    printable_messages = [
        message for message in messages if message.type in ["ai", "human"]
    ]

    for message in printable_messages:
        if isinstance(message.content, str):
            with st.chat_message(message.type):
                st.write(message.content)
        elif isinstance(message.content, list):
            for content in message.content:
                if content["type"] == "text":
                    with st.chat_message(message.type):
                        st.write(content["text"])

    if prompt := st.chat_input():
        with st.chat_message("human"):
            st.write(prompt)

        messages.append(HumanMessage(prompt))

        chat_model = ChatBedrockConverse(
            region_name="ap-northeast-1",
            model="anthropic.claude-3-5-sonnet-20240620-v1:0",
        )

        with open("mcp_config.json", "r") as f:
            config = json.load(f)

        async with MultiServerMCPClient(config["mcpServers"]) as mcp_client:
            tools = mcp_client.get_tools()

            while True:
                try:
                    ai_response = await invoke_chat_model(chat_model, messages, tools)
                    messages.append(ai_response)

                    if isinstance(ai_response.content, str):
                        with st.chat_message("ai"):
                            st.write(ai_response.content)
                    elif isinstance(ai_response.content, list):
                        for content in ai_response.content:
                            if content["type"] == "text":
                                with st.chat_message("ai"):
                                    st.write(content["text"])

                    if ai_response.tool_calls:
                        for tool_call in ai_response.tool_calls:
                            selected_tool = {tool.name.lower(): tool for tool in tools}[
                                tool_call["name"].lower()
                            ]
                            tool_msg = await selected_tool.ainvoke(tool_call)
                            messages.append(tool_msg)
                    else:
                        break
                except Exception as e:
                    st.error(f"エラーが発生しました: {str(e)}")
                    break


asyncio.run(main())
