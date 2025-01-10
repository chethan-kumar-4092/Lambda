import boto3
import json

def lambda_handler(event, context):
    try:
        # Initialize boto3 EC2 client for us-east-1 region
        ec2_client = boto3.client('ec2', region_name='us-east-1')

        # Describe all instances in the region
        instances = ec2_client.describe_instances()

        ami_ids = []

        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']

                # Create an AMI for each instance
                ami_response = ec2_client.create_image(
                    InstanceId=instance_id,
                    Name=f"AMI-{instance_id}-{context.aws_request_id}",
                    Description="Automated AMI created by Lambda",
                    NoReboot=True
                )

                ami_id = ami_response['ImageId']
                ami_ids.append({"InstanceId": instance_id, "AmiId": ami_id})
                print(f"AMI created: {ami_id} for instance {instance_id}")

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "AMIs created successfully",
                "ami_ids": ami_ids
            })
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Error creating AMIs",
                "error": str(e)
            })
        }