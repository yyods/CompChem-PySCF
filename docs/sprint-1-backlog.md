# Sprint 1 Backlog - Infrastructure & Core Setup

**Sprint Goal:** Establish project infrastructure, CI/CD pipeline, and core architecture foundation.

**Duration:** 3 days  
**Estimated Story Points:** 34

---

## User Stories & Tasks

### Epic: Project Infrastructure Setup

#### 🏗️ **Story 1.1: Set up Agile Workflow Infrastructure**
**Story Points:** 5  
**Priority:** Critical  
**Labels:** `infra`, `docs`

**As a** team member  
**I want** proper Agile workflow tools and documentation  
**So that** we can track progress and maintain quality standards

**Acceptance Criteria:**
- [ ] GitHub board with columns: Backlog → In Progress → In Review → Done
- [ ] Issue labels created: `feat`, `fix`, `docs`, `test`, `infra`, `ux`, `experiment`
- [ ] Definition of Done (DoD) document created in `docs/DoD.md`
- [ ] Pull Request template created in `.github/PULL_REQUEST_TEMPLATE.md`

**Tasks:**
- [ ] Create GitHub project board with proper columns
- [ ] Configure issue labels
- [ ] Write DoD document
- [ ] Create PR template with checklist
- [ ] Document branching strategy

---

#### 🔧 **Story 1.2: Establish Repository Structure**
**Story Points:** 3  
**Priority:** Critical  
**Labels:** `infra`

**As a** developer  
**I want** a well-organized repository structure  
**So that** code is maintainable and follows best practices

**Acceptance Criteria:**
- [ ] All directories created per specification layout
- [ ] README.md updated with project overview
- [ ] .gitignore configured to exclude `results/` directory
- [ ] Basic requirements.txt files in place

**Tasks:**
- [ ] Create directory structure: `services/`, `apps/`, `analysis/`, `tests/`, `docs/`
- [ ] Initialize subdirectories with `__init__.py` files
- [ ] Create placeholder requirements.txt files
- [ ] Update main README.md

---

#### ⚙️ **Story 1.3: Set up CI/CD Pipeline**
**Story Points:** 8  
**Priority:** Critical  
**Labels:** `infra`, `test`

**As a** developer  
**I want** automated testing and artifact generation  
**So that** code quality is maintained and builds are consistent

**Acceptance Criteria:**
- [ ] GitHub Actions workflow created in `.github/workflows/ci.yml`
- [ ] Three jobs configured: `tests`, `gui-artifact`, `viz`
- [ ] `PYSCF_DRYRUN=1` environment variable set for tests
- [ ] Time budgets respected: tests ≤3min, gui-artifact ≤1min, viz ≤2min
- [ ] Artifacts uploaded correctly

**Tasks:**
- [ ] Create GitHub Actions workflow file
- [ ] Configure `tests` job with proper dependencies
- [ ] Set up `gui-artifact` job to zip GUI sources
- [ ] Create `viz` job for analysis and plotting
- [ ] Add environment variables and secrets
- [ ] Test workflow execution

---

### Epic: Service Architecture

#### 🌐 **Story 1.4: Create FastAPI Service Foundation**
**Story Points:** 8  
**Priority:** High  
**Labels:** `feat`, `infra`

**As a** system  
**I want** a containerized FastAPI service  
**So that** computational jobs can be processed reliably

**Acceptance Criteria:**
- [ ] FastAPI application created in `services/pyscf_service/app/main.py`
- [ ] Dockerfile configured with PySCF dependencies
- [ ] Docker Compose file created with proper port mapping
- [ ] Service responds to `/health` endpoint
- [ ] Environment variables configured (`OMP_NUM_THREADS=1`)

**Tasks:**
- [ ] Create FastAPI application structure
- [ ] Write Dockerfile for PySCF service
- [ ] Configure docker-compose.yml
- [ ] Implement health check endpoint
- [ ] Set up bind mount for `results/` directory
- [ ] Add error handling and logging

---

#### 📋 **Story 1.5: Define Data Schemas**
**Story Points:** 5  
**Priority:** High  
**Labels:** `feat`

**As a** developer  
**I want** well-defined data schemas  
**So that** API contracts are clear and validated

**Acceptance Criteria:**
- [ ] Pydantic schemas created in `services/pyscf_service/app/schemas.py`
- [ ] Job request schema validates all required fields
- [ ] Job response schema includes all specified fields
- [ ] Client schema created in `apps/pyscf_gui/core/schema.py`
- [ ] Validation rules implemented per ICD specification

**Tasks:**
- [ ] Create JobRequest schema with validation
- [ ] Create JobResponse schema
- [ ] Create ResultData schema
- [ ] Add field validation (method choices, ranges)
- [ ] Create GUI client schemas
- [ ] Add schema documentation

---

#### 🧪 **Story 1.6: Implement Basic Unit Tests**
**Story Points:** 5  
**Priority:** High  
**Labels:** `test`

**As a** developer  
**I want** comprehensive unit tests  
**So that** code reliability is ensured

**Acceptance Criteria:**
- [ ] Service tests created in `tests/test_service.py`
- [ ] GUI core tests created in `tests/test_gui_core.py`
- [ ] Health endpoint test passes
- [ ] Schema validation tests pass
- [ ] Tests run with `PYSCF_DRYRUN=1` in CI

**Tasks:**
- [ ] Write health endpoint test
- [ ] Create job submission validation tests
- [ ] Test schema validation edge cases
- [ ] Set up test fixtures and mocks
- [ ] Configure pytest settings

---

## Sprint Metrics

**Story Point Distribution:**
- Infrastructure: 16 points
- Service Foundation: 13 points  
- Testing: 5 points

**Risk Assessment:**
- **High Risk:** CI/CD setup complexity
- **Medium Risk:** Docker configuration on different platforms
- **Low Risk:** Schema definition and basic tests

**Dependencies:**
- Story 1.1 must complete before others can start PR process
- Story 1.2 enables parallel work on Stories 1.4-1.6
- Story 1.3 depends on Stories 1.5-1.6 for meaningful tests

---

## Sprint Review Criteria

**Must Have (MVP):**
- [x] All critical priority stories completed
- [x] CI pipeline green and functional
- [x] Basic service responds to health checks
- [x] Repository structure follows specification

**Should Have:**
- [x] All unit tests passing
- [x] Documentation updated
- [x] Docker setup working on team machines

**Could Have:**
- [ ] Performance benchmarks established
- [ ] Additional validation rules
- [ ] Extended error handling

---

## Sprint Retrospective Topics

1. **What went well:**
   - Infrastructure setup process
   - Team collaboration on standards

2. **What could be improved:**
   - Docker setup documentation
   - CI pipeline optimization

3. **Action items for next sprint:**
   - Carry forward any incomplete stories
   - Plan GUI development approach
