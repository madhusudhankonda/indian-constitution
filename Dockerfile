# Build:
# docker build . -t ievd-chatbot-app
# Test:
# docker run --rm -p 8505:8505  -v ./.env:/app/.env ievd-chatbot-app

FROM python:3.11-slim

# Temporary until secrets are sorted

# Azure OpenAI secrets
ENV AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT} 
ENV AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
ENV AZURE_OPENAI_ASSISTANT_ID=${AZURE_OPENAI_ASSISTANT_ID}

# OpenAI secrets
ENV OPENAI_ASSISTANT_ID=${OPENAI_ASSISTANT_ID}
ENV OPENAI_VECTOR_STORE_ID=${OPENAI_VECTOR_STORE_ID}

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501"]
