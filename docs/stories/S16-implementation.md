---
StoryID: S16
Title: "Implement Basic Unit Tests"
Sprint: "Sprint 1"
Owner: "QA Engineer"
Status: "Planned"
---
# S16 — Implement Basic Unit Tests: Implementation Strategy

## 1. Objective
Create comprehensive unit test foundation with service and GUI core tests that run in CI with PYSCF_DRYRUN mode to ensure code reliability and enable continuous integration validation.

## 2. Scope & Non-Goals
**Scope:**
- Service tests in `tests/test_service.py`
- GUI core tests in `tests/test_gui_core.py`
- Health endpoint testing
- Schema validation testing
- PYSCF_DRYRUN mode testing setup
- Pytest configuration and fixtures

**Non-Goals:**
- Complete integration testing (Sprint 2)
- GUI visual testing or UI automation
- Performance testing setup
- Advanced test reporting and metrics

## 3. Requirements & Acceptance Criteria
- [ ] Service tests created in `tests/test_service.py`
- [ ] GUI core tests created in `tests/test_gui_core.py`
- [ ] Health endpoint test passes
- [ ] Schema validation tests pass
- [ ] Tests run with `PYSCF_DRYRUN=1` in CI

## 4. Architecture & Data Impact
**Test Components:**
- Pytest framework for test execution
- FastAPI TestClient for API testing
- Mock objects for PySCF components
- Test fixtures for data setup
- Separate test configuration

**Test Isolation:**
- PYSCF_DRYRUN environment variable
- Mock external dependencies
- Temporary file handling for test results
- Clean test state between runs

## 5. Implementation Plan (Step-by-Step)
1. **Set Up Test Framework**
   - Create `tests/` directory with `__init__.py`
   - Configure `pytest.ini` or `pyproject.toml` test settings
   - Set up test fixtures and utilities
   - Configure test discovery patterns

2. **Create Service Tests**
   - Initialize `tests/test_service.py`
   - Import FastAPI TestClient and required modules
   - Create test fixtures for FastAPI app
   - Set up PYSCF_DRYRUN environment handling

3. **Implement Health Endpoint Tests**
   - Test GET /health returns 200 status
   - Validate response JSON structure
   - Check required fields (ok, timestamp, etc.)
   - Test health endpoint availability

4. **Create Schema Validation Tests**
   - Test JobRequest schema with valid data
   - Test validation failure cases
   - Test field range validations
   - Test enum validation for method field
   - Test required field enforcement

5. **Create GUI Core Tests**
   - Initialize `tests/test_gui_core.py`
   - Test schema validation in GUI context
   - Test client utility functions
   - Mock PySide6 components for testing

6. **Configure Test Environment**
   - Set up environment variable handling
   - Configure test data fixtures
   - Add test utilities and helpers
   - Set up cleanup procedures

7. **Integration with CI**
   - Ensure tests work with PYSCF_DRYRUN=1
   - Validate test execution time under budget
   - Configure test reporting and output

## 6. API/Schema Changes
No API changes. Tests validate existing schemas and endpoints.

**Test Configuration:**
```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
env = ["PYSCF_DRYRUN=1"]
```

## 7. Test Plan
**Unit Test Coverage:**
- Health endpoint functionality
- Schema validation (positive and negative cases)
- Environment variable handling
- Basic FastAPI application setup

**Test Categories:**
```python
# Service Tests
def test_health_endpoint_returns_ok()
def test_health_endpoint_response_format()
def test_job_request_schema_validation()
def test_job_request_invalid_method()
def test_job_request_missing_required_fields()

# GUI Core Tests
def test_schema_validation_in_gui_context()
def test_client_utility_functions()
def test_form_validation_helpers()
```

**Edge/Failure Cases:**
- Invalid schema data handling
- Missing environment variables
- Network connection failures (mocked)
- Malformed API responses

**Coverage Target:** >= 90% for testable components

## 8. Verification Checklist (DoD)
- [ ] Service tests created in `tests/test_service.py`
- [ ] GUI core tests created in `tests/test_gui_core.py`
- [ ] Health endpoint test passes
- [ ] Schema validation tests pass
- [ ] Tests run with `PYSCF_DRYRUN=1` in CI
- [ ] All tests pass locally and in CI
- [ ] Test coverage meets >= 90% target
- [ ] Test execution time under 3 minutes total
- [ ] No test dependencies on external services

## 9. Risk, Mitigation, Rollback
**Top Risks:**
- PYSCF_DRYRUN mode not working as expected
- Test dependencies conflict with main dependencies
- Slow test execution exceeding CI budget
- Mock objects not accurately representing real behavior

**Detection Signals:**
- Tests failing in CI but passing locally
- Test execution timeouts
- Mock vs. real implementation behavioral differences
- Dependency conflicts during test runs

**Mitigation:**
- Test PYSCF_DRYRUN mode thoroughly in development
- Use separate test requirements file if needed
- Optimize test execution and use parallel testing
- Keep mocks simple and focused

**Rollback Steps:**
- Disable problematic tests temporarily
- Use simpler mock implementations
- Remove complex test fixtures
- Fall back to manual testing procedures

## 10. Dependencies & Sequencing
**Upstream Dependencies:**
- Repository structure (S12) for test directory
- FastAPI service foundation (S14) for endpoint testing
- Data schemas (S15) for validation testing
- Basic service implementation for testing targets

**Downstream Dependencies:**
- CI/CD pipeline (S13) requires working tests
- Sprint 2 development depends on test foundation
- Code quality gates depend on test coverage

**Sequencing:**
- Requires S14 and S15 completion for meaningful tests
- Should complete before S13 CI integration
- Enables quality gates for all future development

## 11. Telemetry & Observability
**Test Metrics:**
- Test execution time per category
- Test coverage percentage
- Test failure rates and patterns
- CI test execution history

**Monitoring:**
- Test suite execution time trends
- Test reliability and flakiness
- Coverage regression detection
- CI pipeline test feedback

**Reporting:**
- Test results in CI pipeline
- Coverage reports with line-by-line breakdown
- Test performance benchmarks
- Failure analysis and categorization

## 12. Docs & Change Management
**Files to Update:**
- Create: `tests/test_service.py`
- Create: `tests/test_gui_core.py`
- Create: `tests/__init__.py`
- Create: `pytest.ini` or update `pyproject.toml`
- Update: `README.md` (add testing instructions)
- Update: Root requirements file with test dependencies

**Documentation:**
- Testing setup and execution instructions
- Test writing guidelines and standards
- Mock usage patterns and examples
- CI integration documentation

## 13. Work Items
**Branch Name:** `feature/basic-unit-tests`
**PR Title:** "test: implement basic unit tests for service and GUI core with CI integration"
**Labels:** `test`
**Reviewers:** Technical Lead, Backend Developer, DevOps Engineer
**CI Gates:** All tests must pass, coverage threshold met

## Follow-ups
OPEN-QUESTION: Should we set up test database fixtures or rely on mocking for all data?
OPEN-QUESTION: Do we need separate test configurations for different environments (local, CI, staging)?
OPEN-QUESTION: Should we implement visual regression testing for GUI components in this sprint?
