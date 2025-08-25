---
StoryID: S23
Title: "Implement Result Storage and Retrieval"
Sprint: "Sprint 2"
Owner: "Backend Developer"
Status: "Planned"
---
# S23 — Implement Result Storage and Retrieval: Implementation Strategy

## 1. Objective
Create reliable result storage and retrieval system with JSON persistence, atomic writes, file locking, and proper error handling to ensure computational data integrity and accessibility.

## 2. Scope & Non-Goals
**Scope:**
- JSON result storage in `results/{job_id}.json` files
- GET /jobs/{job_id}/result endpoint implementation
- Atomic write operations to prevent data corruption
- File locking for concurrent access safety
- Error handling for missing jobs and file operations
- JSON format validation per ICD specification

**Non-Goals:**
- Database integration or complex persistence layers
- Result compression or optimization
- Advanced backup or replication mechanisms
- Real-time result streaming or websockets

## 3. Requirements & Acceptance Criteria
- [ ] Results stored as JSON in `results/{job_id}.json`
- [ ] `GET /jobs/{job_id}/result` endpoint implemented
- [ ] Atomic writes to prevent corruption
- [ ] Proper error handling for missing jobs
- [ ] JSON format matches ICD specification
- [ ] File locking for concurrent access

## 4. Architecture & Data Impact
**Components:**
- File system storage in mounted `results/` directory
- FastAPI endpoint for result retrieval
- Atomic write implementation using temporary files
- File locking mechanism for concurrent safety
- JSON serialization and validation

**Data Flow:**
1. Calculation completion → Atomic write to results/{job_id}.json
2. Client request → File existence check → Read and return JSON
3. Error cases: Missing file → 404, Read error → 500

**File Structure:**
```
results/
├── {job_id_1}.json
├── {job_id_2}.json
└── ...
```

## 5. Implementation Plan (Step-by-Step)
1. **Create Result Storage Module**
   - Create `ResultStorage` class for file operations
   - Implement atomic write using temporary file + rename
   - Add file locking mechanism using fcntl/msvcrt
   - Include error handling and validation

2. **Implement Atomic Write Functionality**
   - Write data to temporary file with unique name
   - Validate JSON structure before final write
   - Atomic rename operation to final filename
   - Cleanup on failure with proper exception handling

3. **Create Result Retrieval Endpoint**
   - Implement GET /jobs/{job_id}/result route
   - Add job_id validation and sanitization
   - File existence checking with appropriate error responses
   - JSON loading and response formatting

4. **Add File Locking System**
   - Implement cross-platform file locking
   - Handle lock acquisition timeouts
   - Ensure proper lock release in all code paths
   - Add retry logic for lock contention

5. **Integrate with Job Processing**
   - Connect PySCF runner output to storage system
   - Ensure result format matches ICD specification
   - Add error handling for storage failures
   - Include job status tracking and updates

6. **Add Result Validation**
   - Validate JSON structure on write and read
   - Ensure all required fields are present
   - Add data type and format validation
   - Handle corrupted file recovery

## 6. API/Schema Changes
**New Endpoint:**
```python
@app.get("/jobs/{job_id}/result", response_model=ResultData)
async def get_job_result(job_id: str) -> ResultData:
    # Implementation
```

**Result File Format (per ICD):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "system_id": "sha1-10",
  "method": "HF",
  "basis": "def2-SVP",
  "grid_level": 3,
  "conv_tol": 1e-9,
  "charge": 0,
  "spin": 0,
  "energy_hartree": -75.983742,
  "timings": {"wall_s": 0.42},
  "env": {
    "dryrun": false,
    "numpy": "1.26.4",
    "pyscf": "2.4.0"
  },
  "ts": 1724470000.0
}
```

**Storage Class Interface:**
```python
class ResultStorage:
    def store_result(self, job_id: str, result_data: dict) -> None:
        # Atomic write with file locking
        
    def retrieve_result(self, job_id: str) -> dict:
        # Safe read with error handling
        
    def result_exists(self, job_id: str) -> bool:
        # Check file existence
```

## 7. Test Plan
**Unit Tests:**
- Atomic write operations under normal conditions
- File locking acquisition and release
- JSON serialization and deserialization
- Error handling for invalid job_ids
- Concurrent access safety testing

**Integration Tests:**
- Complete store and retrieve cycle
- GET endpoint with valid and invalid job_ids
- File system error handling (permissions, disk full)
- Concurrent read/write operations

**E2E Tests:**
- Full calculation → storage → retrieval workflow
- Multiple clients accessing same results
- Error recovery and graceful degradation
- Performance under load

**Edge/Failure Cases:**
- Disk space exhaustion during write
- Corrupted JSON file handling
- Network mount failures (if applicable)
- Concurrent access race conditions
- Invalid or malicious job_id inputs

**Coverage Target:** >= 95% for storage and retrieval logic

## 8. Verification Checklist (DoD)
- [ ] Results stored as JSON in `results/{job_id}.json`
- [ ] `GET /jobs/{job_id}/result` endpoint implemented
- [ ] Atomic writes to prevent corruption
- [ ] Proper error handling for missing jobs
- [ ] JSON format matches ICD specification
- [ ] File locking for concurrent access
- [ ] Endpoint returns 404 for missing jobs
- [ ] Endpoint returns 500 for system errors
- [ ] All file operations are atomic and safe
- [ ] Concurrent access handled correctly

## 9. Risk, Mitigation, Rollback
**Top Risks:**
- File system performance bottlenecks
- Disk space exhaustion with many results
- File locking deadlocks or race conditions
- JSON corruption due to encoding issues
- Mount point failures in Docker environment

**Detection Signals:**
- Slow response times for result retrieval
- File write failures or partial writes
- Lock acquisition timeouts
- JSON parsing errors on read
- Missing or corrupted result files

**Mitigation:**
- Implement result file rotation or cleanup
- Monitor disk usage and set limits
- Use timeout-based lock acquisition
- Add comprehensive JSON validation
- Test file operations thoroughly in container

**Rollback Steps:**
- Disable result storage temporarily
- Use in-memory result caching
- Return to synchronous calculation mode
- Implement simple file backup system

## 10. Dependencies & Sequencing
**Upstream Dependencies:**
- Story 2.1: Job submission provides job_id tracking
- Story 2.2: PySCF runner provides result data
- Docker volume mounting for results directory

**Downstream Dependencies:**
- Story 2.5: Testing requires working storage system
- GUI client (Sprint 3) needs result retrieval
- Analysis pipeline (Sprint 3) reads result files

**Sequencing:**
- Requires S21 and S22 for integration points
- Should complete before S25 comprehensive testing
- Critical for end-to-end workflow validation

## 11. Telemetry & Observability
**Metrics:**
- Result storage success/failure rates
- File write and read operation timing
- Disk usage and growth patterns
- Concurrent access patterns and contention
- JSON file size distribution

**Logging:**
- Result storage and retrieval operations
- File locking events and timeouts
- Error conditions and recovery actions
- Disk space warnings and cleanup events

**Monitoring:**
- Storage operation performance trends
- Disk usage approaching limits
- File corruption detection and frequency
- Concurrent access bottlenecks

**Alerts:**
- Storage failure rate exceeding 1%
- Disk usage approaching 80% capacity
- File lock contention causing delays
- Repeated JSON corruption events

## 12. Docs & Change Management
**Files to Update:**
- Create: Result storage module in service app
- Update: `services/pyscf_service/app/main.py` (add endpoint)
- Create: Storage troubleshooting documentation
- Update: API documentation with result retrieval examples
- Update: Docker volume documentation

**Technical Documentation:**
- File storage format and organization
- Atomic write implementation details
- File locking mechanism and behavior
- Error handling and recovery procedures
- Performance characteristics and limitations

**Operational Documentation:**
- Disk space monitoring and management
- Result file cleanup and archival procedures
- Backup and recovery procedures
- Troubleshooting common file system issues

## 13. Work Items
**Branch Name:** `feature/result-storage-retrieval`
**PR Title:** "feat: implement atomic result storage and retrieval with file locking"
**Labels:** `feat`
**Reviewers:** Technical Lead, DevOps Engineer, QA Engineer
**CI Gates:** All tests pass, file operation safety validated, performance benchmarks met

## Follow-ups
OPEN-QUESTION: Should we implement result file compression to save disk space?
OPEN-QUESTION: Do we need automatic cleanup of old result files based on age or count?
OPEN-QUESTION: Should we add result file checksums for integrity verification?
OPEN-QUESTION: How should we handle network file system mounts vs local storage?
