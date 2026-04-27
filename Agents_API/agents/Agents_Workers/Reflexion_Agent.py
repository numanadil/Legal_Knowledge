import os
import time
from agents.EVR import *
from agents.utils import *
from agents.states import *
from agents.prompts import *
from agents.ai_model import *
from langsmith import traceable
from agents.configuration import Configuration
from langchain_core.runnables import RunnableConfig



class Reflexion_Agent:
    def __init__(self):
        self.Reflexion_Prompt_obj=Reflexion_Prompt() 
        self.model_1=Ai_Models_Reflexion()
    
    @traceable(name="Bare_Web_Compiled")
    def Bare_Web_Compiled(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        
        configurable = Configuration.from_runnable_config(config)
        prompt=self.Reflexion_Prompt_obj.get_reflexion_web_bare_act_prompt(
                                                                            " ".join(state.get("IT_Act_Agent_answer", [])),
                                                                            " ".join(state.get("BNS_Act_Agent_answer", [])),
                                                                            " ".join(state.get("BSA_Act_Agent_answer", [])),
                                                                            state["Web_Search_answer"],
                                                                            state["User_question"],
                                                                            " ".join(state.get("DPDP_Act_Agent_answer", []))
                                                                          )
        response=self.model_1.get_models(model_name=configurable.reflexion_model, prompt=prompt)
        state["Web_Bare_Act_Reflexion_answers"]=response
        state["event"]="Generating Answers.."
        print("state:::::::",state)
        
        return state
    
    
    @traceable(name="Bare_Act_Compiled")
    def Bare_Act_Compiled(self, state: OverallAgentsState, config: RunnableConfig) -> OverallAgentsState:
        
        configurable = Configuration.from_runnable_config(config)
        prompt = self.Reflexion_Prompt_obj.get_bare_act_reflexion_prompt(
                                                                        " ".join(state.get("IT_Act_Agent_answer", [])),
                                                                        " ".join(state.get("BNS_Act_Agent_answer", [])),
                                                                        " ".join(state.get("BSA_Act_Agent_answer", [])),
                                                                        " ".join(state.get("DPDP_Act_Agent_answer", []))
                                                                        )

        response = self.model_1.get_models(model_name=configurable.reflexion_model, prompt=prompt)
        state["event"]="Generating Answers.."
        state["Bare_Act_Reflexion_answer"] = response
        # state["messages"] = [AIMessage(content=response)]

        return state

