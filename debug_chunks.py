from load_documents import load_docs
from split_doc import split_docs
import os

def debug():
    docs = load_docs()
    pdf_docs = [doc for doc in docs if doc.metadata.get('source', '').endswith('.pdf')]
    
    print(f"Total PDF pages: {len(pdf_docs)}")
    
    splits = split_docs(pdf_docs)
    print(f"Total PDF splits: {len(splits)}")
    
    for i, split in enumerate(splits):
        print(f"--- Split {i} ---")
        print(split.page_content)
        print("-" * 20)

if __name__ == "__main__":
    debug()
