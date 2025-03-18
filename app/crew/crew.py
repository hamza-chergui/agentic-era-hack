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

# mypy: disable-error-code="attr-defined"
from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from .tools import YoutubeCollectorTool, TranscriptsSearchTool


youtube_collector_tool = YoutubeCollectorTool()
transcript_tool = TranscriptsSearchTool()

@CrewBase
class LeaningCrew:
    """Leaning crew"""

    agents_config: dict[str, Any]
    tasks_config: dict[str, Any]

    llm = "vertex_ai/gemini-2.0-flash-001"

    # @agent
    # def writer_agent(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config.get("writer_agent"),
    #         allow_delegation=True,
    #         verbose=True,
    #         llm=self.llm,
    #     )

    # @task
    # def write(self) -> Task:
    #     return Task(
    #         config=self.tasks_config.get("write"),
    #         agent=self.writer_agent(),
    #     )

    @agent
    def collector_agent(self) -> Agent:
        return Agent(
            config=self.agents_config.get("collector_agent"),
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
        )

    @agent
    def teacher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config.get("teacher_agent"),
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
        )

    @task
    def collect_youtube_videos(self) -> Task:
        return Task(
            config=self.tasks_config.get("collect_youtube_videos"),
            agent=self.collector_agent(),
            tools=[youtube_collector_tool]
        )
    @task
    def make_courses(self) -> Task:
        return Task(
            config=self.tasks_config.get("make_courses"),
            agent=self.teacher_agent(),
            tools=[transcript_tool]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Dev Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
