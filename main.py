from fastapi import FastAPI, Request
from datetime import datetime
import json
import subprocess

app = FastAPI()

email_vars = {
    "smtp_host": "smtp.mailserver.com",
    "smtp_port": 587,
    "smtp_username": "your@email.com",
    "smtp_password": "yourpassword",
    "email_from": "your@email.com",
    "email_to": "",
    "email_subject": "",
    "email_body": "",
}

@app.get("/")
async def run_task(request: Request):
    return {"status": "success"}

@app.post("/alert")
async def run_task(request: Request):
    body = await request.body()
    data_json = json.loads(body)

    target = data_json['ssh']['target']
    cmd = data_json['ssh']['command']
    url = data_json['http']['target']
    payload = data_json['http']['body']
    
    inventory = 'inventory'
    playbook = 'playbook.yml'
    ssh_user = 'root'

    cmd = [
        'ansible-playbook',
        '-i', inventory,
        playbook,
        '--limit', target,
        '-e', f'ansible_user={ssh_user} cmd="{cmd}"',
        '-e', f'post_url={url}',
        '-e', f"post_body='{json.dumps(payload)}'"
    ]

    # Run command
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Output results
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
    print("Return code:", result.returncode)
    return result.stdout

