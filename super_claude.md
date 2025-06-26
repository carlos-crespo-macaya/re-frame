# SuperClaude Commands Cheat Sheet

## Analysis & Debugging Commands

### `/user:analyze` - Multi-dimensional code analysis
- `--code` - Code quality review
- `--arch` - Architecture analysis
- `--profile` - Performance profiling
- `--security` - Security assessment
- `--perf` - Performance bottlenecks
- `--watch` - Continuous monitoring
- `--interactive` - Guided improvement

### `/user:troubleshoot` - Debug and fix issues
- `--investigate` - Analyze issues
- `--fix` - Complete bug fixing
- `--five-whys` - Root cause analysis
- `--prod` - Production issues

### `/user:explain` - Technical explanations
- `--depth [ELI5/Beginner/Intermediate/Expert]` - Set depth
- `--visual` - Include diagrams
- `--uc` - Ultra-compressed (~30% size)

## Development Commands

### `/user:build` - Build projects/features
- `--react` - React app
- `--api` - API with docs
- `--magic` - UI generation
- `--init` - New project
- `--feature` - Feature implementation
- `--tdd` - Test-driven development
- `--watch` - Live reload

### `/user:test` - Testing utilities
- `--e2e` - End-to-end tests
- `--integration` - Integration tests
- `--coverage` - Coverage reports
- `--watch` - Auto-test on changes
- `--interactive` - Real-time feedback

### `/user:dev-setup` - Development environment setup
- Initialize development environment
- Configure tools and dependencies

## Improvement & Maintenance

### `/user:improve` - Code/performance optimization
- `--quality` - Code structure
  - `--solid` - SOLID principles
  - `--refactor` - Clean code
  - `--metrics` - Quality reports
- `--perf` - Performance optimization
- `--iterate` - Iterative improvement (85% threshold)
- `--watch` - Continuous improvement

### `/user:cleanup` - Project maintenance
- `--code` - Remove dead code, debug logs
- `--files` - Clean build artifacts
- `--deps` - Remove unused dependencies
- `--git` - Clean branches/history
- `--cfg` - Clean configurations
- `--all` - Comprehensive cleanup
- `--dry-run` - Preview changes

### `/user:scan` - Security validation
- `--validate` - Pre-execution safety
- `--security` - Full security analysis
- `--quick` - Fast critical issues
- `--strict` - Zero-tolerance mode

## Operations Commands

### `/user:deploy` - Application deployment
- `--env [dev/staging/prod]` - Target environment
- `--rollback` - Revert deployment
- `--plan` - Preview deployment

### `/user:git` - Git workflow management
- `--status` - Repository status
- `--commit` - Commit changes
- `--branch` - Branch management
- `--sync` - Fetch/pull/push
- `--merge` - Merge branches
- `--stash` - Temporary changes
- `--history` - Commit history
- `--checkpoint` - Create snapshot
- `--rollback` - Revert to checkpoint

### `/user:migrate` - Database/code migration
- Handle schema changes
- Data migration workflows

## Design & Documentation

### `/user:design` - Software architecture
- `--api` - REST/GraphQL design
- `--ddd` - Domain-driven design
- `--prd` - Product requirements

### `/user:document` - Generate documentation
- `--api` - API documentation
- `--user` - User guides
- `--uc` - Ultra-compressed (~70% reduction)

### `/user:estimate` - Time/complexity predictions
- Project estimation
- Task complexity analysis

## Workflow Commands

### `/user:spawn` - Spawn specialized agents
- `--task "<description>"` - Define specific task
- Parallel execution capability
- Specialized expertise (Frontend/Backend/DevOps/Data)

### `/user:load` - Project context loading
- Load project configuration
- Initialize context

## Universal Flags

### Thinking Modes (apply to any command)
- `--think` - Multi-component analysis
- `--think-hard` - Complex system analysis
- `--ultrathink` - Critical/complete redesign

### MCP Server Controls
- `--c7` - Force Context7 (docs)
- `--seq` - Force Sequential (analysis)
- `--magic` - Force Magic (UI)
- `--pup` - Force Puppeteer (browser)
- `--all-mcp` - Enable all MCPs
- `--no-mcp` - Disable all MCPs

### Planning & Documentation
- `--plan` - Show plan before execution
- `--watch` - Continuous monitoring
- `--interactive` - Step-by-step guidance
- `--uc` or `--ultracompressed` - Reduce output ~70%

## Usage Pattern
```
/user:<command> [arguments] [flags]
```

## Examples
- `/user:analyze --code --security --think`
- `/user:build --react --magic --tdd`
- `/user:troubleshoot --fix --prod --ultrathink`
- `/user:improve --perf --iterate`
- `/user:git --commit --plan`

## Output Locations
- Reports: `.claudedocs/reports/`
- Metrics: `.claudedocs/metrics/`
- Documentation: `/docs/[category]/`

Version: SuperClaude v4.0.0