import os
from ..EVR import *
from ..utils import *
from ..states import *
from ..prompts import *
from ..ai_model import *
from langsmith import traceable
from ..configuration import Configuration
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
    def BSA_route_question(self,state: OverallAgentsState_BSA_Act,config: RunnableConfig) -> OverallAgentsState_BSA_Act:
        configurable = Configuration.from_runnable_config(config)
        prompt = self.BSA_Template_obj.get_router_prompt(state["User_question_BSA_ACT"])
        response = self.model.get_models(model_name=configurable.bare_act_router_model, prompt=prompt)
        route = "retrieve" if response and "VECTORSTORE" in response.upper() else "no_answer"
        state["route_result_BSA"] = route
        state["event"]="Checking Question Relevance.."
        return state
    
    @traceable(name="BSA_retrieve")
    def BSA_retrieve(self,state: OverallAgentsState_BSA_Act,config: RunnableConfig) -> OverallAgentsState_BSA_Act:
        state["BSA_Act_documents"] = self.BSA_retriever.invoke(state["User_question_BSA_ACT"])
        state["event"]="Retrieving Docs.."
        return state
    
    @traceable(name="BSA_dummy")
    def BSA_dummy(self,state: OverallAgentsState_BSA_Act,config: RunnableConfig) -> OverallAgentsState_BSA_Act:
        return state
    
    @traceable(name="BSA_grade_documents")
    def BSA_grade_documents(self,state: OverallAgentsState_BSA_Act,config: RunnableConfig) -> OverallAgentsState_BSA_Act:
        configurable = Configuration.from_runnable_config(config)
        filtered_docs = []
        for doc in state["BSA_Act_documents"]:
            prompt = self.BSA_Template_obj.get_grader_prompt(state["User_question_BSA_ACT"],document=doc.page_content)
            result = self.model.get_models(model_name=configurable.bare_act_grader_model, prompt=prompt)
            if "YES" in result.upper():
                filtered_docs.append(doc)
        state["BSA_Act_documents"] = filtered_docs
        state["event"]="Grading Docs.."
        return state
   
    @traceable(name="BSA_Act_generate_answer")
    def BSA_Act_generate_answer(self,state: OverallAgentsState_BSA_Act,config: RunnableConfig) -> OverallAgentsState_BSA_Act:
        # if len(state["BSA_Act_documents"])>0:
        #     state["BSA_Act_Agent_answer"] = ["No relevant documents found."]
            
        # else:
        #     configurable = Configuration.from_runnable_config(config)
        #     context = "\n\n".join(doc.page_content for doc in state["BSA_Act_documents"])
        #     prompt = self.BSA_Template_obj.get_answer_prompt(context=context, question=state["User_question_BSA_ACT"])
        #     response = self.model.get_models(model_name=configurable.bare_act_answer_model, prompt=prompt)
        #     state["BSA_Act_Agent_answer"] = [response]
        # state["event"]="Generating Answers.."
        # return state
        configurable = Configuration.from_runnable_config(config)
        context = "\n\n".join(doc.page_content for doc in state["BSA_Act_documents"])
        prompt = self.BSA_Template_obj.get_answer_prompt(context=context, question=state["User_question_BSA_ACT"])
        response = self.model.get_models(model_name=configurable.bare_act_answer_model, prompt=prompt)
        state["BSA_Act_Agent_answer"] = [response]
        state["event"]="Generating Answers.."
        return state



    
    @traceable(name="BSA_no_answer")
    def BSA_no_answer(self,state: OverallAgentsState_BSA_Act,config: RunnableConfig) -> OverallAgentsState_BSA_Act:
        state["BSA_Act_Agent_answer"] = ["I am unable to answer this question as it is outside my knowledge base."]
        state["event"]="Generating Answers.."
        return state

