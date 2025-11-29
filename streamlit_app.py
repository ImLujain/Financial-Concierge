import streamlit as st
import asyncio
import uuid
from typing import Dict, List
import os

# Google ADK imports
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
)

# Page configuration
st.set_page_config(
    page_title="Financial Assistant",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS - Modern dark theme with excellent UX
st.markdown("""
<style>
    /* Import better fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main container - Dark theme */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 100%);
    }

    .main .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }

    .sub-header {
        font-size: 1rem;
        color: #9ca3af;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }

    /* Chat messages - Clean, no boxes */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 1.2rem 0 !important;
        margin-bottom: 0 !important;
    }

    /* User messages */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background-color: rgba(102, 126, 234, 0.05) !important;
        border-radius: 16px;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
    }

    [data-testid="stChatMessage"] p {
        color: #e5e7eb;
        line-height: 1.7;
        font-size: 0.95rem;
    }

    /* User message text color */
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p {
        color: #c7d2fe;
    }

    /* Avatar styling */
    [data-testid="stChatMessageAvatarUser"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 50%;
    }

    [data-testid="stChatMessageAvatarAssistant"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        border-radius: 50%;
    }

    /* Chat input - Modern design */
    [data-testid="stChatInput"] {
        background-color: #1f2937 !important;
        border: 2px solid #374151 !important;
        border-radius: 16px !important;
        padding: 0.5rem !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #e5e7eb !important;
        background-color: transparent !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #6b7280 !important;
    }

    /* Sidebar - Modern dark design */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1f2937 !important;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f3f4f6 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 1rem !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #d1d5db !important;
        font-size: 0.875rem !important;
    }

    /* Input fields in sidebar */
    [data-testid="stSidebar"] input {
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
        color: #e5e7eb !important;
        border-radius: 8px !important;
    }

    [data-testid="stSidebar"] input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }

    /* Button styling - Modern gradient buttons */
    .stButton button {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #374151;
        border-radius: 10px;
        color: #e5e7eb;
        font-weight: 500;
        font-size: 0.875rem;
        width: 100%;
        padding: 0.65rem 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        letter-spacing: 0.01em;
    }

    .stButton button:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-color: #667eea;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    /* Status indicators - Clean design */
    .element-container div[data-testid="stSuccess"],
    .element-container div[data-testid="stError"] {
        background-color: transparent !important;
        padding: 0.4rem 0 !important;
        font-size: 0.875rem !important;
        border: none !important;
    }

    .element-container div[data-testid="stSuccess"] {
        color: #10b981 !important;
    }

    .element-container div[data-testid="stError"] {
        color: #ef4444 !important;
    }

    /* Divider */
    hr {
        margin: 1.5rem 0;
        border-color: #374151;
        opacity: 0.5;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #1f2937;
    }

    ::-webkit-scrollbar-thumb {
        background: #374151;
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #4b5563;
    }

    /* Text selection */
    ::selection {
        background-color: rgba(102, 126, 234, 0.3);
        color: #e5e7eb;
    }

    /* Info boxes */
    .element-container div[data-testid="stInfo"] {
        background-color: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        color: #93c5fd !important;
        border-radius: 8px !important;
    }

    /* Empty state message */
    .empty-state {
        text-align: center;
        padding: 3rem 2rem;
        color: #6b7280;
    }

    .empty-state h3 {
        color: #9ca3af;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
APP_NAME = "financial_assistant"
USER_ID = "streamlit_user"
API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# A2A Server URLs
CALCULATOR_URL = "http://localhost:8010"
WATCHLIST_URL = "http://localhost:8002"
SEARCH_URL = "http://localhost:8003"

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = f"streamlit_session_{uuid.uuid4().hex[:8]}"

if "initialized" not in st.session_state:
    st.session_state.initialized = False

if "watchlist" not in st.session_state:
    st.session_state.watchlist = {}

# Store conversation history to maintain context across thread-isolated requests
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []


def create_root_agent():
    """Create the root agent (can be called from any thread)."""
    import warnings
    warnings.filterwarnings('ignore')

    # Set API key
    if API_KEY:
        os.environ["GOOGLE_API_KEY"] = API_KEY
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

    # Create RemoteA2aAgent proxies with error handling
    remote_calculator_agent = RemoteA2aAgent(
        name="calculator_agent",
        description="Remote financial calculator that performs P/E ratios, returns, and portfolio analysis.",
        agent_card=f"{CALCULATOR_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    remote_watchlist_agent = RemoteA2aAgent(
        name="watchlist_agent",
        description="Remote watchlist manager that tracks stocks of interest.",
        agent_card=f"{WATCHLIST_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    remote_search_agent = RemoteA2aAgent(
        name="search_agent",
        description="Remote market research specialist that searches for current stock information.",
        agent_card=f"{SEARCH_URL}{AGENT_CARD_WELL_KNOWN_PATH}",
    )

    # Create Root Agent
    root_agent = LlmAgent(
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        name="financial_assistant",
        description="Comprehensive financial assistant coordinating research, calculations, and watchlist.",
        instruction="""You are a comprehensive financial assistant that helps users with stock research and investment analysis.

        IMPORTANT: Always respond in English, regardless of the user's location or native language.

        You coordinate three specialist sub-agents via A2A protocol:
        1. **calculator_agent** - Use this for P/E ratios, returns, portfolio analysis
        2. **watchlist_agent** - Use this to add/remove/view stocks in the watchlist
        3. **search_agent** - Use this for current stock prices, news, company data, market research

        When a user asks about stocks:
        - Delegate to search_agent for current market information
        - Delegate to calculator_agent for financial calculations
        - Delegate to watchlist_agent for watchlist management
        - Combine insights from agents when needed
        - Suggest adding interesting stocks to the watchlist

        Always use the appropriate sub-agent for each task.
        Remember context from previous messages in the conversation.""",
        sub_agents=[remote_calculator_agent, remote_watchlist_agent, remote_search_agent],
    )

    return root_agent


def create_session_sync(session_id):
    """Create a new session (synchronous wrapper)."""
    import asyncio
    import threading
    from queue import Queue

    result_queue = Queue()

    def run_in_thread():
        """Run async code in a dedicated thread with persistent event loop."""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Create session service in this thread
            session_service = InMemorySessionService()

            async def _create():
                session = await session_service.create_session(
                    app_name=APP_NAME,
                    user_id=USER_ID,
                    session_id=session_id
                )
                return session

            # Run the coroutine
            result = loop.run_until_complete(_create())
            result_queue.put(("success", result))

        except Exception as e:
            result_queue.put(("error", str(e)))
        finally:
            # Don't close the loop - let it be garbage collected
            pass

    # Start thread and wait for result
    thread = threading.Thread(target=run_in_thread, daemon=True)
    thread.start()
    thread.join(timeout=30)

    if result_queue.empty():
        st.error("Error: Session creation timed out")
        return None

    status, result = result_queue.get()
    if status == "error":
        st.error(f"Error creating session: {result}")
        return None

    return result


def send_message_sync(session_id, message: str, conversation_history: list):
    """Send a message to the agent and get response (synchronous wrapper)."""
    import asyncio
    import threading
    from queue import Queue

    result_queue = Queue()

    def run_in_thread():
        """Run async code in a dedicated thread with persistent event loop."""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Create session service in this thread
            session_service = InMemorySessionService()

            # Create root agent and runner in this thread with its own event loop
            root_agent = create_root_agent()
            runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

            async def _send():
                # Create session
                session = await session_service.create_session(
                    app_name=APP_NAME,
                    user_id=USER_ID,
                    session_id=session_id
                )

                # Replay conversation history by actually running through the agent
                # This ensures the agent processes and remembers the context
                # Only replay the last 6 messages (3 exchanges) to avoid timeout
                recent_history = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history

                for i, hist_msg in enumerate(recent_history):
                    if hist_msg["role"] == "user":
                        # Send historical user message
                        hist_content = types.Content(parts=[types.Part(text=hist_msg["content"])])
                        # Run through agent but don't collect response (we already have it)
                        async for event in runner.run_async(
                            user_id=USER_ID,
                            session_id=session_id,
                            new_message=hist_content
                        ):
                            # Just process, don't capture
                            pass

                # Now send the actual new message
                test_content = types.Content(parts=[types.Part(text=message)])

                response_text = ""
                async for event in runner.run_async(
                    user_id=USER_ID,
                    session_id=session_id,
                    new_message=test_content
                ):
                    if event.is_final_response() and event.content:
                        for part in event.content.parts:
                            if hasattr(part, "text"):
                                response_text += part.text

                return response_text

            # Run the coroutine
            result = loop.run_until_complete(_send())
            result_queue.put(("success", result))

        except Exception as e:
            result_queue.put(("error", str(e)))
        finally:
            # Don't close the loop - let it be garbage collected
            pass

    # Start thread and wait for result
    thread = threading.Thread(target=run_in_thread, daemon=True)
    thread.start()
    thread.join(timeout=60)

    if result_queue.empty():
        return "Error: Request timed out"

    status, result = result_queue.get()
    if status == "error":
        return f"Error: {result}"

    return result or "No response received"


# Main app
def main():
    # Header
    st.markdown('<div class="main-header">📊 Financial Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-powered multi-agent financial analysis</div>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("🔧 Settings")

        # API Key input
        api_key_input = st.text_input(
            "Google API Key",
            value=API_KEY,
            type="password",
            help="Enter your Google AI API key"
        )

        if api_key_input:
            os.environ["GOOGLE_API_KEY"] = api_key_input

        st.divider()

        # Server status
        st.header("🌐 A2A Server Status")

        import requests

        def check_server(url, name):
            try:
                response = requests.get(f"{url}/.well-known/agent-card.json", timeout=2)
                if response.status_code == 200:
                    st.success(f"✅ {name}")
                else:
                    st.error(f"❌ {name}")
            except:
                st.error(f"❌ {name} (Offline)")

        check_server(CALCULATOR_URL, "Calculator Agent")
        check_server(WATCHLIST_URL, "Watchlist Agent")
        check_server(SEARCH_URL, "Search Agent")

        st.divider()

        # Session info
        st.header("📝 Session Info")
        st.text(f"Session ID: {st.session_state.session_id[:16]}...")

        if st.button("🔄 New Conversation"):
            st.session_state.messages = []
            st.session_state.session_id = f"streamlit_session_{uuid.uuid4().hex[:8]}"
            st.session_state.initialized = False
            st.session_state.conversation_history = []
            st.rerun()

        st.divider()

        # Quick actions
        st.header("⚡ Quick Actions")

        example_queries = [
            "Find Apple stock price",
            "Analyze my portfolio",
            "Show my watchlist",
            "Latest NVIDIA news"
        ]

        for query in example_queries:
            if st.button(query, key=f"quick_{query}"):
                st.session_state.messages.append({"role": "user", "content": query})
                st.rerun()

    # Main chat area
    st.markdown("<br>", unsafe_allow_html=True)

    # Create session if not initialized
    if not st.session_state.initialized:
        with st.spinner("Initializing session..."):
            session = create_session_sync(st.session_state.session_id)
            if session:
                st.session_state.initialized = True
            else:
                st.error("⚠️ Failed to initialize session")
                st.info("Make sure the A2A servers are running on ports 8010, 8002, and 8003")
                if st.button("🔄 Retry Connection"):
                    st.rerun()
                st.stop()

    # Display chat messages or empty state
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div class="empty-state">
            <h3>👋 Welcome to Financial Assistant</h3>
            <p>Start by asking a question about stocks, portfolios, or market analysis.</p>
            <p style="margin-top: 1rem; font-size: 0.875rem;">Try: "What's the current price of Apple stock?"</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about stocks, portfolios, or financial analysis..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Get assistant response (pass current conversation history for context)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_message_sync(
                    st.session_state.session_id,
                    prompt,
                    st.session_state.conversation_history
                )
                st.markdown(response)

        # Add both user and assistant messages to conversation history
        st.session_state.conversation_history.append({"role": "user", "content": prompt})
        st.session_state.conversation_history.append({"role": "model", "content": response})

        # Add assistant response to display messages
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()


if __name__ == "__main__":
    main()
