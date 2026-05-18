# Contributing Guide

Thank you for your interest in contributing to Agentic Memory! This guide outlines the process for contributing code, documentation, and improvements.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please treat all contributors with respect.

## Getting Started

### 1. Fork the Repository

```bash
git clone https://github.com/your-username/agentcore-memory.git
cd agentcore-memory
```

### 2. Create a Feature Branch

```bash
git checkout -b feat/my-feature
# or
git checkout -b fix/my-bug
# or
git checkout -b docs/my-documentation
```

### 3. Set Up Development Environment

```bash
npm install
npm run dev
npm test
```

## Development Workflow

### Code Style

- **TypeScript:** Strict mode enabled
- **Formatting:** Prettier (automatic on save)
- **Linting:** ESLint configuration provided
- **Imports:** Absolute imports using `@/` alias

### Running Tests

```bash
# Run all tests
npm test

# Run specific test suite
npm test -- src/memory

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

### Type Checking

```bash
npm run type-check

# Should produce no errors
```

### Building

```bash
npm run build

# Output goes to ./dist
```

## Creating a Pull Request

### Before Submitting

- [ ] Fork the repository
- [ ] Create feature branch from `main`
- [ ] Make changes and commit (see Commit Guidelines below)
- [ ] Run tests: `npm test`
- [ ] Run linting: `npm run lint`
- [ ] Run type check: `npm run type-check`
- [ ] Update documentation if needed
- [ ] Rebase on latest main: `git rebase main`

### Commit Guidelines

Use conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Code style changes (no logic)
- `refactor` - Code refactor (no logic change)
- `perf` - Performance improvement
- `test` - Test changes
- `chore` - Build/tool changes

**Examples:**
```
feat(memory): add semantic search capability
fix(auth): resolve OAuth callback bug
docs(setup): clarify AWS configuration steps
test(memory): add integration tests for DynamoDB
```

### Opening PR

1. Push your branch: `git push origin feat/my-feature`
2. Open GitHub PR from your fork to `main`
3. Fill out the PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests pass
- [ ] Linting passes
- [ ] Types check
- [ ] Documentation updated
- [ ] Committed with conventional format
```

## Reporting Issues

### Bug Report

```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 12]
- Node.js: [e.g., 18.0.0]
- npm: [e.g., 9.0.0]

## Additional Context
Screenshots, logs, etc.
```

### Feature Request

```markdown
## Description
Clear description of desired feature

## Use Case
Why this feature is needed

## Proposed Implementation
How you think it should work

## Alternatives Considered
Other approaches considered
```

## Code Review Process

### What We Look For

1. **Functionality** - Does the code do what it claims?
2. **Tests** - Is there appropriate test coverage?
3. **Documentation** - Are changes documented?
4. **Performance** - Any performance implications?
5. **Security** - Any security concerns?
6. **Style** - Does it follow project conventions?

### Responding to Reviews

- Be respectful and professional
- Explain your reasoning
- Request clarification if unclear
- Update code based on feedback
- Push new commits (don't force push during review)

## Testing Guidelines

### Test Structure

```typescript
describe('MemoryService', () => {
  describe('capture', () => {
    it('should store interaction in DynamoDB', async () => {
      const memory = new MemoryService();
      const result = await memory.capture({
        sessionId: 'test-123',
        interaction: { input: 'test', output: 'test' }
      });
      expect(result.id).toBeDefined();
    });
  });
});
```

### Test Coverage

- Aim for 80%+ coverage
- Test happy paths and error cases
- Mock external dependencies
- Use meaningful test names

### Integration Tests

```bash
# Run integration tests (requires AWS credentials)
npm run test:integration

# Run against LocalStack
npm run test:integration -- --local
```

## Documentation Standards

### Code Comments

Only write comments for the "why", not the "what":

```typescript
// Good: Explains business logic
// We retry on network errors but not auth errors
if (error.code === 'NETWORK') {
  await retry();
}

// Bad: States the obvious
// Check if error code is NETWORK
if (error.code === 'NETWORK') {
```

### Documentation Files

- Use clear, concise language
- Include examples where helpful
- Link to related documentation
- Keep formatting consistent

### API Documentation

Use JSDoc for public APIs:

```typescript
/**
 * Store an agent interaction in persistent memory
 * @param interaction - The interaction to store
 * @returns Promise resolving to stored memory record
 * @throws {ValidationError} if interaction is invalid
 * @example
 * const memory = await service.capture({
 *   sessionId: 'user-123',
 *   interaction: { input: 'hello', output: 'hi' }
 * });
 */
async capture(interaction: Interaction): Promise<Memory>
```

## Performance Considerations

When contributing performance-sensitive code:

1. Benchmark before/after
2. Document performance implications
3. Avoid unnecessary allocations
4. Use efficient algorithms (O(log n) preferred over O(n²))
5. Profile with real data volumes

## Security Considerations

- Never commit secrets or credentials
- Sanitize user inputs
- Use parameterized queries
- Keep dependencies updated
- Report security issues privately

## Helpful Resources

- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [SETUP.md](./SETUP.md) - Development setup
- [EXAMPLES.md](./EXAMPLES.md) - Code examples
- [AWS SDK Documentation](https://docs.aws.amazon.com/sdk-for-javascript/)

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Creating a Release

1. Update version in `package.json`
2. Update `CHANGELOG.md`
3. Commit: `chore: release v1.2.3`
4. Create Git tag: `git tag v1.2.3`
5. Push and create GitHub release

## Community

- **Discussions:** GitHub Discussions
- **Issues:** GitHub Issues
- **Email:** [maintainer email]

## Thanks!

Your contributions help make Agentic Memory better for everyone. We appreciate your effort!
