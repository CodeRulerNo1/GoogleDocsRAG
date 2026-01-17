import streamlit as st
# --- SQLite Fix for Streamlit Cloud / ChromaDB ---
import sys
import os
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass
# -------------------------------------------------

import datetime
import time
from load_documents import load_docs
from split_doc import split_docs
from storing_doc import store_docs
from RAG_agent import retrieve_context
from chromaDB import vector_store
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from chat_model import model
from google_doc_loader import load_google_doc

# Page Configuration
st.set_page_config(page_title="Affordable Organics AI Assistant", layout="wide")

# Title and Description
st.title("AI Assistant")
st.markdown("Your autonomous agent for knowledge retrieval and document analysis.")

def process_and_store(docs):
    """Processes documents: splits and stores them in the vector store."""
    if not docs:
        return 0
    
    splits = split_docs(docs)
    ids = store_docs(splits)
    return len(ids)

def clear_vector_store():
    """Clears all documents from the vector store."""
    try:
        existing_data = vector_store.get()
        if existing_data and "ids" in existing_data and existing_data["ids"]:
            vector_store.delete(existing_data["ids"])
            return True
    except Exception as e:
        st.error(f"Error clearing vector store: {e}")
    return False

def safe_invoke_model(messages, max_retries=3):
    """Invokes the model with rate limit handling."""
    retries = 0
    while retries < max_retries:
        try:
            return model.invoke(messages)
        except Exception as e:
            error_str = str(e).lower()
            if "rate limit" in error_str or "quota" in error_str or "429" in error_str:
                wait_time = (2 ** retries) * 1  # Exponential backoff
                time.sleep(wait_time)
                retries += 1
            else:
                raise e
    raise Exception("Rate limit exceeded after multiple retries.")

def rephrase_query(query, history):
    """Rephrases the query based on conversation history for better retrieval."""
    if not history:
        return query
    
    history_text = "\n".join([f"{('User' if isinstance(m, HumanMessage) else 'AI')}: {m.content}" for m in history[-10:]])
    
    rephrase_prompt = f"""Given the following conversation history and a follow-up question, rephrase the follow-up question to be a standalone question that can be used for document retrieval. 
    
    History:
    {history_text}
    
    Follow-up Question: {query}
    Standalone Question:"""
    
    try:
        response = safe_invoke_model([HumanMessage(content=rephrase_prompt)])
        return response.content.strip()
    except:
        return query

def check_ambiguity(query, history):
    """
    Checks if the query is ambiguous and requires clarification.
    Returns (is_ambiguous, clarification_message)
    """
    # Simple check for very short queries
    if len(query.split()) < 3 and not history:
        return True, "Could you please provide more details or context for your question?"

    check_prompt = f"""Analyze the following user query. Is it ambiguous or unclear such that you cannot reasonably answer it even with access to relevant documents?
    
    Query: {query}
    
    If it is ambiguous, respond with "YES: [Clarifying Question]".
    If it is clear, respond with "NO".
    
    Examples:
    Query: \"tell me about it\" (without history) -> YES: What specific topic are you referring to?
    Query: \"What is the price of organic apples?\" -> NO
    """
    
    try:
        response = safe_invoke_model([HumanMessage(content=check_prompt)])
        content = response.content.strip()
        if content.startswith("YES:"):
            return True, content.replace("YES:", "").strip()
        return False, None
    except:
        return False, None

# Sidebar for Document Management
with st.sidebar:
    st.header("Document Management")
    
    # Google Doc Ingestion
    st.subheader("Ingest Google Doc")
    gdoc_url = st.text_input("Public Google Doc URL", placeholder="https://docs.google.com/document/d/...")
    if st.button("Ingest Google Doc"):
        if gdoc_url:
            with st.spinner("Fetching and processing Google Doc..."):
                docs, error = load_google_doc(gdoc_url)
                if error:
                    st.error(error)
                else:
                    num_chunks = process_and_store(docs)
                    st.success(f"Successfully ingested Google Doc! ({num_chunks} chunks)")
        else:
            st.warning("Please enter a URL first.")

    st.divider()    
    
    # Local File Upload
    st.subheader("Upload Local Files")
    uploaded_files = st.file_uploader(
        "Upload Documents (PDF/DOCX/TXT)", 
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )
    
    if st.button("Process Uploaded Files"):
        if uploaded_files:
            upload_dir = "uploaded_documents"
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            new_docs = []
            for uploaded_file in uploaded_files:
                file_path = os.path.join(upload_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            with st.spinner("Processing files..."):
                # We reuse the existing load_docs which reads from uploaded_documents
                docs = load_docs(upload_dir)
                num_chunks = process_and_store(docs)
                st.success(f"Processed {len(uploaded_files)} files! ({num_chunks} chunks added)")
        else:
            st.warning("No files uploaded.")

    st.divider()    
    
    if st.button("Clear Knowledge Base"):
        if clear_vector_store():
            st.success("Knowledge base cleared.")
        else:
            st.info("Knowledge base is already empty or could not be cleared.")

    st.markdown("### Current Files")
    if os.path.exists("uploaded_documents"):
        files = os.listdir("uploaded_documents")
        if files:
            for f in files:
                st.text(f"📄 {f}")
        else:
            st.text("No local documents found.")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(message.content)

# User Input
if prompt := st.chat_input("Ask a question about the ingested documents..."):
    # Add user message to state
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        with st.spinner("Thinking..."):
            try:
                # 0. Check Ambiguity (if no recent history, or explicitly ambiguous)
                # Only check if history is empty to avoid interrupting conversational flow
                is_ambiguous = False
                clarification = None
                
                if not st.session_state.messages[:-1]: 
                    is_ambiguous, clarification = check_ambiguity(prompt, st.session_state.messages[:-1])

                if is_ambiguous:
                    message_placeholder.markdown(clarification)
                    st.session_state.messages.append(AIMessage(content=clarification))
                else:
                    # 1. Rephrase query if there's history
                    standalone_query = rephrase_query(prompt, st.session_state.messages[:-1])
                    
                    # 2. Retrieve Context
                    # Using top-3 as per requirement
                    retrieved_docs = vector_store.similarity_search(standalone_query, k=3)
                    
                    if not retrieved_docs:
                        answer = "This info isn't in the document. Please ingest a document first or ask something else."
                        message_placeholder.markdown(answer)
                        st.session_state.messages.append(AIMessage(content=answer))
                    else:
                        context_elements = []
                        sources_info = []
                        for i, doc in enumerate(retrieved_docs):
                            source = os.path.basename(doc.metadata.get('source', 'Unknown'))
                            context_elements.append(f"[Source {i+1}]: {source}\nContent: {doc.page_content}")
                            sources_info.append(f"Source {i+1}: {source}")
                        
                        context_str = "\n\n".join(context_elements)
                        
                        system_prompt = f"""You are a helpful AI Assistant. Answer the user's question based ONLY on the provided Context. 
                        
                        Context:
                        {context_str}
                        
                        Instructions:
                        1. Provide accurate, context-aware answers.
                        2. ALWAYS include inline citations. Use the format [Source X] (e.g., [Source 1]). 
                           If the text mentions a specific section (e.g., "Section 2.3"), include that as well (e.g., [Source 1, Section 2.3]).
                        3. If the answer is not in the context, say "This info isn't in the document."
                        4. Maintain a professional and concise tone.
                        """
                        
                        # Prepare messages with history (up to 5 prior exchanges)
                        history_msgs = st.session_state.messages[:-1]
                        chat_history = history_msgs[-10:]
                        
                        messages = [SystemMessage(content=system_prompt)]
                        messages.extend(chat_history)
                        messages.append(HumanMessage(content=prompt))
                        
                        # 3. Streaming Response
                        full_response = ""
                        # Wrap streaming in a try block for rate limits, though stream() might behave differently
                        try:
                            for chunk in model.stream(messages):
                                full_response += chunk.content
                                message_placeholder.markdown(full_response + "▌")
                        except Exception as e:
                            if "rate limit" in str(e).lower() or "429" in str(e):
                                message_placeholder.error("Rate limit exceeded. Please try again in a moment.")
                                full_response = "Rate limit exceeded. Please try again in a moment."
                            else:
                                raise e
                        
                        message_placeholder.markdown(full_response)
                        
                        # Add to state
                        st.session_state.messages.append(AIMessage(content=full_response))
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
