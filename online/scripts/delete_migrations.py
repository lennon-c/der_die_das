from pathlib import Path
import subprocess
import os

DB =  Path.cwd() / 'db.sqlite3' 

def run():
 
    migrations = Path.cwd().glob(r"*/migrations/00*.py")
    for f in migrations:
        print(f'deleting {f}')
        f.unlink()

    print(f'deleting {DB}')
    DB.unlink()

    # Navigate to the directory where manage.py is located
    os.chdir("..")  

    # Run makemigrations within the Poetry environment
    subprocess.run(["poetry", "run", "python", "online/manage.py", "makemigrations"])
    subprocess.run(["poetry", "run", "python", "online/manage.py", "migrate"])


 
