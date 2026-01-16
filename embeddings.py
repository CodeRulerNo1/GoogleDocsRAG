import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Logic: Prioritize Google Gemini, then OpenAI, then fallback to Ollama.
if google_api_key:
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=google_api_key)
elif openai_api_key:
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_api_key)
else:
    embeddings = OllamaEmbeddings(model="llama3.2")