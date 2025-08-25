---
StoryID: S13
Title: "Set up CI/CD Pipeline"
Sprint: "Sprint 1"
Owner: "DevOps Engineer"
Status: "Planned"
---
# S13 — Set up CI/CD Pipeline: Implementation Strategy

## 1. Objective
Establish automated GitHub Actions CI/CD pipeline with three distinct jobs (tests, gui-artifact, viz) that enforce quality gates, generate artifacts, and respect timing budgets per technical specification.

## 2. Scope & Non-Goals
**Scope:**
- GitHub Actions workflow configuration
- Three jobs: tests, gui-artifact, viz
- Environment variable configuration for PYSCF_DRYRUN
- Artifact upload and management
- Timing budget enforcement (tests ≤3min, gui-artifact ≤1min, viz ≤2min)

**Non-Goals:**
- Complex deployment automation
- Multi-environment CI (only main branch initially)
- Advanced security scanning (separate story)
- Performance benchmarking automation

## 3. Requirements & Acceptance Criteria
- [ ] GitHub Actions workflow created in `.github/workflows/ci.yml`
- [ ] Three jobs configured: `tests`, `gui-artifact`, `viz`
- [ ] `PYSCF_DRYRUN=1` environment variable set for tests
- [ ] Time budgets respected: tests ≤3min, gui-artifact ≤1min, viz ≤2min
- [ ] Artifacts uploaded correctly

## 4. Architecture & Data Impact
**Components:**
- GitHub Actions runner (Ubuntu latest)
- Python 3.10+ environment
- Docker for service testing
- Artifact storage in GitHub

**Dependencies:**
- pytest for testing framework
- PySide6 for GUI components
- pandas/matplotlib for analysis
- FastAPI/httpx for service testing

## 5. Implementation Plan (Step-by-Step)
1. **Create Workflow File Structure**
   - Create `.github/workflows/ci.yml`
   - Define workflow triggers (push, pull_request on main)
   - Set up job matrix and environment configuration

2. **Configure Tests Job**
   - Set up Python 3.10 environment
   - Install dependencies: pytest, httpx, fastapi, pydantic, requests, PySide6
   - Set `PYSCF_DRYRUN=1` environment variable
   - Run `pytest -q` for service and GUI core tests
   - Add timeout: 3 minutes maximum

3. **Configure GUI Artifact Job**
   - Set up lightweight environment
   - Create ZIP archive of `apps/pyscf_gui` directory
   - Upload as `PySCF-GUI-sources.zip` artifact
   - Add timeout: 1 minute maximum

4. **Configure Viz Job**
   - Set up Python environment with pandas, matplotlib
   - Install analysis dependencies from `analysis/requirements.txt`
   - Run `analysis/aggregate.py` if results exist
   - Run `analysis/plots.py` if CSV generated
   - Upload `analysis_out/` directory as artifacts
   - Add timeout: 2 minutes maximum

5. **Add Job Dependencies and Conditions**
   - Tests job runs unconditionally
   - GUI artifact job runs in parallel with tests
   - Viz job runs conditionally (only if results/*.json exist)

6. **Configure Artifact Management**
   - Set artifact retention policy
   - Configure proper artifact naming
   - Add artifact download instructions in README

## 6. API/Schema Changes
No API or schema changes. Configuration only affects CI/CD pipeline.

**GitHub Actions Workflow Structure:**
```yaml
name: CI Pipeline
on: [push, pull_request]
jobs:
  tests:
    runs-on: ubuntu-latest
    timeout-minutes: 3
    env:
      PYSCF_DRYRUN: 1
    steps: [...]
  
  gui-artifact:
    runs-on: ubuntu-latest
    timeout-minutes: 1
    steps: [...]
  
  viz:
    runs-on: ubuntu-latest
    timeout-minutes: 2
    steps: [...]
```

## 7. Test Plan
**Unit Tests:**
- Workflow YAML syntax validation
- Job configuration verification
- Environment variable propagation

**Integration Tests:**
- Complete workflow execution
- Artifact generation and upload
- Timeout enforcement verification

**E2E Tests:**
- Full PR workflow with CI checks
- Artifact download and validation
- Multi-job parallel execution

**Edge/Failure Cases:**
- Timeout scenarios for each job
- Missing dependencies handling
- Artifact upload failures
- Empty results directory handling

**Coverage Target:** 100% (workflow execution paths)

## 8. Verification Checklist (DoD)
- [ ] GitHub Actions workflow created in `.github/workflows/ci.yml`
- [ ] Three jobs configured: `tests`, `gui-artifact`, `viz`
- [ ] `PYSCF_DRYRUN=1` environment variable set for tests
- [ ] Time budgets respected: tests ≤3min, gui-artifact ≤1min, viz ≤2min
- [ ] Artifacts uploaded correctly
- [ ] Workflow triggers on push and pull_request
- [ ] All jobs pass on clean repository
- [ ] Timeout enforcement working correctly

## 9. Risk, Mitigation, Rollback
**Top Risks:**
- GitHub Actions quota limits exceeded
- Dependency installation timeouts
- Artifact storage limitations
- Cross-platform compatibility issues

**Detection Signals:**
- Workflow failures or timeouts
- Missing or corrupted artifacts
- Slow job execution times
- Resource limit warnings

**Mitigation:**
- Use dependency caching for faster builds
- Implement progressive timeout warnings
- Monitor GitHub Actions usage metrics
- Test workflow on feature branches first

**Rollback Steps:**
- Disable workflow temporarily
- Revert to manual testing procedures
- Remove problematic job configurations
- Restore previous CI setup if exists

## 10. Dependencies & Sequencing
**Upstream Dependencies:**
- Repository structure (S12) must be complete
- Basic test files must exist (S16)
- Requirements files must be properly configured

**Downstream Dependencies:**
- All future PRs will require green CI
- Artifact generation enables deployment workflows
- Testing framework supports all development

**Sequencing:**
- Requires S12 (structure) and S16 (basic tests)
- Should complete before major development work
- Enables parallel development with quality gates

## 11. Telemetry & Observability
**Metrics:**
- Job execution times and success rates
- Artifact generation success rates
- Resource usage (compute minutes)
- Queue times and concurrency

**Monitoring:**
- GitHub Actions workflow insights
- Artifact download statistics
- Build failure notifications
- Performance trend analysis

**Alerting:**
- Workflow failure notifications
- Timeout warning alerts
- Artifact generation failures
- Unusual resource usage spikes

## 12. Docs & Change Management
**Files to Update:**
- Create: `.github/workflows/ci.yml`
- Update: `README.md` (add CI status badge and artifact info)
- Update: `docs/sprint-1-backlog.md` (mark story complete)
- Create: `.github/workflows/README.md` (workflow documentation)

**Change Communication:**
- Team notification of CI requirements
- PR process update with CI gates
- Artifact usage documentation

## 13. Work Items
**Branch Name:** `feature/ci-cd-pipeline`
**PR Title:** "feat: establish GitHub Actions CI/CD pipeline with tests, artifacts, and viz jobs"
**Labels:** `infra`, `test`
**Reviewers:** Technical Lead, Backend Developer
**CI Gates:** Workflow syntax validation, test execution

## Follow-ups
OPEN-QUESTION: Should we implement branch protection rules requiring CI success before merge?
OPEN-QUESTION: Do we need separate workflow files for different trigger events (push vs PR)?
OPEN-QUESTION: Should viz job create artifacts even when no results exist (empty analysis)?
