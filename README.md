# Agentic Memory - Agent Core Runtime with Persistent Memory

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)

**Agentic Memory** is an enterprise-grade runtime framework for building AI agents with persistent memory capabilities. It provides a complete solution for managing agent state, session persistence, identity integration, and semantic memory retrieval.

> **Reference Implementation:** This is a production-ready reference implementation. For enterprise deployments, see [agentcore-identity](https://github.com/johnruiz24/agentcore-identity) for OAuth2 integration patterns.

## 🎯 Quick Start (5 Minutes)

### Prerequisites
- Node.js 18+ or Python 3.11+
- AWS Account with appropriate permissions ({{AWS_ACCOUNT_ID}})
- Docker (optional, for containerized deployment)

### Installation

```bash
# Clone the repository
git clone https://github.com/johnruiz24/agentcore-memory.git
cd agentcore-memory

# Configure environment
cp .env.example .env
# Edit .env with your AWS credentials (replace {{PLACEHOLDERS}} with actual values)

# Install dependencies
npm install
# or for Python: pip install -r requirements.txt

# Run tests to verify setup
npm test

# Start the agent runtime
npm start
```

### Your First Agent Memory

```typescript
import { AgentCore } from './src/agent/runtime';
import { MemoryService } from './src/memory/service';

// Initialize agent runtime
const agent = new AgentCore({
  agentId: 'my-first-agent',
  region: '{{AWS_REGION}}'
});

// Initialize memory service
const memory = new MemoryService({
  tableName: '{{TABLE_MEMORY_STORE}}'
});

// Store interaction memory
await memory.capture({
  sessionId: 'session-123',
  agentId: 'my-first-agent',
  interaction: {
    input: 'What is the weather?',
    output: 'The weather is sunny with 72°F',
    timestamp: new Date().toISOString()
  }
});

// Retrieve related memories using semantic search
const relatedMemories = await memory.semanticSearch({
  query: 'weather information',
  sessionId: 'session-123',
  limit: 5
});

console.log('Retrieved memories:', relatedMemories);
```

## ✨ Key Features

### 🧠 **Persistent Memory**
- Store and retrieve agent interactions with full context
- Semantic search across memory using embeddings
- Automatic memory cleanup and archival

### 🔐 **Multi-Provider Identity**
- OAuth2 authentication (GitHub, Google, custom providers)
- Per-user credential vault with KMS encryption
- PKCE flow for secure token exchange

### 🚀 **Production Ready**
- Containerized deployment (ECS Fargate, Docker)
- Zero-trust security model
- Comprehensive audit logging
- Automatic failover and recovery

### 🔄 **Session Management**
- Multi-turn conversation context
- Session persistence across restarts
- Automatic session expiration and cleanup

### 📊 **Semantic Capabilities**
- Embedding-based memory retrieval
- Natural language search over agent history
- Similarity-based conversation context

## 📚 Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** — System design, components, and data flows
- **[SETUP.md](./SETUP.md)** — Installation, configuration, and deployment guides
- **[EXAMPLES.md](./EXAMPLES.md)** — Runnable code examples and common patterns
- **[CONTRIBUTING.md](./CONTRIBUTING.md)** — Development guidelines and contribution process
- **[AGENTS.md](./AGENTS.md)** — Repository structure and organization

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Clients & APIs                     │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │      API Gateway / Router        │
        └──────────────┬───────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
    ┌────────┐   ┌─────────┐   ┌──────────┐
    │ Agent  │   │ Memory  │   │ Identity │
    │ Core   │   │ Service │   │ Service  │
    │Runtime │   └────┬────┘   └────┬─────┘
    └────────┘        │             │
         │             ▼             ▼
         │        ┌─────────┐   ┌─────────┐
         └───────▶│DynamoDB │   │ OAuth   │
                  │  Store  │   │Providers│
                  └─────────┘   └─────────┘
```

For detailed architecture, see [ARCHITECTURE.md](./ARCHITECTURE.md) and [docs/diagrams/](./docs/diagrams/).

## 🔧 Configuration

All configuration is managed via environment variables. See [.env.example](./.env.example) for a complete list.

### Essential Variables

```bash
# AWS Configuration
AWS_PROFILE={{AWS_PROFILE}}                    # AWS CLI profile
AWS_REGION={{AWS_REGION}}                      # AWS region

# Storage
TABLE_MEMORY_STORE={{TABLE_MEMORY_STORE}}      # DynamoDB memory table
TABLE_SESSIONS={{TABLE_SESSIONS}}              # DynamoDB session table

# Identity
COGNITO_POOL_ID={{COGNITO_POOL_ID}}            # Cognito user pool
COGNITO_CLIENT_ID={{COGNITO_CLIENT_ID}}        # Cognito app client

# Bedrock
BEDROCK_MODEL_ID={{BEDROCK_MODEL_ID}}          # Claude model ID
```

## 📖 Usage Examples

### Example 1: Basic Memory Storage

```typescript
const memory = new MemoryService();
await memory.capture({
  sessionId: 'user-123',
  interaction: {
    input: 'Hello, how are you?',
    output: 'I am doing well, thank you!'
  }
});
```

### Example 2: Semantic Search

```typescript
const results = await memory.semanticSearch({
  query: 'previous conversation about weather',
  sessionId: 'user-123',
  limit: 10
});

results.forEach(result => {
  console.log(`Score: ${result.similarity}`);
  console.log(`Memory: ${result.interaction.output}`);
});
```

For more examples, see [EXAMPLES.md](./EXAMPLES.md).

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests for specific component
npm test -- src/memory

# Run with coverage
npm test -- --coverage

# Run end-to-end tests
npm run test:e2e
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build Docker image
docker build -t agentcore-memory:latest .

# Run container
docker run -p 8080:8080 \
  --env AWS_PROFILE={{AWS_PROFILE}} \
  --env AWS_REGION={{AWS_REGION}} \
  agentcore-memory:latest
```

### AWS ECS Deployment

See [SETUP.md](./SETUP.md) for CloudFormation templates and deployment procedures.

### Kubernetes

For Kubernetes deployments, use the provided Helm charts (see `deployment/helm/`).

## 🔒 Security

- All credentials stored in KMS-encrypted vault
- Per-user access control via Identity Service
- Zero-trust authentication model
- Audit logging for all operations
- Regular security assessments

See [SETUP.md](./SETUP.md) for security configuration details.

## 🐛 Troubleshooting

### Common Issues

**Q: Memory queries are slow**  
A: Ensure DynamoDB has sufficient provisioned capacity. Check [SETUP.md](./SETUP.md#scaling) for scaling guidelines.

**Q: Identity provider integration failing**  
A: Verify OAuth2 credentials in .env. See [EXAMPLES.md](./EXAMPLES.md#oauth2-flow) for correct configuration.

**Q: Agent not persisting state**  
A: Check IAM permissions. Agent needs permissions to read/write to memory tables.

For more help, see the [Troubleshooting](./SETUP.md#troubleshooting) section in SETUP.md.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Commit changes (`git commit -am 'Add my feature'`)
4. Push to branch (`git push origin feat/my-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/johnruiz24/agentcore-memory/issues)
- **Discussions**: [GitHub Discussions](https://github.com/johnruiz24/agentcore-memory/discussions)
- **Documentation**: [Full Documentation](./docs/)

## 🙏 Acknowledgments

- Built with [Bedrock](https://aws.amazon.com/bedrock/)
- Inspired by [agentcore-identity](https://github.com/johnruiz24/agentcore-identity)
- Community contributions from [contributors](./CONTRIBUTING.md)

---

**Ready to get started?** Jump to [Quick Start](#-quick-start-5-minutes) or read the [full documentation](./SETUP.md).

**Questions?** Check [EXAMPLES.md](./EXAMPLES.md) for common patterns and [Troubleshooting](./SETUP.md#troubleshooting) for solutions.
