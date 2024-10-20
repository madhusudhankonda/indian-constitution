import streamlit as st
import os
import logging
from client_util import get_azure_openai_client
from client_util import AZURE_OPENAI_ASSISTANT_ID
from dotenv import load_dotenv
from common_settings import set_page_container_style, hide_streamlit_header_footer
import base64
load_dotenv()

# Set up logging for debugging
logging.basicConfig(level=logging.ERROR)

st.set_page_config(
    page_title="Indian Constitution", 
    page_icon=":books:",
    layout="wide",
    initial_sidebar_state="expanded")
# Function to set background from a local file

def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Encode the background and sidebar images
bg_img = get_img_as_base64("src\images\BG.png")  # Replace with your local background image file
#sidebar_img = get_img_as_base64("sidebar.jpg")  # Replace with your local sidebar image file

# Define the CSS for background images
page_bg_img = f"""
<style>

[data-testid="stAppViewContainer"] > .main {{
background-image: url("data:image/png;base64,{bg_img}");
background-size: cover;
background-position: top left;
background-repeat: no-repeat;
background-attachment: local;
}}

    [data-testid="stChatMessage"].st-emotion-cache-4oy321.eeusbqq4{{
        background: white;
        border: 1px solid black;
    }}
    [data-testid="stChatMessage"].st-emotion-cache-1c7y2kd.eeusbqq4{{
        background: white;
        border: 1px solid black;
    }}
    [data-testid="stBottom"] > div {{
        background: transparent;
    }}

    
[data-testid="stChatInput"] {{
         background: white;
         border: 1px solid black;
        }}
[data-testid="stSidebar"] {{
background: white;
}}

[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
right: 2rem;
}}


[data-testid="stButton"]{{

    color: #0A2081;
    

}}

</style>
"""

# Inject the CSS into the app
st.markdown(page_bg_img, unsafe_allow_html=True)


set_page_container_style(
        max_width = 1100, max_width_100_percent = True,
        padding_top = 0, padding_right = 10, padding_left = 5, padding_bottom = 5
)

st.markdown(hide_streamlit_header_footer(), unsafe_allow_html=True)
col1, col2 = st.columns([90, 10])

with col2:
    reset_button = st.button("Reset", key="reset_button", help="Click to reset the chat")

# Reset the chat if the reset button is clicked
if reset_button:
    st.session_state.messages = []
with col1:
    st.markdown(
        f'''
        <div style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{get_img_as_base64('src/images/3.png')}" style="width: 70px; height: 70px; margin-right: 10px;">
            <p style="color:#0A2081;font-size:30px;font-weight:bold;margin-top:0px;margin-bottom:0px;">Indian Constitution & Amendment Acts AI Chatbot</p>
        </div>
        ''',
        unsafe_allow_html=True
    )
    st.markdown(f'<p style="color:grey;font-size:16px;text-align:center;text-centre:left">{"An AI assistant for querying, interpreting and understanding the Indian Constitution and Amendment Acts"}', unsafe_allow_html=True)

def about():
    st.sidebar.markdown('---')
    st.sidebar.info('''
    ### Indian Constitution 
    #### by https://chocolateminds.com

    Updated: 09 October 2024''')

# Create a two-column layout: 70% for the chat and 30% for model tweaking
col1, col2 = st.columns([4, 1])

LANGUAGE = "English"

# ---- SIDEBAR START -------

st.sidebar.image("src/images/2.png", width=250)
st.sidebar.markdown("<h3 style='color: #0A2081;'>Choose the output language:</h3>", unsafe_allow_html=True)
with st.sidebar:
    LANGUAGE = st.selectbox("options", ["English", "Hindi", "Telugu","Tamil", "Marathi", "Gujarathi", "Kannada","Malayalam"],label_visibility = "collapsed")



constitution_faq = [
    "What are the fundamental rights provided by the Indian Constitution?",
    "What is the Preamble to the Indian Constitution, and what does it signify?",
    "How does the Indian Constitution define the territories of India?",
    "What provisions does the Indian Constitution make regarding citizenship?",
    "What are the Directive Principles of State Policy in the Indian Constitution?",
    "What is the amendment process in the Indian Constitution?",
    "How is the President of India elected, and what are the President's powers and duties?",
    "What are the emergency provisions stated in the Indian Constitution?",
    "What is the significance of the Ninth Schedule in the Indian Constitution?",
    "How are the states formed or reorganized under the Indian Constitution?"
]

amendment_faq = [
    "What were the key changes introduced by the 42nd Amendment Act of 1976, and why is it often referred to as the \"Mini-Constitution\"?",
    "How did the 44th Amendment Act of 1978 alter the provisions related to the declaration of Emergency in India?",
    "What was the significance of the 73rd Amendment Act of 1992 in strengthening local governance in India?",
    "How did the 101st Amendment Act of 2016 transform India's taxation system with the introduction of the Goods and Services Tax (GST)?",
    "What were the objectives and outcomes of the 24th Amendment Act of 1971 in response to the Golak Nath case?",
    "How did the 86th Amendment Act of 2002 impact the right to education in India?",
    "What changes were brought about by the 52nd Amendment Act of 1985, commonly known as the Anti-Defection Law?",
    "How did the 61st Amendment Act of 1988 lower the voting age in India, and what was its significance?",
    "What were the key provisions of the 97th Amendment Act of 2011 related to cooperative societies?",
    "How did the 54th Amendment Act of 1986 revise the salaries of the President, Vice-President, and Governors, and what was the rationale behind it?"
]

def display_faq(faq_list, prefix):
    for question in faq_list:
        if st.button(question, key=f"{prefix}_{question}"):
            st.session_state.faq_question = question
st.sidebar.markdown("<h3 style='color: #0A2081;'>FAQ on Indian Constitution</h3>", unsafe_allow_html=True)

with st.sidebar:
    with st.expander("FAQ on Indian Constitution", expanded=False):
        display_faq(constitution_faq, "const")

st.sidebar.markdown("<h3 style='color: #0A2081;'>FAQ on Amendment Acts</h3>", unsafe_allow_html=True)

with st.sidebar:
    with st.expander("FAQ on Amendment Acts", expanded=False):
        display_faq(amendment_faq, "amend")

st.sidebar.markdown("<h3 style='color: #0A2081;'>How to use?</h3>", unsafe_allow_html=True)

with st.sidebar:
    with st.container(border=1):
        st.markdown(
            """
            Input the question in the chat box in the main page, towards the bottom of the page. 
            
            After writing the query, click the send button and await for reply from the virtual assistant.
            """
        )

st.sidebar.markdown("<h3 style='color: #0A2081;'>About</h3>", unsafe_allow_html=True)

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
if "faq_question" not in st.session_state:
    st.session_state.faq_question = None

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
    # message_content.value += '\n\n**Citations:**\n' + '\n'.join(citations)
    return message_content.value

def generate_response(prompt):
    # Create a new chat thread for the conversation
    chat_thread = client.beta.threads.create()
    st.session_state.thread_id = chat_thread.id

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

   
    with st.spinner("Thinking.."):
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id, run_id=run.id
            )


        messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages if message.run_id == run.id and message.role == "assistant"
        ]

        for message in assistant_messages_for_run:
            logging.debug(f"Processing assistant message: {message}")
            full_response = process_citations(message=message)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            with st.chat_message("assistant", avatar="src/images/1.png"):
                st.markdown(full_response, unsafe_allow_html=True)

# Show existing messages if any...
with st.container():
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="src/images/1.png" if message["role"] == "assistant" else "src\images\Chat Avatar.png"):
            st.markdown(message["content"])

# Handle FAQ questions
if st.session_state.faq_question:
    st.session_state.messages.append({"role": "user", "content": st.session_state.faq_question})
    with st.chat_message("user", avatar="src\images\Chat Avatar.png"):
        st.markdown(f"<p style='color: #0A2081;'>{st.session_state.faq_question}</p>", unsafe_allow_html=True)
    generate_response(st.session_state.faq_question)
    st.session_state.faq_question = None

# Handle user input
if prompt := st.chat_input("What do you want to ask me?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="src\images\Chat Avatar.png"):
        st.markdown(prompt)
    generate_response(prompt)



if __name__ == '__main__':
    about()