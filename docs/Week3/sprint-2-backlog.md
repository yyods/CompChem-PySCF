# Sprint 2 Backlog - Core Service Implementation

**Sprint Goal:** Implement FastAPI service endpoints, PySCF integration, and job processing functionality.

**Duration:** 4 days  
**Estimated Story Points:** 42

---

## User Stories & Tasks

### Epic: Service Implementation

#### 🔬 **Story 2.1: Implement Job Submission Endpoint**
**Story Points:** 8  
**Priority:** Critical  
**Labels:** `feat`

**As a** GUI application  
**I want** to submit computational jobs via REST API  
**So that** quantum chemistry calculations can be performed

**Acceptance Criteria:**
- [ ] `POST /jobs` endpoint accepts job specifications per ICD
- [ ] Validates molecule_xyz, method, basis, and optional parameters
- [ ] Returns job_id (UUID) and status
- [ ] Handles validation errors with 400 status code
- [ ] Handles compute failures with 500 status code and message

**Tasks:**
- [ ] Implement job submission endpoint in `main.py`
- [ ] Add request validation using Pydantic schemas
- [ ] Generate UUID for job tracking
- [ ] Implement error handling and HTTP status codes
- [ ] Add request logging
- [ ] Write endpoint documentation

---

#### ⚡ **Story 2.2: Implement PySCF Runner**
**Story Points:** 13  
**Priority:** Critical  
**Labels:** `feat`

**As a** service  
**I want** to execute PySCF calculations  
**So that** quantum chemistry energies are computed accurately

**Acceptance Criteria:**
- [ ] PySCF runner in `services/pyscf_service/app/runner.py`
- [ ] Supports HF, B3LYP, MP2 methods
- [ ] Handles def2-SVP and other basis sets
- [ ] Implements `PYSCF_DRYRUN` mode for testing
- [ ] Generates `system_id` using sha1 hash
- [ ] Records timing information
- [ ] Includes environment metadata

**Tasks:**
- [ ] Create PySCF calculation runner class
- [ ] Implement method dispatcher (HF/B3LYP/MP2)
- [ ] Add molecule parsing and validation
- [ ] Implement dryrun mode with mock results
- [ ] Add timing measurements
- [ ] Create system_id generator
- [ ] Add environment version capture
- [ ] Handle PySCF exceptions gracefully

---

#### 💾 **Story 2.3: Implement Result Storage and Retrieval**
**Story Points:** 8  
**Priority:** Critical  
**Labels:** `feat`

**As a** system  
**I want** to store and retrieve job results reliably  
**So that** computed data is persistent and accessible

**Acceptance Criteria:**
- [ ] Results stored as JSON in `results/{job_id}.json`
- [ ] `GET /jobs/{job_id}/result` endpoint implemented
- [ ] Atomic writes to prevent corruption
- [ ] Proper error handling for missing jobs
- [ ] JSON format matches ICD specification
- [ ] File locking for concurrent access

**Tasks:**
- [ ] Implement result storage mechanism
- [ ] Create result retrieval endpoint
- [ ] Add atomic file writing
- [ ] Implement job status tracking
- [ ] Add file locking for concurrent safety
- [ ] Handle missing job errors (404)
- [ ] Add result validation

---

#### 🔍 **Story 2.4: Add Service Configuration Management**
**Story Points:** 5  
**Priority:** High  
**Labels:** `feat`, `infra`

**As a** deployment engineer  
**I want** configurable service parameters  
**So that** the service can run in different environments

**Acceptance Criteria:**
- [ ] Environment variables for key settings
- [ ] `OMP_NUM_THREADS=1` enforced
- [ ] `PYSCF_DRYRUN` mode configurable
- [ ] Service port configurable
- [ ] Results directory configurable
- [ ] Configuration validation on startup

**Tasks:**
- [ ] Create configuration management module
- [ ] Add environment variable parsing
- [ ] Implement configuration validation
- [ ] Add default value handling
- [ ] Document configuration options
- [ ] Add startup configuration logging

---

### Epic: Service Testing & Quality

#### 🧪 **Story 2.5: Comprehensive Service Testing**
**Story Points:** 8  
**Priority:** High  
**Labels:** `test`

**As a** developer  
**I want** thorough service testing  
**So that** API reliability is guaranteed

**Acceptance Criteria:**
- [ ] Integration tests for all endpoints
- [ ] Job submission and retrieval flow tests
- [ ] Error condition testing (invalid input, missing jobs)
- [ ] PySCF runner unit tests with dryrun mode
- [ ] Performance and timeout tests
- [ ] All tests pass in CI with `PYSCF_DRYRUN=1`

**Tasks:**
- [ ] Write integration test suite
- [ ] Create job flow end-to-end tests
- [ ] Add error condition test cases
- [ ] Test PySCF runner with mock data
- [ ] Add timeout and performance tests
- [ ] Create test fixtures and utilities
- [ ] Add test data validation

---

## Sprint Metrics

**Story Point Distribution:**
- Core Endpoints: 16 points
- PySCF Integration: 13 points
- Storage & Config: 13 points

**Technical Debt:**
- [ ] Add comprehensive error logging
- [ ] Implement request rate limiting
- [ ] Add health check enhancements

**Risk Assessment:**
- **High Risk:** PySCF integration complexity and dependency management
- **Medium Risk:** File I/O operations and concurrency
- **Low Risk:** Configuration management

**Dependencies:**
- Story 2.1 enables Story 2.3 testing
- Story 2.2 is critical path for all functionality
- Story 2.4 supports all other stories
- Story 2.5 validates all implementations

---

## Sprint Deliverables

### Functional Requirements Coverage:
- **FR-1:** ✅ Service accepts jobs and writes results
- **FR-2:** 🔄 Prerequisite for GUI implementation  
- **FR-3:** 🔄 Depends on Sprint 3 analysis
- **FR-4:** 🔄 CI integration in progress
- **FR-5:** ✅ Enhanced from Sprint 1

### Technical Milestones:
- **M3.2:** Service & GUI core tests pass in CI
- **M3.3:** Local HF/B3LYP runs produce JSONs

---

## API Contract Validation

The following endpoints must be fully functional:

```
GET  /health                 → {ok: true}
POST /jobs                   → {job_id: UUID, status: string}  
GET  /jobs/{job_id}/result   → {job_id, system_id, energy_hartree, ...}
```

**Sample Test Requests:**
```json
// Valid HF calculation
{
  "molecule_xyz": "3\n\nO 0 0 0\nH 0 0.757 0.586\nH 0 -0.757 0.586\n",
  "method": "HF",
  "basis": "def2-SVP",
  "grid_level": 3,
  "conv_tol": 1e-9,
  "spin": 0,
  "charge": 0
}

// Valid B3LYP calculation  
{
  "molecule_xyz": "2\n\nH 0 0 0\nH 0 0 0.74\n",
  "method": "B3LYP", 
  "basis": "def2-SVP",
  "grid_level": 3,
  "conv_tol": 1e-9,
  "spin": 0,
  "charge": 0
}
```

---

## Definition of Done Checklist

For each story to be considered complete:

- [ ] **Code:** Implementation follows specification requirements
- [ ] **Tests:** Unit and integration tests written and passing
- [ ] **Documentation:** API endpoints documented with examples
- [ ] **Review:** Code review completed with approval
- [ ] **Integration:** Works with Docker Compose setup
- [ ] **Performance:** Meets timing requirements (CI ≤ 5min total)
- [ ] **Validation:** Manual testing confirms expected behavior

---

## Sprint Review Criteria

**Must Have (MVP):**
- [x] All endpoints respond correctly
- [x] PySCF calculations complete successfully
- [x] Results stored in proper JSON format
- [x] Error handling covers edge cases

**Should Have:**
- [x] Comprehensive test coverage
- [x] Performance within acceptable limits
- [x] Clear API documentation

**Could Have:**
- [ ] Additional calculation methods
- [ ] Enhanced error messages
- [ ] Request/response logging

---

## Next Sprint Preview

**Sprint 3 Focus:** GUI Implementation & Analysis Pipeline
- PySide6 desktop application
- Service client integration  
- Data analysis and visualization
- End-to-end workflow testing
