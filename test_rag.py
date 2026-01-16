from RAG_agent import retrieve_context
from chat_model import model
from langchain_core.messages import HumanMessage
import os

def test_rag():
    query = "What is the expected tech stack for the AI application?"
    print(f"Query: {query}")
    
    # 1. Retrieve
    # Calling the underlying function directly to get the tuple (content, artifact)
    result = retrieve_context.func(query)
    print(f"Result type: {type(result)}")
    
    if isinstance(result, tuple):
        serialized, raw_docs = result
        for i, doc in enumerate(raw_docs):
            print(f"--- Chunk {i+1} ---")
            print(doc.page_content)
    else:
        serialized = str(result)
        raw_docs = []
    
    print(f"Retrieved {len(raw_docs)} documents.")
    
    # 2. Construct Prompt
    context_elements = []
    for i, doc in enumerate(raw_docs):
        source_name = os.path.basename(doc.metadata.get('source', 'Unknown'))
        context_elements.append(f"[Source {i+1}]: {source_name}\nContent: {doc.page_content}")
    
    context_str = "\n\n".join(context_elements)
    
    system_prompt = f"""You are an HR Assistant. Answer the user's question based ONLY on the context provided below.
    
    Context:
    {context_str}
    
    Instructions:
    1. Answer clearly and concisely.
    2. If the answer is not in the context, say "I cannot find the answer in the provided documents."
    3. CITATIONS REQUIRED: You MUST cite your sources. When using information, add the specific Source ID (e.g., [Source 1]) immediately after the sentence.
    """
    
    messages = [
        HumanMessage(content=system_prompt),
        HumanMessage(content=query)
    ]
    
    # 3. Generate
    print("Generating response...")
    response = model.invoke(messages)
    print("\nResponse:")
    print(response.content)

if __name__ == "__main__":
    test_rag()
