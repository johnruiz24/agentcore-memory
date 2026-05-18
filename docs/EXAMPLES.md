# Examples & Common Patterns

## Example 1: Basic Memory Storage

Store and retrieve a simple agent interaction.

**Scenario:** Agent answers a question, store both input and output.

```typescript
import { MemoryService } from './src/memory/service';

const memory = new MemoryService({
  tableName: '{{TABLE_MEMORY_STORE}}',
  region: '{{AWS_REGION}}'
});

async function basicExample() {
  const sessionId = 'user-123-session-456';
  
  // Capture interaction
  const captured = await memory.capture({
    sessionId,
    agentId: 'question-answerer',
    interaction: {
      input: 'What is the capital of France?',
      output: 'The capital of France is Paris.',
      metadata: {
        model: 'claude-3-sonnet',
        confidence: 0.99,
        processingTimeMs: 245
      }
    }
  });
  
  console.log('Captured memory:', captured.id);
  
  // Retrieve single memory
  const memory1 = await memory.getById(captured.id);
  console.log('Retrieved:', memory1.interaction.output);
  
  // Retrieve all session memories
  const sessionMemories = await memory.getBySession(sessionId);
  console.log(`Found ${sessionMemories.length} memories in session`);
}

basicExample().catch(console.error);
```

**Expected Output:**
```
Captured memory: mem_1234567890abc
Retrieved: The capital of France is Paris.
Found 1 memories in session
```

---

## Example 2: Multi-Turn Conversation

Demonstrate context preservation across multiple turns.

```typescript
async function multiTurnExample() {
  const sessionId = 'conversation-session-789';
  const agentId = 'travel-assistant';
  
  // Turn 1
  await memory.capture({
    sessionId,
    agentId,
    interaction: {
      input: 'I want to plan a trip to Japan',
      output: 'Great! When are you planning to go?'
    }
  });
  
  // Turn 2
  await memory.capture({
    sessionId,
    agentId,
    interaction: {
      input: 'Next month, around May',
      output: 'May is a wonderful time! What interests you - temples, food, modern cities?'
    }
  });
  
  // Turn 3
  await memory.capture({
    sessionId,
    agentId,
    interaction: {
      input: 'I love both temples and food',
      output: 'I recommend visiting Kyoto for temples and Tokyo for food. Budget 10-14 days.'
    }
  });
  
  // Retrieve all conversation turns
  const conversation = await memory.getBySession(sessionId);
  
  console.log('=== Conversation Flow ===');
  conversation.forEach((mem, i) => {
    console.log(`\nTurn ${i + 1}:`);
    console.log(`User: ${mem.interaction.input}`);
    console.log(`Agent: ${mem.interaction.output}`);
  });
}

await multiTurnExample();
```

**Expected Output:**
```
=== Conversation Flow ===

Turn 1:
User: I want to plan a trip to Japan
Agent: Great! When are you planning to go?

Turn 2:
User: Next month, around May
Agent: May is a wonderful time! What interests you...

Turn 3:
User: I love both temples and food
Agent: I recommend visiting Kyoto for temples...
```

---

## Example 3: Semantic Search

Search memories using natural language.

```typescript
async function semanticSearchExample() {
  const sessionId = 'user-123-session-456';
  
  // First, store some memories
  const memories = [
    { input: 'What\'s the weather?', output: 'Sunny, 72°F' },
    { input: 'Tell me about Python', output: 'Python is a programming language...' },
    { input: 'What is a programming language?', output: 'A programming language is...' },
    { input: 'Is it raining?', output: 'No, it\'s sunny today' }
  ];
  
  for (const mem of memories) {
    await memory.capture({
      sessionId,
      agentId: 'qa-bot',
      interaction: mem
    });
  }
  
  // Now search semantically
  const query = 'weather and climate conditions';
  const results = await memory.semanticSearch({
    sessionId,
    query,
    limit: 3
  });
  
  console.log(`\n=== Semantic Search for: "${query}" ===\n`);
  results.forEach((result, i) => {
    console.log(`Result ${i + 1} (Score: ${result.similarity.toFixed(2)})`);
    console.log(`Q: ${result.interaction.input}`);
    console.log(`A: ${result.interaction.output}\n`);
  });
}

await semanticSearchExample();
```

**Expected Output:**
```
=== Semantic Search for: "weather and climate conditions" ===

Result 1 (Score: 0.92)
Q: What's the weather?
A: Sunny, 72°F

Result 2 (Score: 0.87)
Q: Is it raining?
A: No, it's sunny today

Result 3 (Score: 0.45)
Q: Tell me about Python
A: Python is a programming language...
```

---

## Example 4: OAuth2 Authentication Flow

Implement secure user authentication.

```typescript
import { IdentityService } from './src/identity/service';

async function oauth2Example() {
  const identity = new IdentityService({
    githubClientId: process.env.OAUTH_GITHUB_CLIENT_ID,
    githubClientSecret: process.env.OAUTH_GITHUB_CLIENT_SECRET,
    redirectUri: 'https://yourdomain.com/auth/github/callback'
  });
  
  // Step 1: Generate authorization URL
  const authUrl = identity.getAuthorizationUrl('github', {
    state: 'random_state_string_12345'
  });
  console.log('Redirect user to:', authUrl);
  
  // Step 2: User redirects back with code
  const code = 'code_from_github_callback';
  const state = 'random_state_string_12345';
  
  // Step 3: Exchange code for tokens
  const tokens = await identity.exchangeCode('github', {
    code,
    state
  });
  
  console.log('Access Token:', tokens.accessToken);
  console.log('User ID:', tokens.userId);
  
  // Step 4: Create session
  const session = await identity.createSession({
    userId: tokens.userId,
    provider: 'github',
    accessToken: tokens.accessToken
  });
  
  console.log('Session created:', session.sessionId);
}

await oauth2Example();
```

**Expected Output:**
```
Redirect user to: https://github.com/login/oauth/authorize?client_id=...
Access Token: ghu_1234567890abcdefghij...
User ID: user_github_123456
Session created: sess_xyz789...
```

---

## Example 5: Agent Execution with Memory Integration

Full agent flow with context restoration.

```typescript
import { AgentCore } from './src/agent/runtime';
import { MemoryService } from './src/memory/service';

async function agentWithMemoryExample() {
  const agentId = 'customer-support-agent';
  const sessionId = 'customer-session-999';
  
  const agent = new AgentCore({ agentId });
  const memory = new MemoryService();
  
  // Simulate multiple customer interactions
  const interactions = [
    'I want to return my order',
    'Order #12345',
    'It arrived damaged',
    'Can I get a refund?'
  ];
  
  console.log('=== Agent Interaction Flow ===\n');
  
  for (let i = 0; i < interactions.length; i++) {
    const userInput = interactions[i];
    
    // Restore context from previous turns
    const context = await memory.getBySession(sessionId, { limit: 5 });
    
    // Execute agent with context
    const response = await agent.executeRequest({
      input: userInput,
      context: context.map(m => m.interaction),
      sessionId
    });
    
    // Store interaction
    await memory.capture({
      sessionId,
      agentId,
      interaction: {
        input: userInput,
        output: response.output
      }
    });
    
    console.log(`Turn ${i + 1}:`);
    console.log(`Customer: ${userInput}`);
    console.log(`Agent: ${response.output}\n`);
  }
}

await agentWithMemoryExample();
```

**Expected Output:**
```
=== Agent Interaction Flow ===

Turn 1:
Customer: I want to return my order
Agent: I'd be happy to help you with a return. What's your order number?

Turn 2:
Customer: Order #12345
Agent: Thank you. I found order #12345. What's the issue?

Turn 3:
Customer: It arrived damaged
Agent: I'm sorry to hear that. I can process an immediate refund or replacement.

Turn 4:
Customer: Can I get a refund?
Agent: Absolutely. I'm processing a refund for order #12345 now. You should see it in 3-5 business days.
```

---

## Example 6: Batch Memory Import

Import historical memories from external sources.

```typescript
async function batchImportExample() {
  const memory = new MemoryService();
  const sessionId = 'imported-session-001';
  
  // Prepare batch of interactions
  const interactions = [
    {
      timestamp: new Date('2024-01-01T10:00:00Z'),
      input: 'What are your hours?',
      output: 'We\'re open 9AM to 6PM daily'
    },
    {
      timestamp: new Date('2024-01-01T10:05:00Z'),
      input: 'Do you have free shipping?',
      output: 'Free shipping on orders over $50'
    },
    {
      timestamp: new Date('2024-01-01T10:10:00Z'),
      input: 'How long is shipping?',
      output: 'Standard shipping takes 5-7 business days'
    }
  ];
  
  // Batch import
  const results = await memory.batchCapture(
    interactions.map(int => ({
      sessionId,
      agentId: 'faq-bot',
      interaction: int
    }))
  );
  
  console.log(`Imported ${results.successful} of ${results.total} memories`);
  results.failed.forEach(err => console.error('Failed:', err.message));
}

await batchImportExample();
```

**Expected Output:**
```
Imported 3 of 3 memories
```

---

## Running These Examples

```bash
# Install dependencies
npm install

# Run specific example
npx ts-node examples/basic.ts
npx ts-node examples/multi-turn.ts
npx ts-node examples/semantic-search.ts

# Run all examples
npm run examples
```

---

For more information:
- See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- See [SETUP.md](./SETUP.md) for configuration
- See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines
