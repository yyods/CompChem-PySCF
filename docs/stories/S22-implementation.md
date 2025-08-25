---
StoryID: S22
Title: "Implement PySCF Runner"
Sprint: "Sprint 2"
Owner: "Backend Developer"
Status: "Planned"
---
# S22 — Implement PySCF Runner: Implementation Strategy

## 1. Objective
Create comprehensive PySCF calculation runner that supports HF, B3LYP, MP2 methods with dryrun mode, timing measurements, and proper error handling to enable reliable quantum chemistry computations.

## 2. Scope & Non-Goals
**Scope:**
- PySCF runner class in `services/pyscf_service/app/runner.py`
- Method support: HF, B3LYP, MP2
- Basis set handling (def2-SVP and others)
- PYSCF_DRYRUN mode for testing
- System ID generation using SHA1 hash
- Timing measurements and environment metadata
- Exception handling and error reporting

**Non-Goals:**
- Advanced quantum chemistry methods beyond HF/B3LYP/MP2
- Complex basis set optimization or selection
- Multi-threaded or distributed calculations
- Real-time progress reporting or streaming

## 3. Requirements & Acceptance Criteria
- [ ] PySCF runner in `services/pyscf_service/app/runner.py`
- [ ] Supports HF, B3LYP, MP2 methods
- [ ] Handles def2-SVP and other basis sets
- [ ] Implements `PYSCF_DRYRUN` mode for testing
- [ ] Generates `system_id` using sha1 hash
- [ ] Records timing information
- [ ] Includes environment metadata

## 4. Architecture & Data Impact
**Components:**
- PySCF quantum chemistry library integration
- Molecule parsing and geometry handling
- Method dispatcher for different calculation types
- System identification and caching logic
- Environment introspection for metadata

**Data Structures:**
- Input: JobRequest with molecule_xyz, method, basis, parameters
- Output: Calculation results with energy, timing, metadata
- System ID: SHA1 hash of normalized molecule geometry

**Environment Variables:**
- `PYSCF_DRYRUN`: Enable mock calculations for testing
- `OMP_NUM_THREADS`: Control parallelization (set to 1)

## 5. Implementation Plan (Step-by-Step)
1. **Create Runner Class Structure**
   - Initialize `PySCFRunner` class in `runner.py`
   - Add constructor with configuration parameters
   - Set up logging and error handling framework

2. **Implement Molecule Parsing**
   - Parse XYZ coordinate string format
   - Validate molecular structure and atom types
   - Create PySCF molecule object with proper charge/spin
   - Handle common XYZ format variations

3. **Create System ID Generator**
   - Normalize molecule geometry (remove whitespace, standardize format)
   - Generate SHA1 hash of normalized geometry string
   - Return first 10 characters as system_id
   - Add validation and collision detection

4. **Implement Method Dispatcher**
   - Create separate calculation methods for HF, B3LYP, MP2
   - Handle basis set specification and validation
   - Configure grid level for DFT calculations
   - Set convergence tolerances per method

5. **Add PYSCF_DRYRUN Mode**
   - Detect dryrun environment variable
   - Return mock results with realistic structure
   - Include proper timing simulation
   - Maintain consistent system_id generation

6. **Implement Timing and Metadata**
   - Record wall clock time for calculations
   - Capture PySCF, NumPy, Python version information
   - Include dryrun flag in environment metadata
   - Add calculation parameters to result

7. **Add Error Handling**
   - Catch PySCF convergence failures
   - Handle invalid molecular structures
   - Manage memory and resource constraints
   - Provide meaningful error messages

## 6. API/Schema Changes
**Runner Interface:**
```python
class PySCFRunner:
    def calculate(self, job_request: JobRequest) -> CalculationResult:
        # Main calculation interface
        
    def generate_system_id(self, molecule_xyz: str) -> str:
        # System ID generation
        
    def _run_hf(self, mol, basis: str, **kwargs) -> float:
        # HF calculation implementation
        
    def _run_b3lyp(self, mol, basis: str, **kwargs) -> float:
        # B3LYP calculation implementation
        
    def _run_mp2(self, mol, basis: str, **kwargs) -> float:
        # MP2 calculation implementation
```

**Calculation Result Structure:**
```json
{
  "energy_hartree": -75.983742,
  "system_id": "sha1-10-chars",
  "timings": {"wall_s": 0.42},
  "env": {
    "dryrun": false,
    "numpy": "1.26.4",
    "pyscf": "2.4.0",
    "python": "3.10.12"
  },
  "method": "HF",
  "basis": "def2-SVP",
  "converged": true
}
```

## 7. Test Plan
**Unit Tests:**
- System ID generation consistency and uniqueness
- Method dispatcher routing (HF/B3LYP/MP2)
- Molecule parsing with various XYZ formats
- Dryrun mode result generation
- Error handling for invalid inputs
- Timing measurement accuracy

**Integration Tests:**
- Complete calculation workflow with PySCF
- Basis set handling and validation
- Environment metadata collection
- Memory usage and resource management

**E2E Tests:**
- Real calculations with small molecules (H2, H2O)
- Dryrun vs real calculation consistency
- Performance benchmarking with timing limits
- Error recovery and graceful degradation

**Edge/Failure Cases:**
- Invalid molecular geometries
- Unsupported basis sets
- Convergence failures
- Memory exhaustion scenarios
- Concurrent calculation handling

**Coverage Target:** >= 90% for runner logic, 100% for dryrun paths

## 8. Verification Checklist (DoD)
- [ ] PySCF runner in `services/pyscf_service/app/runner.py`
- [ ] Supports HF, B3LYP, MP2 methods
- [ ] Handles def2-SVP and other basis sets
- [ ] Implements `PYSCF_DRYRUN` mode for testing
- [ ] Generates `system_id` using sha1 hash
- [ ] Records timing information
- [ ] Includes environment metadata
- [ ] All methods produce consistent results
- [ ] Error handling covers common failure modes
- [ ] Performance meets timing requirements
- [ ] Memory usage stays within acceptable limits

## 9. Risk, Mitigation, Rollback
**Top Risks:**
- PySCF installation and dependency issues
- Memory consumption with larger molecules
- Calculation convergence failures
- Performance degradation with complex molecules
- Environment inconsistencies across platforms

**Detection Signals:**
- PySCF import or initialization failures
- Memory usage exceeding container limits
- Frequent convergence errors
- Calculation times exceeding reasonable limits
- Platform-specific behavior differences

**Mitigation:**
- Thorough testing with PySCF installation in container
- Implement memory monitoring and limits
- Add convergence retry logic with relaxed settings
- Set reasonable timeout limits for calculations
- Test on all target platforms early

**Rollback Steps:**
- Fall back to mock calculations only
- Disable problematic calculation methods
- Return to simpler calculation implementation
- Use pre-computed results for testing

## 10. Dependencies & Sequencing
**Upstream Dependencies:**
- Sprint 1: Service foundation and schemas completed
- PySCF library properly installed in container
- Environment variable configuration system

**Downstream Dependencies:**
- Story 2.1: Job submission endpoint needs runner integration
- Story 2.3: Result storage needs calculation output format
- Story 2.5: Testing framework needs runner for validation

**Sequencing:**
- Can develop in parallel with S21 using mocked interfaces
- Must complete before S23 result storage integration
- Critical for S25 comprehensive testing

## 11. Telemetry & Observability
**Metrics:**
- Calculation execution time by method and molecule size
- Memory usage patterns during calculations
- Convergence success/failure rates
- System ID distribution and collision rates
- Dryrun vs real calculation performance

**Logging:**
- Calculation start/completion events
- Method and basis set selections
- Convergence warnings and errors
- Resource usage patterns
- Environment metadata capture

**Monitoring:**
- Calculation queue depth and processing rate
- Memory usage trends and peaks
- Error rate patterns by calculation type
- Performance degradation detection

**Alerts:**
- Calculation failures exceeding 10% rate
- Memory usage approaching container limits
- Calculation times exceeding expected ranges
- Repeated convergence failures

## 12. Docs & Change Management
**Files to Update:**
- Create: `services/pyscf_service/app/runner.py`
- Update: `services/pyscf_service/requirements.txt` (ensure PySCF pinned)
- Create: Calculation method documentation
- Update: API documentation with calculation examples
- Create: Troubleshooting guide for calculation issues

**Technical Documentation:**
- Supported methods and basis sets
- System ID generation algorithm
- Dryrun mode behavior and limitations
- Performance characteristics and limitations
- Error handling and recovery procedures

**User Documentation:**
- Calculation parameter selection guide
- Performance expectations and timing
- Common error messages and solutions

## 13. Work Items
**Branch Name:** `feature/pyscf-runner-implementation`
**PR Title:** "feat: implement PySCF runner with HF/B3LYP/MP2 methods and dryrun support"
**Labels:** `feat`
**Reviewers:** Technical Lead, QA Engineer, DevOps Engineer
**CI Gates:** All tests pass with PYSCF_DRYRUN=1, memory usage validation, performance benchmarks

## Follow-ups
OPEN-QUESTION: Should we implement calculation result caching based on system_id to avoid redundant computations?
OPEN-QUESTION: How should we handle very large molecules that might exceed memory limits?
OPEN-QUESTION: Do we need configurable timeout limits for long-running calculations?
OPEN-QUESTION: Should the runner support custom basis set definitions beyond standard sets?
