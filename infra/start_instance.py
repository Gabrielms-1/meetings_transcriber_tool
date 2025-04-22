import boto3

REGION = 'us-east-1'
INSTANCE_ID = 'i-07d18e77ae41a091e'

session = boto3.Session(
    profile_name='personal-aws',
    region_name=REGION
)

ec2 = session.resource('ec2')

def start_instance():
    instance = ec2.Instance(INSTANCE_ID)
    instance.start()
    instance.wait_until_running()

    instance.reload()
    ip = instance.public_ip_address
    print(f"Instance {INSTANCE_ID} started")
    print(f"IP: {ip}")

if __name__ == "__main__":
    start_instance()
