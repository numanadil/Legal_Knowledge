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
def identity(state: OverallAgentsState_BSA_Act,config: RunnableConfig) -> OverallAgentsState_BSA_Act:
    Pre_suffix_obj=Prefix_Suffix()
    # print(state["messages"][0].content)
    last_message = state["messages"][0].content
    state.update({
                "User_question": Pre_suffix_obj.get_prefix() + last_message + Pre_suffix_obj.get_suffix(),
                "User_question_BSA_ACT": Pre_suffix_obj.get_prefix() + last_message + Pre_suffix_obj.get_suffix_BSA_Act(),
                })
    return state

class LegalGraphBuilder_BSA:
    def __init__(self, state_type):
        self.BSA_Act_Agent=BSA_Act_Agent()
        self.Graph = StateGraph(state_type)
        
    def add_nodes(self):
        self.Graph.add_node("start_router", identity)
        
        # BSA Nodes
        self.Graph.add_node("BSA_route_question", self.BSA_Act_Agent.BSA_route_question)
        self.Graph.add_node("BSA_retrieve", self.BSA_Act_Agent.BSA_retrieve)
        self.Graph.add_node("BSA_grade_documents", self.BSA_Act_Agent.BSA_grade_documents)
        self.Graph.add_node("BSA_Act_generate_answer", self.BSA_Act_Agent.BSA_Act_generate_answer)
        self.Graph.add_node("BSA_no_answer", self.BSA_Act_Agent.BSA_no_answer)
        self.Graph.add_node("BSA_dummy", self.BSA_Act_Agent.BSA_dummy)

    def add_edges(self):
        # Entry
        self.Graph.set_entry_point("start_router")
        
        # BSA flow Web Search Edges
        self.Graph.add_edge("start_router", "BSA_route_question")
        self.Graph.add_conditional_edges(
            "BSA_route_question",
            lambda state: state["route_result_BSA"],
            {
                "retrieve": "BSA_retrieve",
                "no_answer": "BSA_dummy"
            }
        )
        self.Graph.add_edge("BSA_retrieve", "BSA_grade_documents")
        self.Graph.add_edge("BSA_grade_documents", "BSA_Act_generate_answer")
        self.Graph.add_edge("BSA_Act_generate_answer",END)
        self.Graph.add_edge("BSA_dummy","BSA_no_answer")
        self.Graph.add_edge("BSA_no_answer", END)

    def build(self):
        self.add_nodes()
        self.add_edges()
        return self.Graph.compile(name="VLANC BSA Parallel Law Agents")



config_BSA = RunnableConfig(configurable={"tracing": True}, run_name="VLANC-LEGAL-AGENT")
_graph_builder_BSA = LegalGraphBuilder_BSA(OverallAgentsState_BSA_Act)
_app_BSA = _graph_builder_BSA.build()
_app_BSA = _app_BSA.with_config(config_BSA)

