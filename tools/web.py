
import trafilatura
from markdownify import markdownify as md
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()
SERPER_API_KEY=os.environ.get("SERPER_API_KEY")
def web_search(query:str) -> dict:
  url = "https://google.serper.dev/search"
  payload = json.dumps({"q": query})
  headers = {
      'X-API-KEY': SERPER_API_KEY,
      'Content-Type': 'application/json'
  }
  #Serper is used to obtain a json string containing the information of the webpage we search. 
  #Due to it being a json string it can be easily converted to a dict which is good for our AI agent.
  #Also since it returns links, we can use this further in our web_fetch tool.
  
  try:
      response = requests.post(url, headers=headers, data=payload, timeout=10)
      response.raise_for_status()
      search_results = response.json()
      
      output = []
      for item in search_results.get("organic", [])[:4]:
          output.append(f"Title: {item.get('title')}\nSnippet: {item.get('snippet')}\nLink: {item.get('link')}\n---")
          
      return {"result":output} if output else {"error":"No answer found"}
  except Exception as e:
      return {"error": f"Error executing web search: {str(e)}"}

  


def web_fetch(url: str) -> dict:
    try:
        # 1. Trafilatura downloads and extracts ONLY the core body content safely
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return {"error": "Failed to download webpage context."}
            
        # Extract core content as clean HTML segment first
        raw_core_html = trafilatura.extract(downloaded, output_format="xml") # XML keeps structure intact
        #XML is used to convert the HTML in a more readable format for the computer and markdownify as it has a more strict structure making it more predictable and easy to read.
        #ATX is a way to represent headings in markdown files which is more token-efficient than the alternative
        if not raw_core_html:
            return {"error": "Trafilatura could not isolate core textual body content."}
            
        # 2. Markdownify converts that isolated core block into crisp, token-lean Markdown
        clean_markdown = md(raw_core_html, heading_style="ATX")
        
        return {
            "url": url,
            "content": clean_markdown[:6000] # Safe token limit window truncation
        }
    except Exception as e:
        return {"error": f"Web fetch pipeline failed: {str(e)}"}
    
