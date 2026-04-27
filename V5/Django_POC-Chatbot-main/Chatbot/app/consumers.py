import uuid
import json
import traceback
from .Langserve_streamer import *
from django.utils import timezone
from channels.generic.websocket import WebsocketConsumer
from .models import (
                     Extension_Data,
                     Extension_Data_IT,
                     Extension_Data_BNS,
                     Extension_Data_DPDP,
                     Extension_Data_BSA,
                     Extension_Data_Web_Search,
                     Langgraph_Deployed_Agent_Name
                    )

class Web_Search_Extension(WebsocketConsumer):
    def connect(self):
        
        self.accept()
        print("WebSocket connected ")
        self.latest_agent = Langgraph_Deployed_Agent_Name.objects.latest('Updated_on')
        self.runner_url=str(self.latest_agent.API_Link).strip()
        self.runner = LangGraphStreamRunner(url=self.runner_url)

    def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            print("Invalid JSON received:", text_data)
            return

        message = text_data_json.get("data") or text_data_json.get("message")
        if not message:
            print("No message field found in:", text_data_json)
            return
        else:
            response = {"reply": f"Server received: {message}"}
            try:
                Thread_Id=uuid.uuid1()
                result = self.runner.run(
                                    agent_name=str(self.latest_agent.Web_Search_Agent).strip(),
                                    input_payload={"messages": str(message).strip()},
                                    thread=Thread_Id

                                    )
                obj_data = Extension_Data_Web_Search(
                                        Thread_Id=Thread_Id,
                                        User_Querry= str(message).strip(), 
                                        Web_Answer=result.get("Web_Search_answer", "No Answer"),
                                        Search_Querry=result.get("search_query", []) ,
                                        Sources_Gathered=result.get("sources_gathered", []) ,
                                        Updated_on=timezone.now()
                                        )
                obj_data.save()
                response_data = {
                                "status": 200,
                                "Web_Search_answer": result.get("Web_Search_answer", "")
                                }
                self.send(text_data=json.dumps(response_data))
            except Exception as e:
                print(f"Error in Web Search Agent: {e}")
                traceback.print_exc()
                response_data = {
                                "status": 500,
                                 "error": str(e)
                                }
                self.send(text_data=json.dumps(response_data))
    def disconnect(self, close_code):
        print(f"Web Search WebSocket disconnected  (code: {close_code})")



class DPDP_Extension(WebsocketConsumer):
    def connect(self):
        
        self.accept()
        print("WebSocket connected ")
        self.latest_agent = Langgraph_Deployed_Agent_Name.objects.latest('Updated_on')
        self.runner_url=str(self.latest_agent.API_Link).strip()
        self.runner = LangGraphStreamRunner(url=self.runner_url)

    def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            print("Invalid JSON received:", text_data)
            return

        message = text_data_json.get("data") or text_data_json.get("message")
        if not message:
            print("No message field found in:", text_data_json)
            return
        else:
            try:
                Thread_Id=uuid.uuid1()
                response = {"reply": f"Server received: {message}"}
                result = self.runner.run(
                                    agent_name=str(self.latest_agent.DPDP_Agent).strip(),
                                    input_payload={"messages": str(message).strip()},
                                    thread=Thread_Id
                                    )

                
                
                obj_data = Extension_Data_DPDP(
                                        Thread_Id=Thread_Id,
                                        User_Querry= str(message).strip(), 
                                        DPDP_Act_Answer=result.get("DPDP_Act_Agent_answer", "No Answer"),
                                        DPDP_Act_Document="\n".join([
                                                                    d["page_content"] 
                                                                    for d in result.get("DPDP_ACT_documents", []) 
                                                                    if isinstance(d, dict) and "page_content" in d and d["page_content"].strip()
                                                                    ]),
                                        Updated_on=timezone.now()
                                        )
                obj_data.save()
                
                response_data = {
                                "status": 200,
                                "DPDP_Act_Agent_answer": " ".join(result.get("DPDP_Act_Agent_answer", ""))
                                }
                self.send(text_data=json.dumps(response_data))
            except Exception as e:
                print(f"Error in DPDP Agent: {e}")
                traceback.print_exc()
                response_data = {
                                "status": 500,
                                 "error": str(e)
                                }
                self.send(text_data=json.dumps(response_data))
            
    def disconnect(self, close_code):
        print(f"DPDP ACT WebSocket disconnected  (code: {close_code})")





class IT_Extension(WebsocketConsumer):
    def connect(self):
        
        self.accept()
        print("WebSocket connected ")
        self.latest_agent = Langgraph_Deployed_Agent_Name.objects.latest('Updated_on')
        self.runner_url=str(self.latest_agent.API_Link).strip()
        self.runner = LangGraphStreamRunner(url=self.runner_url)

    def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            print("Invalid JSON received:", text_data)
            return

        message = text_data_json.get("data") or text_data_json.get("message")
        if not message:
            print("No message field found in:", text_data_json)
            return
        else:
            try:
                Thread_Id=uuid.uuid1()
                response = {"reply": f"Server received: {message}"}
                result = self.runner.run(
                                    agent_name=str(self.latest_agent.IT_Agent).strip(),
                                    input_payload={"messages": str(message).strip()},
                                    thread=Thread_Id
                                    )
                
                obj_data = Extension_Data_IT(
                                        Thread_Id=Thread_Id,
                                        User_Querry= str(message).strip(), 
                                        IT_Act_Answer=result.get("IT_Act_Agent_answer", "No Answer"),
                                        IT_Act_Document="\n".join([
                                                                    d["page_content"] 
                                                                    for d in result.get("IT_ACT_documents", []) 
                                                                    if isinstance(d, dict) and "page_content" in d and d["page_content"].strip()
                                                                    ]),
                                        Updated_on=timezone.now()
                                        )
                obj_data.save()
                
                response_data = {
                                "status": 200,
                                "IT_Act_Agent_answer": " ".join(result.get("IT_Act_Agent_answer", ""))
                                }
                self.send(text_data=json.dumps(response_data))
            except Exception as e:
                print(f"Error in IT Agent: {e}")
                traceback.print_exc()
                response_data = {
                                "status": 500,
                                 "error": str(e)
                                }
                self.send(text_data=json.dumps(response_data))
            
    def disconnect(self, close_code):
        print(f"IT ACT WebSocket disconnected  (code: {close_code})")


class BNS_Extension(WebsocketConsumer):
    def connect(self):
        
        self.accept()
        print("WebSocket connected ")
        self.latest_agent = Langgraph_Deployed_Agent_Name.objects.latest('Updated_on')
        self.runner_url=str(self.latest_agent.API_Link).strip()
        self.runner = LangGraphStreamRunner(url=self.runner_url)

    def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            print("Invalid JSON received:", text_data)
            return

        message = text_data_json.get("data") or text_data_json.get("message")
        if not message:
            print("No message field found in:", text_data_json)
            return
        else:
            try:
                Thread_Id=uuid.uuid1()
                print("Thread_Id",Thread_Id)
                response = {"reply": f"Server received: {message}"}
                result = self.runner.run(
                                    agent_name=str(self.latest_agent.BNS_Agent).strip(),
                                    input_payload={"messages": str(message).strip()},
                                    thread=str(Thread_Id)
                                    )
                obj_data = Extension_Data_BNS(
                                        Thread_Id=Thread_Id,
                                        User_Querry= str(message).strip(), 
                                        BNS_Act_Answer=result.get("BNS_Act_Agent_answer", "No Answer"),
                                        BNS_Act_Document="\n".join([
                                                                    d["page_content"] 
                                                                    for d in result.get("BNS_ACT_documents", []) 
                                                                    if isinstance(d, dict) and "page_content" in d and d["page_content"].strip()
                                                                    ]),
                                        Updated_on=timezone.now()
                                        )
                obj_data.save()
                
                response_data = {
                                "status": 200,
                                "BNS_Act_Agent_answer": " ".join(result.get("BNS_Act_Agent_answer", "No Answer"))
                                }
                self.send(text_data=json.dumps(response_data))
            except Exception as e:
                print(f"Error in BNS Agent: {e}")
                traceback.print_exc()
                response_data = {
                                "status": 500,
                                 "error": str(e)
                                }
                self.send(text_data=json.dumps(response_data))
            
    def disconnect(self, close_code):
        print(f"BNS ACT WebSocket disconnected  (code: {close_code})")

class BSA_Extension(WebsocketConsumer):
    def connect(self):
        self.accept()
        print("WebSocket connected ")
        self.latest_agent = Langgraph_Deployed_Agent_Name.objects.latest('Updated_on')
        self.runner_url=str(self.latest_agent.API_Link).strip()
        self.runner = LangGraphStreamRunner(url=self.runner_url)

    def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            print("Invalid JSON received:", text_data)
            return

        message = text_data_json.get("data") or text_data_json.get("message")
        if not message:
            print("No message field found in:", text_data_json)
            return
        else:
            try:
                Thread_Id=uuid.uuid1()
                response = {"reply": f"Server received: {message}"}
                result = self.runner.run(
                                    agent_name=str(self.latest_agent.BSA_Agent).strip(),
                                    input_payload={"messages": str(message).strip()},
                                    thread=Thread_Id
                                    )
                obj_data = Extension_Data_BSA(
                                        Thread_Id=Thread_Id,
                                        User_Querry= str(message).strip(), 
                                        BSA_Act_Answer=result.get("BSA_Act_Agent_answer", "No Answer"),
                                        BSA_Act_Document="\n".join([
                                                                    d["page_content"] 
                                                                    for d in result.get("BSA_ACT_documents", []) 
                                                                    if isinstance(d, dict) and "page_content" in d and d["page_content"].strip()
                                                                    ]),
                                        Updated_on=timezone.now()
                                        )
                obj_data.save()
                response_data = {
                                "status": 200,
                                "BSA_Act_Agent_answer": " ".join(result.get("BSA_Act_Agent_answer", "No Answer"))
                                }
                self.send(text_data=json.dumps(response_data))
            except Exception as e:
                print(f"Error in BSA Agent: {e}")
                traceback.print_exc()
                response_data = {
                                "status": 500,
                                 "error": str(e)
                                }
                self.send(text_data=json.dumps(response_data))
            
    def disconnect(self, close_code):
        print(f"BSA ACT WebSocket disconnected  (code: {close_code})")



class Chat_Extension(WebsocketConsumer):
    def connect(self):
        self.accept()
        print("WebSocket connected ")
        self.latest_agent = Langgraph_Deployed_Agent_Name.objects.latest('Updated_on')
        self.runner_url=str(self.latest_agent.API_Link).strip()
        self.runner = LangGraphStreamRunner(url=self.runner_url)

    def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            print("Invalid JSON received:", text_data)
            return

        message = text_data_json.get("data") or text_data_json.get("message")
        if not message:
            print("No message field found in:", text_data_json)
            return

    def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            print("Invalid JSON received:", text_data)
            return

        message = text_data_json.get("data") or text_data_json.get("message")
        if not message:
            print("No message field found in:", text_data_json)
            return
        else:
            try:
                Thread_Id=uuid.uuid1()
                response = {"reply": f"Server received: {message}"}
                result = self.runner.run(
                                    agent_name=str(self.latest_agent.Chat).strip(),
                                    input_payload={"messages": str(message).strip()},
                                    thread=Thread_Id
                                    )
                
                
                # obj_data = Extension_Data(
                #                         Thread_Id=Thread_Id,
                #                         User_Querry= str(message).strip(), 
                #                         Web_Search_Answer=result.get("Web_Search_answer", "No Answer"),
                #                         IT_Act_Answer=result.get("IT_Act_Agent_answer", "No Answer"),
                #                         IT_Act_Document="\n".join([
                #                                                     d["page_content"] 
                #                                                     for d in result.get("IT_ACT_documents", []) 
                #                                                     if isinstance(d, dict) and "page_content" in d and d["page_content"].strip()
                #                                                     ]),
                #                         BNS_Act_Answer=result.get("BNS_Act_Agent_answer", "No Answer"),
                #                         BNS_Act_Document="\n".join([
                #                                                     d["page_content"] 
                #                                                     for d in result.get("BNS_ACT_documents", []) 
                #                                                     if isinstance(d, dict) and "page_content" in d and d["page_content"].strip()
                #                                                     ]),
                #                         BSA_Act_Answer=result.get("BSA_Act_Agent_answer", "No Answer"),
                #                         BSA_Act_Document="\n".join([
                #                                                     d["page_content"] 
                #                                                     for d in result.get("BSA_ACT_documents", []) 
                #                                                     if isinstance(d, dict) and "page_content" in d and d["page_content"].strip()
                #                                                     ]),
                #                         DPDP_Act_Answer=result.get("DPDP_Act_Agent_answer", "No Answer"),
                #                         DPDP_Act_Document="\n".join([
                #                                                     d["page_content"] 
                #                                                     for d in result.get("DPDP_ACT_documents", []) 
                #                                                     if isinstance(d, dict) and "page_content" in d and d["page_content"].strip()
                #                                                     ]),
                #                         Acts_Combined_Answers=result.get("Bare_Act_Reflexion_answer", "No Answer"),
                #                         Web_Bare_Act_Combined=result.get("Web_Bare_Act_Reflexion_answers", " No Answer"),
                #                         Updated_on=timezone.now()
                #                         )
                # obj_data.save()
                response_data = {
                                "status": 200,
                                "Web_Bare_Act_Reflexion_answers": result.get("Web_Bare_Act_Reflexion_answers", "No Answer")
                                }
                self.send(text_data=json.dumps(response_data))
                
            except Exception as e:
                print(f"Error in Chat Agent: {e}")
                traceback.print_exc()
                response_data = {
                                "status": 500,
                                 "error": str(e)
                                }
                self.send(text_data=json.dumps(response_data))
            
    def disconnect(self, close_code):
        print(f"Chat WebSocket disconnected  (code: {close_code})")
