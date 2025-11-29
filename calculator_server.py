
import os
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from google.genai import types

# Set API key from environment
os.environ["GOOGLE_API_KEY"] = "add your key here"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

def calculate_pe_ratio(stock_price: float, earnings_per_share: float) -> dict:
    """Calculate Price-to-Earnings ratio."""
    if earnings_per_share == 0:
        return {"error": "EPS cannot be zero"}
    
    pe_ratio = stock_price / earnings_per_share
    return {
        "pe_ratio": round(pe_ratio, 2),
        "stock_price": stock_price,
        "eps": earnings_per_share
    }

def calculate_return(initial_value: float, final_value: float) -> dict:
    """Calculate investment return percentage."""
    if initial_value == 0:
        return {"error": "Initial value cannot be zero"}
    
    return_pct = ((final_value - initial_value) / initial_value) * 100
    return {
        "return_percentage": round(return_pct, 2),
        "initial_value": initial_value,
        "final_value": final_value,
        "profit_loss": round(final_value - initial_value, 2)
    }

def analyze_portfolio(holdings: dict) -> dict:
    """Analyze portfolio allocation."""
    total = sum(holdings.values())
    if total == 0:
        return {"error": "Portfolio value cannot be zero"}
    
    return {
        "total_value": total,
        "holdings": {
            symbol: {
                "value": value,
                "percentage": round((value/total)*100, 2)
            }
            for symbol, value in holdings.items()
        }
    }

calculator_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="calculator_agent",
    description="Financial calculator that performs P/E ratios, returns, and portfolio analysis.",
    instruction="""You are a financial calculator specialist.
    
    Your job is to:
    - Calculate P/E ratios when given stock price and EPS
    - Calculate investment returns and profit/loss
    - Analyze portfolio allocations
    
    Always show your calculations clearly and explain the results.""",
    tools=[calculate_pe_ratio, calculate_return, analyze_portfolio],
)

app = to_a2a(calculator_agent, port=8010)
