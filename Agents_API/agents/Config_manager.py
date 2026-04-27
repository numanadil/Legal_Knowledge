import os
import requests
from dotenv import load_dotenv

load_dotenv()


class APIConfigManager:
    def __init__(self):
        self.api_config_data = None
        self.fetch_api_config()

    def fetch_api_config(self):
        url = os.getenv("API_URL")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.api_config_data = response.json().get('data', {})
            else:
                print(f"Failed to access API. Status Code: {response.status_code}")
                print(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)

    def get_websearch_config(self):
        ws = self.api_config_data.get("websearch_agent", {})
        return type("WebSearchConfig", (), {
            "Querry_Generator_Model": ws.get("Querry_Generator_Model", "gemini-2.0-flash"),
            "Answer_Model": ws.get("Answer_Model", "gemini-2.5-pro"),
            "Initial_Querry": int(ws.get("Initial_Querry", 3)),
            "Max_Research_Loops": int(ws.get("Max_Research_Loops", 2)),
            "Reflection_Model": ws.get("Answer_Model", "gemini-2.5-flash"),
        })()

    def get_bareact_config(self):
        ba = self.api_config_data.get("bare_acts_agent", {})
        return type("BareActConfig", (), {
            "Router_Model": ba.get("Router_Model", "gemini-2.5-flash"),
            "Retriever_Model": ba.get("Retriever_Model", "gemini-2.5-flash"),
            "Grader_Model": ba.get("Grader_Model", "gemini-2.5-flash"),
            "Answer_Model": ba.get("Answer_Model", "gemini-2.5-pro"),
        })()

    def get_github_api_config(self):
        github = self.api_config_data.get("GithubModel_Api", {})
        return type("GithubConfig", (), {
            "API_Path_Githhub": github.get("API_Path_Githhub", "https://models.github.ai/inference"),
            "Updated_on": github.get("Retriever_Model", "No Info"),
        })()

    def get_reflexion_config(self):
        ra = self.api_config_data.get("reflexion_agent", {})
        return type("ReflexionConfig", (), {
            "Reflexion_Model": ra.get("Reflexion_Model", "gemini-2.5-pro"),
        })()

    def get_vector_db_config(self, act_name):
        vdb = self.api_config_data.get("vector_db", {})
        if act_name in vdb and vdb[act_name]:
            entry = vdb[act_name][0]
            return type("VectorDBConfig", (), {
                "id": entry.get("id"),
                "Type": entry.get("Type"),
                "Checked_on": entry.get("Checked_on"),
                "DB_name": entry.get("DB_name"),
                "Status": entry.get("Status"),
                "Records_count": entry.get("Records_count"),
                "Path": entry.get("Path")
            })()
        else:
            raise ValueError(f"No configuration found for '{act_name}'")

    def get_IT_DB_config(self):
        return self.get_vector_db_config("IT ACT 2000")

    def get_BNS_DB_config(self):
        return self.get_vector_db_config("The Bharatiya Nyaya Sanhita, 2023")

    def get_BSA_DB_config(self):
        return self.get_vector_db_config("The Bharatiya Sakshya Adhiniyam, 2023")

    def get_DPDP_DB_config(self):
        return self.get_vector_db_config("THE DIGITAL PERSONAL DATA PROTECTION ACT, 2023")

    def get_Github_inference_endpoint(self):
        return self.get_github_api_config()

