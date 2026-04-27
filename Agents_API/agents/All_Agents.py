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
from agents.Agents_Workers.IT_Act_Agent_all import *
from agents.Agents_Workers.BNS_Act_Agent_all import *
from agents.Agents_Workers.BSA_Act_Agent_all import *
from agents.Agents_Workers.DPDP_Act_Agent_all import *
from agents.Agents_Workers.Reflexion_Agent import *
from agents.Agents_Workers.Websearch_Agent_all import *
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig

load_dotenv()
keys=Get_API_Keys()
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_API_KEY"] = keys.get_Langgraph_API()
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_API")


@traceable(name="identity")
def identity(state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
    Pre_suffix_obj=Prefix_Suffix()
    last_message = state["messages"][0].content
    state.update({
                "User_question": Pre_suffix_obj.get_prefix() + last_message + Pre_suffix_obj.get_suffix(),
                "User_question_IT_ACT": Pre_suffix_obj.get_prefix() + last_message + Pre_suffix_obj.get_suffix_IT_Act(),
                "User_question_BNS_ACT": Pre_suffix_obj.get_prefix() + last_message + Pre_suffix_obj.get_suffix_BNS_Act(),
                "User_question_BSA_ACT": Pre_suffix_obj.get_prefix() + last_message + Pre_suffix_obj.get_suffix_BSA_Act(),
                "User_question_DPDP_ACT": Pre_suffix_obj.get_prefix() + last_message + Pre_suffix_obj.get_suffix_BNS_Act(),
                })
    return state

class LegalGraphBuilder:
    def __init__(self, state_type):
        self.Web_Agent=Websearch_Agent()
        self.IT_Act_Agent=IT_Act_Agent()
        self.BNS_Act_Agent=BNS_Act_Agent()
        self.BSA_Act_Agent=BSA_Act_Agent()
        self.DPDP_Act_Agent=DPDP_Act_Agent()
        self.Reflexion_Agent=Reflexion_Agent()
        self.Graph = StateGraph(state_type)
        
    def add_nodes(self):
        self.Graph.add_node("start_router", identity)
        
        #Web Search Nodes
        self.Graph.add_node("generate_query", self.Web_Agent.generate_query)
        self.Graph.add_node("web_research", self.Web_Agent.web_research)
        self.Graph.add_node("reflection", self.Web_Agent.reflection)
        self.Graph.add_node("finalize_answer", self.Web_Agent.finalize_answer)

        # # IT Act Nodes
        self.Graph.add_node("IT_route_question", self.IT_Act_Agent.IT_route_question)
        self.Graph.add_node("IT_retrieve", self.IT_Act_Agent.IT_retrieve)
        self.Graph.add_node("IT_grade_documents", self.IT_Act_Agent.IT_grade_documents)
        self.Graph.add_node("IT_Act_generate_answer", self.IT_Act_Agent.IT_Act_generate_answer)
        self.Graph.add_node("IT_no_answer", self.IT_Act_Agent.IT_no_answer)
        self.Graph.add_node("IT_dummy", self.IT_Act_Agent.IT_dummy)


        # ## DPDP Nodes
        self.Graph.add_node("DPDP_route_question", self.DPDP_Act_Agent.DPDP_route_question)
        self.Graph.add_node("DPDP_retrieve", self.DPDP_Act_Agent.DPDP_retrieve)
        self.Graph.add_node("DPDP_grade_documents", self.DPDP_Act_Agent.DPDP_grade_documents)
        self.Graph.add_node("DPDP_Act_generate_answer", self.DPDP_Act_Agent.DPDP_Act_generate_answer)
        self.Graph.add_node("DPDP_no_answer", self.DPDP_Act_Agent.DPDP_no_answer)
        self.Graph.add_node("DPDP_dummy", self.DPDP_Act_Agent.DPDP_dummy)



        # # BNS Nodes
        self.Graph.add_node("BNS_route_question", self.BNS_Act_Agent.BNS_route_question)
        self.Graph.add_node("BNS_retrieve", self.BNS_Act_Agent.BNS_retrieve)
        self.Graph.add_node("BNS_grade_documents", self.BNS_Act_Agent.BNS_grade_documents)
        self.Graph.add_node("BNS_Act_generate_answer", self.BNS_Act_Agent.BNS_Act_generate_answer)
        self.Graph.add_node("BNS_no_answer", self.BNS_Act_Agent.BNS_no_answer)
        self.Graph.add_node("BNS_dummy", self.BNS_Act_Agent.BNS_dummy)
        
        # # BSA Nodes
        self.Graph.add_node("BSA_route_question", self.BSA_Act_Agent.BSA_route_question)
        self.Graph.add_node("BSA_retrieve", self.BSA_Act_Agent.BSA_retrieve)
        self.Graph.add_node("BSA_grade_documents", self.BSA_Act_Agent.BSA_grade_documents)
        self.Graph.add_node("BSA_Act_generate_answer", self.BSA_Act_Agent.BSA_Act_generate_answer)
        self.Graph.add_node("BSA_no_answer", self.BSA_Act_Agent.BSA_no_answer)
        self.Graph.add_node("BSA_dummy", self.BSA_Act_Agent.BSA_dummy)

        # Final Synthesis Node
        #self.Graph.add_node("Bare_Act_Compiled", self.Reflexion_Agent.Bare_Act_Compiled)
        self.Graph.add_node("Bare_Web_Compiled",self.Reflexion_Agent.Bare_Web_Compiled,defer=True)

    def add_edges(self):
        # Entry
        self.Graph.set_entry_point("start_router")
        
        #Web Search Edges
        self.Graph.add_edge("start_router", "generate_query")
        self.Graph.add_conditional_edges(
                                        "generate_query", self.Web_Agent.continue_to_web_research, ["web_research"]
                                        )

        self.Graph.add_edge("web_research", "reflection")
        self.Graph.add_conditional_edges(
                                        "reflection", self.Web_Agent.evaluate_research, 
                                        ["web_research", "finalize_answer"]
                                        )
        
        
        self.Graph.add_edge("finalize_answer", "Bare_Web_Compiled")
        
        # IT Act flow Web Search Edges
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
        self.Graph.add_edge("IT_Act_generate_answer", "Bare_Web_Compiled")
        self.Graph.add_edge("IT_dummy","IT_no_answer")
        self.Graph.add_edge("IT_no_answer", "Bare_Web_Compiled")

        # DPDP Act flow Web Search Edges
        self.Graph.add_edge("start_router", "DPDP_route_question")
        self.Graph.add_conditional_edges(
            "DPDP_route_question",
            lambda state: state["route_result_DPDP"],
            {
                "retrieve": "DPDP_retrieve",
                "no_answer": "DPDP_dummy"
            }
        )
        self.Graph.add_edge("DPDP_retrieve", "DPDP_grade_documents")
        self.Graph.add_edge("DPDP_grade_documents", "DPDP_Act_generate_answer")
        self.Graph.add_edge("DPDP_Act_generate_answer", "Bare_Web_Compiled")
        self.Graph.add_edge("DPDP_dummy","DPDP_no_answer")
        self.Graph.add_edge("DPDP_no_answer", "Bare_Web_Compiled")


        #BNS flow Web Search Edges
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
        self.Graph.add_edge("BNS_Act_generate_answer", "Bare_Web_Compiled")
        self.Graph.add_edge("BNS_dummy","BNS_no_answer")
        self.Graph.add_edge("BNS_no_answer","Bare_Web_Compiled")

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
        self.Graph.add_edge("BSA_Act_generate_answer","Bare_Web_Compiled")
        self.Graph.add_edge("BSA_dummy","BSA_no_answer")
        self.Graph.add_edge("BSA_no_answer", "Bare_Web_Compiled")
       
        # # Final BARE ACT Agents Combined  Edges
        #self.Graph.add_edge("Bare_Act_Compiled", "Bare_Web_Compiled")

        self.Graph.add_edge("Bare_Web_Compiled",END)
        
        #self.Graph.add_edge("Bare_Act_Compiled",END)
        

    def build(self):
        self.add_nodes()
        self.add_edges()
        return self.Graph.compile(name="VLANC Parallel Law Agents")



config = RunnableConfig(configurable={"tracing": True}, run_name="VLANC-ALL-LEGAL-AGENT")
_graph_builder = LegalGraphBuilder(OverallAgentsState)
_app = _graph_builder.build()
_app = _app.with_config(config)


