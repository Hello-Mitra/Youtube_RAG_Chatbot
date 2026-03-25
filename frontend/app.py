import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import streamlit as st
from src.logger import logging

st.title("🎥 YouTube RAG Chatbot")
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
                    "http://localhost:5000/api/chat",
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
                st.error(f"Something went wrong: {response.json().get('detail', 'Unknown error')}")

        except requests.exceptions.Timeout:
            logging.error("Request timed out")
            st.error("⏰ Request timed out. The video may be too long. Please try again.")
        except requests.exceptions.ConnectionError:
            logging.error("Could not connect to backend")
            st.error("🔌 Could not connect to backend. Make sure the backend is running.")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            st.error(f"Unexpected error occurred: {str(e)}")