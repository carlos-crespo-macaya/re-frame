# Project Artifacts Index

This document indexes all the planning, coordination, and setup artifacts created during the CBT Assistant POC project setup.

## 📁 Document Locations

### In `re-frame` Repository

#### `/docs/` - Main Documentation
- **`TEAM_COORDINATION_GUIDE.md`** - Complete guide for team collaboration
- **`FRONTEND_MONOREPO_RESPONSE.md`** - Frontend team's response to monorepo proposal
- **`MONOREPO_MIGRATION_CHECKLIST.md`** - Step-by-step migration checklist

#### `/docs/project-setup/` - Setup Artifacts
- **`create_github_issues.py`** - Script to create GitHub issues
- **`summarize_issues.py`** - Script to summarize issues
- **`github_issues.json`** - All 32 issue definitions
- **`GITHUB_ISSUES_SUMMARY.md`** - Summary with issue links
- **`README.md`** - Documentation of setup process

### In `reframe-agents` Repository

#### Integration Planning Documents
- **`INTEGRATION_PLAN.md`** - Detailed integration plan with all tasks
- **`INTEGRATION_REPORT_V2.md`** - Backend team's V2 integration proposal
- **`GITHUB_ISSUES_PROPOSAL.md`** - Proposal for GitHub organization
- **`PHASE_3_ENHANCEMENTS.md`** - Future enhancements after POC

## 🗂️ Document Timeline

1. **Initial Analysis** 
   - `INTEGRATION_ANALYSIS_REPORT.md` - First integration analysis
   - `INTEGRATION_REPORT_V2.md` - Refined proposal from backend

2. **Agreement Phase**
   - `INTEGRATION_UNIFIED_ASSESSMENT.md` - Unified agreement
   - `FRONTEND_MONOREPO_RESPONSE.md` - Frontend approval

3. **Planning Phase**
   - `INTEGRATION_PLAN.md` - Final plan with all tasks
   - `GITHUB_ISSUES_PROPOSAL.md` - GitHub organization strategy

4. **Execution Phase**
   - `MONOREPO_MIGRATION_CHECKLIST.md` - Migration steps
   - `github_issues.json` - Issue definitions
   - Setup scripts execution

5. **Coordination Phase**
   - `TEAM_COORDINATION_GUIDE.md` - Team working agreement
   - `GITHUB_ISSUES_SUMMARY.md` - Issue tracking reference

## 🎯 Purpose of Preservation

### Historical Record
- Shows evolution of technical decisions
- Documents team collaboration process
- Captures requirements and constraints

### Future Reference
- Template for similar projects
- Lessons learned documentation
- Reusable scripts and processes

### Onboarding
- New team members can understand project genesis
- Clear view of architecture decisions
- Understanding of team workflows

### Compliance
- Audit trail of decisions
- Documentation of security considerations
- Record of accessibility commitments

## 🔄 Migration Plan

After Epic 0 (Monorepo Migration) is complete:

1. Copy key documents from `reframe-agents` to `re-frame`:
   ```bash
   cp /Users/carlos/workspace/reframe-agents/INTEGRATION_PLAN.md ./docs/
   cp /Users/carlos/workspace/reframe-agents/PHASE_3_ENHANCEMENTS.md ./docs/
   ```

2. Archive `reframe-agents` repository with final notice

3. Update all document references to point to monorepo

## 📊 Statistics

- **Total Planning Documents**: ~12
- **Total Issues Created**: 32
- **Total Story Points**: 90
- **Labels Created**: 20
- **Milestones**: 3
- **Timeline**: 3.5 weeks

## 🔗 Quick Links

### Active Resources
- [Project Board](https://github.com/users/macayaven/projects/7)
- [Issues List](https://github.com/macayaven/re-frame/issues)
- [Team Coordination Guide](./TEAM_COORDINATION_GUIDE.md)

### Planning Artifacts
- [Integration Plan](/Users/carlos/workspace/reframe-agents/INTEGRATION_PLAN.md)
- [Migration Checklist](./MONOREPO_MIGRATION_CHECKLIST.md)
- [Phase 3 Enhancements](/Users/carlos/workspace/reframe-agents/PHASE_3_ENHANCEMENTS.md)

---

**Note**: This index will be updated after Epic 0 completion when all documents are consolidated in the monorepo.