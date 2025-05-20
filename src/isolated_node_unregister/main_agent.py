import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import  ToolNode, tools_condition
from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from .prompts import prompt_unregister
from .tools_file import call_register_user, call_confirm_registration
import sys

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# imports-----------------------


llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=api_key)


# class state ---------------------
class AgentState(TypedDict):
    status: Literal["registered", "unregistered"]
    user_id: Optional[str]
    pending_user_id: Optional[str] 
    messages: list


# tools -----------------------------
tools = [call_register_user, call_confirm_registration]
llm_with_tools = llm.bind_tools(tools)


# nodes---------------------------

def categorizer(state: AgentState) -> AgentState:
    last_message = state["messages"][-1].content.lower()
    if "book" in last_message or "appointment" in last_message:
        if state["status"] == "unregistered":
            print("User wants to book but is unregistered.")
        else:
            print("User wants to book and is already registered.")
    return state


# unregister node
def unregister_node(state: AgentState) -> AgentState:
    print("🔐 unregister node...")

    user_msg = state["messages"][-1].content.lower()
    updated_messages = state["messages"]


    if "yes" in user_msg or "register me" in user_msg:
        result = call_register_user.invoke({})
        if result.get("user_id"):
            updated_messages.append(AIMessage(content=f"✅ Registration started. Please fill the form: https://your-form-link.com/?user_id={result['user_id']}"))
            return {
                "status": "registered", 
                "user_id": result["user_id"], 
                "pending_user_id": None,
                "messages": updated_messages
            }


    # Case 2: User confirms they submitted the form
    if "i submitted" in user_msg or "i completed" in user_msg:
        user_id = state.get("pending_user_id")
        if user_id:
            confirm = call_confirm_registration.invoke({"user_id": user_id})
            if confirm.get("account_created") == True:
                updated_messages.append(AIMessage(content="🎉 You're now registered! How can I help you?"))
                return {
                    "status": "registered",
                    "user_id": user_id,
                    "pending_user_id": None,
                    "messages": updated_messages
                }
            else:
                updated_messages.append(AIMessage(content="🕐 Still waiting for confirmation. Please make sure you've submitted the form."))
                return {
                    **state,
                    "messages": updated_messages
                }

 
    response = llm.invoke([prompt_unregister] + state["messages"])
    return {
        **state,
        "messages": updated_messages + [response]
    }


# register node ----------------------

def register_node(state: AgentState) -> AgentState:
    print("register node...")
    state["messages"].append(AIMessage(content="Welcome back! What would you like to do?"))
    return state

# reuter node
def categorizer_router(state: AgentState) -> str:
    return "register" if state["status"] == "registered" else "unregister"


# graph ---------------------------

builder = StateGraph(AgentState)

builder.add_node("categorizer", categorizer)
builder.add_node("unregister", unregister_node)
builder.add_node("register", register_node)
builder.add_node('tools', ToolNode(tools))

builder.set_entry_point("categorizer")
builder.add_conditional_edges("categorizer", categorizer_router, {
    "register": "register",
    "unregister": "unregister"
})


builder.add_conditional_edges('unregister', tools_condition)
builder.add_edge('tools', 'unregister')

builder.add_edge("register", END)
builder.add_edge("unregister", END)

graph = builder.compile()




# # first converstaion with unregistered status and user id none
# state = {
#     "status": "unregistered",
#     "user_id": None,
#     "messages": [HumanMessage(content="hi")]
# }

# thread = {"configurable": {"thread_id": "1"}}

# # 1st: greet
# for event in graph.stream(state, thread, stream_mode="values"):
#     state = event
#     last_msg = event["messages"][-1]
#     if isinstance(last_msg, AIMessage):
#         last_msg.pretty_print()
#         print(state['status'], state.get('user_id'))
        
        

        



# # 2nd conversation----------
# state["messages"].append(HumanMessage(content="i want to book ticket"))
# for event in graph.stream(state, thread, stream_mode="values"):
#     state = event
#     last_msg = event["messages"][-1]
#     if isinstance(last_msg, AIMessage):
#         last_msg.pretty_print()
#         print(state['status'], state.get('user_id'))



# # 3rd conversation
# state["messages"].append(HumanMessage(content="yes"))
# for event in graph.stream(state, thread, stream_mode="values"):
#     state = event
#     last_msg = event["messages"][-1]
#     if isinstance(last_msg, AIMessage):
#         last_msg.pretty_print()
#         print(state['status'], state.get('user_id'))


# # 4th connversation
# state["messages"].append(HumanMessage(content="ok i have submit the form"))
# for event in graph.stream(state, thread, stream_mode="values"):
#     state = event
#     last_msg = event["messages"][-1]
#     if isinstance(last_msg, AIMessage):
#         last_msg.pretty_print()
#         print(state['status'], state.get('user_id'))


# #5th conversation
# state["messages"].append(HumanMessage(content="can i book now ?"))
# for event in graph.stream(state, thread, stream_mode="values"):
#     state = event
#     last_msg = event["messages"][-1]
#     if isinstance(last_msg, AIMessage):
#         last_msg.pretty_print()




# Initial state
state = None
thread = {"configurable": {"thread_id": "1"}}

def process_user_input(user_input: str, state: Optional[AgentState]) -> AgentState:
    # Initialize state if it's the first time
    if state is None:
        state = {
            "status": "unregistered",
            "user_id": None,
            "messages": []
        }

    # Add the new message
    state["messages"].append(HumanMessage(content=user_input))

    # Stream the graph
    for event in graph.stream(state, thread, stream_mode="values"):
        state = event
        last_msg = event["messages"][-1]
        if isinstance(last_msg, AIMessage):
            last_msg.pretty_print()
            print(f"Status: {state['status']}, User ID: {state.get('user_id')}")
    
    return state




def main():
    if len(sys.argv) < 2:
        print("Usage: isolated-node-unregister 'your message'")
        return
    user_input = sys.argv[1]
    state = None  # or load state if needed
    process_user_input(user_input, state)