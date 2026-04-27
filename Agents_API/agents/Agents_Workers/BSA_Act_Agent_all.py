import os
from agents.EVR import *
from agents.utils import *
from agents.states import *
from agents.prompts import *
from agents.ai_model import *
from langsmith import traceable
from agents.configuration import Configuration
from langchain_core.runnables import RunnableConfig



class BSA_Act_Agent:
    def __init__(self):
        self.similar_docs=int(os.getenv("similar_docs"))
        config_params = Configuration()
        if config_params.BSA_Act_Vector_db_Status:
            self.EVR_obj_BSA=EVR(model_name=os.getenv("EMB_MODEL"),persist_directory=config_params.BSA_Act_Vector_db_Path,k=self.similar_docs,dbtype=config_params.BSA_Act_Vector_db_Type)
        else:
            raise Exception("Vector DB Status check failed: IT Act Vector DB is not active.")
        self.BSA_emb=self.EVR_obj_BSA.get_embedding()
        self.BSA_vectordb=self.EVR_obj_BSA.get_vectordb()
        self.BSA_retriever=self.EVR_obj_BSA.get_retriever()
        self.BSA_Template_obj=BSA_Act_Prompt_Templates()
        self.model=Ai_Models_Bare_Acts()
    
    @traceable(name="BSA_route_question")   
    def BSA_route_question(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        prompt = self.BSA_Template_obj.get_router_prompt(state["User_question_BSA_ACT"])
        response = self.model.get_models(model_name=configurable.bare_act_router_model, prompt=prompt)
        route = "retrieve" if response and "VECTORSTORE" in response.upper() else "no_answer"
        state["route_result_BSA"] = route
        return state
    
    @traceable(name="BSA_retrieve")
    def BSA_retrieve(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        state["BSA_Act_documents"] = self.BSA_retriever.invoke(state["User_question_BSA_ACT"])
        return state
    
    @traceable(name="BSA_dummy")
    def BSA_dummy(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        return state
    
    @traceable(name="BSA_grade_documents")
    def BSA_grade_documents(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        configurable = Configuration.from_runnable_config(config)
        filtered_docs = []
        for doc in state["BSA_Act_documents"]:
            prompt = self.BSA_Template_obj.get_grader_prompt(state["User_question_BSA_ACT"],document=doc.page_content)
            result = self.model.get_models(model_name=configurable.bare_act_grader_model, prompt=prompt)
            if "YES" in result.upper():
                filtered_docs.append(doc)
        state["BSA_Act_documents"] = filtered_docs
        return state
   
    @traceable(name="BSA_Act_generate_answer")
    def BSA_Act_generate_answer(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        # if len(state["BSA_Act_documents"])>0:
        #     state["BSA_Act_Agent_answer"] = ["No relevant documents found."]
        # else:
        #     configurable = Configuration.from_runnable_config(config)
        #     context = "\n\n".join(doc.page_content for doc in state["BSA_Act_documents"])
        #     prompt = self.BSA_Template_obj.get_answer_prompt(context=context, question=state["User_question_BSA_ACT"])
        #     response = self.model.get_models(model_name=configurable.bare_act_answer_model, prompt=prompt)
        #     state["BSA_Act_Agent_answer"] = [response]
            
        # return state
        configurable = Configuration.from_runnable_config(config)
        context = "\n\n".join(doc.page_content for doc in state["BSA_Act_documents"])
        prompt = self.BSA_Template_obj.get_answer_prompt(context=context, question=state["User_question_BSA_ACT"])
        response = self.model.get_models(model_name=configurable.bare_act_answer_model, prompt=prompt)
        state["BSA_Act_Agent_answer"] = [response]
        return state
            
    
    @traceable(name="BSA_no_answer")
    def BSA_no_answer(self,state: OverallAgentsState,config: RunnableConfig) -> OverallAgentsState:
        state["BSA_Act_Agent_answer"] = ["I am unable to answer this question as it is outside my knowledge base."]
        return state

