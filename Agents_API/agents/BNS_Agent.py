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
from agents.Agents_Workers.BNS_Act_Agent import *
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

load_dotenv()

keys=Get_API_Keys()
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_API_KEY"] = keys.get_Langgraph_API()
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_API")



@traceable(name="identity")
def identity(state: OverallAgentsState_BNS_Act,config: RunnableConfig) -> OverallAgentsState_BNS_Act:
    Pre_suffix_obj=Prefix_Suffix()
    # print(state["messages"][0].content)
    last_message = state["messages"][0].content
    state.update({
                "User_question": Pre_suffix_obj.get_prefix() + last_message + Pre_suffix_obj.get_suffix(),
                "User_question_BNS_ACT": Pre_suffix_obj.get_prefix() + last_message + Pre_suffix_obj.get_suffix_BNS_Act(),
                })
    return state

class LegalGraphBuilder_BNS:
    def __init__(self, state_type):
        self.BNS_Act_Agent=BNS_Act_Agent()
        self.Graph = StateGraph(state_type)
        
    def add_nodes(self):
        self.Graph.add_node("start_router", identity)
        
        # BNS Nodes
        self.Graph.add_node("BNS_route_question", self.BNS_Act_Agent.BNS_route_question)
        self.Graph.add_node("BNS_retrieve", self.BNS_Act_Agent.BNS_retrieve)
        self.Graph.add_node("BNS_grade_documents", self.BNS_Act_Agent.BNS_grade_documents)
        self.Graph.add_node("BNS_Act_generate_answer", self.BNS_Act_Agent.BNS_Act_generate_answer)
        self.Graph.add_node("BNS_no_answer", self.BNS_Act_Agent.BNS_no_answer)
        self.Graph.add_node("BNS_dummy", self.BNS_Act_Agent.BNS_dummy)
    
    def add_edges(self):
        # Entry
        self.Graph.set_entry_point("start_router")
        # BNS flow Web Search Edges
        self.Graph.add_edge("start_router", "BNS_route_question")
        self.Graph.add_conditional_edges(
            "BNS_route_question",
            lambda state: state["route_result_BNS"],
            {
                "retrieve": "BNS_retrieve",
                "no_answer": "BNS_dummy"
            }
        )
        self.Graph.add_edge("BNS_retrieve", "BNS_grade_documents")
        self.Graph.add_edge("BNS_grade_documents", "BNS_Act_generate_answer")
        self.Graph.add_edge("BNS_Act_generate_answer", END)
        self.Graph.add_edge("BNS_dummy","BNS_no_answer")
        self.Graph.add_edge("BNS_no_answer",END)

    def build(self):
        self.add_nodes()
        self.add_edges()
        return self.Graph.compile(name="VLANC BNS Parallel Law Agents")



config_BNS = RunnableConfig(configurable={"tracing": True}, run_name="VLANC-BNS-LEGAL-AGENT")
_graph_builder_BNS = LegalGraphBuilder_BNS(OverallAgentsState_BNS_Act)
_app_BNS = _graph_builder_BNS.build()
_app_BNS = _app_BNS.with_config(config_BNS)

