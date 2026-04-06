import requests
import sys
import time
import random
import os
from src.logger import logging
from src.exception import MyException
from youtube_transcript_api import YouTubeTranscriptApi
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

    def _get_api_instance(self, use_proxy: bool = True):
        try:
            has_proxy = bool(settings.webshare_proxy_username and settings.webshare_proxy_password)
            has_cookies = os.path.exists("cookies.txt")

            if has_proxy and use_proxy:
                logging.info("Using Webshare proxy")
                return YouTubeTranscriptApi(
                    proxy_config=WebshareProxyConfig(
                        proxy_username=settings.webshare_proxy_username,
                        proxy_password=settings.webshare_proxy_password,
                    )
                )
            elif has_cookies:
                logging.info("Using cookies.txt")
                from http.cookiejar import MozillaCookieJar
                session = requests.Session()
                jar = MozillaCookieJar("cookies.txt")
                jar.load(ignore_discard=True, ignore_expires=True)
                session.cookies = jar
                return YouTubeTranscriptApi(http_client=session)
            else:
                logging.warning("No proxy or cookies — direct request")
                return YouTubeTranscriptApi()

        except Exception as e:
            raise MyException(e, sys)

    def initiate_youtube_loader(self) -> YoutubeLoaderArtifact:
        video_id = self.youtube_loader_config.video_id
        retries = 3

        for attempt in range(retries):
            try:
                use_proxy = (attempt == 0)  # first attempt uses proxy, rest use cookies

                logging.info(f"Fetching transcript for video ID: {video_id} (Attempt {attempt + 1})")

                if attempt > 0:
                    logging.info("Proxy failed — retrying with cookies instead")

                ytt_api = self._get_api_instance(use_proxy=use_proxy)  # ← only ONE call ✅
                transcripts = ytt_api.list(video_id)

                data = None

                # Step 1 — try English directly
                try:
                    transcript = transcripts.find_transcript(['en'])
                    data = transcript.fetch()
                    logging.info("English transcript found and fetched")

                except Exception:
                    logging.warning("English transcript not found, trying other languages")

                    # Step 2 — try to find any transcript and translate to English
                    try:
                        transcript = transcripts.find_generated_transcript([
                            'hi', 'bn', 'te', 'ta', 'mr', 'gu', 'kn',
                            'ml', 'or', 'as', 'pa', 'ur', 'ne', 'si'
                        ])
                        translated = transcript.translate('en')
                        data = translated.fetch()
                        logging.info(f"Transcript translated to English from {transcript.language_code}")

                    except Exception:
                        logging.warning("Translation failed — using transcript in original language")

                        all_transcripts = list(transcripts)
                        if not all_transcripts:
                            raise ValueError("No transcripts available for this video")
                        data = all_transcripts[0].fetch()
                        logging.info(f"Using original language: {all_transcripts[0].language_code}")

                transcript_text = " ".join(chunk.text for chunk in data)
                logging.info(f"Transcript fetched — video_id={video_id}, length={len(transcript_text)}")

                return YoutubeLoaderArtifact(
                    transcript=transcript_text,
                    video_id=video_id
                )

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Too Many Requests" in error_str:
                    wait_time = (2 ** attempt) + random.uniform(2, 5)
                    logging.warning(f"Rate limited. Waiting {wait_time:.1f}s... next attempt will use cookies")
                    time.sleep(wait_time)
                else:
                    raise MyException(e, sys)

        raise MyException(
            "YouTube is rate limiting requests. Please try again in a few minutes.",
            sys
        )