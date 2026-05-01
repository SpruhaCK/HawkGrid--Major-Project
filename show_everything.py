import os
import boto3
from dotenv import load_dotenv

# Load keys
load_dotenv('.env', override=True)

target_region = os.getenv('AWS_REGION')
print(f"[*] Searching Account for ANY instances in Region: {target_region}...")

try:
    ec2 = boto3.client('ec2', 
        region_name=target_region,
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    # Notice: NO FILTERS AT ALL. We are asking for everything.
    response = ec2.describe_instances()
    
    count = 0
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            count += 1
            state = instance['State']['Name']
            ip = instance.get('PublicIpAddress', 'No Public IP')
            name_tag = "Unknown"
            
            # Try to grab the Name tag if it exists
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    name_tag = tag['Value']
                    
            print(f"✅ Found: {name_tag} ({instance['InstanceId']}) | State: {state.upper()} | IP: {ip}")
            
    if count == 0:
        print(f"\n❌ AWS confirms: There are ZERO instances (running or stopped) in {target_region}.")
        print("-> Check your browser URL. Does it say 'region=ap-south-1' or 'region=us-east-2'?")
        
except Exception as e:
    print(f"\n🚨 Error: {e}")