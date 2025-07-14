# Project Setup Documentation

This directory contains all the scripts and documentation used to set up the CBT Assistant POC project structure, GitHub issues, and project board.

## Contents

### Setup Scripts
- **`create_github_issues.py`** - Python script to create GitHub issues, labels, and milestones
- **`summarize_issues.py`** - Script to summarize issues by epic and team
- **`github_issues.json`** - Complete issue definitions (32 issues across 3 epics)

### Generated Documentation
- **`GITHUB_ISSUES_SUMMARY.md`** - Summary of all created issues with links

### How These Were Used

1. **Planning Phase**
   - Teams collaborated to define user stories
   - Created JSON structure with all issue details
   
2. **Execution Phase**
   ```bash
   # Created labels and milestones
   python create_github_issues.py --token $GITHUB_TOKEN --repo macayaven/re-frame
   
   # Added issues to project board
   gh project item-add 7 --owner macayaven --url https://github.com/macayaven/re-frame/issues/{135..166}
   ```

3. **Organization Phase**
   - Set up project board columns
   - Organized issues by epic dependencies

## Lessons Learned

1. **Automation is key** - Creating 32 issues manually would have been error-prone
2. **Consistent formatting** - JSON structure ensured all issues follow same format
3. **Labels are important** - Proper labeling helps with filtering and organization
4. **Dependencies matter** - Epic structure enforces proper workflow

## Reusing for Other Projects

To adapt these scripts for another project:

1. Modify `github_issues.json` with your issues
2. Update label colors and names as needed
3. Adjust milestone dates
4. Run the script with your repo details

```bash
python create_github_issues.py --token YOUR_TOKEN --repo owner/repo
```

## Archive Notice

These files are preserved for:
- Historical reference
- Future project setup
- Onboarding documentation
- Troubleshooting if issues need recreation

**Note**: The scripts are no longer needed for day-to-day work but serve as important project artifacts.