from tavily import TavilyClient
import os
from dotenv import load_dotenv
# ================this is Not Required if MCP server implements so delete it==========#
# for Internet Web Search we add Travily MCP Server

load_dotenv()

client = TavilyClient(
    api_key= os.getenv("TAVILY_API_KEY")
)

# tavliy k andar Multiple tool hai but hme internet Search krni hai isliye 
# search tool hi lagega only
def tavily_search(query):
    response = client.search(
        query= query,
        max_results= 5
    )

    results = []

    for i, r in enumerate(response["results"], 1):
        title   = r.get("title", "Unknown")
        url     = r.get("url", "")
        snippet = r.get("content", "").strip()
        # Keep only the first 300 characters to avoid wall-of-text
        if len(snippet) > 300:
            snippet = snippet[:300].rsplit(" ", 1)[0] + "..."

        results.append(f"{i}. **{title}**\n   {url}\n   {snippet}")

    return "\n\n".join(results)
