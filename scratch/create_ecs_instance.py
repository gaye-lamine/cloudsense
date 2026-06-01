import os
import sys
from dotenv import load_dotenv

# Load env variables
load_dotenv()

from alibabacloud_tea_openapi.models import Config
from alibabacloud_ecs20140526.client import Client as EcsClient
from alibabacloud_ecs20140526 import models as ecs_models

def create_tiny_ecs():
    access_key_id = os.getenv("ALIBABA_ACCESS_KEY_ID")
    access_key_secret = os.getenv("ALIBABA_ACCESS_KEY_SECRET")
    region_id = os.getenv("ALIBABA_REGION", "us-east-1")
    
    print(f"AK ID: {access_key_id}")
    print(f"Region: {region_id}")
    
    if not access_key_id or access_key_id == "mock_id":
        print("Error: ALIBABA_ACCESS_KEY_ID is not configured.")
        return
        
    config = Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        region_id=region_id
    )
    
    try:
        client = EcsClient(config)
        
        # 1. Try to find a Security Group
        print("Step 1: Finding an existing Security Group...")
        sg_req = ecs_models.DescribeSecurityGroupsRequest(region_id=region_id)
        sg_resp = client.describe_security_groups(sg_req)
        sgs = sg_resp.body.security_groups.security_group if sg_resp.body.security_groups else []
        
        if not sgs:
            print("❌ No Security Group found. You need to create a Security Group in the Alibaba Cloud Console first.")
            return
            
        sg_id = sgs[0].security_group_id
        print(f"👉 Found Security Group: {sg_id} ({sgs[0].security_group_name})")
        
        # 2. Try to find a VSwitch and VPC
        print("Step 2: Describing images...")
        img_req = ecs_models.DescribeImagesRequest(
            region_id=region_id,
            image_owner_alias="system",
            instance_type="ecs.t5-lc1m1.small" # standard cheap type
        )
        img_resp = client.describe_images(img_req)
        images = img_resp.body.images.image if img_resp.body.images else []
        
        if not images:
            # Fallback to standard Ubuntu image ID for us-east-1
            image_id = "ubuntu_20_04_x64_20G_alibase_20210623.vhd"
        else:
            image_id = images[0].image_id
            
        print(f"👉 Selected Image: {image_id}")
        
        # 3. Create a burstable, extremely cheap instance (ecs.t5-lc1m1.small, roughly $0.01/hour)
        print("Step 3: Creating tiny burstable ECS instance (Pay-As-You-Go)...")
        
        # We try to use DescribeVpc to find vswitch, or run_instances which can automatically assign default network if supported.
        # But we'll try standard CreateInstance with basic parameters.
        req = ecs_models.CreateInstanceRequest(
            region_id=region_id,
            instance_type="ecs.t5-lc1m1.small", 
            image_id=image_id,
            security_group_id=sg_id,
            instance_name="cloudsense-real-ecs-test",
            description="Created by CloudSense agent for live credentials validation",
            instance_charge_type="PostPaid" # Pay-as-you-go
        )
        
        resp = client.create_instance(req)
        instance_id = resp.body.instance_id
        print(f"🎉 Success! Instance created successfully! ID: {instance_id}")
        print("Starting the instance...")
        
        start_req = ecs_models.StartInstanceRequest(instance_id=instance_id)
        client.start_instance(start_req)
        print(f"🚀 Instance {instance_id} is now starting! Refresh the CloudSense dashboard to see it!")
        
    except Exception as e:
        err_str = str(e)
        print("\n❌ Failed to create ECS instance.")
        print(f"Error Details: {err_str}")
        if "Forbidden.RAM" in err_str or "Unauthorized" in err_str:
            print("\n💡 Reason: Your RAM user 'cloudsense-agent' currently has ONLY read-only permissions ('AliyunECSReadOnlyAccess').")
            print("To allow me to create an ECS instance for you, please add the 'AliyunECSFullAccess' permission to this RAM user in your Alibaba Cloud Console.")
        else:
            print("\n💡 Tip: Make sure you have a default VPC, VSwitch, and Security Group configured in the region (us-east-1).")

if __name__ == "__main__":
    create_tiny_ecs()
