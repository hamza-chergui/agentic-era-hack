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

from .crew.learning_crew import LearningCrew

LOCATION = "us-central1"
LLM = "gemini-2.0-flash-001"


@tool
def learning_tool(topic: str) -> str:
    """Use this tool to write an article about a topic."""
    inputs = {"topic": topic}
    return LearningCrew().crew().kickoff(inputs=inputs)


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
            Your tasks are to:
            1. Engage with the user to determine the topic they want to learn about.
            2. Send the query the learning tool
            3. Display a well written article, with a test
        """
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
