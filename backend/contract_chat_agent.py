import os
import sys
from datetime import date
from typing import List, Dict, Any

from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage, AIMessage

# Ensure root paths are available
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from langgraph.graph import START, MessagesState, StateGraph
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False


def get_agent(llm):
    """
    Constructs the contract chat agent bound with both contract search
    tools and the Model Context Protocol (MCP) Knowledge Layer tools.
    Supports both LangGraph (when installed) and LangChain tool execution.
    """
    tools = []

    # 1. Base Contract Search Tools (with graceful fallbacks)
    try:
        from backend.shared.utils.contract_search_tool import ContractSearchTool
        tools.append(ContractSearchTool())
    except Exception:
        pass

    try:
        from backend.shared.utils.enhanced_contract_search_tool import EnhancedContractSearchTool
        tools.append(EnhancedContractSearchTool())
    except Exception:
        pass

    # 2. Knowledge + MCP Layer Tools (Phase 2 Deliverable by Brittany Gunn)
    try:
        from mcp.mcp_tools import (
            search_clause_library,
            get_playbook_rule,
            search_prior_approved_clauses,
            fetch_metadata
        )
    except ImportError:
        from backend.mcp_layer.tools import (
            search_clause_library,
            get_playbook_rule,
            search_prior_approved_clauses,
            fetch_metadata
        )

    mcp_tool_funcs = [
        search_clause_library,
        get_playbook_rule,
        search_prior_approved_clauses,
        fetch_metadata
    ]

    for tool_fn in mcp_tool_funcs:
        tool_obj = getattr(tool_fn, "_tool", tool_fn)
        if tool_obj not in tools:
            tools.append(tool_obj)

    llm_with_tools = llm.bind_tools(tools)

    sys_msg = SystemMessage(
        content=(
            "You are a senior legal AI assistant for contract intelligence. "
            "You are equipped with the Model Context Protocol (MCP) Knowledge Layer to verify legal policies, "
            "benchmark standard clauses, search historical approved precedents, and retrieve jurisdictional constraints.\n\n"
            "Your available tools:\n"
            "1. `search_clause_library`: Benchmark candidate clauses against standard/approved clauses in the library.\n"
            "2. `get_playbook_rule`: Retrieve exact corporate legal playbook rules and policy governance.\n"
            "3. `search_prior_approved_clauses`: Search historical approved precedent clauses to adjust and evaluate contract risk.\n"
            "4. `fetch_metadata`: Retrieve jurisdiction-specific enforceability rules and contract metadata.\n\n"
            "Always ground your recommendations in corporate playbook rules and benchmark clauses. "
            "Explain your findings concisely for executive leadership while preserving legal accuracy.\n"
            f"Today is {date.today()}."
        )
    )

    if HAS_LANGGRAPH:
        def assistant(state: MessagesState):
            return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

        def execute_tools(state: MessagesState):
            messages = state["messages"]
            last_message = messages[-1]

            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                tool_messages = []
                for tool_call in last_message.tool_calls:
                    for tool in tools:
                        tool_name = getattr(tool, "name", getattr(tool, "__name__", None))
                        if tool_name == tool_call['name']:
                            try:
                                if hasattr(tool, "invoke"):
                                    result = tool.invoke(tool_call['args'])
                                else:
                                    result = tool(**tool_call['args'])
                            except Exception as e:
                                result = f"Error executing {tool_name}: {e}"

                            tool_message = ToolMessage(
                                content=str(result),
                                tool_call_id=tool_call['id']
                            )
                            tool_messages.append(tool_message)
                return {"messages": tool_messages}
            return {"messages": []}

        builder = StateGraph(MessagesState)
        builder.add_node("assistant", assistant)
        builder.add_node("tools", execute_tools)
        builder.add_edge(START, "assistant")

        def should_continue(state: MessagesState):
            messages = state["messages"]
            last_message = messages[-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "tools"
            return "__end__"

        builder.add_conditional_edges("assistant", should_continue)
        builder.add_edge("tools", "assistant")
        return builder.compile()

    # Direct LangChain runner fallback when langgraph is not installed
    class DirectToolCallingRunner:
        def __init__(self, bound_llm, tool_list, system_message):
            self.llm = bound_llm
            self.tools = tool_list
            self.sys_msg = system_message

        def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
            input_msgs = inputs.get("messages", [])
            all_msgs = [self.sys_msg] + list(input_msgs)
            response = self.llm.invoke(all_msgs)

            # Check for tool calls and execute
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_messages = []
                for tc in response.tool_calls:
                    for t in self.tools:
                        t_name = getattr(t, "name", getattr(t, "__name__", None))
                        if t_name == tc['name']:
                            try:
                                if hasattr(t, "invoke"):
                                    r = t.invoke(tc['args'])
                                else:
                                    r = t(**tc['args'])
                            except Exception as err:
                                r = f"Error executing {t_name}: {err}"
                            tool_messages.append(ToolMessage(content=str(r), tool_call_id=tc['id']))
                # Follow up with model
                follow_up = self.llm.invoke(all_msgs + [response] + tool_messages)
                return {"messages": list(input_msgs) + [response] + tool_messages + [follow_up]}

            return {"messages": list(input_msgs) + [response]}

    return DirectToolCallingRunner(llm_with_tools, tools, sys_msg)
