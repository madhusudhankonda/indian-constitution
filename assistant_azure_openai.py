import time
from openai import AzureOpenAI
import streamlit as st
import logging

import os

from dotenv import load_dotenv

load_dotenv()

# Access your secrets
azure_api_key = os.getenv('AZURE_API_KEY')

# Set up logging for debugging
logging.basicConfig(level=logging.ERROR)

# Configuration
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ASSISTANT_ID = os.getenv('AZURE_OPENAI_ASSISTANT_ID')

st.set_page_config(page_title="Indian Constitution", page_icon=":books:")

# OpenAI client initialization
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-05-01-preview"
    # api_version="2024-02-15-preview"
)
# api_version="2024-05-01-preview"


def process_citations(message):
    """Process citations from the message and append footnotes with citations."""
    message_content = message.content[0].text
    annotations = message_content.annotations
    citations = []

    logging.debug(f"Processing message: {message_content.value}")

    # Iterate over annotations and add citations
    for index, annotation in enumerate(annotations):
        logging.debug(f"Annotation: {annotation}")

        # Replace the citation marker with footnote
        message_content.value = message_content.value.replace(annotation.text, f' [{index + 1}]')

        # Gather citation details
        if (file_citation := getattr(annotation, 'file_citation', None)):
            cited_file = client.files.retrieve(file_citation.file_id)
            quote_text = file_citation.quote if file_citation.quote else "--"
            citations.append(f'[{index + 1}] "{quote_text}" from {cited_file.filename}')
            logging.debug(f"Citation added: {quote_text} from {cited_file.filename}")

    # Add citations at the end of the message
    message_content.value += '\n\n**Citations:**\n' + '\n'.join(citations)
    return message_content.value

if "openai_model" not in st.session_state:
    st.session_state.openai_model = "gpt-4o"
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show existing messages if any...
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input for the user
if prompt := st.chat_input("Ask me!"):
    
    # Create a new chat thread for the conversation
    chat_thread = client.beta.threads.create()
    st.session_state.thread_id = chat_thread.id

    # Add the user's message to the state and display it on the screen
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Send the user's message to the thread
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id, 
        role="user", 
        content=prompt
    )

    # Create a run with specific instructions to provide detailed answers with citations
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=AZURE_OPENAI_ASSISTANT_ID,
        instructions="""
        Please answer the questions using only the knowledge provided in the uploaded Indian Constitution PDF file.

        - Include direct quotes from the relevant sections of the document in your answer.
        - Ensure that the 'quote' field in the file_citation includes the exact text from the document.
        - Provide detailed answers in English, with citations at the end.
        - The citations should reference specific articles or sections, including the quoted text.
        """,
    )

    # Show a spinner while the assistant is generating the response
    with st.spinner("Generating response..."):
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id, run_id=run.id
            )

        # Retrieve the messages added by the assistant
        messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages if message.run_id == run.id and message.role == "assistant"
        ]

        for message in assistant_messages_for_run:
            logging.debug(f"Processing assistant message: {message}")
            full_response = process_citations(message=message)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            with st.chat_message("assistant"):
                st.markdown(full_response, unsafe_allow_html=True)
