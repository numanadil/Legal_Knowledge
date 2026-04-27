import os
import sys
from agents.EVR import *
from agents.utils import *
from agents.states import *
from agents.prompts import *
from agents.ai_model import *
from dotenv import load_dotenv
from langsmith import traceable
from langgraph.graph import StateGraph
from agents.Agents_Workers.IT_Act_Agent import *
from agents.Agents_Workers.BNS_Act_Agent import *
from agents.Agents_Workers.BSA_Act_Agent import *
from agents.Agents_Workers.Reflexion_Agent import *
from agents.Agents_Workers.Websearch_Agent import *
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

load_dotenv()

keys=Get_API_Keys()
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_API_KEY"] = keys.get_Langgraph_API()
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_API")




@traceable(name="identity")
def identity(state: OverallAgentsState_IT_Act,config: RunnableConfig) -> OverallAgentsState_IT_Act:
    Pre_suffix_obj=Prefix_Suffix()
    # print(state["messages"][0].content)
    last_message = state["messages"][0].content
    state.update({
                "User_question": Pre_suffix_obj.get_prefix() + last_message + Pre_suffix_obj.get_suffix(),
                "User_question_IT_ACT": Pre_suffix_obj.get_prefix() + last_message + Pre_suffix_obj.get_suffix_IT_Act(),
                
                })
    return state

class LegalGraphBuilder_IT:
    def __init__(self, state_type):
        self.IT_Act_Agent=IT_Act_Agent()
        self.Graph = StateGraph(state_type)
        
    def add_nodes(self):
        self.Graph.add_node("start_router", identity)
        
       
        # IT Act Nodes
        self.Graph.add_node("IT_route_question", self.IT_Act_Agent.IT_route_question)
        self.Graph.add_node("IT_retrieve", self.IT_Act_Agent.IT_retrieve)
        self.Graph.add_node("IT_grade_documents", self.IT_Act_Agent.IT_grade_documents)
        self.Graph.add_node("IT_Act_generate_answer", self.IT_Act_Agent.IT_Act_generate_answer)
        self.Graph.add_node("IT_no_answer", self.IT_Act_Agent.IT_no_answer)
        self.Graph.add_node("IT_dummy", self.IT_Act_Agent.IT_dummy)

    def add_edges(self):
        # Entry
        self.Graph.set_entry_point("start_router")
        
        # IT Act flow 
        self.Graph.add_edge("start_router", "IT_route_question")
        self.Graph.add_conditional_edges(
            "IT_route_question",
            lambda state: state["route_result_IT"],
            {
                "retrieve": "IT_retrieve",
                "no_answer": "IT_dummy"
            }
        )
        self.Graph.add_edge("IT_retrieve", "IT_grade_documents")
        self.Graph.add_edge("IT_grade_documents", "IT_Act_generate_answer")
        self.Graph.add_edge("IT_Act_generate_answer", END)
        self.Graph.add_edge("IT_dummy","IT_no_answer")
        self.Graph.add_edge("IT_no_answer", END)

    def build(self):
        self.add_nodes()
        self.add_edges()
        return self.Graph.compile(name="VLANC IT Parallel Law Agents")



config_IT = RunnableConfig(configurable={"tracing": True}, run_name="VLANC-IT-LEGAL-AGENT")
_graph_builder_IT = LegalGraphBuilder_IT(OverallAgentsState_IT_Act)
_app_IT = _graph_builder_IT.build()
_app_IT = _app_IT.with_config(config_IT)
