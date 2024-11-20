# ECP_Project

## Week 8/9 Presentation of AWS Cloud Implementation
User Stories Covered: 
- User Story 1: Traditional to Cloud Infrastructure
- User Story 3: Automation and Operational Efficiency

## Adjustments made to User Stories: 
- Invoke Lambda Function to provision cloud resources (VPC, EC2 Instances, RDS Instances, etc.)
- Create Step Function to trigger Lambda Functions to create cloud infrastructure
- Step Functions are executed via AWS CLI command "curl -X POST -d '{"input": "{}", "stateMachineArn":"arn:aws:states:us-east-1:767397761895:stateMachine:Infra-Setup"}' https://scnixsh1m5.execute-api.us-east-1.amazonaws.com/dev/infra-setup"
