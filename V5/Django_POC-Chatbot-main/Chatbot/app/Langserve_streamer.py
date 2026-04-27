import uuid
import asyncio
from typing import Optional, Any, Dict
from langgraph_sdk import get_client
"""
multitask_strategy="reject"
multitask_strategy="enqueue",
 multitask_strategy="interrupt",
 multitask_strategy="rollback",
"""

class LangGraphStreamRunner:
    def __init__(self, url: str):
        self.client = get_client(url=url)
        self.output_data: Optional[Dict[str, Any]] = None
        self.multitask_strategy="rollback"
    async def _stream_handler(
                            self,
                            agent_name: str,
                            input_payload: Dict[str, Any],
                            thread
                            ) -> None:
        try:
            print(thread)
            async for chunk in self.client.runs.stream(None, 
                                                      agent_name, 
                                                      input=input_payload,
                                                      multitask_strategy=self.multitask_strategy
                                                      ):
                if isinstance(chunk.data, dict):
                    data = chunk.data
                    event = data.get("event", "").strip()
                    if event == "Generating Answers..":
                        self.output_data = data  
                        # print("self.output_data::::",self.output_data)
        except Exception as e:
            self.output_data = {"error": str(e)}

    def run(
            self,
            agent_name: str,
            input_payload: Dict[str, Any],
            thread
            ) -> Optional[Dict[str, Any]]:
        asyncio.run(self._stream_handler(agent_name, input_payload,thread))
        return self.output_data
