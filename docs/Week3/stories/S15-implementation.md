---
StoryID: S15
Title: "Define Data Schemas"
Sprint: "Sprint 1"
Owner: "Backend Developer"
Status: "Planned"
---
# S15 — Define Data Schemas: Implementation Strategy

## 1. Objective
Create comprehensive Pydantic data schemas for service and client APIs to ensure clear contracts, data validation, and type safety across the entire application stack.

## 2. Scope & Non-Goals
**Scope:**
- Pydantic schemas in `services/pyscf_service/app/schemas.py`
- Job request and response schema definitions
- Result data schema per ICD specification
- Client schemas in `apps/pyscf_gui/core/schema.py`
- Field validation rules per specification
- Schema documentation and examples

**Non-Goals:**
- Database schema definitions (no DB required)
- Complex schema versioning system
- Advanced validation logic beyond field constraints
- Schema migration tools

## 3. Requirements & Acceptance Criteria
- [ ] Pydantic schemas created in `services/pyscf_service/app/schemas.py`
- [ ] Job request schema validates all required fields
- [ ] Job response schema includes all specified fields
- [ ] Client schema created in `apps/pyscf_gui/core/schema.py`
- [ ] Validation rules implemented per ICD specification

## 4. Architecture & Data Impact
**Schema Components:**
- `JobRequest`: Input validation for computational jobs
- `JobResponse`: Standard response format with job_id and status
- `ResultData`: Complete calculation result format
- Client schemas for GUI application use

**Validation Rules (Per ICD):**
- `molecule_xyz`: Required string (XYZ format)
- `method`: Enum ["HF", "B3LYP", "MP2"]
- `basis`: Required string (e.g., "def2-SVP")
- `grid_level`: Integer [0..9]
- `conv_tol`: Float [1e-12..1e-2]
- `charge`: Integer
- `spin`: Integer >= 0

## 5. Implementation Plan (Step-by-Step)
1. **Create Service Schema Foundation**
   - Create `services/pyscf_service/app/schemas.py`
   - Import Pydantic BaseModel, Field, validator
   - Set up common validation functions

2. **Define JobRequest Schema**
   - Required fields: molecule_xyz, method, basis
   - Optional fields: grid_level, conv_tol, charge, spin
   - Method enum validation: HF, B3LYP, MP2
   - Range validators for numeric fields
   - XYZ format basic validation

3. **Define JobResponse Schema**
   - job_id: UUID string
   - status: Enum ["done", "queued", "running"]
   - Optional message field for errors
   - Timestamp field

4. **Define ResultData Schema**
   - All required fields per ICD specification:
     - job_id, system_id, method, basis
     - grid_level, conv_tol, charge, spin
     - energy_hartree, timings, env, ts
   - Proper field types and constraints
   - Environment metadata structure

5. **Create Client Schemas**
   - Create `apps/pyscf_gui/core/schema.py`
   - Mirror service schemas for client use
   - Add GUI-specific validation helpers
   - Form validation utilities

6. **Add Schema Documentation**
   - Docstrings for all schema classes
   - Field descriptions and examples
   - Validation error message customization
   - Usage examples in docstrings

## 6. API/Schema Changes
**New Schemas:**

```python
# JobRequest Schema
{
  "molecule_xyz": "3\n\nO 0 0 0\nH 0 0.757 0.586\nH 0 -0.757 0.586\n",
  "method": "HF",
  "basis": "def2-SVP",
  "grid_level": 3,
  "conv_tol": 1e-9,
  "spin": 0,
  "charge": 0
}

# JobResponse Schema
{
  "job_id": "uuid-string",
  "status": "done|queued|running",
  "message": "optional error message"
}

# ResultData Schema
{
  "job_id": "uuid",
  "system_id": "sha1-10",
  "method": "HF",
  "basis": "def2-SVP",
  "grid_level": 3,
  "conv_tol": 1e-9,
  "charge": 0,
  "spin": 0,
  "energy_hartree": -75.983742,
  "timings": {"wall_s": 0.42},
  "env": {"dryrun": false, "numpy": "1.26.4", "pyscf": "2.4.0"},
  "ts": 1724470000.0
}
```

## 7. Test Plan
**Unit Tests:**
- Schema validation with valid data
- Field validation rules enforcement
- Enum validation for method and status
- Range validation for numeric fields
- Required field validation

**Integration Tests:**
- Schema serialization/deserialization
- FastAPI integration with Pydantic
- Error message format validation
- Cross-schema compatibility

**E2E Tests:**
- Complete request/response cycle validation
- GUI form to schema conversion
- Schema to JSON API payload conversion

**Edge/Failure Cases:**
- Invalid XYZ format handling
- Out-of-range numeric values
- Missing required fields
- Invalid enum values
- Malformed JSON input

**Coverage Target:** >= 95% for schema validation logic

## 8. Verification Checklist (DoD)
- [ ] Pydantic schemas created in `services/pyscf_service/app/schemas.py`
- [ ] Job request schema validates all required fields
- [ ] Job response schema includes all specified fields
- [ ] Client schema created in `apps/pyscf_gui/core/schema.py`
- [ ] Validation rules implemented per ICD specification
- [ ] All schema fields have proper types and constraints
- [ ] Enum validation works for method and status fields
- [ ] Range validation enforced for numeric fields
- [ ] Schema documentation complete with examples

## 9. Risk, Mitigation, Rollback
**Top Risks:**
- Validation rules too restrictive for valid scientific input
- Performance impact of complex validation
- Schema compatibility issues between service and client
- XYZ format validation complexity

**Detection Signals:**
- Valid scientific inputs being rejected
- Slow validation performance
- Schema mismatch errors between components
- Complex XYZ parsing failures

**Mitigation:**
- Start with permissive validation, tighten incrementally
- Benchmark validation performance early
- Share common schema definitions between components
- Use simple XYZ format validation initially

**Rollback Steps:**
- Revert to simple dictionary-based data structures
- Remove complex validation temporarily
- Use basic type hints without Pydantic
- Implement manual validation where needed

## 10. Dependencies & Sequencing
**Upstream Dependencies:**
- Repository structure (S12) for file placement
- Requirements files updated with Pydantic

**Downstream Dependencies:**
- FastAPI service implementation (S14, Sprint 2)
- GUI client implementation (Sprint 3)
- Testing framework (S16) needs schemas for validation

**Sequencing:**
- Can develop in parallel with S14 (service foundation)
- Should complete before Sprint 2 API implementation
- Required for meaningful S16 (testing) implementation

## 11. Telemetry & Observability
**Metrics:**
- Schema validation success/failure rates
- Validation performance timing
- Common validation error patterns
- Schema usage statistics

**Logging:**
- Validation errors with sanitized input data
- Schema version and compatibility info
- Performance metrics for complex validations

**Monitoring:**
- Validation error rate trends
- Schema compatibility issues
- Performance degradation alerts

## 12. Docs & Change Management
**Files to Update:**
- Create: `services/pyscf_service/app/schemas.py`
- Create: `apps/pyscf_gui/core/schema.py`
- Update: `services/pyscf_service/requirements.txt` (add pydantic)
- Update: `apps/pyscf_gui/requirements.txt` (add pydantic)
- Update: API documentation with schema examples

**Documentation:**
- Schema field documentation and examples
- Validation rule explanations
- Error message reference guide
- Integration examples for developers

## 13. Work Items
**Branch Name:** `feature/data-schemas`
**PR Title:** "feat: define Pydantic data schemas with validation per ICD specification"
**Labels:** `feat`
**Reviewers:** Technical Lead, Frontend Developer
**CI Gates:** Schema validation tests, type checking, documentation generation

## Follow-ups
OPEN-QUESTION: Should we implement custom XYZ format validation or rely on PySCF parsing?
OPEN-QUESTION: Do we need schema versioning for future API evolution?
OPEN-QUESTION: Should validation error messages be user-friendly for GUI display?
