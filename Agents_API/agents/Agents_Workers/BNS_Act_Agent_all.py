import os
from agents.EVR import *
from agents.utils import *
from agents.states import *
from agents.prompts import *
from agents.ai_model import *
from langsmith import traceable
from agents.configuration import Configuration
from langchain_core.runnables import RunnableConfig


class BNS_Act_Agent:
    def __init__(self):
        self.similar_docs=int(os.getenv("similar_docs"))
        config_params = Configuration()
        if config_params.BNS_Act_Vector_db_Status:
            self.EVR_obj_BNS=EVR(model_name=os.getenv("EMB_MODEL"),persist_directory=config_params.BNS_Act_Vector_db_Path,k=self.similar_docs,dbtype=config_params.BNS_Act_Vector_db_Type)
        else:
            raise Exception("Vector DB Status check failed: IT Act Vector DB is not active.")
        self.BNS_emb=self.EVR_obj_BNS.get_embedding()
        self.BNS_vectordb=self.EVR_obj_BNS.get_vectordb()
        self.BNS_retriever=self.EVR_obj_BNS.get_retriever()
        self.BNS_Template_obj=BNS_Act_Prompt_Templates()
        self.model=Ai_Models_Bare_Acts()
    
    @traceable(name="BNS_route_question")   
    def BNS_route_question(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        prompt = self.BNS_Template_obj.get_router_prompt(state["User_question_BNS_ACT"])
        response = self.model.get_models(model_name=configurable.bare_act_router_model, prompt=prompt)
        route = "retrieve" if response and "VECTORSTORE" in response.upper() else "no_answer"
        state["route_result_BNS"] = route
        return state
    
    @traceable(name="BNS_retrieve")
    def BNS_retrieve(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        state["BNS_Act_documents"] = self.BNS_retriever.invoke(state["User_question_BNS_ACT"])
        return state
    
    @traceable(name="BNS_dummy")
    def BNS_dummy(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        return state
    
    @traceable(name="BNS_grade_documents")
    def BNS_grade_documents(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        filtered_docs = []
        for doc in state["BNS_Act_documents"]:
            prompt = self.BNS_Template_obj.get_grader_prompt(state["User_question_BNS_ACT"],document=doc.page_content)
            result = self.model.get_models(model_name=configurable.bare_act_grader_model, prompt=prompt)
            if "YES" in result.upper():
                filtered_docs.append(doc)
        state["BNS_Act_documents"] = filtered_docs
        return state
    
    @traceable(name="BNS_Act_generate_answer")
    def BNS_Act_generate_answer(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        # if len(state["BNS_Act_documents"])>0:
        #     state["BNS_Act_Agent_answer"] = ["No relevant documents found."]
        #     return state
        # else:
        #     configurable = Configuration.from_runnable_config(config)
        #     context = "\n\n".join(doc.page_content for doc in state["BNS_Act_documents"])
        #     prompt = self.BNS_Template_obj.get_answer_prompt(context=context, question=state["User_question_BNS_ACT"])
        #     response = self.model.get_models(model_name=configurable.bare_act_answer_model, prompt=prompt)
        #     state["BNS_Act_Agent_answer"] = [response]
        #     return state
        configurable = Configuration.from_runnable_config(config)
        context = "\n\n".join(doc.page_content for doc in state["BNS_Act_documents"])
        prompt = self.BNS_Template_obj.get_answer_prompt(context=context, question=state["User_question_BNS_ACT"])
        response = self.model.get_models(model_name=configurable.bare_act_answer_model, prompt=prompt)
        state["BNS_Act_Agent_answer"] = [response]
        return state
    
    @traceable(name="BNS_no_answer")
    def BNS_no_answer(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        state["BNS_Act_Agent_answer"] = ["I am unable to answer this question as it is outside my knowledge base."]
        return state
        
    
