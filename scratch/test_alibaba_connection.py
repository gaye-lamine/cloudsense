import os
import sys
from dotenv import load_dotenv

# Load env variables
load_dotenv()

from alibabacloud_tea_openapi.models import Config
from alibabacloud_ecs20140526.client import Client as EcsClient
from alibabacloud_ecs20140526 import models as ecs_models

def test_alibaba():
    access_key_id = os.getenv("ALIBABA_ACCESS_KEY_ID")
    access_key_secret = os.getenv("ALIBABA_ACCESS_KEY_SECRET")
    region_id = os.getenv("ALIBABA_REGION", "us-east-1")
    
    print(f"AK ID: {access_key_id}")
    print(f"Region: {region_id}")
    
    if not access_key_id or access_key_id == "mock_id":
        print("Error: ALIBABA_ACCESS_KEY_ID is not configured or is mock.")
        return
        
    config = Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        region_id=region_id
    )
    
    try:
        client = EcsClient(config)
        request = ecs_models.DescribeInstancesRequest(region_id=region_id)
        response = client.describe_instances(request)
        
        print("Success! Response received:")
        instances = response.body.instances.instance
        print(f"Found {len(instances)} instances.")
        for idx, inst in enumerate(instances):
            print(f"Instance {idx}: ID={inst.instance_id}, Name={inst.instance_name}, Status={inst.status}, Type={inst.instance_type}")
            
    except Exception as e:
        print(f"Error querying ECS: {e}")

if __name__ == "__main__":
    test_alibaba()
