

import os
import sys
import django
from django.utils import timezone

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Chatbot.settings")
django.setup()

from langchain_chroma import Chroma
from configuration.models import VectorDBInformation
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings




class VectorDBStatusChecker:
    def __init__(self, db_type="chroma", persist_directory="../DATABASE/vector_db_laws"):
        self.db_type = db_type
        self.persist_directory = os.path.abspath(persist_directory)
        self.embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectordb = None
        self.records_count = 0
        self.db_name = os.path.basename(self.persist_directory)

        if self.db_type == "chroma":
            if os.path.exists(self.persist_directory):
                self.vectordb = Chroma(persist_directory=self.persist_directory, embedding_function=self.embedding)
            else:
                print("Chroma database not found.")
        else:  # FAISS
            if os.path.exists(os.path.join(self.persist_directory, "index.faiss")):
                self.vectordb = FAISS.load_local(folder_path=self.persist_directory, embeddings=self.embedding)
            else:
                print(" FAISS database not found.")

    def check_status(self):
        status = False

        if self.vectordb is None:
            print(" Vector DB not loaded.")
        else:
            try:
                docs = self.vectordb.similarity_search("test", k=1)
                if self.db_type == "chroma":
                    self.records_count = self.vectordb._collection.count() 
                elif self.db_type == "faiss":
                    self.records_count = len(self.vectordb.index_to_docstore)
                status = len(docs) > 0
                print(f"Vector DB ready: {self.records_count} documents")
            except Exception as e:
                print(f"Error while checking DB: {e}")

        # Save status to Django DB
        obj, created = VectorDBInformation.objects.update_or_create(
                        DB_name=self.db_name,  
                        defaults={
                                "Type": self.db_type,
                                "Checked_on": timezone.now(), 
                                "Status": status,
                                "Records_count": self.records_count,
                                "Path": self.persist_directory
                                }
                            )
        print("\n=== Vector DB Information Saved ===")
        print(f"DB Name       : {obj.DB_name}")
        print(f"Type          : {obj.Type}")
        print(f"Checked On    : {obj.Checked_on}")
        print(f"Status        : {'Ready' if obj.Status else 'Not Ready'}")
        print(f"Records Count : {obj.Records_count}")
        print(f"Path          : {obj.Path}")
        print("===================================\n")

# if __name__ == "__main__":
#     Vector_DB_Path="../DB_Vector/"
#     for db in os.listdir(Vector_DB_Path):
#         checker = VectorDBStatusChecker(
#             db_type="chroma",
#             persist_directory=os.path.join(Vector_DB_Path, db)
#         )
#         checker.check_status()
        