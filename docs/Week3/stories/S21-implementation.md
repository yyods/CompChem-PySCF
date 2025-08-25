---
StoryID: S21
Title: "Implement Job Submission Endpoint"
Sprint: "Sprint 2"
Owner: "Backend Developer"
Status: "Planned"
---
# S21 — Implement Job Submission Endpoint: Implementation Strategy

## 1. Objective
Create fully functional `POST /jobs` endpoint that accepts quantum chemistry job specifications, validates input parameters per ICD, and returns job tracking information to enable GUI-to-service computational workflow.

## 2. Scope & Non-Goals
**Scope:**
- POST /jobs endpoint implementation in FastAPI
- Request validation using Pydantic schemas
- UUID generation for job tracking
- HTTP status code handling (200, 400, 500)
- Request logging and error reporting
- Integration with existing service foundation

**Non-Goals:**
- Actual PySCF calculation execution (Story 2.2)
- Result storage implementation (Story 2.3)
- Advanced authentication or rate limiting
- Job queuing or scheduling mechanisms

## 3. Requirements & Acceptance Criteria
- [ ] `POST /jobs` endpoint accepts job specifications per ICD
- [ ] Validates molecule_xyz, method, basis, and optional parameters
- [ ] Returns job_id (UUID) and status
- [ ] Handles validation errors with 400 status code
- [ ] Handles compute failures with 500 status code and message

## 4. Architecture & Data Impact
**Components Touched:**
- `services/pyscf_service/app/main.py` - endpoint implementation
- `services/pyscf_service/app/schemas.py` - request/response schemas
- FastAPI application routing and middleware

**API Contract:**
```
POST /jobs
Content-Type: application/json
Body: JobRequest schema per ICD specification
Response: JobResponse with job_id and status
```

**Data Flow:**
1. Receive JSON request → Validate schema → Generate UUID → Return response
2. Error cases: validation failure → 400, system error → 500

## 5. Implementation Plan (Step-by-Step)
1. **Import Required Dependencies**
   - Add FastAPI route decorators and HTTPException
   - Import UUID generation utilities
   - Import Pydantic validation schemas from S15

2. **Implement POST /jobs Endpoint**
   - Create async endpoint function with JobRequest parameter
   - Add route decorator with proper HTTP method and path
   - Implement request validation using Pydantic auto-validation

3. **Add UUID Generation**
   - Generate unique job_id using uuid4()
   - Ensure UUID string format consistency
   - Add job_id to response payload

4. **Implement Error Handling**
   - Catch Pydantic validation errors → 400 response
   - Handle system/unexpected errors → 500 response
   - Format error messages for client consumption

5. **Add Request Logging**
   - Log incoming job submissions (sanitized)
   - Log validation failures and error conditions
   - Include job_id in all relevant log entries

6. **Create Response Formatting**
   - Use JobResponse schema for consistent output
   - Include job_id, status, and optional message fields
   - Ensure JSON serialization compatibility

## 6. API/Schema Changes
**New Endpoint:**
```python
@app.post("/jobs", response_model=JobResponse)
async def submit_job(job_request: JobRequest) -> JobResponse:
    # Implementation details
```

**Request Schema (JobRequest):**
```json
{
  "molecule_xyz": "3\n\nO 0 0 0\nH 0 0.757 0.586\nH 0 -0.757 0.586\n",
  "method": "HF",
  "basis": "def2-SVP",
  "grid_level": 3,
  "conv_tol": 1e-9,
  "spin": 0,
  "charge": 0
}
```

**Response Schema (JobResponse):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Job submitted successfully"
}
```

## 7. Test Plan
**Unit Tests:**
- Valid job submission with all required fields
- Valid job submission with optional fields
- Invalid method validation (not in HF/B3LYP/MP2)
- Missing required fields (molecule_xyz, basis)
- Invalid XYZ format handling
- UUID generation uniqueness

**Integration Tests:**
- HTTP POST request/response cycle
- FastAPI schema validation integration
- Error response format validation
- Content-Type and header handling

**E2E Tests:**
- Complete client-to-server job submission
- Error scenarios with proper HTTP status codes
- Response time and performance validation

**Edge/Failure Cases:**
- Malformed JSON request body
- Extremely large molecule_xyz input
- Invalid numeric ranges for optional parameters
- Concurrent job submission stress testing

**Coverage Target:** >= 95% for endpoint logic

## 8. Verification Checklist (DoD)
- [ ] `POST /jobs` endpoint accepts job specifications per ICD
- [ ] Validates molecule_xyz, method, basis, and optional parameters
- [ ] Returns job_id (UUID) and status
- [ ] Handles validation errors with 400 status code
- [ ] Handles compute failures with 500 status code and message
- [ ] Endpoint responds within acceptable time limits (<1s)
- [ ] All unit and integration tests passing
- [ ] Error messages are clear and actionable
- [ ] Request logging captures necessary information

## 9. Risk, Mitigation, Rollback
**Top Risks:**
- Pydantic validation performance with large molecules
- UUID collision (extremely unlikely but possible)
- Memory usage with large XYZ coordinate strings
- FastAPI middleware interference with validation

**Detection Signals:**
- Slow response times on job submission
- Validation errors not properly caught
- Duplicate job_id generation
- Memory consumption spikes

**Mitigation:**
- Implement input size limits for XYZ coordinates
- Use uuid4() for cryptographically strong randomness
- Add memory monitoring and limits
- Test validation performance with realistic data

**Rollback Steps:**
- Disable POST /jobs endpoint temporarily
- Return to mock implementation for testing
- Revert to previous FastAPI application state
- Use manual job ID generation if UUID issues occur

## 10. Dependencies & Sequencing
**Upstream Dependencies:**
- Sprint 1: FastAPI service foundation (S14) completed
- Sprint 1: Data schemas (S15) implemented and tested
- Repository structure and basic testing framework

**Downstream Dependencies:**
- Story 2.2: PySCF runner needs job specifications
- Story 2.3: Result storage needs job_id tracking
- Story 2.5: Comprehensive testing builds on this endpoint

**Sequencing:**
- Should complete early in Sprint 2
- Enables parallel development of S22 and S23
- Required for meaningful S25 integration testing

## 11. Telemetry & Observability
**Metrics:**
- Job submission request rate and volume
- Validation error rate by error type
- Response time percentiles (p50, p95, p99)
- UUID generation performance

**Logging:**
- Job submission events with sanitized parameters
- Validation failure details and patterns
- Error conditions with stack traces
- Request/response timing information

**Monitoring:**
- HTTP status code distribution
- Error rate trends and spikes
- Memory usage during validation
- Concurrent request handling

**Alerts:**
- Error rate exceeding 5% threshold
- Response time exceeding 2s consistently
- Memory usage approaching container limits

## 12. Docs & Change Management
**Files to Update:**
- Update: `services/pyscf_service/app/main.py`
- Update: API documentation with endpoint examples
- Create: Integration test documentation
- Update: `README.md` with API usage examples

**API Documentation:**
- Endpoint description and purpose
- Request/response schema examples
- Error codes and troubleshooting
- Integration guide for client developers

**Change Communication:**
- API endpoint availability announcement
- Integration guide for GUI development team
- Error handling patterns and best practices

## 13. Work Items
**Branch Name:** `feature/job-submission-endpoint`
**PR Title:** "feat: implement POST /jobs endpoint with validation and error handling"
**Labels:** `feat`
**Reviewers:** Technical Lead, DevOps Engineer, Frontend Developer
**CI Gates:** All tests pass, API documentation generated, performance benchmarks met

## Follow-ups
OPEN-QUESTION: Should we implement request size limits to prevent memory exhaustion with large molecules?
OPEN-QUESTION: Do we need job submission rate limiting per client to prevent abuse?
OPEN-QUESTION: Should the endpoint accept batch job submissions or only single jobs?
