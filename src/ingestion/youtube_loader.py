import sys
from src.logger import logging
from src.exception import MyException
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

class YoutubeLoader:
    def load(self, video_id: str) -> str:
        try:
            logging.info(f"Fetching transcript for video ID: {video_id}")
            transcripts = YouTubeTranscriptApi().list(video_id)
            try:
                transcript = transcripts.find_transcript(['en'])
                logging.info("English transcript found")
            except:
                logging.warning("English transcript not found, trying other languages")
                transcript = transcripts.find_generated_transcript(['bn', 'hi', 'en'])
                transcript = transcript.translate('en')
                logging.info("Transcript translated to English")
            data = transcript.fetch()
            logging.info("Transcript fetched successfully")
            return " ".join(chunk["text"] for chunk in data)
        except TranscriptsDisabled:
            raise MyException("No captions available for this video.", sys)
        except Exception as e:
            raise MyException(e, sys)