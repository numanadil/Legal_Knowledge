import os
from ..EVR import *
from ..utils import *
from ..states import *
from ..prompts import *
from ..ai_model import *
from langsmith import traceable
from ..configuration import Configuration
from langchain_core.runnables import RunnableConfig


class DPDP_Act_Agent:
    def __init__(self):
        config_params = Configuration()
        self.similar_docs=int(os.getenv("similar_docs"))
        if config_params.DPDP_Act_Vector_db_Status:
            self.EVR_obj_DPDP=EVR(model_name=os.getenv("EMB_MODEL"),persist_directory=config_params.DPDP_Act_Vector_db_Path,k=self.similar_docs,dbtype=config_params.DPDP_Act_Vector_db_Type)
        else:
            raise Exception("Vector DB Status check failed: DPDP Act Vector DB is not active.")
        self.DPDP_emb=self.EVR_obj_DPDP.get_embedding()
        self.DPDP_vectordb=self.EVR_obj_DPDP.get_vectordb()
        self.DPDP_retriever=self.EVR_obj_DPDP.get_retriever()
        self.DPDP_Template_obj=DPDP_Act_Prompt_Templates()
        self.model=Ai_Models_Bare_Acts()
    
    @traceable(name="DPDP_route_question")   
    def DPDP_route_question(self,state: OverallAgentsState_DPDP_Act,config: RunnableConfig) -> OverallAgentsState_DPDP_Act:
        configurable = Configuration.from_runnable_config(config)
        prompt = self.DPDP_Template_obj.get_router_prompt(state["User_question_DPDP_ACT"])
        response = self.model.get_models(model_name=configurable.bare_act_router_model, prompt=prompt)
        route = "retrieve" if response and "VECTORSTORE" in response.upper() else "no_answer"
        state["route_result_DPDP"] = route
        
        return state
    
    @traceable(name="DPDP_retrieve")
    def DPDP_retrieve(self,state: OverallAgentsState_DPDP_Act,config: RunnableConfig) -> OverallAgentsState_DPDP_Act:
        state["DPDP_Act_documents"] = self.DPDP_retriever.invoke(state["User_question_DPDP_ACT"])
        return state
    
    @traceable(name="DPDP_dummy")
    def DPDP_dummy(self,state: OverallAgentsState_DPDP_Act,config: RunnableConfig) -> OverallAgentsState_DPDP_Act:
        return state
    
    @traceable(name="DPDP_grade_documents")
    def DPDP_grade_documents(self,state: OverallAgentsState_DPDP_Act,config: RunnableConfig) -> OverallAgentsState_DPDP_Act:
        configurable = Configuration.from_runnable_config(config)
        filtered_docs = []
        for doc in state["DPDP_Act_documents"]:
            prompt = self.DPDP_Template_obj.get_grader_prompt(state["User_question_DPDP_ACT"],document=doc.page_content)
            result = self.model.get_models(model_name=configurable.bare_act_grader_model, prompt=prompt)
            if "YES" in result.upper():
                filtered_docs.append(doc)
        state["DPDP_Act_documents"] = filtered_docs
        
        return state
    
    @traceable(name="DPDP_Act_generate_answer")
    def DPDP_Act_generate_answer(self,state: OverallAgentsState_DPDP_Act,config: RunnableConfig) -> OverallAgentsState_DPDP_Act:
        # print(",,,,,,,,,,,",)
        # if len(state["DPDP_Act_documents"])>0:
        #     state["DPDP_Act_Agent_answer"] = ["No relevant documents found."]
            
        # else:
        #     configurable = Configuration.from_runnable_config(config)
        #     context = "\n\n".join(doc.page_content for doc in state["DPDP_Act_documents"])
        #     prompt = self.DPDP_Template_obj.get_answer_prompt(context=context, question=state["User_question_DPDP_ACT"])
        #     response = self.model.get_models(model_name=configurable.bare_act_answer_model, prompt=prompt)
        #     state["DPDP_Act_Agent_answer"] = [response]
        # state["event"]="Generating Answers.."
        # return state
        configurable = Configuration.from_runnable_config(config)
        context = "\n\n".join(doc.page_content for doc in state["DPDP_Act_documents"])
        prompt = self.DPDP_Template_obj.get_answer_prompt(context=context, question=state["User_question_DPDP_ACT"])
        response = self.model.get_models(model_name=configurable.bare_act_answer_model, prompt=prompt)
        state["DPDP_Act_Agent_answer"] = [response]
        
        return state
    
    @traceable(name="DPDP_no_answer")
    def DPDP_no_answer(self,state: OverallAgentsState_DPDP_Act,config: RunnableConfig) -> OverallAgentsState_DPDP_Act:
        state["DPDP_Act_Agent_answer"] = ["I am unable to answer this question as it is outside my knowledge base."]
        
        return state
        
    
