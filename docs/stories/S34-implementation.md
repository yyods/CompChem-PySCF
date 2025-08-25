---
StoryID: S34
Title: "Implement Service Client Integration"
Sprint: "Sprint 3"
Owner: "Backend Developer"
Status: "Planned"
---
# S34 — Implement Service Client Integration: Implementation Strategy

## 1. Objective
Create robust HTTP client for GUI-to-service communication with job submission, result retrieval, error handling, and progress indication to enable complete workflow integration.

## 2. Scope & Non-Goals
**Scope:**
- HTTP client implementation in `apps/pyscf_gui/core/client.py`
- `submit_job()` method with comprehensive error handling
- `get_result()` method with proper JSON parsing
- Service connectivity validation and health checking
- Timeout and retry mechanisms for reliability
- Progress indication during network requests

**Non-Goals:**
- Advanced authentication or security features
- Complex retry strategies or circuit breakers
- Real-time result streaming or websockets
- Caching or offline functionality

## 3. Requirements & Acceptance Criteria
- [ ] HTTP client in `apps/pyscf_gui/core/client.py`
- [ ] `submit_job()` method with error handling
- [ ] `get_result()` method with proper parsing
- [ ] Service connectivity validation
- [ ] Timeout and retry mechanisms
- [ ] Progress indication during requests

## 4. Architecture & Data Impact
**Client Components:**
- HTTP client using requests library
- Service endpoint configuration
- Request/response data transformation
- Error handling and exception mapping
- Progress tracking and user feedback

**Service Integration:**
```
GUI Client ←→ HTTP Client ←→ FastAPI Service
    │              │              │
Input Form    submit_job()     POST /jobs
Results       get_result()     GET /jobs/{id}/result
Health UI     check_health()   GET /health
```

**Data Flow:**
1. Form data → Client validation → HTTP request → Service
2. Service response → Client parsing → GUI display
3. Errors → Client handling → User feedback

## 5. Implementation Plan (Step-by-Step)
1. **Create HTTP Client Class**
   - Initialize requests session with proper configuration
   - Set up base URL and service endpoint configuration
   - Add request/response logging infrastructure
   - Configure timeout and connection settings

2. **Implement Job Submission Method**
   - Create `submit_job()` method accepting form data
   - Transform GUI data to service API format
   - Handle HTTP request/response cycle
   - Parse job_id from response and return to GUI

3. **Implement Result Retrieval Method**
   - Create `get_result()` method with job_id parameter
   - Handle HTTP GET request to results endpoint
   - Parse JSON response and validate structure
   - Transform service data to GUI display format

4. **Add Service Health Checking**
   - Implement `check_health()` method for connectivity
   - Validate service availability before operations
   - Provide clear feedback for service status
   - Handle connection failures gracefully

5. **Implement Error Handling**
   - Map HTTP status codes to user-friendly messages
   - Handle network connectivity issues
   - Parse service error responses and extract messages
   - Create exception hierarchy for different error types

6. **Add Timeout and Retry Logic**
   - Configure appropriate timeouts for different operations
   - Implement simple retry logic for transient failures
   - Add progress indication during long operations
   - Handle user cancellation of requests

## 6. API/Schema Changes
**Client Interface:**
```python
class PySCFServiceClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    async def submit_job(self, job_data: JobFormData) -> str:
        # Submit calculation job, return job_id
        
    async def get_result(self, job_id: str) -> Dict[str, Any]:
        # Retrieve calculation result
        
    async def check_health(self) -> bool:
        # Check service health
        
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        # Common response handling
```

**Error Handling:**
```python
class ServiceClientError(Exception):
    """Base client exception"""
    
class ServiceUnavailableError(ServiceClientError):
    """Service connectivity issues"""
    
class ValidationError(ServiceClientError):
    """Input validation failures"""
    
class CalculationError(ServiceClientError):
    """Calculation execution failures"""
```

**Data Transformation:**
```python
# GUI Form Data → Service Request
{
    "molecule_xyz": form.xyz_text,
    "method": form.method,
    "basis": form.basis,
    "grid_level": form.grid_level,
    "conv_tol": form.conv_tol,
    "charge": form.charge,
    "spin": form.spin
}

# Service Response → GUI Display
{
    "job_id": response["job_id"],
    "status": response["status"],
    "energy_hartree": result["energy_hartree"],
    "method": result["method"],
    "basis": result["basis"],
    ...
}
```

## 7. Test Plan
**Unit Tests:**
- HTTP client initialization and configuration
- Job submission data transformation
- Result retrieval and parsing
- Error handling for various HTTP status codes
- Timeout and retry logic

**Integration Tests:**
- Complete job submission workflow with mock service
- Result retrieval with valid and invalid job IDs
- Service health checking under different conditions
- Error scenarios with appropriate user feedback

**E2E Tests:**
- Full GUI → Client → Service → GUI workflow
- Network failure scenarios and recovery
- Service unavailability handling
- Long-running calculation simulation

**Edge/Failure Cases:**
- Network connectivity interruptions
- Service timeouts and slow responses
- Malformed service responses
- Invalid job IDs and missing results
- Concurrent request handling

**Coverage Target:** >= 95% for client logic and error handling

## 8. Verification Checklist (DoD)
- [ ] HTTP client in `apps/pyscf_gui/core/client.py`
- [ ] `submit_job()` method with error handling
- [ ] `get_result()` method with proper parsing
- [ ] Service connectivity validation
- [ ] Timeout and retry mechanisms
- [ ] Progress indication during requests
- [ ] All HTTP status codes handled appropriately
- [ ] Error messages provide clear user guidance
- [ ] Client handles service unavailability gracefully
- [ ] Request/response logging for debugging

## 9. Risk, Mitigation, Rollback
**Top Risks:**
- Service unavailability breaking GUI functionality
- Network timeout issues affecting user experience
- HTTP request/response format mismatches
- Performance issues with synchronous requests

**Detection Signals:**
- Frequent connection timeouts
- HTTP 500 errors from service
- JSON parsing failures
- User reports of unresponsive interface

**Mitigation:**
- Implement comprehensive service health checking
- Use appropriate timeout values and user feedback
- Add request/response validation and logging
- Consider asynchronous request handling for UI responsiveness

**Rollback Steps:**
- Implement mock service client for offline testing
- Use cached responses for development
- Provide manual calculation result input
- Fall back to command-line service interaction

## 10. Dependencies & Sequencing
**Upstream Dependencies:**
- Sprint 2: Service API endpoints fully implemented
- Story 3.2: Input form provides data structure
- Story 3.1: Application framework for integration

**Downstream Dependencies:**
- Story 3.3: Results display needs client data
- Story 3.5: Error handling builds on client errors
- Complete workflow requires service integration

**Sequencing:**
- Requires Sprint 2 service completion
- Can develop with input form (S32) in parallel
- Should complete before results display integration

## 11. Telemetry & Observability
**Metrics:**
- Request/response times by endpoint
- Success/failure rates for service calls
- Error frequency by type and status code
- Network timeout and retry statistics

**Logging:**
- HTTP request/response details (sanitized)
- Service health check results
- Error conditions and exception handling
- User workflow completion patterns

**Monitoring:**
- Service connectivity and availability
- Client performance and responsiveness
- Error rate trends and patterns
- Network latency and timeout frequency

**Alerts:**
- High service error rates
- Frequent connectivity failures
- Request timeout thresholds exceeded
- Service unavailability detection

## 12. Docs & Change Management
**Files to Update:**
- Create: `apps/pyscf_gui/core/client.py`
- Update: GUI components to use client
- Create: Client configuration documentation
- Create: Error handling guide for users
- Update: Integration testing procedures

**Technical Documentation:**
- HTTP client architecture and design
- Service integration patterns and best practices
- Error handling strategies and implementation
- Request/response format specifications

**User Documentation:**
- Network requirements and connectivity
- Common error messages and solutions
- Service configuration and setup
- Troubleshooting connection issues

## 13. Work Items
**Branch Name:** `feature/service-client-integration`
**PR Title:** "feat: implement HTTP service client with error handling and progress indication"
**Labels:** `feat`
**Reviewers:** Technical Lead, Backend Developer, QA Engineer
**CI Gates:** Client tests pass, service integration validated, error handling comprehensive

## Follow-ups
OPEN-QUESTION: Should we implement request caching to avoid redundant service calls?
OPEN-QUESTION: Do we need asynchronous request handling to keep GUI responsive?
OPEN-QUESTION: Should we add request queuing for multiple simultaneous calculations?
OPEN-QUESTION: How should we handle service version compatibility and API changes?
