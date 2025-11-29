
import os
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from google.genai import types

os.environ["GOOGLE_API_KEY"] = "AIzaSyCUEInF6S0S0XUvmZTPVAWoPlQSDOmCHPs"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

class WatchlistManager:
    def __init__(self):
        self.watchlists = {}
    
    def add_to_watchlist(self, user_id: str, symbol: str, note: str = "") -> dict:
        if user_id not in self.watchlists:
            self.watchlists[user_id] = {}
        symbol = symbol.upper()
        self.watchlists[user_id][symbol] = note
        return {
            "status": "success",
            "action": "added",
            "symbol": symbol,
            "note": note,
            "watchlist_size": len(self.watchlists[user_id])
        }
    
    def remove_from_watchlist(self, user_id: str, symbol: str) -> dict:
        symbol = symbol.upper()
        if user_id in self.watchlists and symbol in self.watchlists[user_id]:
            del self.watchlists[user_id][symbol]
            return {
                "status": "success",
                "action": "removed",
                "symbol": symbol,
                "watchlist_size": len(self.watchlists[user_id])
            }
        return {"status": "error", "message": f"{symbol} not found in watchlist"}
    
    def get_watchlist(self, user_id: str) -> dict:
        if user_id not in self.watchlists:
            return {"status": "success", "watchlist": {}, "count": 0}
        return {
            "status": "success",
            "watchlist": self.watchlists[user_id],
            "count": len(self.watchlists[user_id])
        }

watchlist_manager = WatchlistManager()

def add_to_watchlist(symbol: str, note: str = "") -> dict:
    """Add a stock to your watchlist with optional notes."""
    return watchlist_manager.add_to_watchlist("default", symbol, note)

def remove_from_watchlist(symbol: str) -> dict:
    """Remove a stock from your watchlist."""
    return watchlist_manager.remove_from_watchlist("default", symbol)

def get_my_watchlist() -> dict:
    """Get all stocks in your watchlist."""
    return watchlist_manager.get_watchlist("default")

watchlist_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="watchlist_agent",
    description="Watchlist manager that tracks stocks of interest.",
    instruction="""You are a watchlist management specialist.
    
    Your job is to:
    - Add stocks to the user's watchlist with notes
    - Remove stocks from the watchlist
    - Show the current watchlist
    
    When adding stocks, encourage users to add notes about why they're interested.""",
    tools=[add_to_watchlist, remove_from_watchlist, get_my_watchlist],
)

app = to_a2a(watchlist_agent, port=8002)
