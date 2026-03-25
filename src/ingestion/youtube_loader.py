import sys
import time
import random
import os
from src.logger import logging
from src.exception import MyException
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from youtube_transcript_api.proxies import WebshareProxyConfig
from config.settings import settings

class YoutubeLoader:
    def _get_api_instance(self):
        """Try proxy first, fall back to cookies, then plain"""
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

    def load(self, video_id: str) -> str:
        retries = 10
        for attempt in range(retries):
            try:
                logging.info(f"Fetching transcript for video ID: {video_id} (Attempt {attempt+1})")

                ytt_api = self._get_api_instance()
                transcripts = ytt_api.list(video_id)

                try:
                    transcript = transcripts.find_transcript(['en'])
                except:
                    transcript = transcripts.find_generated_transcript(['bn', 'hi', 'en'])
                    transcript = transcript.translate('en')

                data = transcript.fetch()

                return " ".join(chunk.text for chunk in data)

            except Exception as e:
                if "429" in str(e):
                    wait_time = (2 ** attempt) + random.uniform(1, 3)
                    logging.warning(f"Rate limited. Retrying in {wait_time:.2f}s...")
                    time.sleep(wait_time)
                else:
                    raise MyException(e, sys)

        raise MyException("Failed after multiple retries due to rate limiting", sys)