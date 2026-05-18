# Repository Structure & Navigation

## Purpose
This document describes the structure of the agentcore-memory repository and provides guidance for developers and AI agents working with the codebase.

## Directory Tree

```
agentcore-memory/
├── README.md                 # Project overview and quick start
├── ARCHITECTURE.md          # System design and architecture documentation
├── SETUP.md                # Installation and deployment guide
├── EXAMPLES.md             # Runnable code examples
├── CONTRIBUTING.md         # Contribution guidelines
├── AGENTS.md               # This file - repository structure
├── LICENSE                 # MIT License
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── package.json            # NPM dependencies
├── tsconfig.json           # TypeScript configuration
├── jest.config.js          # Jest test configuration
├── eslint.config.js        # ESLint configuration
├── docker-compose.yml      # Docker Compose for local dev
├── Dockerfile              # Container image definition
│
├── src/                    # Application source code
│   ├── agent/              # Agent runtime and execution
│   │   ├── runtime.ts      # Agent core runtime
│   │   ├── types.ts        # Agent type definitions
│   │   └── utils.ts        # Agent utilities
│   │
│   ├── memory/             # Memory service and persistence
│   │   ├── service.ts      # Memory service implementation
│   │   ├── store.ts        # DynamoDB persistence layer
│   │   ├── embedding.ts    # Vector embedding service
│   │   └── types.ts        # Memory type definitions
│   │
│   ├── identity/           # Authentication and authorization
│   │   ├── service.ts      # Identity service
│   │   ├── oauth.ts        # OAuth2 implementation
│   │   ├── vault.ts        # Credential vault (KMS)
│   │   └── types.ts        # Identity types
│   │
│   ├── api/                # HTTP API endpoints
│   │   ├── routes.ts       # API route definitions
│   │   ├── middleware.ts   # Express middleware
│   │   ├── handlers.ts     # Request handlers
│   │   └── errors.ts       # Error handling
│   │
│   ├── models/             # Data models and schemas
│   │   ├── agent.ts        # Agent model
│   │   ├── memory.ts       # Memory model
│   │   ├── session.ts      # Session model
│   │   └── user.ts         # User model
│   │
│   ├── utils/              # Shared utilities
│   │   ├── logger.ts       # Logging utility
│   │   ├── config.ts       # Configuration loader
│   │   ├── aws.ts          # AWS SDK utilities
│   │   └── helpers.ts      # Helper functions
│   │
│   └── index.ts            # Application entry point
│
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   │   ├── memory.test.ts
│   │   ├── auth.test.ts
│   │   └── api.test.ts
│   │
│   ├── integration/        # Integration tests
│   │   ├── memory-store.test.ts
│   │   ├── oauth-flow.test.ts
│   │   └── agent-execution.test.ts
│   │
│   └── e2e/               # End-to-end tests
│       ├── agent-flow.test.ts
│       └── memory-retrieval.test.ts
│
├── examples/               # Runnable code examples
│   ├── basic/              # Basic memory operations
│   │   ├── store.ts
│   │   └── retrieve.ts
│   │
│   ├── oauth2-flow/        # OAuth2 authentication
│   │   ├── github.ts
│   │   └── google.ts
│   │
│   ├── multi-turn/         # Multi-turn conversations
│   │   ├── conversation.ts
│   │   └── context-restore.ts
│   │
│   └── semantic-search/    # Semantic memory search
│       ├── search.ts
│       └── embeddings.ts
│
├── docs/                   # Documentation
│   ├── diagrams/           # Architecture diagrams (generated)
│   │   ├── system-architecture.png
│   │   ├── component-interactions.png
│   │   ├── memory-flow.png
│   │   ├── agent-lifecycle.png
│   │   └── api-request-flow.png
│   │
│   ├── guides/             # How-to guides
│   │   ├── local-development.md
│   │   ├── aws-setup.md
│   │   └── troubleshooting.md
│   │
│   └── api/                # API documentation
│       ├── endpoints.md
│       └── schemas.md
│
├── deployment/            # Infrastructure as Code
│   ├── cloudformation/     # CloudFormation templates
│   │   ├── tables.yaml     # DynamoDB tables
│   │   ├── roles.yaml      # IAM roles
│   │   └── ecs.yaml        # ECS deployment
│   │
│   ├── helm/               # Kubernetes Helm charts
│   │   ├── values.yaml
│   │   ├── templates/
│   │   └── Chart.yaml
│   │
│   ├── docker/             # Docker-related files
│   │   ├── Dockerfile.prod
│   │   └── docker-compose.prod.yml
│   │
│   └── scripts/            # Deployment scripts
│       ├── deploy.sh
│       └── teardown.sh
│
└── scripts/                # Utility scripts
    ├── setup.sh            # Initial setup
    ├── test.sh             # Run tests
    └── deploy.sh           # Deploy to AWS
```

## Key Files Explained

### Root Configuration Files

| File | Purpose |
|------|---------|
| `package.json` | NPM dependencies and scripts |
| `tsconfig.json` | TypeScript compiler options |
| `jest.config.js` | Test runner configuration |
| `eslint.config.js` | Code linter rules |
| `.env.example` | Environment variable template |
| `Dockerfile` | Container image definition |
| `docker-compose.yml` | Local development environment |

### Source Code Modules

#### `/src/agent/`
**Responsibilities:** Agent runtime and execution
- **runtime.ts** - Core agent execution engine
- **types.ts** - TypeScript interfaces for agent
- **utils.ts** - Helper functions for agents

**Integration Points:** Memory service, Identity service, Bedrock API

#### `/src/memory/`
**Responsibilities:** Persistent memory storage and retrieval
- **service.ts** - Main memory service API
- **store.ts** - DynamoDB persistence layer
- **embedding.ts** - Vector embedding generation
- **types.ts** - Memory data structures

**Integration Points:** DynamoDB, embedding service, semantic search

#### `/src/identity/`
**Responsibilities:** Authentication and credential management
- **service.ts** - Identity service API
- **oauth.ts** - OAuth2 / OIDC implementation
- **vault.ts** - KMS-encrypted credential storage
- **types.ts** - Auth data structures

**Integration Points:** OAuth providers, KMS, session management

#### `/src/api/`
**Responsibilities:** HTTP API and request routing
- **routes.ts** - Express route definitions
- **middleware.ts** - Authentication, logging middleware
- **handlers.ts** - Request handler functions
- **errors.ts** - Error handling and responses

**Integration Points:** Agent core, memory service, identity service

### Test Organization

| Directory | Purpose | Run Command |
|-----------|---------|-------------|
| `tests/unit/` | Isolated component tests | `npm test -- unit` |
| `tests/integration/` | Service interaction tests | `npm test -- integration` |
| `tests/e2e/` | End-to-end user flows | `npm run test:e2e` |

### Examples

Each example demonstrates a specific use case and is self-contained:

```bash
# Run individual example
npx ts-node examples/basic/store.ts
npx ts-node examples/oauth2-flow/github.ts
npx ts-node examples/multi-turn/conversation.ts
npx ts-node examples/semantic-search/search.ts
```

### Documentation

| File | Audience | Purpose |
|------|----------|---------|
| `README.md` | All users | Project overview and quick start |
| `ARCHITECTURE.md` | Technical leads, developers | System design details |
| `SETUP.md` | DevOps, developers | Installation and deployment |
| `EXAMPLES.md` | Developers | Code samples and patterns |
| `CONTRIBUTING.md` | Contributors | Development guidelines |

### Deployment

- **CloudFormation** - Infrastructure definitions (DynamoDB, IAM, ECS)
- **Helm Charts** - Kubernetes deployment configurations
- **Scripts** - Automated deployment and teardown

## Common Tasks

### Adding a New Feature

1. Create feature branch: `git checkout -b feat/my-feature`
2. Add code to appropriate module in `src/`
3. Add tests to `tests/`
4. Update documentation if needed
5. Submit PR

### Running Tests

```bash
npm test              # All tests
npm test -- unit     # Unit tests only
npm test -- --coverage  # With coverage report
```

### Building for Production

```bash
npm run build        # Compile TypeScript
npm run lint         # Check code style
npm run type-check   # TypeScript type checking
```

### Local Development

```bash
npm install
npm run dev          # Start with hot reload
npm test -- --watch  # Tests in watch mode
```

## Dependencies

### External Services
- **AWS Bedrock** - LLM inference
- **DynamoDB** - Persistent storage
- **Cognito / OAuth** - Authentication

### Key Packages
- `aws-sdk` - AWS SDK v3
- `express` - HTTP framework
- `typescript` - Type system
- `jest` - Test framework
- `eslint` - Code linting

## Code Standards

### TypeScript
- Strict mode enabled
- All functions typed
- No `any` types without JSDoc explanation

### Naming Conventions
- Classes: `PascalCase` (e.g., `MemoryService`)
- Functions: `camelCase` (e.g., `captureMemory`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`)
- Files: `kebab-case` (e.g., `memory-service.ts`) or match class name

### Testing
- Test files: `*.test.ts`
- Describe blocks: module name
- Test names: describe what happens

## For AI Agents

When working with this codebase:

1. **Understand Architecture:** Read [ARCHITECTURE.md](./ARCHITECTURE.md) first
2. **Check Examples:** Look in `examples/` for similar patterns
3. **Follow Conventions:** Match existing code style
4. **Update Tests:** Add tests for new functionality
5. **Document Changes:** Update relevant documentation

### File Ownership by Feature

- **Memory operations** → `/src/memory/`, `tests/memory/`
- **Auth/Identity** → `/src/identity/`, `tests/identity/`
- **Agent execution** → `/src/agent/`, `tests/agent/`
- **HTTP API** → `/src/api/`, `tests/api/`
- **Infrastructure** → `/deployment/`

## Debugging Tips

- Check logs: `npm run logs`
- Enable debug mode: `DEBUG=* npm start`
- Use X-Ray: See configuration in SETUP.md
- Check CloudWatch: AWS console or `aws logs`

## Performance Considerations

- Memory queries should complete < 100ms
- Agent execution < 5 seconds typical
- Batch operations for bulk inserts
- Use caching for frequently accessed data

## Security Notes

- Never commit `.env` files with real credentials
- Use `{{PLACEHOLDER}}` format in documentation
- Keep dependencies updated
- Review security implications of changes

---

**Questions?** Check [README.md](./README.md) or [SETUP.md](./SETUP.md) for more information.

**Contributing?** Read [CONTRIBUTING.md](./CONTRIBUTING.md) first.
