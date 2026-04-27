import os
from agents.EVR import *
from agents.utils import *
from agents.states import *
from agents.prompts import *
from agents.ai_model import *
from dotenv import load_dotenv
from langsmith import traceable
from langgraph.graph import StateGraph
from langgraph.graph import StateGraph, END
from agents.Agents_Workers.IT_Act_Agent import *
from agents.Agents_Workers.BNS_Act_Agent import *
from agents.Agents_Workers.BSA_Act_Agent import *
from agents.Agents_Workers.Reflexion_Agent import *
from agents.Agents_Workers.Websearch_Agent import *
from langchain_core.runnables import RunnableConfig


load_dotenv()

keys=Get_API_Keys()
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_API_KEY"] = keys.get_Langgraph_API()
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGCHAIN_API")




@traceable(name="identity")
def identity(state: OverallAgentsState_Web_Search,config: RunnableConfig) -> OverallAgentsState_Web_Search:
    Pre_suffix_obj=Prefix_Suffix()
    # print(state["messages"][0].content)
    last_message = state["messages"][0].content
    state.update({
                "User_question": Pre_suffix_obj.get_prefix() + last_message + Pre_suffix_obj.get_suffix(),
                })
    return state

class LegalGraphBuilder_Web_Search:
    def __init__(self, state_type):
        self.Web_Agent=Websearch_Agent()
        self.Graph = StateGraph(state_type)
        
    def add_nodes(self):
        self.Graph.add_node("start_router", identity)
        
        #Web Search Nodes
        self.Graph.add_node("generate_query", self.Web_Agent.generate_query)
        self.Graph.add_node("web_research", self.Web_Agent.web_research)
        self.Graph.add_node("reflection", self.Web_Agent.reflection)
        self.Graph.add_node("finalize_answer", self.Web_Agent.finalize_answer)
    
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
        
        self.Graph.add_edge("finalize_answer", END)
        
    
    def build(self):
        self.add_nodes()
        self.add_edges()
        return self.Graph.compile(name="VLANC Web Search Parallel Law Agents")



config_Web_Search = RunnableConfig(configurable={"tracing": True}, run_name="VLANC-Web_Search-LEGAL-AGENT")
_graph_builder_Web_Search = LegalGraphBuilder_Web_Search(OverallAgentsState_Web_Search)
_app_Web_Search = _graph_builder_Web_Search.build()
_app_Web_Search = _app_Web_Search.with_config(config_Web_Search)
