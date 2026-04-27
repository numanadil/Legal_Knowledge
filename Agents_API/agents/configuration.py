import os
import sys
from agents.Config_manager import *
from typing import Any, Optional
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig

config_manager = APIConfigManager()
class Configuration(BaseModel):
    """The configuration for the agent."""

    Github_Inference_API: str=Field(
      default_factory=lambda:config_manager.get_Github_inference_endpoint().API_Path_Githhub,
      description="Github Models API Inference Path"
    )

    
    DPDP_Act_Vector_db_Path: str = Field(
        default_factory=lambda: config_manager.get_IT_DB_config().Path,
        description="Vector DB Path for the DPDP Sct 2025 Model"
    )
    DPDP_Act_Vector_db_Status: bool = Field(
        default_factory=lambda: config_manager.get_IT_DB_config().Status,
        description=" Status of Vector DB for the DPDP Sct 2025 Model"
    )
    DPDP_Act_Vector_db_Name: str = Field(
        default_factory=lambda: config_manager.get_IT_DB_config().DB_name,
        description=" Name of Vector DB for the DPDP Sct 2025 Model"
    )
    DPDP_Act_Vector_db_Type: str = Field(
        default_factory=lambda: config_manager.get_IT_DB_config().Type,
        description=" Type of Vector DB for the DPDP Sct 2025 Model"
    )


    IT_Act_Vector_db_Path: str = Field(
        default_factory=lambda: config_manager.get_IT_DB_config().Path,
        description="Vector DB Path for the IT ACT 2000 Model"
    )
    IT_Act_Vector_db_Status: bool = Field(
        default_factory=lambda: config_manager.get_IT_DB_config().Status,
        description=" Status of Vector DB for the IT ACT 2000 Model"
    )
    IT_Act_Vector_db_Name: str = Field(
        default_factory=lambda: config_manager.get_IT_DB_config().DB_name,
        description=" Name of Vector DB for the IT ACT 2000 Model"
    )
    IT_Act_Vector_db_Type: str = Field(
        default_factory=lambda: config_manager.get_IT_DB_config().Type,
        description=" Type of Vector DB for the IT ACT 2000 Model"
    )

    BNS_Act_Vector_db_Path: str = Field(
        default_factory=lambda: config_manager.get_BNS_DB_config().Path,
        description="Vector DB Path for the BNS ACT 2023 Model"
    )
    BNS_Act_Vector_db_Status: bool = Field(
        default_factory=lambda: config_manager.get_BNS_DB_config().Status,
        description=" Status of Vector DB for the BNS ACT 2023 Model"
    )
    BNS_Act_Vector_db_Name: str = Field(
        default_factory=lambda: config_manager.get_BNS_DB_config().DB_name,
        description=" Name of Vector DB for the BNS ACT 2023 Model"
    )
    BNS_Act_Vector_db_Type: str = Field(
        default_factory=lambda: config_manager.get_BNS_DB_config().Type,
        description=" Type of Vector DB for the BNS ACT 2023 Model"
    )

    BSA_Act_Vector_db_Path: str = Field(
        default_factory=lambda: config_manager.get_BSA_DB_config().Path,
        description="Vector DB Path for the BSA ACT 2023 Model"
    )
    BSA_Act_Vector_db_Status: bool = Field(
        default_factory=lambda: config_manager.get_BSA_DB_config().Status,
        description=" Status of Vector DB for the BSA ACT 2023 Model"
    )
    BSA_Act_Vector_db_Name: str = Field(
        default_factory=lambda: config_manager.get_BSA_DB_config().DB_name,
        description=" Name of Vector DB for the BSA ACT 2023 Model"
    )
    BSA_Act_Vector_db_Type: str = Field(
        default_factory=lambda: config_manager.get_BSA_DB_config().Type,
        description=" Type of Vector DB for the BSA ACT 2023 Model"
    )

    bare_act_router_model: str = Field(
        default_factory=lambda: config_manager.get_bareact_config().Router_Model,
        description="The name of the language model to use for routing"
    )
    bare_act_retriever_model: str = Field(
        default_factory=lambda: config_manager.get_bareact_config().Retriever_Model,
        description="The name of the model to retrieve legal documents"
    )
    bare_act_grader_model: str = Field(
        default_factory=lambda: config_manager.get_bareact_config().Grader_Model,
        description="The name of the model to grade legal documents"
    )
    bare_act_answer_model: str = Field(
        default_factory=lambda: config_manager.get_bareact_config().Answer_Model,
        description="The name of the model to answer legal queries"
    )

    reflexion_model: str = Field(
        default_factory=lambda: config_manager.get_reflexion_config().Reflexion_Model,
        description="The name of the model used for reflection"
    )

    query_generator_model: str = Field(
        default_factory=lambda: config_manager.get_websearch_config().Querry_Generator_Model,
        description="The name of the model for generating search queries"
    )
    reflection_model: str = Field(
        default_factory=lambda: config_manager.get_websearch_config().Reflection_Model,
        description="The name of the reflection model"
    )
    answer_model: str = Field(
        default_factory=lambda: config_manager.get_websearch_config().Answer_Model,
        description="The name of the model to answer search queries"
    )
    number_of_initial_queries: int = Field(
        default_factory=lambda: config_manager.get_websearch_config().Initial_Querry,
        description="Number of initial queries to generate"
    )
    max_research_loops: int = Field(
        default_factory=lambda: config_manager.get_websearch_config().Max_Research_Loops,
        description="Maximum number of web research loops"
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        configurable = config.get("configurable", {}) if config else {}

        raw_values = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }
        values = {k: v for k, v in raw_values.items() if v is not None}
        return cls(**values)


# if __name__ == "__main__":
#     config = Configuration()
#     for field, value in config.model_dump().items():
#         print(f"{field}: {value}")