import boto3
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize EC2 client
ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
    try:
        # Get all snapshots owned by the account
        snapshots = ec2_client.describe_snapshots(OwnerIds=['self'])['Snapshots']

        if not snapshots:
            logger.info("No snapshots found.")
        else:
            for snapshot in snapshots:
                snapshot_id = snapshot['SnapshotId']
                volume_id = snapshot.get('VolumeId', 'UnknownVolume')
                description = snapshot.get('Description', 'No description')

                logger.info(f"Deleting snapshot {snapshot_id} for volume {volume_id} ({description})")

                # Delete the snapshot
                ec2_client.delete_snapshot(SnapshotId=snapshot_id)

                logger.info(f"Snapshot {snapshot_id} deleted successfully.")

        return {
            'statusCode': 200,
            'body': 'Snapshots deleted successfully!'
        }

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {
            'statusCode': 500,
            'body': f"Error: {e}"
        }
