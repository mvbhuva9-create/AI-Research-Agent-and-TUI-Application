import requests
import json
import io
from pypdf import PdfReader  # Used for reading downloaded binary stream PDFs

# ---------------------------------------------------------------------------
# Tool 1: paper_search
# ---------------------------------------------------------------------------
def paper_search(query: str, limit: int = 5) -> dict:
    """
    Queries the Hugging Face Daily Papers API to find research papers.
    Returns paper IDs, titles, abstracts, and authors.
    """
    try:
        # 1. Hit the Hugging Face API
        url = "https://huggingface.co/api/daily_papers"
        params = {"search": query}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        papers_data = response.json()
        results = []
      #requests is what is used to send packets over the internet and in our case, .get tellls the server we want to
      #simply read what is at the url with the search params. we used requests in our other web tools as well
        # 2. Extract relevant metadata fields cleanly
        for paper in papers_data[:limit]:
            # The API returns nested dicts containing arXiv ids and summary blocks
            paper_info = paper.get("paper", {})
            results.append({
                "id": paper_info.get("id"),  # e.g., "2401.12345"
                "title": paper_info.get("title"),
                "summary": paper_info.get("summary"),
                "published_at": paper.get("publishedAt")
            })
            
        return {
            "query": query,
            "papers_found": len(results),
            "papers": results
        }
        
    except Exception as e:
        return {"error": f"Hugging Face paper search failed: {str(e)}"}


# ---------------------------------------------------------------------------
# Tool 2: read_paper
# ---------------------------------------------------------------------------
def read_paper(paper_id: str, start_page: int = 1, max_pages: int = 5) -> dict:
    try:
        # Strategy A: Try the fast Markdown endpoint first
        md_url = f"https://huggingface.co/papers/{paper_id}.md"
        response = requests.get(md_url, timeout=10)
        
        # If HF gives us a clean, full-text Markdown file
        if response.status_code == 200 and len(response.text) > 3000: 
            return {
                "paper_id": paper_id,
                "source": "huggingface_markdown",
                "content": response.text
            }
            
        
        #This is a fallback option in case there does not exist a md file of the paper we want
        #we are using pypdf to extract the pages and read them and basically parse the data into a readable format
        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
        pdf_response = requests.get(pdf_url, timeout=15)
        pdf_response.raise_for_status()
        
        reader = PdfReader(io.BytesIO(pdf_response.content))
        total_pages = len(reader.pages)
        
        extracted_pages = []
        end_page = min(start_page + max_pages - 1, total_pages)
        #reader is a object of pdfreader class and it has the properties of pages which tells us the number of pages
        # as well as lets us access each page separately and also has the method extract_text() which extracts all the text for us
        
        for p in range(start_page, end_page + 1):
            text = reader.pages[p - 1].extract_text()
            extracted_pages.append(f"--- PAGE {p} ---\n{text}")
            
        return {
            "paper_id": paper_id,
            "source": "arxiv_pdf_extractor",
            "total_pages": total_pages,
            "content": "\n\n".join(extracted_pages)
        }
        
    except Exception as e:
        return {"error": f"Failed to retrieve paper content: {str(e)}"}