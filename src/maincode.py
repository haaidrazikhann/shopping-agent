import asyncio
from typing import Dict, Any, List
from langchain_core.messages import ToolMessage, AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.func import task,entrypoint
from langgraph.graph import START, END, StateGraph,add_messages
from langgraph.prebuilt import ToolNode
from functions import tools, toolkit
from llms import llama
from states import State

sys_msg = """You are a friendly and helpful shopping assistant, here to make the shopping experience smooth and enjoyable. Start by introducing yourself and asking how you can assist the user.  

You can help with the following:  
- Searching for products  
- Adding items to the cart  
- Removing items from the cart  
- Viewing the cart  
- Proceeding to checkout  

When a user searches for products, display relevant options and ask if they’d like to add any to their cart. After adding an item, check if they want to continue shopping or proceed to checkout. Guide them step by step and ensure they have a seamless experience."""


@task
def call_model(messages):
    """Call model with a sequence of messages."""
    response = llama.bind_tools(tools).invoke([sys_msg] + messages)
    return response


@task
def call_tool(tool_call):
    tool = toolkit[tool_call["name"]]
    observation = tool.invoke(tool_call["args"])
    return ToolMessage(content=observation, tool_call_id=tool_call["id"])


checkpointer = MemorySaver()


@entrypoint(checkpointer=checkpointer)
def agent(messages, previous):
    if previous is not None:
        messages = add_messages(previous, messages)

    llm_response = call_model(messages).result()
    while True:
        if not llm_response.tool_calls:
            break

        tool_result_futures = [
            call_tool(tool_call) for tool_call in llm_response.tool_calls
        ]
        tool_results = [fut.result() for fut in tool_result_futures]

        # Append to message list
        messages = add_messages(messages, [llm_response, *tool_results])

        # Call model again
        llm_response = call_model(messages).result()

    # Generate final response
    messages = add_messages(messages, llm_response)
    return entrypoint.final(value=llm_response, save=messages)


config = {"configurable": {"thread_id": "1"}}

async def conversation_loop():
    while True:
        inp = input("\nEnter (or type 'exit' to quit): ")
        if inp.lower() == "exit":
            print("Exiting the shopping assistant. Have a great day!")
            break

        user_message = {"role": "user", "content": f"{inp}"}
        print("\nUser:", inp)

        for step in agent.stream([user_message], config):
            for task_name, message in step.items():
                if task_name == "agent":
                    continue  # Just print task updates
                print(f"\n{task_name}:")
                message.pretty_print()


# Run the agent and stream the messages to the console.
async def main() -> None:
    await conversation_loop()


def run_main():
    asyncio.run(main())

if __name__ == "__main__":
    run_main()