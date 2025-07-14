# Monorepo Migration Checklist

## Day 1: Prepare re-frame Repository ✅

### Frontend Team Tasks
- [ ] Create `frontend/` directory
- [ ] Move all current files into `frontend/`:
  ```bash
  mkdir frontend
  git mv app components lib public src types *.json *.js *.ts frontend/
  git mv .env.example frontend/
  ```
- [ ] Create `backend/` directory
- [ ] Update root `.gitignore` for monorepo
- [ ] Create root `docker-compose.yml`
- [ ] Create root `README.md` with monorepo structure
- [ ] Commit changes: "Prepare monorepo structure"

### Backend Team Tasks
- [ ] Prepare reframe-agents for migration
- [ ] Ensure all tests pass
- [ ] Document any special setup requirements

## Day 2: Merge Backend Code

### Joint Team Tasks
- [ ] Add reframe-agents as remote:
  ```bash
  git remote add backend-origin https://github.com/[org]/reframe-agents
  git fetch backend-origin
  ```
- [ ] Merge using subtree to preserve history:
  ```bash
  git subtree add --prefix=backend backend-origin/main --squash
  ```
- [ ] Verify file structure:
  ```
  re-frame/
  ├── backend/
  │   ├── src/
  │   ├── tests/
  │   └── ...
  ├── frontend/
  │   ├── app/
  │   ├── components/
  │   └── ...
  └── docker-compose.yml
  ```
- [ ] Test local development:
  ```bash
  docker-compose up
  ```
- [ ] Fix any path or configuration issues

## Day 3: Update CI/CD

### Frontend Team Tasks
- [ ] Move existing workflows to handle frontend path:
  ```yaml
  on:
    push:
      paths:
        - 'frontend/**'
  ```
- [ ] Add integration test workflow
- [ ] Update deployment scripts

### Backend Team Tasks
- [ ] Create backend deployment workflow
- [ ] Add backend-specific tests to CI
- [ ] Configure Cloud Run deployment

## Day 4: GitHub Setup

### Joint Team Tasks
- [ ] Create labels:
  ```bash
  # Using GitHub CLI
  gh label create "epic-1-local" --color "0052CC"
  gh label create "epic-2-production" --color "5319E7"
  gh label create "team-backend" --color "0E8A16"
  gh label create "team-frontend" --color "FB8C00"
  gh label create "team-shared" --color "FDD835"
  gh label create "priority-P0" --color "D32F2F"
  gh label create "priority-P1" --color "F57C00"
  gh label create "priority-P2" --color "FBC02D"
  gh label create "size-1" --color "E3F2FD"
  gh label create "size-2" --color "BBDEFB"
  gh label create "size-3" --color "90CAF9"
  gh label create "size-5" --color "64B5F6"
  gh label create "blocked" --color "000000"
  gh label create "needs-discussion" --color "7B1FA2"
  ```

- [ ] Create milestones:
  ```bash
  gh milestone create "POC Epic 1: Local Docker" --due "2025-01-25"
  gh milestone create "POC Epic 2: Cloud Run" --due "2025-02-07"
  ```

- [ ] Run issue creation script
- [ ] Create GitHub Project Board
- [ ] Configure board columns and automation

## Day 5: Finalization

### Frontend Team Tasks
- [ ] Update repository description
- [ ] Add backend team as collaborators
- [ ] Configure branch protection:
  - Require PR reviews
  - Require status checks
  - Dismiss stale reviews

### Backend Team Tasks
- [ ] Archive reframe-agents repository
- [ ] Add deprecation notice:
  ```markdown
  # ⚠️ This repository has been archived
  
  Development has moved to the monorepo:
  👉 https://github.com/[org]/re-frame
  ```
- [ ] Update any external documentation links

### Joint Team Tasks
- [ ] Final testing of complete setup
- [ ] Team kickoff meeting
- [ ] Assign first tasks from GitHub issues

## Success Criteria

- [ ] Both frontend and backend build successfully
- [ ] `docker-compose up` starts both services
- [ ] Integration tests pass
- [ ] CI/CD pipelines work for both services
- [ ] All team members have access
- [ ] GitHub issues created and assigned

## Quick Commands Reference

```bash
# Local development
docker-compose up

# Run frontend only
docker-compose up frontend

# Run backend only  
docker-compose up backend

# Run tests
docker-compose run frontend-tests
docker-compose run backend-tests
docker-compose run integration-tests

# View logs
docker-compose logs -f frontend
docker-compose logs -f backend
```

## Repository Structure Verification

```
✓ backend/
  ✓ src/
  ✓ tests/
  ✓ Dockerfile
  ✓ pyproject.toml
✓ frontend/
  ✓ app/
  ✓ components/
  ✓ Dockerfile
  ✓ package.json
✓ docker-compose.yml
✓ .github/workflows/
✓ docs/
✓ scripts/
✓ README.md
```

---

**Ready to Start**: Once both teams confirm, we begin with Day 1! 🚀