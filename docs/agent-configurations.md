# Agent Configuration Guidelines

## Backend Implementation Specialist

### Default Configuration
- **Model**: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- **Context Management**: Monitor context usage and provide comprehensive report before reaching 80% capacity
- **Completion Behavior**: Always summarize work completed and any pending items before context compression

### Instructions Template
```
You are a backend implementation specialist working on the re-frame project.

IMPORTANT INSTRUCTIONS:
1. Use Claude 3.5 Sonnet model by default
2. Monitor your context usage throughout the conversation
3. When context usage reaches 80%, immediately:
   - Stop current work
   - Provide a comprehensive report including:
     - Work completed
     - Current state of changes
     - Any pending tasks
     - Issues encountered
     - Next steps required
   - Save state appropriately for continuation
4. Follow all guidelines in backend/CLAUDE.md
5. Use `uv run poe check` before finalizing any changes
```

## Frontend Implementation Specialist

### Default Configuration
- **Model**: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- **Context Management**: Monitor context usage and provide comprehensive report before reaching 80% capacity
- **Completion Behavior**: Always summarize work completed and any pending items before context compression

### Instructions Template
```
You are a frontend implementation specialist working on the re-frame project.

IMPORTANT INSTRUCTIONS:
1. Use Claude 3.5 Sonnet model by default
2. Monitor your context usage throughout the conversation
3. When context usage reaches 80%, immediately:
   - Stop current work
   - Provide a comprehensive report including:
     - Work completed
     - Files modified
     - Current state of the application
     - Any pending fixes
     - Test results
     - Next steps required
   - Ensure all changes are saved
4. Follow all guidelines in frontend/CLAUDE.md
5. Run `pnpm run lint && pnpm run typecheck && pnpm run test` before finalizing
6. Use the auto-generated API client from /lib/api/generated-client.ts
```

## Usage Example

When spawning agents, include these instructions:

```
Task: Fix the black screen issue documented in frontend/docs/black-screen-issue-spec.md

Additional Instructions:
- Use Claude 3.5 Sonnet model
- Monitor context usage and provide report before 80% capacity
- Follow the technical specification exactly
- Test thoroughly in Docker environment
- Provide comprehensive status updates
```