
import os
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.genai import types

os.environ["GOOGLE_API_KEY"] = "AIzaSyCUEInF6S0S0XUvmZTPVAWoPlQSDOmCHPs"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

search_agent = Agent(
    model=Gemini(model="gemini-2.0-flash-lite", retry_options=retry_config),
    name="search_agent",
    description="Market research specialist that searches for current stock information.",
    instruction="""You are a market research specialist.
    
    Your job is to:
    - Search for current stock prices and news
    - Find company financial data and earnings reports
    - Research market trends and analysis
    
    Always provide sources and recent information.""",
    tools=[google_search],
)

app = to_a2a(search_agent, port=8003)
