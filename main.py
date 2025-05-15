from fastapi import FastAPI, Request
from datetime import datetime
from dotenv import load_dotenv
import json as j, subprocess, os
 
load_dotenv()
app = FastAPI()

# default
PLAYBOOK = 'playbook.yml'
INVENTORY = 'inventory'
TARGET = 'all'
 
@app.get("/")
async def run_task(request: Request):
    return {"status": "success"}

def stdout(cmd: list[str]):
    # Run command
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Output results
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
    print("Return code:", result.returncode)
    return result.stdout

def buildDefaultParam(json: dict):
    if 'target' in json:
        TARGET = json['target']
    if 'playbook' in json:
        PLAYBOOK = json['playbook']
    if 'inventory' in json:
        INVENTORY = json['inventory']

    return [
        'ansible-playbook', 
        '-i', INVENTORY, PLAYBOOK, 
        '--limit', TARGET, 
        '-e', f'ansible_user=root'
    ]

def buildEmail(json: dict) -> list[str]:
    email_vars = {
        "smtp_host": os.getenv('smpt_host'),
        "smtp_port": os.getenv('smtp_port'),
        "smtp_username": os.getenv('smtp_username'),
        "smtp_password": os.getenv('smtp_password'),
        "email_from": os.getenv('smtp_from'),
        "email_to": "",
        "email_subject": "",
        "email_body": "",
    }
    email_vars["email_to"] = json['target']
    email_vars["email_subject"] = json['subject']
    email_vars["email_body"] = json['body']

    return ['-e', f'{k}="{v}"' for k, v in email_vars.items()]

def buildApiCallParam(json: dict) -> list[str]:
    return [
        '-e', f'post_url={json['url']}',
        '-e', f'post_body={json['post_body']}'
    ]

def buildSshCommandParam(json: dict) -> list[str]:
    return [
        '-e', f'command={json['command']}'
    ]

def buildSshLogParam(json: dict) -> list[str]:
    return [
        '-e', f'log={json["content"]}', 
        '-e', f'log_name={json['destination_path']}'
    ]

@app.post("/ssh_log")
async def log_ssh(req: Request):
    body = await req.body()
    data = j.loads(body)

    cmd = buildDefaultParam(data) + buildSshLogParam(data['ssh_log']) + ['-e', 'event=ssh_log']
    return stdout(cmd)

@app.post("/ssh_command")
async def ssh_command(req: Request):
    body = await req.body()
    data = j.loads(body)

    cmd = buildDefaultParam(data) + buildSshCommandParam(data['ssh_command']) + ['-e', 'event=ssh_command']
    return stdout(cmd)

@app.post("/api_call")
async def api_call(req: Request):
    body = await req.body()
    data = j.loads(body)

    cmd = buildDefaultParam(data) + buildApiCallParam(data['api_call']) + ['-e', 'event=api']
    return stdout(cmd)

@app.post("/email")
async def email(req: Request):
    body = await req.body()
    data = j.loads(body)

    cmd = buildDefaultParam(data) + buildEmail(data['email']) + ['-e', 'event=email']
    return stdout(cmd)

@app.post("/disaster_1")
async def run_task(request: Request):
    body = await request.body()
    data = j.loads(body)
    
    cmd = buildDefaultParam(data) 
    + buildSshLogParam(data['ssh_log'])
    + buildSshCommandParam(data['ssh_command'])
    + ['-e', 'event=disaster_1']

    return stdout(cmd)
