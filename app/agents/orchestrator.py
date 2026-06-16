"""
LangGraph orchestrator (Day 14+).

Replaces hardcoded if/elif routing with LangGraph StateGraph.
Preserves all Day 13 behavior exactly:
- Regex-based intent classification
- State-based routing (awaiting_product_selection takes precedence)
- Existing handle_customer_request() and handle_product_request() calls
- Conversation state fields (last_product_name, pending_candidates, etc.)

TypedDict for state; backward compatible with dict-based state handling.
"""

from typing import TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from app.agents.customer_agent import handle_customer_request
from app.agents.product_agent import handle_product_request

class AgentState(TypedDict, total=False):
    """
    LangGraph orchestrator state (Day 13 fields preserved).
    
    TypedDict allows mixed required/optional fields with total=False.
    """
    # Graph-level fields
    messages: list[BaseMessage]
    mode: str
    business_id: int
    session_id: str
    intent: str
    
    # Day 13 state fields (preserved exactly)
    last_product_name: str
    awaiting_product_selection: bool
    pending_candidates: list
    pending_stock: int
    
    # Output
    agent_result: dict


async def intent_classifier(state: AgentState) -> AgentState:
    """
    Classify intent from message (preserving Day 13 regex logic).
    
    Regex routing: "add customer", "add product", "update product", "update stock".
    State-based: awaiting_product_selection takes precedence.
    """
    # Day 13: State-based routing takes precedence
    if state.get("awaiting_product_selection", False):
        state["intent"] = "product_selection"
        return state
    
    # Day 13: Regex-based intent classification
    messages = state.get("messages", [])
    if messages:
        message = messages[-1].content
        message_lower = message.lower()
        
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


def build_orchestrator_graph(checkpointer):
    """
    Build and compile LangGraph orchestrator.
    
    Args:
        checkpointer: AsyncPostgresSaver instance (from app.main lifespan)
    
    Returns:
        Compiled LangGraph with checkpointer bound for state persistence.
    
    Graph structure (Day 13 behavior preserved):
    
    START
      ↓
    intent_classifier (regex logic)
      ↓
    intent_router (conditional: customer | product | fallback)
      ├→ customer_agent_node
      ├→ product_agent_node
      └→ fallback_node
      ↓
    END
    """
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("intent_classifier", intent_classifier)
    graph.add_node("customer_agent_node", customer_agent_node)
    graph.add_node("product_agent_node", product_agent_node)
    graph.add_node("fallback_node", fallback_node)
    
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
    
    # All agent nodes end
    graph.add_edge("customer_agent_node", END)
    graph.add_edge("product_agent_node", END)
    graph.add_edge("fallback_node", END)
    
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
        Phase 3A: Removed state parameter. State is now loaded from PostgreSQL checkpoints
        by graph.ainvoke() automatically. No need for conversation_state.py dual persistence.
        
        Graph and thread_id are passed by caller (main.py prepared them in startup).
        This keeps route_message testable and flexible.
    """
    # Convert dict → AgentState
    # Phase 3A: Initial values don't matter - graph.ainvoke() with thread_id will load
    # state from PostgreSQL checkpoints and override these defaults
    agent_state: AgentState = {
        "messages": [HumanMessage(content=message)],
        "mode": "owner",  # Phase 1: owner mode only
        "business_id": business_id,
        "session_id": session_id,
        "intent": "",
        "last_product_name": "",
        "awaiting_product_selection": False,
        "pending_candidates": [],
        "pending_stock": 0,
        "agent_result": {},
    }
    
    # Invoke graph with correct checkpointer config
    result_state = await graph.ainvoke(
        agent_state,
        config={
            "configurable": {
                "thread_id": thread_id,
            }
        },
    )
    
    # Phase 3A: Removed state dict update - no need to update conversation_state.py
    # State is now persisted to PostgreSQL by AsyncPostgresSaver automatically
    
    # Return agent result (same format as old orchestrator)
    return result_state.get("agent_result", {})