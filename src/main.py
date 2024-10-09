import streamlit as st
import os
import logging
from client_util import get_azure_openai_client
from client_util import AZURE_OPENAI_ASSISTANT_ID
from dotenv import load_dotenv
from common_settings import set_page_container_style
load_dotenv()

# Set up logging for debugging
logging.basicConfig(level=logging.ERROR)

st.set_page_config(
    page_title="Indian Constitution", 
    page_icon=":books:",
    layout="wide",
    initial_sidebar_state="expanded")

set_page_container_style(
        max_width = 1100, max_width_100_percent = True,
        padding_top = 0, padding_right = 10, padding_left = 5, padding_bottom = 10
)
st.markdown(
    "<div style='background-color:#fc9d03;padding:5px;text-align:center;'>"
    "<h1 style='color:white;'>Indian Constitution Chatbot</h1>"
    "</div>",
    unsafe_allow_html=True
)
st.info(

    """
    **An intelligent AI chatbot for querying, studying, referring and understanding Indian Constitution, its articles, rights, and historical significance!**
    """)

def about():
    st.sidebar.markdown('---')
    st.sidebar.info('''
    ### Indian Constitution 
    #### by chocolateminds.com

    Updated: 09 October 2024''')
# Create a two-column layout: 70% for the chat and 30% for model tweaking
col1, col2, col3 = st.columns([1, 2, 1])

LANGUAGE = "English"

with col3: 
    LANGUAGE = st.selectbox("Choose the output language:", ["English", "Hindi", "Telugu","Tamil"])



# ---- SIDEBAR START -------

st.sidebar.image("src/images/indian-constitution-logo4.png", width=290)

st.sidebar.header("Frequently Asked Questions")

with st.sidebar:
    with st.expander("Frequently Asked Questions"):
        st.markdown(
            """
        1. What are the fundamental rights provided by the Indian Constitution?

        2. What is the Preamble to the Indian Constitution, and what does it signify?

        3. How does the Indian Constitution define the territories of India?

        4. What provisions does the Indian Constitution make regarding citizenship?

        5. What are the Directive Principles of State Policy in the Indian Constitution?

        6. What is the amendment process in the Indian Constitution?

        7. How is the President of India elected, and what are the President's powers and duties?

        8. What are the emergency provisions stated in the Indian Constitution?

        9. What is the significance of the Ninth Schedule in the Indian Constitution?

        10. How are the states formed or reorganized under the Indian Constitution?
        """
        )

st.sidebar.header("How to use?")

with st.sidebar:
    with st.container(border=1):
        st.markdown(
            """
            Input the question in the chat box in the main page, towards the bottom of the page. 
            
            After writing the query, click the send button and await for reply from the virtual assistant.
            """

        )

st.sidebar.header("About")

with st.sidebar:
    with st.container(border=1):
        st.markdown(
            "Welcome to Indian Constitution ChatBot, an AI-powered Virtual Assistant designed to help you understand, quiz, query Indian Constitution."
        )
        st.markdown("Created by [Chocolateminds](https://www.chocolateminds.com/).")
        
    

# ---- SIDEBAR END -------

# OpenAI client initialization with error handling

try:
    client = get_azure_openai_client()
    logging.debug("Client successfully initialized!")
except Exception as e:
    st.error(f"Error initializing client: {str(e)}")

if "openai_model" not in st.session_state:
    st.session_state.openai_model = "gpt-4o"
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show existing messages if any...
with st.container():
    for message in st.session_state.messages:
        with st.chat_message(message["role"],avatar="src/images/answer.png"):
            st.markdown(message["content"])

# -- PROCESS CITATIONS ---
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
            quote_text = getattr(file_citation, 'quote', None) or \
                            getattr(file_citation, 'text', None) or\
                            'Citation'
            citations.append(f'[{index + 1}] "{quote_text}" from {cited_file.filename}')
            logging.debug(f"Citation added: {quote_text} from {cited_file.filename}")

    # Add citations at the end of the message
    message_content.value += '\n\n**Citations:**\n' + '\n'.join(citations)
    return message_content.value

# -- CHAT START --

if prompt := st.chat_input("What do you want to ask me?"):
    
    # Create a new chat thread for the conversation
    chat_thread = client.beta.threads.create()
    st.session_state.thread_id = chat_thread.id

    # Add the user's message to the state and display it on the screen
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="src/images/question.png"):
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
        instructions=f"""
        Please answer the questions in {LANGUAGE} and  using only the knowledge provided in the uploaded Indian Constitution PDF files.

        - There is a file for each of the language in vector store - you must consult the respective file. 
        For example, if the LANGUAGE is telugu, you must retrieve answers from ic-telugu.pdf file a
        - Include direct quotes from the relevant sections of the document in your answer.
        - Ensure that the 'quote' field in the file_citation includes the exact text from the document.
        - Provide detailed answers in {LANGUAGE}, with citations at the end.
        - The citations should reference specific articles or sections, including the quoted text.
        """,
    )
    print(run)
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
            with st.chat_message("assistant", avatar="src/images/answer.png"):
                st.markdown(full_response, unsafe_allow_html=True)


if __name__ == '__main__':
    about()