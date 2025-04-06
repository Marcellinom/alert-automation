from fastapi import FastAPI, Request
from datetime import datetime
from dotenv import load_dotenv
import json, subprocess, os

load_dotenv()
app = FastAPI()


@app.get("/")
async def run_task(request: Request):
    return {"status": "success"}

@app.post("/alert")
async def run_task(request: Request):
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
        
    body = await request.body()
    data_json = json.loads(body)

    target = data_json['ssh']['target']
    cmd = data_json['ssh']['command']
    url = data_json['http']['target']
    payload = data_json['http']['body']

    email_vars["mail_to"] = data_json['mail']['target']
    email_vars["mail_subject"] = data_json['mail']['subject']
    email_vars["mail_body"] = data_json['mail']['body']
    
    inventory = 'inventory'
    playbook = 'playbook.yml'
    ssh_user = 'root'
    mail_config = ' -e '.join(f'{k}="{v}"' for k, v in email_vars.items())

    cmd = [
        'ansible-playbook',
        '-i', inventory,
        playbook,
        '--limit', target,
        '-e', f'ansible_user={ssh_user} cmd="{cmd}"',
        '-e', f'post_url={url}',
        '-e', f"post_body='{json.dumps(payload)}'",
        '-e', mail_config
    ]

    # Run command
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Output results
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
    print("Return code:", result.returncode)
    return result.stdout

