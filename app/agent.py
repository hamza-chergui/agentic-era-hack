# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# mypy: disable-error-code="union-attr"
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from .crew.crew import LeaningCrew

LOCATION = "us-central1"
LLM = "gemini-2.0-flash-001"


@tool
def learning_tool(topic: str) -> str:
    """Use this tool to write an article about a topic."""
    inputs = {"topic": topic}
    return LeaningCrew().crew().kickoff(inputs=inputs)


tools = [learning_tool]

# 2. Set up the language model
llm = ChatVertexAI(
    model=LLM, location=LOCATION, temperature=0, max_tokens=4096, streaming=True
).bind_tools(tools)


# 3. Define workflow components
def should_continue(state: MessagesState) -> str:
    """Determines whether to use the crew or end the conversation."""
    last_message = state["messages"][-1]
    return "learning_crew" if last_message.tool_calls else END


def call_model(state: MessagesState, config: RunnableConfig) -> dict[str, BaseMessage]:
    """Calls the language model and returns the response."""
    system_message = (

        """
            You are Maestro, an AI agent responsible for assisting the user in finding educational content.
            You task is to:
            1. Engage with the user to determine the topic they want to learn about.
            2. Send the query the learning tool
            3. Display a well written article.
        """

        # """ 
        # You are Maestro, an AI agent responsible for assisting the user in finding educational content.
        # Your task is to:
        # 1. Engage with the user to determine the topic they want to learn about.
        # 2. Convert the topic into a well-structured YouTube search query.
        # 3. Send the query to the learning tool for content retrieval.
        # 4. 
        # """


        # "You are an expert Lead Software Engineer Manager.\n"
        # "Your role is to speak to a user and understand what kind of code they need to "
        # "build.\n"
        # "Part of your task is therefore to gather requirements and clarifying ambiguity "
        # "by asking followup questions. Don't ask all the questions together as the user "
        # "has a low attention span, rather ask a question at the time.\n"
        # "Once the problem to solve is clear, you will call your tool for writing the "
        # "solution.\n"
        # "Remember, you are an expert in understanding requirements but you cannot code, "
        # "use your coding tool to generate a solution. Keep the test cases if any, they "
        # "are useful for the user."
    )

    messages_with_system = [{"type": "system", "content": system_message}] + state[
        "messages"
    ]
    # Forward the RunnableConfig object to ensure the agent is capable of streaming the response.
    response = llm.invoke(messages_with_system, config)
    return {"messages": response}


# 4. Create the workflow graph
workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("learning_crew", ToolNode(tools))
workflow.set_entry_point("agent")

# 5. Define graph edges
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("learning_crew", "agent")

# 6. Compile the workflow
agent = workflow.compile()
