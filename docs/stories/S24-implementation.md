---
StoryID: S24
Title: "Add Service Configuration Management"
Sprint: "Sprint 2"
Owner: "DevOps Engineer"
Status: "Planned"
---
# S24 — Add Service Configuration Management: Implementation Strategy

## 1. Objective
Implement comprehensive configuration management system with environment variables, validation, and proper defaults to enable flexible service deployment across different environments while maintaining reproducibility.

## 2. Scope & Non-Goals
**Scope:**
- Environment variable configuration system
- Configuration validation on startup
- Default value handling and documentation
- OMP_NUM_THREADS=1 enforcement
- PYSCF_DRYRUN mode configuration
- Service port and results directory configuration
- Configuration logging and diagnostics

**Non-Goals:**
- Complex configuration file formats (YAML, TOML)
- Runtime configuration changes without restart
- Configuration encryption or secrets management
- Advanced configuration templating systems

## 3. Requirements & Acceptance Criteria
- [ ] Environment variables for key settings
- [ ] `OMP_NUM_THREADS=1` enforced
- [ ] `PYSCF_DRYRUN` mode configurable
- [ ] Service port configurable
- [ ] Results directory configurable
- [ ] Configuration validation on startup

## 4. Architecture & Data Impact
**Configuration Components:**
- Environment variable parsing and validation
- Configuration dataclass or Pydantic model
- Startup validation and error reporting
- Default value specification and documentation

**Key Configuration Variables:**
- `OMP_NUM_THREADS`: Parallelization control (default: 1)
- `PYSCF_DRYRUN`: Testing mode flag (default: false)
- `SERVICE_PORT`: HTTP service port (default: 8000)
- `RESULTS_DIR`: Result storage directory (default: /app/results)
- `LOG_LEVEL`: Logging verbosity (default: INFO)

**Validation Rules:**
- Port numbers: 1024-65535 range
- Directory paths: must be writable
- Boolean flags: true/false/1/0 parsing
- Numeric values: range and type validation

## 5. Implementation Plan (Step-by-Step)
1. **Create Configuration Module**
   - Create `services/pyscf_service/app/config.py`
   - Define configuration dataclass with typed fields
   - Add environment variable parsing logic
   - Include default values and validation rules

2. **Implement Environment Variable Parsing**
   - Use os.environ for variable access
   - Add type conversion utilities (str→int, str→bool)
   - Handle missing variables with defaults
   - Validate parsed values against constraints

3. **Add Configuration Validation**
   - Port number range validation
   - Directory existence and write permission checks
   - Boolean flag parsing with multiple formats
   - Numeric range validation where applicable

4. **Integrate with Application Startup**
   - Load configuration during FastAPI app initialization
   - Validate configuration before starting server
   - Log configuration values (sanitized) on startup
   - Fail fast with clear error messages for invalid config

5. **Implement OMP_NUM_THREADS Enforcement**
   - Set environment variable in application code
   - Validate the setting is properly applied
   - Log warning if threads setting is not respected
   - Document impact on calculation reproducibility

6. **Add Configuration Documentation**
   - Document all environment variables and their purposes
   - Include examples for different deployment scenarios
   - Add troubleshooting guide for common configuration issues
   - Create configuration template files

## 6. API/Schema Changes
**Configuration Structure:**
```python
@dataclass
class ServiceConfig:
    # Core service settings
    service_port: int = 8000
    results_dir: str = "/app/results"
    log_level: str = "INFO"
    
    # PySCF calculation settings
    omp_num_threads: int = 1
    pyscf_dryrun: bool = False
    
    # Optional settings
    max_calculation_time: int = 300
    max_memory_mb: int = 1024
```

**Environment Variables:**
```bash
# Required/Important
OMP_NUM_THREADS=1
PYSCF_DRYRUN=false
SERVICE_PORT=8000
RESULTS_DIR=/app/results

# Optional
LOG_LEVEL=INFO
MAX_CALCULATION_TIME=300
MAX_MEMORY_MB=1024
```

**Configuration Validation:**
```python
def validate_config(config: ServiceConfig) -> None:
    # Port range validation
    if not (1024 <= config.service_port <= 65535):
        raise ValueError("SERVICE_PORT must be between 1024 and 65535")
    
    # Directory validation
    if not os.path.exists(config.results_dir):
        raise ValueError(f"RESULTS_DIR {config.results_dir} does not exist")
```

## 7. Test Plan
**Unit Tests:**
- Environment variable parsing with various input types
- Default value application when variables are missing
- Configuration validation with valid and invalid inputs
- Type conversion edge cases (bool parsing, int ranges)
- Error message clarity and usefulness

**Integration Tests:**
- Complete application startup with various configurations
- OMP_NUM_THREADS environment variable enforcement
- Results directory creation and permission validation
- Configuration logging and diagnostics

**E2E Tests:**
- Docker container startup with custom environment variables
- Service behavior changes with different configurations
- Configuration persistence across container restarts

**Edge/Failure Cases:**
- Invalid port numbers (negative, too large, non-numeric)
- Non-existent or non-writable directories
- Malformed boolean values
- Missing required environment variables
- Configuration conflicts or contradictions

**Coverage Target:** >= 95% for configuration parsing and validation

## 8. Verification Checklist (DoD)
- [ ] Environment variables for key settings
- [ ] `OMP_NUM_THREADS=1` enforced
- [ ] `PYSCF_DRYRUN` mode configurable
- [ ] Service port configurable
- [ ] Results directory configurable
- [ ] Configuration validation on startup
- [ ] Clear error messages for invalid configuration
- [ ] All environment variables documented
- [ ] Default values work correctly
- [ ] Configuration logging shows sanitized values

## 9. Risk, Mitigation, Rollback
**Top Risks:**
- Environment variable conflicts between different deployment methods
- Configuration validation too strict preventing legitimate use cases
- OMP_NUM_THREADS not being respected by underlying libraries
- Platform-specific environment variable behavior differences

**Detection Signals:**
- Application startup failures due to configuration
- Unexpected behavior with different environment settings
- Performance differences suggesting threading issues
- Configuration validation blocking valid deployments

**Mitigation:**
- Test configuration on all target platforms
- Use permissive validation with warnings for edge cases
- Validate OMP_NUM_THREADS effectiveness with test calculations
- Provide clear documentation and examples

**Rollback Steps:**
- Use hardcoded configuration values temporarily
- Disable strict validation mode
- Fall back to Docker Compose environment defaults
- Provide configuration override mechanisms

## 10. Dependencies & Sequencing
**Upstream Dependencies:**
- Sprint 1: Service foundation and Docker setup completed
- Basic application structure and startup sequence

**Downstream Dependencies:**
- Story 2.2: PySCF runner needs OMP_NUM_THREADS setting
- Story 2.3: Result storage needs results directory configuration
- Story 2.5: Testing needs PYSCF_DRYRUN configuration

**Sequencing:**
- Can develop early in Sprint 2 in parallel with other stories
- Should complete before S22 PySCF runner for threading control
- Required for proper S25 testing with dryrun mode

## 11. Telemetry & Observability
**Metrics:**
- Configuration loading success/failure rates
- Environment variable usage patterns
- Startup time impact of configuration validation
- Configuration error frequency by variable type

**Logging:**
- Configuration values loaded at startup (sanitized)
- Environment variable validation results
- Configuration errors and warnings
- OMP_NUM_THREADS enforcement status

**Monitoring:**
- Application startup success rates
- Configuration-related error patterns
- Performance impact of different settings
- Threading behavior validation

**Alerts:**
- Repeated configuration validation failures
- OMP_NUM_THREADS not being respected
- Invalid configuration causing startup failures
- Performance degradation with configuration changes

## 12. Docs & Change Management
**Files to Update:**
- Create: `services/pyscf_service/app/config.py`
- Update: `services/pyscf_service/app/main.py` (integrate configuration)
- Update: `docker-compose.yml` (environment variable examples)
- Create: Configuration documentation and examples
- Update: `README.md` with configuration instructions

**Documentation:**
- Complete environment variable reference
- Configuration examples for different scenarios
- Troubleshooting guide for common issues
- Performance tuning recommendations
- Security considerations for configuration

**Change Communication:**
- Environment variable requirements for deployment
- Configuration best practices for different environments
- Migration guide for existing deployments

## 13. Work Items
**Branch Name:** `feature/service-configuration-management`
**PR Title:** "feat: add comprehensive service configuration with environment variables and validation"
**Labels:** `feat`, `infra`
**Reviewers:** Technical Lead, Backend Developer, QA Engineer
**CI Gates:** Configuration validation tests pass, documentation complete, Docker integration tested

## Follow-ups
OPEN-QUESTION: Should we support configuration file overrides in addition to environment variables?
OPEN-QUESTION: Do we need runtime configuration validation or health checks for configuration drift?
OPEN-QUESTION: Should we implement configuration hot-reloading for development environments?
OPEN-QUESTION: How should we handle sensitive configuration values like API keys in future versions?
