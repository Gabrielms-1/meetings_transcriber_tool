import boto3
import time
import socket
import requests

REGION = 'us-east-1'
INSTANCE_ID = 'i-07d18e77ae41a091e'
JSON_PATH = 'data/transcripts/2025-04-08 09-02-19_transcript_backup.json'
OUTPUT_PATH = 'summ.md'

session = boto3.Session(
    profile_name='personal-aws',
    region_name=REGION
)
ec2 = session.resource('ec2')
ssm = session.client('ssm')
def start_instance():
    instance = ec2.Instance(INSTANCE_ID)
    instance.start()
    instance.wait_until_running()
    instance.reload()
    return instance.public_ip_address

def run_server_via_ssm(instance_id: str, timeout: int = 300):
    cmd = [
        "cd /home/ubuntu/meetings_transcriber_tool",
        "source venv/bin/activate",

        "nohup uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1 --lifespan on > uvicorn.log 2>&1 &"
    ]

    resp = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': cmd},
    )
    cmd_id = resp['Command']['CommandId']
    start = time.time()
    while time.time() - start < timeout:
        inv = ssm.get_command_invocation(CommandId=cmd_id, InstanceId=instance_id)
        if inv['Status'] in ('Success','Failed','TimedOut','Cancelled'):
            break
        time.sleep(2)
    else:
        raise TimeoutError("SSM command did not finish in time")
    
    if inv['Status'] != 'Success':
        raise RuntimeError(f"SSM command failed: {inv['StandardErrorContent']}")
    return inv

def wait_for_port(host: str, port: int, timeout: int = 300):
    """Waits until the port is listening on the instance."""
    
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=5):
                return
        except OSError:
            time.sleep(5)
    raise TimeoutError(f"Port {port} on {host} did not open in {timeout}s")

def call_endpoint(ip: str, json_path: str, output_path: str):
    print(f"IP: {ip}")
    url = f"http://{ip}:8000/summarize"
    wait_for_port(ip, 8000)

    with open(json_path, 'rb') as f:
        resp = requests.post(url, files={'file': f})
    resp.raise_for_status()
    
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(resp.text)

if __name__ == "__main__":
    ip = start_instance()
    print("Instance is running at:", ip)
    
    run_server_via_ssm(INSTANCE_ID, timeout=120)
    print("Server is running at port 8000")
    
    print("Calling endpoint to process the file...")
    call_endpoint(ip, JSON_PATH, OUTPUT_PATH)
    
    print("Result saved in", OUTPUT_PATH)
    # optional: stop the instance
    inst = ec2.Instance(INSTANCE_ID)
    inst.stop()
    inst.wait_until_stopped()
    print("Instance stopped.")