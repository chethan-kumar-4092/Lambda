import boto3
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # Initialize boto3 client for EC2
    ec2_client = boto3.client('ec2', region_name='us-east-1')
    
    try:
        # Get all EC2 instances with attached volumes
        instances = ec2_client.describe_instances()
        
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                logger.info(f"Processing instance {instance_id}")
                
                # Get the attached volumes
                volumes = instance.get('BlockDeviceMappings', [])
                
                for volume in volumes:
                    volume_id = volume['Ebs']['VolumeId']
                    logger.info(f"Creating snapshot for volume {volume_id}")
                    
                    # Create a snapshot
                    snapshot_description = f"Snapshot of {volume_id} from instance {instance_id} on {datetime.utcnow().isoformat()}"
                    response = ec2_client.create_snapshot(
                        VolumeId=volume_id,
                        Description=snapshot_description
                    )
                    
                    snapshot_id = response['SnapshotId']
                    logger.info(f"Snapshot {snapshot_id} created for volume {volume_id}")
                    
        return {
            'statusCode': 200,
            'body': 'Snapshots created successfully!'
        }
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {
            'statusCode': 500,
            'body': f"Error: {e}"
        }
