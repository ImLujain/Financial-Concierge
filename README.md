#  Financial Concierge

AI-powered multi-agent financial assistant built with Google's Agent Development Kit (ADK) using Agent-to-Agent (A2A) protocol. Get real-time stock data, perform financial calculations, and manage your watchlist through natural conversation.

##  Architecture

This application demonstrates a **multi-agent** pattern with a root agent coordinating three specialized sub-agents via HTTP-based A2A protocol:

```
┌─────────────────────────────────────────┐
│      Streamlit UI (Root Agent)          │
│    (Port: Default Streamlit)             │
│  - Gemini 2.5 Flash Lite                 │
│  - Coordinates sub-agents                │
│  - Maintains conversation context        │
└──────────┬──────────┬───────────┬────────┘
           │          │           │
    A2A    │   A2A    │    A2A    │
    HTTP   │   HTTP   │    HTTP   │
           │          │           │
┌──────────▼─────┐ ┌──▼────────┐ ┌▼──────────────┐
│  Calculator    │ │ Watchlist │ │ Search Agent  │
│    Agent       │ │   Agent   │ │ (Port: 8003)  │
│ (Port: 8010)   │ │(Port:8002)│ │               │
├────────────────┤ ├───────────┤ ├───────────────┤
│ Gemini 2.5     │ │ Gemini2.5 │ │ Gemini 2.0    │
│ Flash Lite     │ │ Flash Lite│ │ Flash Lite    │
├────────────────┤ ├───────────┤ ├───────────────┤
│ • P/E Ratios   │ │ • Add/Del │ │ • Google      │
│ • Returns      │ │   Stocks  │ │   Search      │
│ • Portfolio    │ │ • View    │ │ • Market News │
│   Analysis     │ │   List    │ │ • Stock Data  │
└────────────────┘ └───────────┘ └───────────────┘
```



##  Quick Start

### Prerequisites

- Python 3.8+
- Google AI API Key ([Get one here](https://aistudio.google.com/app/apikey))

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd "Financial Concierge"

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

**Important**: All three A2A servers must be running before starting the Streamlit app.

1. **Start Calculator Agent** (Terminal 1):
```bash
uvicorn calculator_server:app --host localhost --port 8010 --reload
# Runs on http://localhost:8010
```

2. **Start Watchlist Agent** (Terminal 2):
```bash
uvicorn watchlist_server:app --host localhost --port 8002 --reload
# Runs on http://localhost:8002
```

3. **Start Search Agent** (Terminal 3):
```bash
uvicorn search_server:app --host localhost --port 8003 --reload
# Runs on http://localhost:8003
```

4. **Start Streamlit UI** (Terminal 4):
```bash
streamlit run streamlit_app.py
```

5. Open your browser to `http://localhost:8501`

6. Enter your Google API Key in the sidebar

### Verifying Server Status

The sidebar shows real-time status of all three A2A servers:
- ✅ Green checkmark = Server running and accessible
- ❌ Red X = Server offline or unreachable

##  Usage Examples

### Stock Research
```
"What's the current price of Apple stock?"
"Find the latest news about Tesla"
"Search for Microsoft earnings report"
```

### Financial Calculations
```
"Calculate P/E ratio for a stock with price $150 and EPS $5"
"What's my return if I bought at $100 and sold at $150?"
"Analyze my portfolio: {'AAPL': 10000, 'MSFT': 15000, 'GOOGL': 8000}"
```

### Watchlist Management
```
"Add NVIDIA to my watchlist with note 'AI leader'"
"Show my watchlist"
"Remove AAPL from watchlist"
```

### Multi-Agent Workflows
```
"Research Tesla stock and add it to my watchlist"
"Find Apple's current price and calculate the P/E ratio"
"Show me my watchlist and get the latest news for each stock"
```

##  Technical Details

### Agent Specifications

| Agent | Model | Port | Purpose | Tools |
|-------|-------|------|---------|-------|
| Root | gemini-2.5-flash-lite | N/A | Orchestrator | 3 sub-agents |
| Calculator | gemini-2.5-flash-lite | 8010 | Financial math | `calculate_pe_ratio`, `calculate_return`, `analyze_portfolio` |
| Watchlist | gemini-2.5-flash-lite | 8002 | Stock tracking | `add_to_watchlist`, `remove_from_watchlist`, `get_my_watchlist` |
| Search | gemini-2.0-flash-lite | 8003 | Market research | `google_search` |

### Retry Configuration

All agents use exponential backoff retry for resilience:
```python
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)
```

### Session Management

- **Session ID**: Generated per browser session as `streamlit_session_{uuid}`
- **User ID**: Static `"streamlit_user"` for all sessions

- **Storage**: In-memory (resets on server restart)


## Environment Variables

The application uses these environment variables (set via code or `.env`):

```bash
GOOGLE_API_KEY=your_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

**Note**: API keys are currently hardcoded in the server files. For production, use environment variables or a secrets manager.

##  UI Features

- **Modern Dark Theme**: Clean gradient design with Inter font
- **Real-time Server Status**: Live monitoring of all A2A agents
- **Session Management**: New conversation button to reset context
- **Quick Actions**: Pre-built example queries for common tasks
- **Empty State**: Helpful prompts when starting a new conversation
- **Responsive Layout**: Optimized for desktop and mobile viewing


##  License

Educational project - use as reference for learning Google ADK and A2A patterns.

## 🔗 Resources

- [Google ADK Documentation](https://cloud.google.com/generative-ai-app-builder/docs/agent-development-kit)
- [Agent-to-Agent Protocol](https://google.github.io/agent-to-agent/)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Google AI Studio](https://aistudio.google.com)
