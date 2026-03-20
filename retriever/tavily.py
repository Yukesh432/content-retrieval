from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()


tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
# response = tavily_client.research("What is visual encodings")

# print(response)

# # extract content from response
# if response and "results" in response and len(response["results"]) > 0:
#     for result in response["results"]:
#         print("Title:", result.get("title"))
#         print("Content:", result.get("content"))
#         print("-" * 40)
# else:
#     print("No results found.")

response = tavily_client.get_research("d37f784c-40bf-4c39-bd53-181d1e321769")
print(response)