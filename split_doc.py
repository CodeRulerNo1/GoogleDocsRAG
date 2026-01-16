from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_docs(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,  # roughly 500 tokens
        chunk_overlap=200, 
        add_start_index=True,
    )
    all_splits = text_splitter.split_documents(docs)
    return all_splits

