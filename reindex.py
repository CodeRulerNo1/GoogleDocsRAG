from load_documents import load_docs
from split_doc import split_docs
from storing_doc import store_docs
from chromaDB import vector_store

def reindex():
    print("Clearing vector store...")
    try:
        existing_data = vector_store.get()
        if existing_data and "ids" in existing_data and existing_data["ids"]:
            vector_store.delete(existing_data["ids"])
            print(f"Deleted {len(existing_data['ids'])} existing chunks.")
    except Exception as e:
        print(f"Nothing to clear or error: {e}")

    print("Loading documents...")
    docs = load_docs()
    print(f"Loaded {len(docs)} documents.")
    
    if docs:
        print("Splitting documents...")
        splits = split_docs(docs)
        print(f"Created {len(splits)} splits.")
        
        print("Storing documents...")
        ids = store_docs(splits)
        print(f"Stored {len(ids)} chunks.")
    else:
        print("No documents found to index.")

if __name__ == "__main__":
    reindex()
