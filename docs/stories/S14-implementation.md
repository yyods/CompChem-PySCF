---
StoryID: S14
Title: "Create FastAPI Service Foundation"
Sprint: "Sprint 1"
Owner: "Backend Developer"
Status: "Planned"
---
# S14 — Create FastAPI Service Foundation: Implementation Strategy

## 1. Objective
Create containerized FastAPI service foundation with health endpoint, Docker configuration, and environment setup to enable reliable computational job processing infrastructure.

## 2. Scope & Non-Goals
**Scope:**
- FastAPI application structure in `services/pyscf_service/app/main.py`
- Dockerfile with PySCF dependencies
- Docker Compose configuration with port mapping
- Health check endpoint implementation
- Environment variable configuration
- Results directory bind mount setup

**Non-Goals:**
- Complete job processing endpoints (Sprint 2)
- PySCF calculation implementation
- Advanced error handling and logging
- Production-grade security configuration

## 3. Requirements & Acceptance Criteria
- [ ] FastAPI application created in `services/pyscf_service/app/main.py`
- [ ] Dockerfile configured with PySCF dependencies
- [ ] Docker Compose file created with proper port mapping
- [ ] Service responds to `/health` endpoint
- [ ] Environment variables configured (`OMP_NUM_THREADS=1`)

## 4. Architecture & Data Impact
**Components:**
- FastAPI web framework
- Docker container with Python 3.10+
- PySCF quantum chemistry library
- Results directory mounted from host

**API Endpoints:**
- `GET /health` → `{"ok": true}`

**Environment Variables:**
- `OMP_NUM_THREADS=1` (for reproducible calculations)
- `PYSCF_DRYRUN` (for testing mode)

**Docker Network:**
- Service exposed on port 8000
- Results volume mounted to host `results/` directory

## 5. Implementation Plan (Step-by-Step)
1. **Create FastAPI Application Structure**
   - Initialize `services/pyscf_service/app/main.py`
   - Import FastAPI and create application instance
   - Configure CORS and basic middleware
   - Add application metadata (title, version, description)

2. **Implement Health Endpoint**
   - Create `GET /health` endpoint
   - Return JSON response: `{"ok": true}`
   - Add basic service status information
   - Include timestamp and version info

3. **Create Dockerfile**
   - Base image: `python:3.10-slim`
   - Install system dependencies for PySCF
   - Copy and install Python requirements
   - Set working directory and expose port 8000
   - Configure environment variables
   - Set up non-root user for security

4. **Configure Requirements**
   - Update `services/pyscf_service/requirements.txt`
   - Add: fastapi, uvicorn, pydantic, pyscf, numpy
   - Pin versions for reproducibility
   - Include development dependencies (pytest, httpx)

5. **Create Docker Compose Configuration**
   - Define pyscf_service in `docker-compose.yml`
   - Configure port mapping (8000:8000)
   - Set up volume mount for results directory
   - Configure environment variables
   - Add development-friendly settings (auto-reload)

6. **Test Service Startup**
   - Build Docker image successfully
   - Start service via Docker Compose
   - Verify health endpoint accessibility
   - Confirm results directory binding

## 6. API/Schema Changes
**New Endpoints:**
```
GET /health
Response: 200 OK
Content-Type: application/json
{
  "ok": true,
  "timestamp": "2025-08-25T10:00:00Z",
  "version": "1.0.0",
  "service": "pyscf_service"
}
```

**Docker Configuration:**
- Service accessible at `http://localhost:8000`
- Results mounted to `./results:/app/results`
- Environment: `OMP_NUM_THREADS=1`

## 7. Test Plan
**Unit Tests:**
- FastAPI application initialization
- Health endpoint response validation
- Environment variable loading

**Integration Tests:**
- Docker container build and startup
- Health endpoint via HTTP request
- Results directory mounting verification

**E2E Tests:**
- Complete Docker Compose startup
- Service accessibility from host
- Container shutdown and cleanup

**Edge/Failure Cases:**
- Port conflict scenarios
- Missing results directory
- Invalid environment variables
- Container resource limitations

**Coverage Target:** >= 90% for FastAPI application code

## 8. Verification Checklist (DoD)
- [ ] FastAPI application created in `services/pyscf_service/app/main.py`
- [ ] Dockerfile configured with PySCF dependencies
- [ ] Docker Compose file created with proper port mapping
- [ ] Service responds to `/health` endpoint
- [ ] Environment variables configured (`OMP_NUM_THREADS=1`)
- [ ] Docker container builds without errors
- [ ] Service starts and stops cleanly
- [ ] Results directory bind mount functional
- [ ] Health endpoint returns expected JSON format

## 9. Risk, Mitigation, Rollback
**Top Risks:**
- PySCF dependency installation complexity
- Docker build timeouts or failures
- Port conflicts with existing services
- Cross-platform Docker compatibility issues

**Detection Signals:**
- Docker build failures
- Service startup errors
- Health endpoint timeouts
- Container resource exhaustion

**Mitigation:**
- Use proven PySCF Docker installation methods
- Implement build caching for dependencies
- Configure dynamic port assignment option
- Test on all target platforms early

**Rollback Steps:**
- Stop and remove Docker containers
- Revert Dockerfile and compose changes
- Use mock service for development
- Return to local Python development setup

## 10. Dependencies & Sequencing
**Upstream Dependencies:**
- Repository structure (S12) completed
- Requirements files structure in place
- Docker installed on development machines

**Downstream Dependencies:**
- Job processing endpoints (Sprint 2)
- GUI client integration (Sprint 3)
- CI/CD testing integration (S13)

**Sequencing:**
- Requires S12 completion for file structure
- Can develop in parallel with S15 (schemas)
- Should complete before S16 (testing) for proper test targets

## 11. Telemetry & Observability
**Metrics:**
- Service startup time
- Health endpoint response time
- Container resource usage (CPU, memory)
- Build time and success rate

**Logging:**
- Application startup and shutdown events
- Health check request logging
- Environment variable validation
- Error conditions and exceptions

**Monitoring:**
- Docker container health status
- Service availability monitoring
- Resource usage tracking
- Build pipeline success rates

## 12. Docs & Change Management
**Files to Update:**
- Create: `services/pyscf_service/app/main.py`
- Create: `services/pyscf_service/Dockerfile`
- Create: `docker-compose.yml`
- Update: `services/pyscf_service/requirements.txt`
- Update: `README.md` (add Docker setup instructions)

**Documentation:**
- Docker setup and usage instructions
- Service API documentation (health endpoint)
- Troubleshooting guide for common Docker issues
- Development workflow with containers

## 13. Work Items
**Branch Name:** `feature/fastapi-service-foundation`
**PR Title:** "feat: create FastAPI service foundation with Docker and health endpoint"
**Labels:** `feat`, `infra`
**Reviewers:** Technical Lead, DevOps Engineer
**CI Gates:** Docker build test, health endpoint test, container security scan

## Follow-ups
OPEN-QUESTION: Should we implement graceful shutdown handling for the FastAPI service?
OPEN-QUESTION: Do we need health check endpoints with more detailed system information (disk space, memory)?
OPEN-QUESTION: Should the Dockerfile use multi-stage builds to reduce image size?
