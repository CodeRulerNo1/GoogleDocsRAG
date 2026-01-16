# Affordable Organics AI Assistant (RAG Application)

This is a Retrieval-Augmented Generation (RAG) AI application built with **Streamlit** and **LangChain**. It allows users to ingest documents (PDF, DOCX, TXT, or Google Docs), creates a searchable knowledge base using embeddings, and allows users to chat with the documents using an AI model.

The application is designed to be **model-agnostic** and cloud-ready, prioritizing **Google Gemini** for high performance and cost-effectiveness, with fallback options to OpenAI or local models (Ollama).

## Features

*   **Multi-Source Ingestion:** Support for local files (PDF, DOCX, TXT) and public Google Doc URLs.
*   **Intelligent Retrieval:** Uses vector embeddings (ChromaDB) to find the most relevant document sections.
*   **Conversational AI:** Maintains chat history and context for natural interactions.
*   **Smart Model Selection:** 
    *   **Primary:** Google Gemini (Cloud) - Fast, powerful, and cost-effective.
    *   **Secondary:** OpenAI (Cloud) - Industry standard fallback.
    *   **Fallback:** Ollama (Local) - Runs completely offline if no cloud keys are provided.
*   **Citations:** providing inline sources for every claim (e.g., `[Source 1]`).

## Prerequisites

*   **Python 3.10+**
*   **Git** installed.
*   (Optional) **Google API Key** for Gemini (Recommended).
*   (Optional) **OpenAI API Key**.
*   (Optional) **Ollama** installed locally for offline use.

## Installation

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-folder>
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    Create a `.env` file in the root directory and add your API keys:
    ```env
    GOOGLE_API_KEY=your_google_api_key_here
    OPENAI_API_KEY=your_openai_api_key_here  # Optional
    ```
    *If no keys are provided, the app will attempt to use a local Ollama instance.*

## Usage

Run the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

1.  **Ingest Documents:** Use the sidebar to upload files or paste a Google Doc URL.
2.  **Chat:** Ask questions in the chat interface. The AI will answer based *only* on the provided documents.

## Deployment Guide

### Option 1: Streamlit Community Cloud (Recommended)

Streamlit Community Cloud is the easiest way to deploy this application for free.

1.  **Push to GitHub:**
    *   Initialize a git repo: `git init`
    *   Add files: `git add .`
    *   Commit: `git commit -m "Initial commit"`
    *   Create a repository on GitHub.
    *   Link remote: `git remote add origin <your-github-repo-url>`
    *   Push: `git push -u origin master` (or `main`)

2.  **Deploy:**
    *   Go to [share.streamlit.io](https://share.streamlit.io/).
    *   Sign in with GitHub.
    *   Click **"New app"**.
    *   Select your repository, branch, and main file path (`app.py`).
    *   Click **"Deploy!"**.

3.  **Configure Secrets (Crucial):**
    *   Once deployed, go to your app's **Settings** -> **Secrets**.
    *   Add your API keys in TOML format:
        ```toml
        GOOGLE_API_KEY = "your_key_here"
        OPENAI_API_KEY = "your_key_here"
        ```
    *   *Note: Local Ollama will NOT work on Streamlit Cloud. You must provide a Google or OpenAI key.*

### Option 2: Docker / VPS

If you prefer to host it yourself (e.g., DigitalOcean, AWS):

1.  **Build Docker Image:**
    (Create a `Dockerfile` first - standard Python generic setup)
    ```bash
    docker build -t affordable-organics .
    ```
2.  **Run Container:**
    ```bash
    docker run -p 8501:8501 -e GOOGLE_API_KEY=your_key affordable-organics
    ```

## Troubleshooting

*   **Rate Limits:** If you see "Resource Exhausted" errors, the app handles this with automatic backoff, but you may need to wait or upgrade your API tier.
*   **Model Not Found:** Ensure your API key has access to the models specified in `chat_model.py` (currently `gemini-flash-latest`).