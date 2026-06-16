"""
LLM-driven tool selection and execution.

Uses Groq/Claude to understand natural language and decide which tool to call
with what arguments, replacing hardcoded regex patterns.
"""

from typing import Any, Optional
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from app.llm import get_llm
from pydantic import BaseModel, Field


# ============================================================================
# CUSTOMER AGENT TOOLS
# ============================================================================

class CreateCustomerInput(BaseModel):
    """Input for creating a new customer."""
    name: str = Field(..., description="Customer full name")
    phone: str = Field(..., description="10-digit phone number")
    state: str = Field(default="Karnataka", description="Customer state")


class GetCustomerInput(BaseModel):
    """Input for looking up a customer."""
    name: str = Field(..., description="Customer name to search for")


# ============================================================================
# PRODUCT AGENT TOOLS
# ============================================================================

class CreateProductInput(BaseModel):
    """Input for creating a new product."""
    name: str = Field(..., description="Product name")
    hsn: str = Field(..., description="HSN code (4-8 digits)")
    sell_price: float = Field(..., description="Selling price in INR")
    gst_rate: int = Field(..., description="GST rate as percentage (0-28)")
    stock: int = Field(..., description="Initial stock quantity")


class UpdateProductStockInput(BaseModel):
    """Input for updating product stock."""
    product_name: str = Field(..., description="Product name or partial match")
    stock: int = Field(..., description="New stock quantity")


# ============================================================================
# LLM TOOL CALLING - CUSTOMER AGENT
# ============================================================================

async def llm_customer_intent(
    message: str,
    business_id: int,
) -> dict:
    """
    Use LLM to understand customer intent and decide which tool to call.
    
    Returns:
        {
            "tool": "create_customer" | "get_customer" | "unknown",
            "parameters": {...},
            "confidence": float,
        }
    """
    
    llm = get_llm()
    
    # Define available tools with schemas
    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_customer",
                "description": "Create a new customer with name and phone number",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Customer name"},
                        "phone": {"type": "string", "description": "10-digit phone number"},
                        "state": {"type": "string", "description": "Customer state (default: Karnataka)"},
                    },
                    "required": ["name", "phone"],
                },
            },
        },
    ]
    
    # System prompt for customer agent
    system_prompt = """You are a customer management assistant. 
    Analyze the user's message to determine what action to take.
    
    If the user wants to create a new customer, use the create_customer tool.
    Extract the customer name and 10-digit phone number.
    If state is not mentioned, use 'Karnataka'.
    
    Only use the create_customer tool if the user explicitly wants to ADD or CREATE a customer.
    Do not infer customer creation from ambiguous statements."""
    
    # Call LLM with tool definitions
    response = await llm.bind_tools(tools).ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=message),
    ])
    
    # Parse tool calls from response
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_call = response.tool_calls[0]
        
        if tool_call['name'] == 'create_customer':
            return {
                "tool": "create_customer",
                "parameters": tool_call.get('args', {}),
                "confidence": 0.95,
            }
    
    # If no tool called, return unknown
    return {
        "tool": "unknown",
        "parameters": {},
        "confidence": 0.0,
    }


# ============================================================================
# LLM TOOL CALLING - PRODUCT AGENT
# ============================================================================

async def llm_product_intent(
    message: str,
    business_id: int,
) -> dict:
    """
    Use LLM to understand product intent and decide which tool to call.
    
    Returns:
        {
            "tool": "create_product" | "update_stock" | "unknown",
            "parameters": {...},
            "confidence": float,
        }
    """
    
    llm = get_llm()
    
    # Define available tools with schemas
    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_product",
                "description": "Create a new product with details",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Product name"},
                        "hsn": {"type": "string", "description": "HSN code (4-8 digits)"},
                        "sell_price": {"type": "number", "description": "Selling price in INR"},
                        "gst_rate": {"type": "integer", "description": "GST rate percentage"},
                        "stock": {"type": "integer", "description": "Initial stock quantity"},
                    },
                    "required": ["name", "hsn", "sell_price", "gst_rate", "stock"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "update_stock",
                "description": "Update stock quantity for an existing product",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_name": {"type": "string", "description": "Product name or partial match"},
                        "stock": {"type": "integer", "description": "New stock quantity"},
                    },
                    "required": ["product_name", "stock"],
                },
            },
        },
    ]
    
    # System prompt for product agent
    system_prompt = """You are a product inventory assistant.
    Analyze the user's message to determine what action to take.
    
    If the user wants to CREATE or ADD a new product, use the create_product tool.
    Extract: product name, HSN code, selling price, GST rate, and stock quantity.
    
    If the user wants to UPDATE or CHANGE stock for an existing product, use the update_stock tool.
    Extract: product name and new stock quantity.
    
    Only use tools if the user explicitly wants to create/update products.
    Do not infer actions from ambiguous statements."""
    
    # Call LLM with tool definitions
    response = await llm.bind_tools(tools).ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=message),
    ])
    
    # Parse tool calls from response
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_call = response.tool_calls[0]
        
        if tool_call['name'] == 'create_product':
            return {
                "tool": "create_product",
                "parameters": tool_call.get('args', {}),
                "confidence": 0.95,
            }
        elif tool_call['name'] == 'update_stock':
            return {
                "tool": "update_stock",
                "parameters": tool_call.get('args', {}),
                "confidence": 0.95,
            }
    
    # If no tool called, return unknown
    return {
        "tool": "unknown",
        "parameters": {},
        "confidence": 0.0,
    }
