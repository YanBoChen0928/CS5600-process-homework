# CS 5600 Project Progress Update #2

**Student:** Yan-Bo Chen  
**Date:** November 18, 2025  
**Project:** Workload Characterization of Medical RAG on ARM Architecture and GPU-accelerated Configurations

---

## 1. Problem Statement

This project characterizes the system-level performance of medical RAG (Retrieval-Augmented Generation) deployments, comparing CPU-only and GPU-accelerated configurations to inform deployment decisions for privacy-sensitive, resource-constrained medical environments.

**Research Question:** What are the performance characteristics (latency, CPU utilization, memory footprint) of medical RAG workloads under CPU-only (ARM M2 Pro) and GPU-accelerated (x86 + RTX 4090) configurations, and what is the performance-cost trade-off between these deployment options?

---

## 2. Approach and Methodology

This study compares two deployment configurations on the same medical RAG pipeline:

### Configuration 1: ARM CPU-Only (Primary Focus)
- **Hardware:** Apple MacBook Pro M2 Pro
- **CPU:** 10-core ARM (6 Performance + 4 Efficiency cores)
- **Memory:** 16GB unified memory
- **Runtime:** Ollama 0.12.6 with Llama-3.2-3B (CPU-only mode)
- **Test Scale:** 100 queries × 5 runs = 500 data points (reduced from 10 runs for efficiency)

### Configuration 2: x86 + GPU (Comparison Baseline)
- **Hardware:** Lab workstation with Intel i9 + RTX 4090
- **Status:** To be conducted if lab access is available
- **Test Scale:** Subset of queries for comparison

### Software Stack & Tools
- **LLM Runtime:** Ollama (local inference server)
- **Model:** Llama-3.2-3B (quantized, Q4_K medium, 2.0 GB)
- **Base System:** OnCallGuide.ai medical RAG pipeline
- **Profiling Tools:**
  - Python 3.11 with psutil for system metrics
  - time.perf_counter() for high-resolution timing
  - Activity Monitor for execution verification

---

## 3. Project Tasks and Timeline

### Phase 1: Setup & Instrumentation (Oct 21 - Nov 20)

#### ✅ Completed Tasks (Oct 21 - Nov 18):
- **Environment Setup** (Oct 21-28)
  - ✅ Python virtual environment created and configured
  - ✅ Ollama 0.12.6 installed via Homebrew
  - ✅ Llama-3.2-3B model downloaded (2.0 GB, Q4_K medium)
  - ✅ Dependencies installed (psutil, time.perf_counter verified)

- **CPU-Only Configuration** (Oct 28 - Nov 18)
  - ✅ Created custom Modelfile with `num_gpu 0` parameter
  - ✅ Built CPU-only model variant: `llama3.2-cpu`
  - ✅ Added `num_thread 8` for explicit CPU thread allocation
  - ✅ Verified CPU-only execution via Activity Monitor and server logs
    - Confirmed: 0 layers offloaded to GPU
    - Confirmed: library=cpu (not Metal)
    - Confirmed: CPU usage 400-800% during inference
    - Confirmed: GPU usage 0-5% (idle)

#### 🔄 In Progress (Nov 18-20):
- **Profiling Code Development** (Nov 18-19)
  - ⏳ Implement minimal profiler script (psutil + time.perf_counter)
  - ⏳ Create automated query execution loop
  - ⏳ Design CSV output format for metrics collection

- **Initial Testing** (Nov 19-20)
  - ⏳ Prepare 10-20 medical test queries
  - ⏳ Run small-scale validation (10 queries × 1 run)
  - ⏳ Verify data collection pipeline

- **Code Freeze Preparation** (Nov 20)
  - ⏳ Final code testing and bug fixes
  - ⏳ Document setup and execution procedures
  - ⏳ Ensure code is ready for unattended execution

### Phase 2: Data Collection (Nov 20 - Nov 28)
- **Primary Dataset Collection**
  - ⏸️ Expand to 100 medical queries
  - ⏸️ Execute 100 queries × 5 runs = 500 data points
  - ⏸️ Monitor and validate data quality during collection

- **Optional: x86 + GPU Baseline** (if lab access available)
  - ⏸️ Setup same profiling code on lab workstation
  - ⏸️ Run subset of queries for comparison

### Phase 3: Analysis & Visualization (Nov 21 - Dec 6)
- **Data Analysis**
  - ⏸️ Statistical analysis (median, p50, p95 latency)
  - ⏸️ CPU utilization patterns (P-cores vs E-cores)
  - ⏸️ Memory footprint characterization

- **Visualization**
  - ⏸️ Latency distribution plots
  - ⏸️ CPU/memory usage over time
  - ⏸️ Per-core utilization heatmaps

### Phase 4: Report & Presentation (Dec 2 - Dec 9)
- **Final Report**
  - ⏸️ Write comprehensive analysis
  - ⏸️ Document findings and insights
  - ⏸️ Prepare presentation materials

**Legend:**
- ✅ = Completed
- ⏳ = In Progress (Current Focus)
- ⏸️ = Scheduled (Not Started)

---

## 4. Progress to Date (as of November 18, 2025)

### Major Accomplishments

**Environment Setup: 100% Complete**
- Successfully installed and configured Ollama 0.12.6 on M2 Pro
- Downloaded and verified Llama-3.2-3B model (model ID: a80c4f17acd5)
- All profiling dependencies (psutil, time module) tested and functional

**CPU-Only Configuration: 100% Complete and Verified**

The critical challenge of forcing CPU-only execution on macOS has been successfully resolved. Initial attempts using environment variables (`OLLAMA_NUM_GPU=0`) were insufficient, as Ollama continued to use Metal GPU acceleration by default.

**Solution Implementation:**
1. Created custom Modelfile with explicit CPU-only parameters:
   ```
   FROM llama3.2:3b
   PARAMETER num_gpu 0
   PARAMETER num_thread 8
   ```

2. Built new model variant: `ollama create llama3.2-cpu -f Modelfile-cpu`

3. Comprehensive verification conducted:

**Verification Evidence:**
- **Server Logs Analysis:**
  - ✅ `library=cpu` (not `library=Metal`)
  - ✅ `layers.offload=0` (0 out of 29 layers on GPU)
  - ✅ `load_tensors: offloaded 0/29 layers to GPU`
  - ✅ `memory.gpu_overhead="0 B"` (zero GPU memory)
  - ✅ `CPU model buffer size = 1918.35 MiB` (all model weights in CPU memory)

- **Activity Monitor Verification:**
  - ✅ CPU usage: 400-800% during inference (using 4-8 cores actively)
  - ✅ GPU usage: 0-5% (idle, no inference workload)
  - ✅ GPU History graph: flat line (no GPU activity spikes)

- **Command-Line Monitoring:**
  - ✅ Verified via `ps aux | grep ollama` showing CPU percentage 50-114%
  - ✅ Process running on CPU with no Metal library engagement for computation

**Key Technical Insight:** While Metal framework initialization still occurs (macOS default behavior), the actual model inference runs entirely on CPU. The combination of `num_gpu 0` and `num_thread 8` successfully forces CPU-only execution despite macOS's deep Metal integration.

---

## 5. Remaining Tasks and Milestones

### Immediate Priority (Nov 18-20): Code Freeze Preparation

**Critical Understanding:** The November 20th code freeze deadline means all profiling code must be complete and tested. Data collection (1000 data points) will occur AFTER code freeze, during the experimental phase.

**Nov 18 Evening (4 hours):**
- Implement minimal profiler script (~50 lines)
  - psutil integration for CPU/memory metrics
  - time.perf_counter() for latency measurement
  - CSV output format design
- Test profiler with 2-3 sample queries

**Nov 19 (Full Day):**
- Prepare initial medical query dataset (10-20 queries minimum)
- Create automated execution script (run_experiment.py)
- Conduct small-scale validation: 10 queries × 1 run
- Verify CSV format and data completeness
- Debug and refine profiling code

**Nov 20 Morning (Code Freeze Day):**
- Final code testing and validation
- Document setup procedures and execution instructions
- Ensure code can run unattended for extended periods
- Create simple README for execution
- **Deliverable:** Production-ready profiling code

### Post-Code Freeze (Nov 20 onwards): Experimental Phase
- **Nov 20-28:** Execute full data collection (100 queries × 5 runs = 500 data points)
- **Nov 21-Dec 6:** Data analysis and visualization
- **Dec 2-9:** Final report writing and presentation preparation

---

## 6. Challenges Overcome and Lessons Learned

### Challenge 1: Ollama Metal GPU Acceleration (RESOLVED ✅)

**Problem:** macOS Ollama defaults to Metal GPU acceleration, making CPU-only profiling impossible.

**Initial Failed Attempts:**
- Environment variable `OLLAMA_NUM_GPU=0`: Ignored by Ollama
- Environment variable `OLLAMA_NO_METAL=1`: Not recognized
- Both resulted in all 29 model layers offloading to GPU

**Successful Solution:**
- Custom Modelfile approach with dual parameters:
  - `num_gpu 0`: Disables GPU layer offloading
  - `num_thread 8`: Explicitly allocates CPU threads
- Creating dedicated model variant ensures repeatable CPU-only execution

**Verification Methodology:**
- Multi-pronged approach: server logs + Activity Monitor + CLI monitoring
- Looking for: `layers.offload=0` and `library=cpu` in logs
- Observing: High CPU usage (400-800%) with minimal GPU activity (0-5%)

**Key Lesson:** macOS's deep Metal integration requires model-level configuration rather than runtime environment variables. The solution is now documented and reproducible.

### Challenge 2: Environment Setup Incompleteness (RESOLVED ✅ Nov 17)

**Problem Discovered:** On November 17, during preparation for profiling code development, discovered that the medical-rag-profiling directory established in October contained only compiled Python cache files (.pyc), missing the actual source code (.py files) needed for RAG pipeline integration.

**Root Cause:** During initial October 28 setup, directory structure was visually confirmed but actual file contents were not verified. Only `__pycache__/` directories with compiled bytecode existed; the source Python files (generation.py, retrieval.py, llm_clients.py, etc.) were absent.

**Impact:** Could not proceed with Ollama integration without RAG pipeline source code.

**Resolution (Nov 17):**
1. Located complete source code in GenAI-OnCallAssistant repository
2. Verified all dependencies already installed in venv_cs5600Project/ (no reinstallation needed)
3. Executed systematic migration:
   - Backed up existing customization/ folder
   - Copied complete src/ directory with all Python sources
   - Copied supporting modules (app.py, requirements, .env template)
   - Cleaned Python cache files to prevent conflicts
   - Verified all modules importable
4. Documented entire process in Source Code Migration Log for future reference

**Lessons Learned:**
- Always verify file contents, not just directory structure
- Run import tests (`python -c "from src import module"`) during setup
- Check for actual .py files using `find . -name "*.py" -type f`
- Document assumptions explicitly and verify before confirming "setup complete"

**Current Status:** Source code migration complete. All RAG pipeline components now available for Ollama integration work.

### Challenge 3: Timeline Adjustment (ACKNOWLEDGED)

**Professor Feedback:** "Most of the practical work is to come... this is a very doable project if you stay on track."

**Response:**
- Acknowledge the compressed timeline for remaining work
- Prioritize minimal viable profiler (MVP) over complex instrumentation
- Focus on core metrics: latency, CPU usage, memory footprint
- Defer advanced features (per-layer breakdown, I/O profiling) to optional extensions

**Risk Mitigation:**
- Simple 50-line profiler reduces implementation risk
- Small-scale validation (10 queries) before full data collection
- Code freeze deadline ensures focus on execution rather than development

---

## 7. Current Status and Next Immediate Steps

### Project Health: On Track ✅

**Strengths:**
- ✅ Critical CPU-only configuration fully resolved and verified
- ✅ Environment setup complete and tested
- ✅ Clear understanding of remaining scope
- ✅ Realistic timeline with appropriate prioritization

**Risks:**
- ⚠️ Tight timeline for profiling code development (48 hours remaining)
- ⚠️ Uncertainty regarding x86+GPU lab access (optional baseline)

### This Week's Focus (Nov 18-20)

**Monday Evening (Nov 18) - RAG Integration:**
- Complete source code migration verification
- Create local Ollama LLM client wrapper (llm_local_ollama.py)
- Modify RAG pipeline generation.py to use local inference
- Test end-to-end RAG workflow: query → retrieval → generation
- Verify CPU-only execution maintained during full pipeline

**Tuesday (Nov 19) - Profiling System:**
- Implement profiling module (workload_profiler.py)
  - psutil for CPU/memory metrics
  - time.perf_counter() for latency
  - JSON output per query
- Create automated experiment runner (run_experiment.py)
- Prepare medical query datasets (10 for testing, 100 for full run)
- Build automated execution pipeline
- Run small-scale validation: 10 queries × 1 run
- Verify data collection and storage

**Wednesday Morning (Nov 20 - Code Freeze):**
- Final testing and debugging
- Create deployment package for x86 system
- Documentation and README
- Confirm production readiness
- **Deliverable:** Complete, tested, ready-to-run profiling system

### Success Criteria for Code Freeze

By November 20, 11:59 PM, the project must have:
1. ✅ Working profiler script that collects: latency, CPU%, memory usage
2. ✅ Automated query execution loop (tested with 10+ queries)
3. ✅ CSV output with correct format and complete data
4. ✅ Documentation for running experiments
5. ✅ Verified code can execute unattended for extended periods

After code freeze, only experiment execution, data analysis, and report writing remain.

---

## 8. Conclusion

Significant progress has been made since Update #1. The critical CPU-only configuration challenge has been completely resolved with a verified, reproducible solution. The project is now entering the final implementation phase before code freeze.

The remaining 48 hours will focus on delivering a minimal but complete profiling system. The simplified approach (50-line profiler, small validation set) reduces risk while ensuring all core requirements are met.

Professor Schmidt's feedback regarding timeline concerns has been acknowledged and addressed through prioritization and scope management. The project remains feasible and on track for successful completion within the semester timeline.

**Next Update:** Will be provided after code freeze (Nov 20) with initial experimental results and updated timeline for analysis phase.
