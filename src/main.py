import streamlit as st
import os
import logging
from typing import List
import base64
from dotenv import load_dotenv
from common_settings import set_page_container_style, hide_streamlit_header_footer
from chroma_utils import ChromaDBClient
from openai import AzureOpenAI  

# Set up logging for debugging
logging.basicConfig(level=logging.ERROR)

# Load environment variables
load_dotenv()

MODEL = "gpt-4o"
TEMPERATURE=0.7,
MAX_TOKENS=500

# Initialize OpenAI
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
LANGUAGE=""

# Create prompt for OpenAI
system_prompt = f"""You are an expert on the Indian Constitution. Answer questions in {LANGUAGE} 
using only the following context. Include relevant citations from the context in your answer.

Context:
{{context}}

Citations format:
{{citations}}

Make sure the answers are eloborate and factually correct. 

Please format your response with citations at the end, referencing specific sections and page numbers.
"""
# Initialize ChromaDB client
chroma_client = ChromaDBClient(persist_directory="./chroma_db")

# Streamlit page configuration
st.set_page_config(
    page_title="Indian Constitution", 
    page_icon=":books:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to encode images as base64
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Load and apply background image
bg_img = get_img_as_base64("src/images/BG.png")
with open("styles.css") as f:
    css = f.read().replace("{bg_img}", bg_img)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Apply page container style
set_page_container_style(
    max_width=1100,
    max_width_100_percent=True,
    padding_top=0,
    padding_right=10,
    padding_left=5,
    padding_bottom=5
)

# Hide Streamlit header and footer
st.markdown(hide_streamlit_header_footer(), unsafe_allow_html=True)

# Create header layout
col1, col2 = st.columns([90, 10])

# Reset button
with col2:
    reset_button = st.button("Reset chat", key="reset_button", help="Click to reset the chat")

# Reset chat if button clicked
if reset_button:
    st.session_state.messages = []

# Header content
with col1:
    st.markdown(
        f'''
        <div style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{get_img_as_base64('src/images/3.png')}" 
                 style="width: 70px; height: 70px; margin-right: 10px;">
            <p style="color:#0A2081;font-size:30px;font-weight:bold;margin-top:0px;margin-bottom:0px;">
                Indian Constitution & Amendment Acts AI Chatbot
            </p>
        </div>
        ''',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<p style="color:grey;font-size:18px;text-align:center;text-centre:center">'
        f'{"An AI assistant for querying the Indian Constitution and Amendment Acts"}</p>',
        unsafe_allow_html=True
    )

# About function for sidebar
def about():
    st.sidebar.markdown('---')
    st.sidebar.info('''
    ### Indian Constitution 
    #### by https://chocolateminds.com

    Updated: 09 October 2024''')

# Create main layout
col1, col2 = st.columns([4, 1])

# Initialize session state
if "openai_model" not in st.session_state:
    st.session_state.openai_model = "gpt-4"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "faq_question" not in st.session_state:
    st.session_state.faq_question = None

# Sidebar content
st.sidebar.image("src/images/2.png", width=250)
st.sidebar.markdown("<h3 style='color: #0A2081;'>Choose the output language:</h3>", unsafe_allow_html=True)

# Language selection
with st.sidebar:
    LANGUAGE = st.selectbox(
        "options",
        ["English", "Hindi", "Telugu", "Tamil", "Marathi", "Gujarathi", "Kannada", "Malayalam"],
        label_visibility="collapsed"
    )

# FAQ lists
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
    "What were the key changes introduced by the 42nd Amendment Act of 1976?",
    "How did the 44th Amendment Act of 1978 alter the Emergency provisions?",
    "What was the significance of the 73rd Amendment Act of 1992?",
    "How did the 101st Amendment Act of 2016 implement GST?",
    "What were the objectives of the 24th Amendment Act of 1971?",
    "How did the 86th Amendment Act of 2002 impact education?",
    "What is the Anti-Defection Law (52nd Amendment Act of 1985)?",
    "How did the 61st Amendment Act of 1988 change voting rights?",
    "What were the key provisions of the 97th Amendment Act of 2011?",
    "What did the 54th Amendment Act of 1986 change about official salaries?"
]

# Function to display FAQ buttons
def display_faq(faq_list, prefix):
    for question in faq_list:
        if st.button(question, key=f"{prefix}_{question}"):
            st.session_state.faq_question = question

# Display FAQ sections in sidebar
st.sidebar.markdown("<h3 style='color: #0A2081;'>FAQ on Indian Constitution</h3>", unsafe_allow_html=True)
with st.sidebar:
    with st.expander("FAQ on Indian Constitution", expanded=False):
        display_faq(constitution_faq, "const")

st.sidebar.markdown("<h3 style='color: #0A2081;'>FAQ on Amendment Acts</h3>", unsafe_allow_html=True)
with st.sidebar:
    with st.expander("FAQ on Amendment Acts", expanded=False):
        display_faq(amendment_faq, "amend")

# How to use section
st.sidebar.markdown("<h3 style='color: #0A2081;'>How to use?</h3>", unsafe_allow_html=True)
with st.sidebar:
    with st.container(border=1):
        st.markdown(
            """
            Input the question in the chat box in the main page, towards the bottom of the page. 
            
            After writing the query, click the send button and await for reply from the virtual assistant.
            """
        )

# About section
st.sidebar.markdown("<h3 style='color: #0A2081;'>About</h3>", unsafe_allow_html=True)
with st.sidebar:
    with st.container(border=1):
        st.markdown(
            "Welcome to Indian Constitution ChatBot, an AI-powered Virtual Assistant designed to help you "
            "understand, quiz, query Indian Constitution."
        )
        st.markdown("Created by [Chocolateminds](https://www.chocolateminds.com/).")

def generate_response(prompt: str, language: str) -> str:
    """Generate response using ChromaDB and OpenAI"""
    try:
        # Query ChromaDB for relevant context
        collection_name = f"constitution_{language.lower()}"
        results = chroma_client.query_collection(
            collection_name=collection_name,
            query_text=prompt
        )

        # Prepare context from retrieved documents
        # context = "\n".join([doc for doc in results['documents'][0]])
        # citations = [meta for meta in results['metadatas'][0]]
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        # Get response from OpenAI using the new client
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS
        )

        return response.choices[0].message.content

    except Exception as e:
        logging.error(f"Error generating response: {str(e)}")
        return f"An error occurred: {str(e)}"

# Display existing chat messages
with st.container():
    for message in st.session_state.messages:
        with st.chat_message(
            message["role"],
            avatar="src/images/1.png" if message["role"] == "assistant" else "src/images/chat_avatar.png"
        ):
            st.markdown(message["content"])

# Handle FAQ questions
if st.session_state.faq_question:
    st.session_state.messages.append({"role": "user", "content": st.session_state.faq_question})
    with st.chat_message("user", avatar="src/images/chat_avatar.png"):
        st.markdown(f"<p style='color: #0A2081;'>{st.session_state.faq_question}</p>", unsafe_allow_html=True)
    
    with st.spinner("Generating response..."):  # Spinner starts here
        response = generate_response(st.session_state.faq_question, LANGUAGE)
    # Spinner ends here

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant", avatar="src/images/1.png"):
        st.markdown(response, unsafe_allow_html=True)
    
    st.session_state.faq_question = None

# Handle user input
if prompt := st.chat_input("What do you want to ask me?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="src/images/chat_avatar.png"):
        st.markdown(prompt)
    
    with st.spinner("Generating response..."):  # Spinner starts here
        response = generate_response(prompt, LANGUAGE)
    # Spinner ends here

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant", avatar="src/images/1.png"):
        st.markdown(response, unsafe_allow_html=True)

# Run about function if this is the main script
if __name__ == '__main__':
    about()