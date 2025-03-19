from crewai import Agent, Task, Crew

from crewai.tools import BaseTool
from google.cloud import storage

from youtube_transcript_api import YouTubeTranscriptApi
import typing as t
import os
import requests

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
BUCKET_NAME = "bucket-agentic-era-hack"


class YoutubeCollectorTool(BaseTool):
    name: str ="Youtube Links Collector Tool"
    description: str = ("Find the youtube video related to a topic.")
    def _run(self, topic: str) -> list:
        videos = self.search_youtube(topic)
        videos_list = [video for video in videos if video['source'] == 'YouTube']
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
            try :
                video_id = video['link'].split('v=')[-1]
                
                ytt_api = YouTubeTranscriptApi()
                fetched_transcript = ytt_api.fetch(video_id, languages=['en'])
                raw_transcript = "\n".join([snippet.text for snippet in fetched_transcript.snippets])
                transcripts = transcripts+ raw_transcript + "\n"
            except :
                continue
        return transcripts


class StoreGCSTool(BaseTool):
    name: str = "Store GCS Tool"
    description: str = "Store a received content (test or course) in folder_name/document_title in GCS bucket"

    def _run(self, folder_name:str, document_title:str, content_to_store: t.Any) -> str: 
        self.upload_to_gcs(content_to_store, f"{folder_name}/{document_title}")

    def upload_to_gcs(self, source_text, destination_blob_name):
        """Uploads a file to a Google Cloud Storage bucket."""
        print('************************************ SToriiiiing', destination_blob_name)
        # Initialize a GCS client
        client = storage.Client()

        # Get the bucket
        bucket = client.bucket(BUCKET_NAME)

        # Create a blob (GCS object)
        blob = bucket.blob(destination_blob_name)

        # Upload the file
        blob.upload_from_string(source_text)

        print(f"File uploaded to gs://{BUCKET_NAME}/{destination_blob_name}")