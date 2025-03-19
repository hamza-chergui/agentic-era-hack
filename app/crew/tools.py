from crewai import Agent, Task, Crew

from crewai.tools import BaseTool

from youtube_transcript_api import YouTubeTranscriptApi

import os
import requests

SERPER_API_KEY = os.getenv("SERPER_API_KEY")


class YoutubeCollectorTool(BaseTool):
    name: str ="Youtube Links Collector Tool"
    description: str = ("Find the youtube video related to a topic.")
    def _run(self, topic: str) -> list:
        videos = self.search_youtube(topic)
        videos_list = [video for video in videos if video['source'] == 'YouTube'][:5]  # Filtrer avant la boucle
        return videos_list

    def search_youtube(self,query):
        url = "https://google.serper.dev/videos"
        headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
        payload = {"q": query}

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            results = response.json()
            return results.get("videos", [])
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return []

class TranscriptsSearchTool(BaseTool):
    name: str = "Transcripts Search Tool"
    description: str = "Search for transcripts of a youtube video."

    def _run(self, videos_list: list) -> str:
        transcripts = ""
        for video in videos_list:
            video_id = video['link'].split('v=')[-1]
            
            ytt_api = YouTubeTranscriptApi()
            fetched_transcript = ytt_api.fetch(video_id, languages=['en'])
            raw_transcript = "\n".join([snippet.text for snippet in fetched_transcript.snippets])
            transcripts = transcripts+ raw_transcript + "\n"
        return transcripts
