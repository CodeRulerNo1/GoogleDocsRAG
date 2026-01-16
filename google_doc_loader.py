import requests
import re
from langchain_core.documents import Document

def load_google_doc(url):
    """
    Fetches the content of a public Google Doc as text.
    Handles private links, empty docs, and invalid URLs.
    """
    try:
        # Extract doc ID from URL
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
        if not match:
            return None, "Invalid Google Doc URL. Please ensure it follows the format: https://docs.google.com/document/d/DOC_ID/..."
        
        doc_id = match.group(1)
        export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
        
        # Follow redirects is True by default in requests, but we might want to check if we ended up at a login page
        response = requests.get(export_url, allow_redirects=True)
        
        # Check for successful response
        if response.status_code == 200:
            # Google often redirects private docs to a login page (accounts.google.com) returning 200 OK.
            if "accounts.google.com" in response.url or "signin" in response.url:
                return None, "🔒 This link appears to be private. Please change the sharing settings to 'Anyone with the link' and try again."
            
            content = response.text.strip()
            
            if not content:
                return None, "⚠️ The document appears to be empty. Please check the content."
                
            # Create a LangChain Document object
            doc = Document(
                page_content=content,
                metadata={"source": url, "title": "Google Doc"}
            )
            return [doc], None
            
        elif response.status_code == 401 or response.status_code == 403:
             return None, "🔒 Access denied. Please ensure the link is shared with 'Anyone with the link'."
             
        elif response.status_code == 404:
            return None, "❌ Document not found. Please check the URL."
            
        else:
            return None, f"Failed to fetch Google Doc (Status Code: {response.status_code})"
            
    except Exception as e:
        return None, f"An error occurred: {str(e)}"