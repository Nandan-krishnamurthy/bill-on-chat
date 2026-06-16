"""
LangGraph orchestrator (Day 14+).

Replaces hardcoded if/elif routing with LangGraph StateGraph.
Includes state trimming to keep conversation history bounded.

Features:
- LLM-driven intent classification and tool selection
- State-based routing (awaiting_product_selection takes precedence)
- Message archival for bounded checkpoint state
- Conversation state fields for multi-turn support
"""

from typing import TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from app.agents.customer_agent import handle_customer_request
from app.agents.product_agent import handle_product_request
from app.services.message_archival import archive_old_messages
from app.services.llm_tools import llm_customer_intent, llm_product_intent

class AgentState(TypedDict, total=False):
    """
    LangGraph orchestrator state (Day 13 fields + Week 3 archival).
    
    TypedDict allows mixed required/optional fields with total=False.
    """
    # Graph-level fields
    messages: list[BaseMessage]
    mode: str
    business_id: int
    session_id: str
    intent: str
    
    # Conversation state fields
    last_product_name: str
    awaiting_product_selection: bool
    pending_candidates: list
    pending_stock: int
    
    # Week 3: Message archival tracking
    archived_message_count: int
    
    # Output
    agent_result: dict


async def intent_classifier(state: AgentState) -> AgentState:
    """
    Classify intent using LLM (Week 3 replacement for regex).
    
    Uses Groq-driven intent recognition with fallback to regex for backward compatibility.
    State-based routing (awaiting_product_selection) takes precedence.
    """
    import re
    
    # State-based routing takes precedence
    if state.get("awaiting_product_selection", False):
        state["intent"] = "product_selection"
        return state
    
    # Get message and business_id
    messages = state.get("messages", [])
    business_id = state.get("business_id", 0)
    
    if not messages:
        state["intent"] = "unknown"
        return state
    
    message = messages[-1].content
    message_lower = message.lower()
    
    # Explicit numeric check for product selection disambiguation
    if re.match(r"^\s*\d+\s*$", message_lower):
        state["intent"] = "unknown"
        return state
    
    # Use LLM-driven intent classification
    try:
        # Try customer intent first
        customer_result = await llm_customer_intent(message, business_id)
        if customer_result["tool"] == "create_customer" and customer_result["confidence"] > 0.5:
            state["intent"] = "create_customer"
            return state
        
        # Try product intent
        product_result = await llm_product_intent(message, business_id)
        if product_result["tool"] in ["create_product", "update_stock"] and product_result["confidence"] > 0.5:
            state["intent"] = "update_product"
            return state
        
        # If LLM is uncertain, fall back to regex
        if "add customer" in message_lower:
            state["intent"] = "create_customer"
        elif (
            "add product" in message_lower
            or "update product" in message_lower
            or "update stock" in message_lower
        ):
            state["intent"] = "update_product"
        else:
            state["intent"] = "unknown"
    except Exception as e:
        # On LLM failure, fall back to regex
        print(f"LLM classification failed: {e}, using regex fallback")
        if "add customer" in message_lower:
            state["intent"] = "create_customer"
        elif (
            "add product" in message_lower
            or "update product" in message_lower
            or "update stock" in message_lower
        ):
            state["intent"] = "update_product"
        else:
            state["intent"] = "unknown"
    
    return state


def intent_router(state: AgentState) -> str:
    """
    Conditional router: intent → node name.
    
    Replaces if/elif branches in old orchestrator.
    """
    intent = state.get("intent", "unknown")
    
    if intent == "create_customer":
        return "customer_agent_node"
    elif intent in ["update_product", "product_selection"]:
        return "product_agent_node"
    else:
        return "fallback_node"


async def customer_agent_node(state: AgentState) -> AgentState:
    """
    Delegate to existing handle_customer_request().
    
    Extracts message from state, calls handler, stores result.
    """
    messages = state.get("messages", [])
    if messages:
        message = messages[-1].content
        business_id = state.get("business_id", 0)
        
        # Call existing handler
        result = await handle_customer_request(message, business_id)
        state["agent_result"] = result
    else:
        state["agent_result"] = {
            "success": False,
            "message": "No message provided",
        }
    
    return state


async def product_agent_node(state: AgentState) -> AgentState:
    """
    Delegate to existing handle_product_request().
    
    Converts AgentState fields to dict for handler compatibility,
    then extracts updated fields back to state.
    """
    messages = state.get("messages", [])
    if messages:
        message = messages[-1].content
        business_id = state.get("business_id", 0)
        
        # Convert AgentState fields to dict (handler expects dict)
        state_dict = {
            "last_product_name": state.get("last_product_name", ""),
            "awaiting_product_selection": state.get("awaiting_product_selection", False),
            "pending_candidates": state.get("pending_candidates", []),
            "pending_stock": state.get("pending_stock", 0),
        }
        
        # Call existing handler (modifies state_dict in-place)
        result = await handle_product_request(message, business_id, state_dict)
        
        # Extract updated fields back to AgentState
        state["last_product_name"] = state_dict.get("last_product_name", "")
        state["awaiting_product_selection"] = state_dict.get("awaiting_product_selection", False)
        state["pending_candidates"] = state_dict.get("pending_candidates", [])
        state["pending_stock"] = state_dict.get("pending_stock", 0)
        state["agent_result"] = result
    else:
        state["agent_result"] = {
            "success": False,
            "message": "No message provided",
        }
    
    return state


async def fallback_node(state: AgentState) -> AgentState:
    """Handle unsupported intents."""
    state["agent_result"] = {
        "success": False,
        "message": "Unsupported command",
    }
    return state


async def state_trimming_node(state: AgentState) -> AgentState:
    """
    Trim messages to bounded state and archive old messages.
    
    Runs after all agent nodes to keep checkpoint state bounded.
    """
    messages = state.get("messages", [])
    business_id = state.get("business_id", 0)
    session_id = state.get("session_id", "")
    archived_count = state.get("archived_message_count", 0)
    
    if not session_id or not business_id:
        return state
    
    thread_id = f"{business_id}:{session_id}"
    
    # Archive old messages if exceeding limit
    trimmed_messages, new_archived_count = await archive_old_messages(
        business_id=business_id,
        session_id=session_id,
        thread_id=thread_id,
        messages=messages,
        archived_message_count=archived_count,
    )
    
    state["messages"] = trimmed_messages
    state["archived_message_count"] = new_archived_count
    
    return state


def build_orchestrator_graph(checkpointer):
    """
    Build and compile LangGraph orchestrator.
    
    Args:
        checkpointer: AsyncPostgresSaver instance (from app.main lifespan)
    
    Returns:
        Compiled LangGraph with checkpointer bound for state persistence.
    
    Graph structure:
    
    START
      ↓
    intent_classifier
      ↓
    intent_router (conditional: customer | product | fallback)
      ├→ customer_agent_node
      ├→ product_agent_node
      └→ fallback_node
      ↓
    state_trimming_node (archive old messages, keep state bounded)
      ↓
    END
    """
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("intent_classifier", intent_classifier)
    graph.add_node("customer_agent_node", customer_agent_node)
    graph.add_node("product_agent_node", product_agent_node)
    graph.add_node("fallback_node", fallback_node)
    graph.add_node("state_trimming_node", state_trimming_node)
    
    # Add edges
    graph.add_edge(START, "intent_classifier")
    
    # Conditional routing based on intent
    graph.add_conditional_edges(
        "intent_classifier",
        intent_router,
        {
            "customer_agent_node": "customer_agent_node",
            "product_agent_node": "product_agent_node",
            "fallback_node": "fallback_node",
        },
    )
    
    # All agent nodes go to state trimming
    graph.add_edge("customer_agent_node", "state_trimming_node")
    graph.add_edge("product_agent_node", "state_trimming_node")
    graph.add_edge("fallback_node", "state_trimming_node")
    
    # State trimming goes to end
    graph.add_edge("state_trimming_node", END)
    
    return graph.compile(
        checkpointer=checkpointer
    )


async def route_message(
    message: str,
    business_id: int,
    session_id: str,
    thread_id: str,
    graph,
) -> dict:
    """Route message through LangGraph orchestrator.
    
    Input:
        message: User message
        business_id: Tenant ID
        session_id: Session ID (for state tracking)
        thread_id: Thread ID for checkpointer (business_id:session_id)
        graph: Compiled LangGraph (from app.state.orchestrator_graph)
    
    Output:
        Agent result dict (with "success" and "message" keys)
    
    Note:
        State Persistence (Phase 3B + Week 3):
        - graph.ainvoke() with thread_id loads state from PostgreSQL checkpoints
        - We only provide fields that are always fresh per request (messages, context)
        - Conversation state fields are loaded from checkpoint
        - State trimming node archives old messages and keeps checkpoint bounded
    """
    # Only initialize request-specific fields
    # Conversation state will be loaded from PostgreSQL checkpoint by graph.ainvoke()
    agent_state: AgentState = {
        "messages": [HumanMessage(content=message)],
        "mode": "owner",
        "business_id": business_id,
        "session_id": session_id,
    }
    
    # Invoke graph with correct checkpointer config
    # LangGraph will merge agent_state with checkpoint state (if exists)
    # Checkpoint state takes precedence for fields not explicitly provided
    result_state = await graph.ainvoke(
        agent_state,
        config={
            "configurable": {
                "thread_id": thread_id,
            }
        },
    )
    
    # Return agent result (saved by last node before END)
    return result_state.get("agent_result", {})