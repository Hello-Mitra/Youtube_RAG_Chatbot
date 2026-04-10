import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import streamlit as st
from src.logger import logging

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")

st.title("🎥 InsightStream — Extract insights from video content")
st.markdown("Ask any question about a YouTube video!")

video_id = st.text_input("Enter YouTube Video ID:", placeholder="e.g. Y0SbCp4fUvA")
question = st.text_input("Ask a question:", placeholder="e.g. Can you summarize this video?")

if st.button("Ask"):
    if not video_id or not question:
        st.warning("Please enter both a Video ID and a question.")
    else:
        try:
            logging.info(f"Sending request - video_id: {video_id}, question: {question}")

            with st.spinner("⏳ Fetching transcript and processing... this may take 1-3 minutes for the first question..."):
                response = requests.post(
                    f"{BACKEND_URL}/api/chat",
                    json={"question": question, "video_id": video_id},
                    timeout=300
                )

            if response.status_code == 200:
                logging.info("Response received successfully")
                st.success("✅ Answer:")
                st.write(response.json()["answer"])
                st.info("💡 Tip: Follow-up questions on the same video will be much faster!")
            else:
                logging.error(f"Backend returned error: {response.status_code}")
                # ✅ Safe JSON parsing — handles empty or non-JSON responses
                try:
                    detail = response.json().get("detail", "Unknown error")
                except Exception:
                    detail = response.text or f"HTTP {response.status_code} error"
                st.error(f"Something went wrong: {detail}")

        except requests.exceptions.Timeout:
            logging.error("Request timed out")
            st.error("⏰ Request timed out. The video may be too long. Please try again.")
        except requests.exceptions.ConnectionError:
            logging.error("Could not connect to backend")
            st.error("🔌 Could not connect to backend. Make sure the backend is running.")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            # ✅ Show actual error message not just str(e) which causes JSONDecodeError confusion
            error_msg = str(e)
            if "Expecting value" in error_msg:
                st.error("❌ Backend returned an empty response. The request may have timed out or the video transcript could not be fetched.")
            elif "rate" in error_msg.lower() or "429" in error_msg:
                st.error("⏳ YouTube is rate limiting requests. Please wait a few minutes and try again.")
            elif "TranscriptsDisabled" in error_msg:
                st.error("❌ Transcripts are disabled for this video. Please try a different video.")
            elif "NoTranscriptFound" in error_msg:
                st.error("❌ No transcript found for this video. Please try a video with captions enabled.")
            else:
                st.error(f"❌ Unexpected error: {error_msg}")