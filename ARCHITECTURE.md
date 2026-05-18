# Architecture - Agentic Memory System

## System Overview

Agentic Memory is a distributed system providing persistent, searchable memory for AI agents running on AWS. The architecture follows a microservices pattern with clear separation of concerns.

### Core Components

1. **Agent Core Runtime** - Host and orchestrate agent execution
2. **Memory Service** - Capture, store, and retrieve interaction memories
3. **Identity Service** - Multi-provider OAuth2 authentication
4. **API Gateway** - HTTP interface for all operations
5. **Storage Layer** - DynamoDB for persistence, S3 for artifacts

## Architecture Diagram

See [docs/diagrams/system-architecture.png](./docs/diagrams/system-architecture.png) for a visual overview.

## Detailed Architecture

### 1. Agent Core Runtime

**Purpose:** Execute agent logic and manage lifecycle

**Responsibilities:**
- Initialize and configure agents
- Route incoming requests
- Manage session context
- Invoke Bedrock models
- Call external tools and APIs

**Technology Stack:**
- Node.js 18+ or Python 3.11+
- AWS SDK v3
- TypeScript for type safety

**API:**
```typescript
class AgentCore {
  constructor(config: AgentConfig);
  initialize(): Promise<void>;
  executeRequest(request: AgentRequest): Promise<AgentResponse>;
  shutdown(): Promise<void>;
}
```

### 2. Memory Service

**Purpose:** Persistent, searchable storage for agent interactions

**Capabilities:**
- Store interaction records (input/output/metadata)
- Semantic search using embeddings
- Query by session, agent, or semantic similarity
- Automatic memory retention policies
- TTL-based cleanup

**Data Model:**
```typescript
interface Memory {
  id: string;
  sessionId: string;
  agentId: string;
  timestamp: ISO8601;
  interaction: {
    input: string;
    output: string;
    metadata: Record<string, any>;
  };
  embedding?: number[]; // For semantic search
  ttl?: number; // Seconds until expiration
}
```

**Storage:** DynamoDB with GSI for efficient queries
- Primary Key: `sessionId#timestamp`
- GSI 1: `agentId#timestamp`
- GSI 2: `embeddings` (for semantic search)

### 3. Identity Service

**Purpose:** Secure, multi-provider authentication

**Features:**
- OAuth2 / OpenID Connect support
- GitHub, Google, custom providers
- PKCE flow for security
- Token management and refresh
- Per-user credential vault (KMS encrypted)

**Flow:**
```
User → OAuth Provider → Identity Service → Agent Core
  ↓         ↓                ↓                 ↓
Browser   Cognito         KMS Vault     Session Created
```

### 4. API Gateway

**Purpose:** HTTP interface and request routing

**Endpoints:**
- `POST /agent/request` - Execute agent request
- `GET /memory/search` - Semantic memory search
- `POST /memory/capture` - Store interaction
- `GET /memory/{sessionId}` - Retrieve session memories
- `POST /auth/login` - Initiate OAuth login
- `GET /auth/callback` - OAuth callback handler

### 5. Storage Layer

**DynamoDB Tables:**

| Table | Purpose | Keys |
|-------|---------|------|
| Memory Store | Interaction persistence | PK: sessionId#timestamp |
| Sessions | Session state | PK: sessionId |
| Tokens | OAuth token cache | PK: userId |
| Audit Log | Compliance/audit trail | PK: timestamp#userId |

**S3 Buckets:**
- `artifacts/` - Large interaction artifacts
- `logs/` - Application logs
- `backups/` - Automated backups

## Data Flow

### Request Flow

```
HTTP Request
    ↓
API Gateway (authorize)
    ↓
Agent Core (route)
    ↓
Memory Service (restore context)
    ↓
Agent Execution (invoke model)
    ↓
Memory Service (capture output)
    ↓
HTTP Response
```

### Memory Capture Flow

```
Agent Execution Complete
    ↓
Extract Interaction (input/output)
    ↓
Generate Embeddings
    ↓
Store in DynamoDB
    ↓
Update Indices
    ↓
Cleanup (TTL/archival)
```

### Semantic Search Flow

```
User Query
    ↓
Generate Query Embedding
    ↓
Vector Search (LSH/HNSW)
    ↓
Rank by Similarity
    ↓
Return Top-K Results
```

## Security Model

### Zero-Trust Architecture

1. **Authentication:** All requests authenticated via OAuth2
2. **Authorization:** RBAC per session/agent
3. **Encryption in Transit:** TLS 1.3
4. **Encryption at Rest:** KMS keys per deployment
5. **Audit Logging:** All operations logged to DynamoDB

### Credential Management

- User credentials stored in KMS-encrypted vault
- OAuth tokens cached with TTL
- Automatic rotation of service credentials
- Secure credential injection via environment

## Scalability Considerations

### Horizontal Scaling

- Agent Core: Stateless, scales via ECS/Lambda
- Memory Service: Partitioned by sessionId
- Identity Service: Cached tokens reduce OAuth calls
- API Gateway: Auto-scaling in AWS

### Performance Optimization

- DynamoDB on-demand pricing for variable workloads
- Embedding cache to avoid recomputation
- Connection pooling for database access
- CloudFront caching for static content

### Limits & Quotas

| Resource | Default Limit | Scaling |
|----------|---------------|---------|
| Session size | 100 MB | DynamoDB item size limit |
| Memory queries | 100/sec | On-demand autoscaling |
| Embedding dimension | 1536 | Configurable |
| Session TTL | 30 days | Configurable per agent |

## Deployment Topologies

### Development

```
Laptop → LocalStack (DynamoDB) → Python/Node runtime
```

### Staging

```
EC2 → RDS Proxy → DynamoDB → Lambda → Bedrock
```

### Production

```
ALB → ECS Fargate (Agent Core)
  ├─ Auto Scaling Group
  ├─ DynamoDB Global Tables (multi-region)
  ├─ RDS for session state
  ├─ Elasticache for caching
  └─ CloudFront for CDN
```

## Integration Points

### Bedrock Integration

Agent Core integrates with AWS Bedrock for LLM invocation:

```typescript
const bedrock = new BedrockRuntimeClient();
const response = await bedrock.invokeModel({
  modelId: '{{BEDROCK_MODEL_ID}}',
  body: JSON.stringify(prompt)
});
```

### External Tools

Agent Core can invoke external APIs:

```typescript
// Register tool
agent.registerTool({
  name: 'weather',
  description: 'Get weather for a location',
  handler: async (location) => {
    // Call external API
  }
});
```

## Monitoring & Observability

### CloudWatch Metrics

- Request latency
- Memory query time
- Token cache hit rate
- Error rates per component

### Logging

- Application logs → CloudWatch Logs
- Audit logs → DynamoDB (compliance)
- Error logs → SNS (alerting)

### Tracing

- X-Ray tracing for request flows
- OpenTelemetry support for custom spans

## Disaster Recovery

### Backup Strategy

- DynamoDB Point-in-Time Recovery (PITR)
- Daily snapshots to S3
- Cross-region replication
- Recovery Time Objective (RTO): 1 hour
- Recovery Point Objective (RPO): 15 minutes

### Failover

- Multi-AZ deployment for agent core
- Read replicas for databases
- Automated health checks and circuit breakers

## Future Roadmap

- [ ] Vector database integration (Pinecone, Weaviate)
- [ ] Multi-language support
- [ ] Agent-to-agent communication
- [ ] Distributed tracing enhancements
- [ ] GraphQL API
- [ ] Real-time WebSocket support

---

For deployment instructions, see [SETUP.md](./SETUP.md).
For examples, see [EXAMPLES.md](./EXAMPLES.md).
