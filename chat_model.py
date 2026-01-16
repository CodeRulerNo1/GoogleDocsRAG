import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Logic: Prioritize Google Gemini, then OpenAI, then fallback to Ollama.
if google_api_key:
    # Using Gemini Flash Latest
    model = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=google_api_key)
elif openai_api_key:
    # Using GPT-4o-mini
    model = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key)
else:
    # Fallback to Ollama
    print("Warning: No Cloud API key found. Falling back to local Ollama (llama3.2).")
    model = ChatOllama(model="llama3.2")