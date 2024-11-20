import json
import boto3

def lambda_handler(event, context):
    #Initialise AWS Resources
    s3 = boto3.client('s3')
    
    try:  
        # Create S3 Bucket
        bucket_name="Project Web Bucket"
        s3.create_bucket(Bucket=bucket_name, CreateBucketConstraint={'LocationConstraint': 'us-east-1'})

        # Bucket Policy 
        bucket_policy = {
            "Version": "2024-11-19",
            "Statement": {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }
        }
        s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(bucket_policy))

        # Response Json
        response = {
            "S3 Bucket Name": bucket_name 
        }
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }
