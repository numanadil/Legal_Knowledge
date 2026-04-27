import os
from agents.EVR import *
from agents.utils import *
from agents.states import *
from agents.prompts import *
from agents.ai_model import *
from langsmith import traceable
from agents.configuration import Configuration
from langchain_core.runnables import RunnableConfig




##########################
### START IT ACT AGENTS #####
##########################

class IT_Act_Agent:
    def __init__(self):
        config = Configuration()
        self.similar_docs=int(os.getenv("similar_docs"))
        config = Configuration()
        if config.IT_Act_Vector_db_Status:
            self.EVR_obj_IT=EVR(model_name=os.getenv("EMB_MODEL"),persist_directory=config.IT_Act_Vector_db_Path,k=self.similar_docs,dbtype=config.IT_Act_Vector_db_Type)
        else:
            raise Exception("Vector DB Status check failed: BSA Act Vector DB is not active.")
        self.IT_vectordb=self.EVR_obj_IT.get_vectordb()
        self.IT_retriever=self.EVR_obj_IT.get_retriever()
        self.IT_Template_obj=IT_Act_Prompt_Templates()
        self.model=Ai_Models_Bare_Acts()
        
    @traceable(name="IT_route_question")   
    def IT_route_question(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        configurable= Configuration.from_runnable_config(config)
        prompt = self.IT_Template_obj.get_router_prompt(state["User_question_IT_ACT"])
        response = self.model.get_models(model_name=configurable.bare_act_router_model, prompt=prompt)
        route = "retrieve" if response and "VECTORSTORE" in response.upper() else "no_answer"
        state["route_result_IT"] = route
        
        return state
    
    @traceable(name="IT_retrieve")   
    def IT_retrieve(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        state["IT_ACT_documents"] = self.IT_retriever.invoke(state["User_question_IT_ACT"])
        return state
    
    @traceable(name="IT_dummy")
    def IT_dummy(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        return state
    
    @traceable(name="IT_grade_documents")
    def IT_grade_documents(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        filtered_docs = []
        for doc in state["IT_ACT_documents"]:
            prompt = self.IT_Template_obj.get_grader_prompt(state["User_question_IT_ACT"],document=doc.page_content)
            result = self.model.get_models(model_name=configurable.bare_act_grader_model, prompt=prompt)
            if "YES" in result.upper():
                filtered_docs.append(doc)
        state["IT_ACT_documents"] = filtered_docs
        return state
    
    @traceable(name="IT_Act_generate_answer")
    def IT_Act_generate_answer(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        # if len(state["IT_ACT_documents"])>0:
        #     state["IT_Act_Agent_answer"] = ["No relevant documents found."]
        # else:
        #     configurable = Configuration.from_runnable_config(config)
        #     context = "\n\n".join(doc.page_content for doc in state["IT_ACT_documents"])
        #     prompt = self.IT_Template_obj.get_answer_prompt(context=context, question=state["User_question_IT_ACT"])
        #     response = self.model.get_models(model_name=configurable.bare_act_answer_model, prompt=prompt)
        #     state["IT_Act_Agent_answer"] = [response]
        # return state
        configurable = Configuration.from_runnable_config(config)
        context = "\n\n".join(doc.page_content for doc in state["IT_ACT_documents"])
        prompt = self.IT_Template_obj.get_answer_prompt(context=context, question=state["User_question_IT_ACT"])
        response = self.model.get_models(model_name=configurable.bare_act_answer_model, prompt=prompt)
        state["IT_Act_Agent_answer"] = [response]
        return state
    
    @traceable(name="IT_no_answer")
    def IT_no_answer(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        state["IT_Act_Agent_answer"] = ["I am unable to answer this question as it is outside my knowledge base."]
        return state
        
##########################
### END IT ACT AGENTS #####
##########################


