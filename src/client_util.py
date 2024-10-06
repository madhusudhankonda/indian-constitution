from openai import AzureOpenAI, OpenAI
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

# Configuration
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ASSISTANT_ID = os.getenv('AZURE_OPENAI_ASSISTANT_ID')

OPENAI_ASSISTANT_ID = os.getenv('OPENAI_ASSISTANT_ID')
OPENAI_VECTOR_STORE_ID= os.getenv('OPENAI_VECTOR_STORE_ID')
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')


def get_azure_openai_client():
    if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT:
        logging.error("Azure OpenAI API Key or Endpoint not set")
        return None
    # OpenAI client initialization
    return AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version="2024-05-01-preview"
    )

def get_openai_client():
    if not OPENAI_API_KEY:
        logging.error("OpenAI API Key is not set")
        return None
    return OpenAI(api_key=OPENAI_API_KEY)
