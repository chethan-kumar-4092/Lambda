import boto3
import datetime
import os
from botocore.exceptions import ClientError

# Initialize AWS EC2 client
ec2_client = boto3.client('ec2', region_name='us-east-1')

# Environment variables
RETENTION_DAYS = "0"  # e.g., 30
AMI_NAME_PREFIX = "AMI-"     # e.g., 'AMI-' to filter AMIs created by automation

def lambda_handler(event, context):
    try:
        # Calculate the retention period
        retention_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=RETENTION_DAYS)
        print(f"Deleting AMIs older than: {retention_date.isoformat()}")
        
        # Get all AMIs owned by the account
        images = ec2_client.describe_images(Owners=['self'])['Images']

        for image in images:
            # Check if the AMI matches the naming convention
            if AMI_NAME_PREFIX in image['Name']:
                # Parse the creation date of the AMI
                creation_date = datetime.datetime.fromisoformat(image['CreationDate'].replace('Z', '+00:00'))
                
                if creation_date < retention_date:
                    image_id = image['ImageId']
                    print(f"Deleting AMI: {image_id} (Created on: {creation_date})")

                    # Deregister the AMI
                    ec2_client.deregister_image(ImageId=image_id)
                    print(f"AMI {image_id} deregistered.")

                    # Delete associated snapshots
                    for block_device in image.get('BlockDeviceMappings', []):
                        if 'Ebs' in block_device:
                            snapshot_id = block_device['Ebs']['SnapshotId']
                            try:
                                ec2_client.delete_snapshot(SnapshotId=snapshot_id)
                                print(f"Snapshot {snapshot_id} deleted.")
                            except ClientError as e:
                                print(f"Error deleting snapshot {snapshot_id}: {e}")
                                
        return {
            'statusCode': 200,
            'body': "AMI cleanup completed."
        }

    except ClientError as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': f"An error occurred: {e.response['Error']['Message']}"
        }
