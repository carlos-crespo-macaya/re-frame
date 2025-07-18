# GitHub Issues Summary - CBT Assistant POC

## Project Board
- **URL**: https://github.com/users/macayaven/projects/7
- **Name**: CBT Assistant POC
- **Total Issues**: 32

## Epic 0: Monorepo Migration (5 issues)
**Milestone**: Preliminary: Monorepo Migration (Due: Jan 20, 2025)

- [#135](https://github.com/macayaven/re-frame/issues/135) - [Epic-0.1] [Frontend] Prepare re-frame repository structure
- [#136](https://github.com/macayaven/re-frame/issues/136) - [Epic-0.2] [DevOps] Merge backend code using git subtree
- [#137](https://github.com/macayaven/re-frame/issues/137) - [Epic-0.3] [DevOps] Update CI/CD workflows for monorepo
- [#138](https://github.com/macayaven/re-frame/issues/138) - [Epic-0.4] [Shared] Create GitHub labels and milestones
- [#139](https://github.com/macayaven/re-frame/issues/139) - [Epic-0.5] [Backend] Archive reframe-agents repository

## Epic 1: Local Docker Deployment (14 issues)
**Milestone**: POC Epic 1: Local Docker (Due: Jan 31, 2025)

### Backend Tasks (6)
- [#140](https://github.com/macayaven/re-frame/issues/140) - [Epic-1.1] [Backend] Docker Configuration
- [#141](https://github.com/macayaven/re-frame/issues/141) - [Epic-1.2] [Backend] Local API Route Implementation
- [#142](https://github.com/macayaven/re-frame/issues/142) - [Epic-1.3] [Backend] Audio Conversion for Local Testing
- [#143](https://github.com/macayaven/re-frame/issues/143) - [Epic-1.4] [Backend] Simple Session Management
- [#144](https://github.com/macayaven/re-frame/issues/144) - [Epic-1.5] [Backend] SSE Implementation for Local
- [#145](https://github.com/macayaven/re-frame/issues/145) - [Epic-1.6] [Backend] Local Integration Testing

### Frontend Tasks (6)
- [#146](https://github.com/macayaven/re-frame/issues/146) - [Epic-1.7] [Frontend] Frontend Docker Configuration
- [#147](https://github.com/macayaven/re-frame/issues/147) - [Epic-1.8] [Frontend] Local Environment Configuration
- [#148](https://github.com/macayaven/re-frame/issues/148) - [Epic-1.9] [Frontend] SSE Client Enhancement
- [#149](https://github.com/macayaven/re-frame/issues/149) - [Epic-1.10] [Frontend] CBT UI Components
- [#150](https://github.com/macayaven/re-frame/issues/150) - [Epic-1.11] [Frontend] Audio Format Documentation
- [#151](https://github.com/macayaven/re-frame/issues/151) - [Epic-1.12] [Frontend] Local Integration Tests

### Shared Tasks (2)
- [#164](https://github.com/macayaven/re-frame/issues/164) - [Epic-S1] [Shared] Basic Integration Documentation
- [#165](https://github.com/macayaven/re-frame/issues/165) - [Epic-S2] [Shared] End-to-End Testing Framework

## Epic 2: Cloud Run Production (13 issues)
**Milestone**: POC Epic 2: Cloud Run (Due: Feb 14, 2025)

### Backend Tasks (6)
- [#152](https://github.com/macayaven/re-frame/issues/152) - [Epic-2.1] [Backend] Cloud Run Configuration
- [#153](https://github.com/macayaven/re-frame/issues/153) - [Epic-2.2] [Backend] Production Security Hardening
- [#154](https://github.com/macayaven/re-frame/issues/154) - [Epic-2.3] [Backend] Cloud Storage Integration
- [#155](https://github.com/macayaven/re-frame/issues/155) - [Epic-2.4] [Backend] Basic Monitoring
- [#156](https://github.com/macayaven/re-frame/issues/156) - [Epic-2.5] [Backend] Basic Performance Verification
- [#157](https://github.com/macayaven/re-frame/issues/157) - [Epic-2.6] [Backend] POC Deployment Verification

### Frontend Tasks (6)
- [#158](https://github.com/macayaven/re-frame/issues/158) - [Epic-2.7] [Frontend] Production Build Optimization
- [#159](https://github.com/macayaven/re-frame/issues/159) - [Epic-2.8] [Frontend] Production Environment Configuration
- [#160](https://github.com/macayaven/re-frame/issues/160) - [Epic-2.9] [Frontend] Basic Error Handling (POC)
- [#161](https://github.com/macayaven/re-frame/issues/161) - [Epic-2.10] [Frontend] Basic Accessibility (POC)
- [#162](https://github.com/macayaven/re-frame/issues/162) - [Epic-2.11] [Frontend] Basic Performance Verification (POC)
- [#163](https://github.com/macayaven/re-frame/issues/163) - [Epic-2.12] [Frontend] Production Deployment Pipeline

### Shared Tasks (1)
- [#166](https://github.com/macayaven/re-frame/issues/166) - [Epic-S3] [Shared] Security Review

## Key Dependencies

1. **Epic 0 → Epic 1**: Must complete monorepo migration before starting local deployment
2. **Epic 1 → Testing**: Must complete and test locally before proceeding to Epic 2
3. **Testing → Epic 2**: Only proceed to Cloud Run after successful local testing

## Quick Links

- **Repository**: https://github.com/macayaven/re-frame
- **Project Board**: https://github.com/users/macayaven/projects/7
- **Milestones**: https://github.com/macayaven/re-frame/milestones

## Next Steps

1. **Frontend Team**: Start with issue #135 (repository restructuring)
2. **Backend Team**: Prepare for issue #136 (code merge)
3. **Both Teams**: Review all issues and add time estimates
4. **Project Board**: Move Epic 0 issues to "Ready" column

---

**Total Issues**: 32  
**Total Story Points**: 90  
**Timeline**: 3.5 weeks for POC completion