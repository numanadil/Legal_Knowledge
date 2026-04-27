
import os
import sys
import shutil
import django
from tqdm import tqdm
from datetime import datetime as dt


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Chatbot.settings")
django.setup()


def Vector_DB_Backup():
    Vector_DB_Path = "../DB_Vector/"
    source_db_dirs = [d for d in os.listdir(Vector_DB_Path) if os.path.isdir(os.path.join(Vector_DB_Path, d))]
    
    backup_folder = f"../DB_Backup/Vector_DB/Database-Backup-{dt.isoformat(dt.now())}"
    
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    for dir_name in tqdm(source_db_dirs, desc="Backing up Vector DB directories"):
        print(f"==Backup Started for {dir_name} @ {dt.isoformat(dt.now())}==")
        source_folder = os.path.join(Vector_DB_Path, dir_name)
        backup_path = os.path.join(backup_folder, dir_name)
        shutil.copytree(source_folder, backup_path)
        print(f"==Backup Completed for {dir_name} @ {dt.isoformat(dt.now())} in {backup_folder} ==")
    
    
if __name__ == "__main__":
    Vector_DB_Backup()
    

