from langgraph_sdk import get_client
import asyncio

client = get_client(url="http://localhost:2024")

async def main():
    async for chunk in client.runs.stream(
                                         None,  
                                        "agent_WS_test", 
                                        input={
                                                "messages":  
                                                "What is LangGraph?",
                                              },
                                        ):
        print(f"Receiving new event of type: {chunk.event}...")
        if isinstance(chunk.data, dict):
                data = chunk.data
                print("data:::",data)
                # user_q = data.get("User_question", "No question found.")
                # print("User Question:")
                # print(user_q, "\n")
                # event = data.get("event", [])
                # if event:
                #         print("event:")
                #         print(event) 
                #         if event=="Generating Answers..":
                #                 print(data.get("BSA_Act_Agent_answer", "No question found."))
                
    print("\n\n")


asyncio.run(main())