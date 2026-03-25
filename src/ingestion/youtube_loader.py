import sys
import time
import random
import os
from src.logger import logging
from src.exception import MyException
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from youtube_transcript_api.proxies import WebshareProxyConfig
from config.settings import settings
from entity.config_entity import YoutubeLoaderConfig
from entity.artifact_entity import YoutubeLoaderArtifact


class YoutubeLoader:
    def __init__(self, youtube_loader_config: YoutubeLoaderConfig):
        try:
            logging.info("Initializing YoutubeLoader")
            self.youtube_loader_config = youtube_loader_config
            logging.info("YoutubeLoader initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def _get_api_instance(self):
        try:
            if settings.webshare_proxy_username and settings.webshare_proxy_password:
                logging.info("Using Webshare proxy")
                return YouTubeTranscriptApi(
                    proxy_config=WebshareProxyConfig(
                        proxy_username=settings.webshare_proxy_username,
                        proxy_password=settings.webshare_proxy_password,
                    )
                )
            elif os.path.exists("cookies.txt"):
                logging.info("Using cookies.txt")
                return YouTubeTranscriptApi(cookie_path="cookies.txt")
            else:
                logging.warning("No proxy or cookies configured, trying direct request")
                return YouTubeTranscriptApi()
        except Exception as e:
            raise MyException(e, sys)

    def initiate_youtube_loader(self) -> YoutubeLoaderArtifact:
        video_id = self.youtube_loader_config.video_id
        retries = 10

        for attempt in range(retries):
            try:
                logging.info(f"Fetching transcript for video ID: {video_id} (Attempt {attempt + 1})")

                ytt_api = self._get_api_instance()
                transcripts = ytt_api.list(video_id)

                try:
                    transcript = transcripts.find_transcript(['en'])
                    logging.info("English transcript found")
                except:
                    logging.warning("English transcript not found, trying other languages")
                    transcript = transcripts.find_generated_transcript(['bn', 'hi', 'en'])
                    transcript = transcript.translate('en')
                    logging.info("Transcript translated to English")

                data = transcript.fetch()
                transcript_text = " ".join(chunk.text for chunk in data)

                logging.info(f"Transcript fetched successfully for video ID: {video_id}")

                youtube_loader_artifact = YoutubeLoaderArtifact(
                    transcript=transcript_text,
                    video_id=video_id
                )

                logging.info(f"YoutubeLoader artifact: {youtube_loader_artifact.video_id}, transcript length: {len(transcript_text)}")
                return youtube_loader_artifact

            except Exception as e:
                if "429" in str(e):
                    wait_time = (2 ** attempt) + random.uniform(1, 3)
                    logging.warning(f"Rate limited. Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)
                else:
                    raise MyException(e, sys)

        raise MyException("Failed after multiple retries due to rate limiting", sys)