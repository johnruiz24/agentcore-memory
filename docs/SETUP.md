# Setup & Configuration Guide

## Prerequisites

### System Requirements
- **OS:** macOS 12+, Linux (Ubuntu 20.04+), Windows with WSL2
- **Runtime:** Node.js 18+ or Python 3.11+
- **Package Manager:** npm 9+ or pip 22+
- **Git:** Version 2.30+
- **Docker:** Optional, for containerized deployment

### AWS Requirements
- AWS Account with permissions for:
  - DynamoDB (read/write)
  - IAM (role creation)
  - Secrets Manager (credential storage)
  - CloudWatch (logging)
  - Bedrock (model invocation)

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/johnruiz24/agentcore-memory.git
cd agentcore-memory
```

### 2. Configure Environment Variables

```bash
# Copy template
cp .env.example .env

# Edit with your values (replace {{PLACEHOLDERS}} with actual AWS resources)
# Required variables for development:
AWS_PROFILE={{AWS_PROFILE}}
AWS_REGION={{AWS_REGION}}
TABLE_MEMORY_STORE={{TABLE_MEMORY_STORE}}
TABLE_SESSIONS={{TABLE_SESSIONS}}
```

### 3. Install Dependencies

**For Node.js:**
```bash
npm install
npm run build
npm run test
```

**For Python:**
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
pytest
```

### 4. Verify Installation

```bash
# Check configuration
npm run config:check

# Run tests
npm test

# Expected output: All tests passing
```

## Docker Setup

### Build Image

```bash
docker build -t agentcore-memory:dev \
  --build-arg NODE_ENV=development \
  .
```

### Run Container

```bash
docker run -it \
  -p 8080:8080 \
  -e AWS_PROFILE={{AWS_PROFILE}} \
  -e AWS_REGION={{AWS_REGION}} \
  -v ~/.aws:/root/.aws:ro \
  agentcore-memory:dev
```

### Docker Compose

```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## AWS Configuration

### Create DynamoDB Tables

```bash
# Use CloudFormation (recommended)
aws cloudformation create-stack \
  --stack-name agentcore-memory-tables \
  --template-body file://deployment/tables-cfn.yaml \
  --region {{AWS_REGION}}

# Or create manually
aws dynamodb create-table \
  --table-name {{TABLE_MEMORY_STORE}} \
  --attribute-definitions AttributeName=sessionId,AttributeType=S AttributeName=timestamp,AttributeType=N \
  --key-schema AttributeName=sessionId,KeyType=HASH AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --region {{AWS_REGION}}
```

### Setup IAM Role

```bash
# Create role for agent execution
aws iam create-role \
  --role-name AgentCoreRole \
  --assume-role-policy-document file://deployment/trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name AgentCoreRole \
  --policy-arn arn:aws:iam::{{AWS_ACCOUNT_ID}}:policy/DynamoDBAccess
```

### Configure Bedrock Access

```bash
# Request model access (if needed)
aws bedrock create-model-customization-job \
  --region {{AWS_REGION}} \
  --model-id {{BEDROCK_MODEL_ID}}
```

## OAuth2 Setup

### GitHub Integration

1. Go to GitHub Settings → Developer applications
2. Create OAuth App
3. Set Authorization callback URL to: `https://your-domain.com/auth/github/callback`
4. Copy Client ID and Secret
5. Add to .env:

```bash
OAUTH_GITHUB_CLIENT_ID=<your_client_id>
OAUTH_GITHUB_CLIENT_SECRET=<your_client_secret>
```

### Google Integration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials
3. Set Authorized redirect URIs: `https://your-domain.com/auth/google/callback`
4. Add to .env:

```bash
OAUTH_GOOGLE_CLIENT_ID=<your_client_id>
OAUTH_GOOGLE_CLIENT_SECRET=<your_client_secret>
```

## Deployment

### To AWS ECS Fargate

```bash
# Build and push image
aws ecr get-login-password --region {{AWS_REGION}} | \
  docker login --username AWS --password-stdin {{AWS_ACCOUNT_ID}}.dkr.ecr.{{AWS_REGION}}.amazonaws.com

docker tag agentcore-memory:latest {{AWS_ACCOUNT_ID}}.dkr.ecr.{{AWS_REGION}}.amazonaws.com/agentcore-memory:latest
docker push {{AWS_ACCOUNT_ID}}.dkr.ecr.{{AWS_REGION}}.amazonaws.com/agentcore-memory:latest

# Deploy via CloudFormation
aws cloudformation deploy \
  --template-file deployment/ecs-stack.yaml \
  --stack-name agentcore-memory \
  --parameter-overrides \
    ImageUri={{AWS_ACCOUNT_ID}}.dkr.ecr.{{AWS_REGION}}.amazonaws.com/agentcore-memory:latest \
  --region {{AWS_REGION}}
```

### To Kubernetes

```bash
helm install agentcore-memory ./deployment/helm \
  --set image.repository={{ECR_REPO}}/agentcore-memory \
  --set awsProfile={{AWS_PROFILE}} \
  --set awsRegion={{AWS_REGION}}
```

## Scaling

### Horizontal Scaling

```bash
# Scale ECS service
aws ecs update-service \
  --cluster agentcore-memory \
  --service agent-core-runtime \
  --desired-count 5
```

### DynamoDB Capacity

```bash
# Switch to provisioned capacity if needed
aws dynamodb update-table \
  --table-name {{TABLE_MEMORY_STORE}} \
  --billing-mode PROVISIONED \
  --provisioned-throughput ReadCapacityUnits=100,WriteCapacityUnits=100
```

## Monitoring & Logging

### CloudWatch Logs

```bash
# View logs
aws logs tail /aws/ecs/agentcore-memory --follow

# Query with Insights
aws logs start-query \
  --log-group-name /aws/ecs/agentcore-memory \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | stats count() by @message'
```

### X-Ray Tracing

```bash
# Enable X-Ray in code
import AWSXRay from 'aws-xray-sdk-core';
const ddb = AWSXRay.client(new DynamoDBClient({}));
```

## Troubleshooting

### Issue: DynamoDB Access Denied

**Solution:**
```bash
# Verify IAM permissions
aws iam get-user-policy --user-name $USERNAME --policy-name DynamoDBAccess

# Add required permissions
aws iam put-user-policy --user-name $USERNAME \
  --policy-name DynamoDBAccess \
  --policy-document file://deployment/dynamodb-policy.json
```

### Issue: OAuth Callback Failing

**Solution:**
1. Verify callback URL matches provider configuration
2. Check that domain is publicly accessible
3. Verify SSL certificate is valid
4. Check CORS settings in API Gateway

### Issue: Memory Queries Slow

**Solution:**
1. Check DynamoDB metrics in CloudWatch
2. Ensure indexes are being used
3. Consider on-demand billing
4. Add caching layer (Redis/ElastiCache)

## Security Hardening

### Enable Encryption

```bash
# Enable DynamoDB encryption
aws dynamodb update-table \
  --table-name {{TABLE_MEMORY_STORE}} \
  --sse-specification Enabled=true,SSEType=KMS,KeyArn=arn:aws:kms:{{AWS_REGION}}:{{AWS_ACCOUNT_ID}}:key/{{KEY_ID}}
```

### Setup VPC

```bash
# Deploy in private subnets
aws ec2 create-security-group \
  --group-name agentcore-memory-sg \
  --description "Security group for Agent Core" \
  --vpc-id {{VPC_ID}}
```

### Enable Audit Logging

```bash
# Enable CloudTrail
aws cloudtrail create-trail \
  --name agentcore-memory-trail \
  --s3-bucket-name {{S3_BUCKET_LOGS}}
```

## Performance Tuning

### Connection Pooling

```typescript
// Configure connection pool size
const dynamodb = new DynamoDBClient({
  maxAttempts: 3,
  requestMinContentLength: 1024
});
```

### Caching Strategy

```typescript
// Use Redis for hot data
const redis = new Redis({
  host: '{{REDIS_ENDPOINT}}',
  ttl: 3600  // 1 hour
});
```

---

For examples, see [EXAMPLES.md](./EXAMPLES.md).
For architecture details, see [ARCHITECTURE.md](./ARCHITECTURE.md).
