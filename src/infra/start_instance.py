import boto3
import time
import socket
import requests

REGION = 'us-east-1'
INSTANCE_ID = "i-07d18e77ae41a091e"
JSON_PATH = 'data/transcripts/2025-04-08 09-02-19_transcript_backup.json'
OUTPUT_PATH = 'data/summaries/GA-Box-2025-04-08.md'

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
    
    print(f"Instance {INSTANCE_ID} started at {instance.public_ip_address}")

    return instance.public_ip_address

def run_server_via_ssm(instance_id: str, timeout: int):
    cmd = [
        "source /home/ubuntu/meetings_transcriber_tool/venv/bin/activate && \
        cd /home/ubuntu/meetings_transcriber_tool && \
        ./start_server.sh"
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
        time.sleep(5)
    else:
        raise TimeoutError("SSM command did not finish in time")
    
    if inv['Status'] != 'Success':
        raise RuntimeError(f"SSM command failed: {inv['StandardErrorContent']}")
    return inv

def wait_for_api(ip, port=8000, path="/docs", timeout=200):
    url = f"http://{ip}:{port}{path}"
    print(f"Waiting for {url} to be available...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                print("API is available! Time elapsed:", time.time() - start_time)
                return True
        except Exception as e:
            print(f"Waiting... {e}")
            time.sleep(3)
    raise TimeoutError(f"Timeout waiting for API at {url}")

def call_endpoint(ip: str, json_path: str, output_path: str):
    print("Calling endpoint...")
    print(f"IP: {ip}")
    url = f"http://{ip}:8000/summarize"
    wait_for_api(ip)

    with open(json_path, 'rb') as f:
        resp = requests.post(url, files={'file': f})
    resp.raise_for_status()
    
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(resp.text)

if __name__ == "__main__":
    ip = "44.192.67.210"#start_instance()
    
    print("Instance is running at:", ip)
    try:
        run_server_via_ssm(INSTANCE_ID, timeout=400)
        print("Server is running at port 8000")
    except Exception as e:
        print(f"Error running server: {e}")
    
    try:
        print("Calling endpoint to process the file...")
        call_endpoint(ip, JSON_PATH, OUTPUT_PATH)
        print("Result saved in", OUTPUT_PATH)
    except Exception as e:
        print(f"Error calling endpoint: {e}")

    print("Stopping instance...")
    inst = ec2.Instance(INSTANCE_ID)
    inst.stop()
    inst.wait_until_stopped()
    print("Instance stopped.")