# GitHub Discussions Creation Guide

This guide explains how to create discussions programmatically using GitHub's GraphQL API, including solutions to common formatting issues.

## Prerequisites

1. **GitHub CLI installed**: `gh` command available
2. **Authenticated**: Run `gh auth login` if needed
3. **Repository access**: Write permissions to the repository

## Step 1: Get Required IDs

### Get Repository Node ID
```bash
gh api repos/macayaven/re-frame --jq '.node_id'
# Output: R_kgDOO_P4CA
```

### Get Discussion Category IDs
```bash
gh api graphql -f query='
query {
  repository(owner: "macayaven", name: "re-frame") {
    discussionCategories(first: 10) {
      nodes {
        id
        name
        description
      }
    }
  }
}'
```

Output will show category IDs like:
- General: `DIC_kwDOO_P4CM4Cs54v`
- Daily Standups: `DIC_kwDOO_P4CM4Cs7U_`
- Blockers: `DIC_kwDOO_P4CM4Cs7VG`

## Step 2: Create Discussion - Method 1 (File-based - RECOMMENDED)

This method avoids quote escaping issues by using a file.

### Create GraphQL mutation file
```bash
cat > /tmp/create_discussion.graphql << 'EOF'
mutation {
  createDiscussion(input: {
    repositoryId: "R_kgDOO_P4CA",
    categoryId: "DIC_kwDOO_P4CM4Cs54v",
    title: "Your Discussion Title Here",
    body: "Your discussion body here.\n\nSupports **markdown** formatting!\n\n## Headers work\n\n- Bullet points\n- Work fine\n\n### Code blocks too\n\n```bash\necho \"Hello World\"\n```\n\nJust use \\n for line breaks."
  }) {
    discussion {
      id
      url
    }
  }
}
EOF
```

### Execute the mutation
```bash
gh api graphql -F query=@/tmp/create_discussion.graphql
```

## Step 3: Create Discussion - Method 2 (Python Script)

For complex discussions with lots of formatting, use this Python script:

```python
#!/usr/bin/env python3
import subprocess
import json

def create_discussion(title, body, category_id="DIC_kwDOO_P4CM4Cs54v", repo_id="R_kgDOO_P4CA"):
    """Create a GitHub discussion using GraphQL API"""
    
    # Escape the body for GraphQL
    escaped_body = body.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    
    mutation = f'''
    mutation {{
      createDiscussion(input: {{
        repositoryId: "{repo_id}",
        categoryId: "{category_id}",
        title: "{title}",
        body: "{escaped_body}"
      }}) {{
        discussion {{
          id
          url
        }}
      }}
    }}
    '''
    
    # Write to temp file
    with open('/tmp/discussion_mutation.graphql', 'w') as f:
        f.write(mutation)
    
    # Execute via GitHub CLI
    result = subprocess.run(
        ['gh', 'api', 'graphql', '-F', 'query=@/tmp/discussion_mutation.graphql'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        print(f"✅ Discussion created: {data['data']['createDiscussion']['discussion']['url']}")
    else:
        print(f"❌ Error: {result.stderr}")

# Example usage
if __name__ == "__main__":
    title = "🚨 BLOCKED: Backend API Integration"
    
    body = """## Issue Blocked
- Issue: #142 - Audio conversion implementation
- PR: #145

## What's Blocking
The audio conversion library requires specific system dependencies that aren't available in our Docker image.

## What I've Tried
1. Added ffmpeg to Dockerfile
2. Tried using python-only solution
3. Researched alternative libraries

## What I Need
- [ ] Decision on audio conversion approach
- [ ] Help with Docker configuration
- [ ] @frontend-team input on audio format requirements

## Impact
- **Severity**: High
- **Other blocked work**: All audio-related features

## Proposed Solutions
1. Use cloud-based audio conversion service
2. Pre-process audio on frontend
3. Include system dependencies in Docker image
"""
    
    # For blockers category
    create_discussion(title, body, category_id="DIC_kwDOO_P4CM4Cs7VG")
```

## Common Issues and Solutions

### 1. Quote Escaping Problems

**Problem**: Quotes in your text break the GraphQL query.

**Solution**: Use the file-based method or escape quotes:
- Single quotes: `'` → `'"'"'` (in bash)
- Double quotes: `"` → `\"`
- Or use the Python script which handles this automatically

### 2. Newline Issues

**Problem**: Multi-line text doesn't format correctly.

**Solution**: Use `\n` for line breaks:
```graphql
body: "Line 1\n\nLine 2\n\n## Header\n\nMore text"
```

### 3. Code Blocks in Discussions

**Problem**: Code blocks with backticks cause parsing errors.

**Solution**: Escape backticks or use the file method:
```graphql
body: "Here's code:\n\n\```bash\necho \"test\"\n\```\n\nMore text"
```

### 4. Special Characters

**Problem**: Characters like `@`, `#`, `*` may cause issues.

**Solution**: These usually work fine, but if issues occur:
- `@mentions` work as-is: `@backend-team`
- Issue references work: `#135`
- Markdown works: `**bold**`, `*italic*`

## Quick Templates

### Daily Standup Update
```bash
cat > /tmp/standup.graphql << 'EOF'
mutation {
  createDiscussion(input: {
    repositoryId: "R_kgDOO_P4CA",
    categoryId: "DIC_kwDOO_P4CM4Cs7U_",
    title: "Backend Team Standup - Jan 16",
    body: "### Backend Team - Jan 16\n\n**Yesterday:**\n- Reviewed integration documentation\n- Prepared reframe-agents for merge\n\n**Today:**\n- Waiting for #135 completion\n- Reviewing CI/CD requirements\n- Planning git subtree merge strategy\n\n**Blockers:**\n- Blocked by #135 (frontend repo preparation)\n\n**Help Needed:**\n- Confirmation on Python version for monorepo (3.11 or 3.12?)"
  }) {
    discussion {
      url
    }
  }
}
EOF

gh api graphql -F query=@/tmp/standup.graphql
```

### Blocker Report
```bash
cat > /tmp/blocker.graphql << 'EOF'
mutation {
  createDiscussion(input: {
    repositoryId: "R_kgDOO_P4CA",
    categoryId: "DIC_kwDOO_P4CM4Cs7VG",
    title: "🚨 BLOCKED: Git Subtree Merge Failing",
    body: "## Issue Blocked\n- Issue: #136 - Merge backend code using git subtree\n\n## What's Blocking\nGit subtree command failing with merge conflicts in CI/CD files.\n\n## What I've Tried\n1. Manual conflict resolution\n2. Different merge strategies\n3. Excluding .github directory\n\n## What I Need\n- [ ] @frontend-team help with CI/CD file conflicts\n- [ ] Decision on which CI/CD config to keep\n\n## Impact\n- **Severity**: High\n- **Other blocked work**: All subsequent Epic 0 tasks"
  }) {
    discussion {
      url
    }
  }
}
EOF

gh api graphql -F query=@/tmp/blocker.graphql
```

## Alternative: Using GitHub Web UI

If CLI methods are challenging, the web UI is simpler:

1. Go to: https://github.com/macayaven/re-frame/discussions
2. Click "New discussion"
3. Select category
4. Write using normal Markdown
5. Submit

## Tips for Success

1. **Always test locally first**: Write your content in a markdown file and preview it
2. **Use the file method**: Avoids 90% of escaping issues
3. **Keep it simple**: Don't over-format, plain text with basic markdown works best
4. **Check the output**: The API returns the discussion URL on success
5. **Use templates**: Create reusable templates for common discussion types

## Need Help?

If you encounter issues:
1. Check the error message - it usually indicates the problem
2. Try the file-based method instead of inline
3. Simplify your formatting and add complexity gradually
4. Post in the General discussion category for help

---

*This guide is based on creating discussions #168 and #169 in the re-frame repository.*