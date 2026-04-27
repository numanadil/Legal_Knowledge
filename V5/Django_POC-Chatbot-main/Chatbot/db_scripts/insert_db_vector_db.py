

import os
import sys
import django
from tqdm import tqdm
from back_up import *
from check_db_status import *
from datetime import datetime as dt



project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Chatbot.settings")
django.setup()

from django.conf import settings

from configuration.models import BareActFileModel
from langchain_chroma import Chroma
from langchain_community.vectorstores import  FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


class VectorDBBuilder:
    def __init__(self, persist_directory,embedding="all-MiniLM-L6-v2",db="chroma"):
        self.persist_directory = persist_directory
        self.embedding = HuggingFaceEmbeddings(model_name=embedding)
        self.documents = []
        self.db_type = db

    def load_document(self, file_path, act_name):
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        documents = text_splitter.split_documents(pages)

        for doc in documents:
            doc.metadata["act"] = act_name

        self.documents.extend(documents)
        print(f"Loaded and processed: {act_name}")

    def build_vector_store(self):
        if not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory)
        
        if self.db_type == "chroma":
            vectordb = Chroma.from_documents(self.documents, self.embedding, persist_directory=self.persist_directory)
            # vectordb.persist()
            print("Chroma Vector Store Created and Persisted Successfully!")
        else:
            vectordb = FAISS.from_documents(self.documents, self.embedding)
            print("FAISS Vector Store Created Successfully!")

if __name__ == "__main__":
    # Vector_DB_Backup()
    file_objects = BareActFileModel.objects.all()
    for file_obj in tqdm(file_objects, desc="Building Vector DBs", unit="file"):
        print(f"\n=== Processing: {file_obj.Act_name} ===")
        builder = VectorDBBuilder(
                                  persist_directory=f"../DB_Vector/{file_obj.Act_name}", #-{dt.now().isoformat()}
                                  embedding="all-MiniLM-L6-v2",
                                  db="chroma"
                                 )

        file_path = os.path.join(str(settings.MEDIA_ROOT), str(file_obj.doc))
        builder.load_document(file_path, file_obj.Act_name)
        builder.build_vector_store()
        print(f"Finished Vector DB Creation for: {file_obj.Act_name}")

    Vector_DB_Path = "../DB_Vector/"
    db_dirs = [d for d in os.listdir(Vector_DB_Path) if os.path.isdir(os.path.join(Vector_DB_Path, d))]
    for db in tqdm(db_dirs, desc="Checking Vector DB Status", unit="DB"):
        persist_dir = os.path.join(Vector_DB_Path, db)
        checker = VectorDBStatusChecker(
                                        db_type="chroma",
                                        persist_directory=persist_dir
                                        )
        checker.check_status()