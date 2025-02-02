import subprocess
import os

def start_frontend():
    # Command to start the frontend
    subprocess.Popen(["npm", "start"], cwd=os.path.join(os.getcwd(), "frontend"))
    # Command to run the script
    subprocess.Popen(["node", "src/server.js"], cwd=os.path.join(os.getcwd(), "frontend"))

def start_backend():
    # Command to start the backend
    subprocess.Popen(["python", "manage.py", "runserver"], cwd=os.path.join(os.getcwd(), "backend"))

if __name__ == "__main__":
    start_frontend()
    # start_backend()