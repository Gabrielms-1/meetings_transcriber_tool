import boto3
import time
import socket
import requests
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

REGION = 'us-east-1'
INSTANCE_ID = "i-07d18e77ae41a091e"
JSON_PATH = 'data/transcripts/2025-04-08 09-02-19_transcript_backup.json'
OUTPUT_PATH = 'data/summaries/GA-Box-2025-04-08.md'

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=0.3,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET", "POST"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

session = boto3.Session(
    profile_name='personal-aws',
    region_name=REGION
)
ec2 = session.resource('ec2')
ssm = session.client('ssm')

def start_instance():
    instance = ec2.Instance(INSTANCE_ID)
    state = instance.state['Name']
    if state == 'running':
        logger.info(f"Instance {INSTANCE_ID} is already running")
        return instance.public_ip_address
    else:
        instance.start()
        instance.wait_until_running()
        instance.reload()
        logger.info(f"Instance {INSTANCE_ID} started at {instance.public_ip_address}")

    return instance.public_ip_address

def run_server_via_ssm(instance_id: str, timeout: int):
    # cmd = [
    #     "source /home/ubuntu/meetings_transcriber_tool/venv/bin/activate && \
    #     cd /home/ubuntu/meetings_transcriber_tool && \
    #     ./start_server.sh"
    # ]

    cmd = [
        "cd /home/ubuntu/meetings_transcriber_tool && \
        chmod +x start_server.sh && \
        . /home/ubuntu/meetings_transcriber_tool/venv/bin/activate && \
        ./start_server.sh"
    ]

    resp = ssm.send_command(
        InstanceIds=[instance_id],
        DocumentName="AWS-RunShellScript",
        Parameters={'commands': cmd},
    )
    
    cmd_id = resp['Command']['CommandId']
    inv = None
    start = time.time()
    while time.time() - start < timeout:
        inv = ssm.get_command_invocation(CommandId=cmd_id, InstanceId=instance_id)
        if inv['Status'] in ('Success','Failed','TimedOut','Cancelled'):
            break
        time.sleep(5)
    else:
        raise TimeoutError("SSM command did not finish in time")
    
    if inv['Status'] != 'Success':
        error = inv.get('StandardErrorContent', 'Unknown error')
        logger.error(f"SSM command failed: {error}")
        raise RuntimeError(f"SSM command failed: {error}")
    return inv

def wait_for_api(ip, port=8000, path="/docs", timeout=200):
    url = f"http://{ip}:{port}{path}"
    logger.info(f"Waiting for {url} to be available...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            r = session.get(url, timeout=(5, 5))
            if r.status_code == 200:
                elapsed = time.time() - start_time
                logger.info(f"API is available! Time elapsed: {elapsed}")
                return True
        except Exception as e:
            time.sleep(3)
    
    raise TimeoutError(f"Timeout waiting for API at {url}")

def call_endpoint(ip: str, json_path: str, output_path: str):
    url = f"http://{ip}:8000/summarize"
    logger.info(f"Calling endpoint at {url} with file {json_path}")
    wait_for_api(ip)

    with open(json_path, 'rb') as f:
        resp = requests.post(url, files={'file': f}, timeout=(5, 400))
    resp.raise_for_status()
    
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(resp.text)
    logger.info(f"Output saved to {output_path}")

if __name__ == "__main__":
    ip_address = "44.192.67.210"#start_instance()
    
    logger.info(f"Instance is running at: {ip_address}")
    try:
        run_server_via_ssm(INSTANCE_ID, timeout=400)
        logger.info("Server is running at port 8000")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        raise
    
    try:
        call_endpoint(ip_address, JSON_PATH, OUTPUT_PATH)
    except Exception as e:
        logger.error(f"Error calling endpoint: {e}")
        raise

    logger.info("Stopping instance...")
    inst = ec2.Instance(INSTANCE_ID)
    inst.stop()
    inst.wait_until_stopped()
    logger.info("Instance stopped.")