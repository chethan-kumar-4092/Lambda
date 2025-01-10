import boto3
import os
from botocore.exceptions import ClientError

# Initialize AWS resources
ec2_client = boto3.client('ec2', region_name='us-east-1')
sns_client = boto3.client('sns', region_name='us-east-1')

# Environment variables for SNS Topic ARN and volume ID
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:136311431139:demo-sns"  # e.g., arn:aws:sns:us-east-1:123456789012:MyTopic
VOLUME_ID = "vol-079dc97fabd4ad31d"         # e.g., vol-1234abcd

def lambda_handler(event, context):
    try:
        # Create snapshot
        print(f"Creating snapshot for volume: {VOLUME_ID}")
        response = ec2_client.create_snapshot(
            VolumeId=VOLUME_ID,
            Description=f"Snapshot of {VOLUME_ID} initiated by Lambda"
        )
        snapshot_id = response['SnapshotId']
        print(f"Snapshot created with ID: {snapshot_id}")

        # Send SNS notification
        message = f"Snapshot {snapshot_id} has been created successfully for volume {VOLUME_ID}."
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="EBS Snapshot Created",
            Message=message
        )
        print("SNS notification sent.")
        
        return {
            'statusCode': 200,
            'body': f"Snapshot {snapshot_id} created and notification sent."
        }

    except ClientError as e:
        error_message = f"Error occurred: {e.response['Error']['Message']}"
        print(error_message)

        # Send failure notification via SNS
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="EBS Snapshot Creation Failed",
            Message=error_message
        )
        
        return {
            'statusCode': 500,
            'body': error_message
        }
