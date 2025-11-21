# CS5600 Project Progress Update #1

**Student:** Yan-Bo Chen  
**Date:** October 28, 2025  
**Project:** Workload Characterization of CPU-Based Medical RAG on ARM Architecture

---

## 1. Problem Statement

Medical AI systems increasingly require on-premise deployment due to privacy regulations (HIPAA) and data sovereignty constraints. While GPU-based LLM inference has been extensively characterized, clinical and edge environments often depend on CPU-only deployments on ARM architectures such as Apple Silicon.

**Research Question:** What are the system-level performance characteristics of CPU-only medical RAG workloads on ARM architecture (Apple M2 Pro)?

This project addresses a critical gap: existing workload characterization studies primarily target x86 CPUs or GPU-accelerated systems, leaving ARM CPU-only inference uncharacterized. By profiling CPU utilization, memory footprint, and latency breakdown across a 5-layer medical RAG pipeline, we establish a performance baseline that informs ARM-specific system design and deployment strategies for resource-constrained, privacy-sensitive medical AI environments.

---

## 2. Methodology & Approach

### Hardware Environment
- **Platform:** Apple MacBook Pro M2 Pro
- **CPU:** 10-core ARM (6 Performance cores + 4 Efficiency cores)
- **Memory:** 16GB unified memory
- **OS:** macOS Ventura 13.4

### Software Stack
- **LLM Runtime:** Ollama (local inference server)
- **Model:** Llama-3.2-3B (quantized, CPU-only configuration)
- **Base System:** OnCallGuide.ai medical RAG pipeline
- **Profiling Tools:** Python psutil, time.perf_counter()

### Pipeline Architecture (5 Layers)
The medical RAG system consists of:
1. **Input Validation:** Medical query classification and safety checks
2. **Embedding Generation:** sentence-transformers for query vectorization
3. **Vector Retrieval:** Annoy index for similarity search
4. **Result Validation:** Quality assessment of retrieved documents
5. **LLM Generation:** Llama-3.2-3B for response generation

### Measurement Strategy
**Metrics Collected:**
- Per-layer timing (time.perf_counter())
- CPU utilization per core (psutil.cpu_percent(percpu=True))
- Memory usage and allocation patterns (psutil.Process.memory_info())
- Query characteristics (length, type, complexity)

**Test Corpus:**
- 100 medical queries: 50 emergency scenarios, 50 treatment consultations
- 10 runs per query for statistical significance
- Report p50/p95 latency distributions

**Control Measures:**
- Background processes disabled (Spotlight, iCloud sync)
- CPU-only execution verified via Activity Monitor
- Consistent environment across all test runs

### Code Repository
Project structure at: `/Users/yanbochen/IdeaProjects/CS5600-Homework/CS5600-process-homework/FinalProjectCode/medical-rag-profiling/`

**Key Components:**
- `llm_local_client.py`: Ollama API wrapper (to be implemented)
- `workload_profiler.py`: Metrics collection class (to be implemented)
- `customization_pipeline.py`: Existing RAG pipeline (modification in progress)

GitHub repository: *[To be created and made public after initial code completion]*

---

## 3. Project Tasks (Complete Timeline)

### Phase 1: Setup & Instrumentation (Oct 23 - Oct 31)
- Environment setup and dependency installation
- Ollama installation and model download
- Local LLM client implementation
- Profiling instrumentation integration
- Initial validation testing

### Phase 2: Data Collection (Nov 1 - Nov 10)
- Prepare 100-query test corpus from existing evaluation set
- Configure controlled test environment
- Execute profiling runs (100 queries × 10 iterations)
- Validate data quality and consistency
- Store results in structured JSON format

### Phase 3: Validation & Analysis (Nov 11 - Nov 20)
- Additional validation runs for edge cases
- Statistical analysis (p50, p95, distributions)
- Bottleneck identification and characterization
- Emergency vs treatment query comparison
- **November 20: CODE FREEZE**

### Phase 4: Report & Presentation (Nov 21 - Dec 9)
- Generate visualizations (matplotlib/seaborn)
- Write analysis report and deployment recommendations
- Prepare final presentation
- Documentation and code cleanup

---

## 4. Tasks Accomplished (as of Oct 28)

### ✅ Project Planning & Research
- Research gap identified and validated through literature review
- Two-page project proposal submitted (Oct 23)
- Methodology and timeline established
- Related work analysis completed (6 peer-reviewed papers)

### ✅ Environment Setup (Phase 1A: Steps 1-12)
- **Hardware Verification:**
  - M2 Pro specifications confirmed (10-core ARM, 16GB RAM)
  - CPU topology mapped (6 P-cores, 4 E-cores)
  
- **Development Environment:**
  - Project directory structure created
  - Python virtual environment configured (`venv_cs5600Project`)
  - Dependencies installed from `requirements_optimized.txt`
  - psutil and profiling libraries verified

- **Ollama & Model Setup:**
  - Ollama 0.12.6 installed via Homebrew
  - Llama-3.2-3B model downloaded (2.0 GB)
  - Model verified: `llama3.2:3b` (ID: a80c4f17acd5)
  - Ollama server tested and operational

### ✅ Technical Validation
- Confirmed Llama-3.2-3B memory requirements (~4-6GB)
- Verified Ollama compatibility with M2 Pro ARM architecture
- Identified profiling approach (psutil + time module)

---

## 5. Tasks To Be Accomplished (with Timeline)

### 🔄 Immediate Next Steps (Oct 29 - Oct 31)
**Phase 1A Completion:**
- [ ] **Oct 29 (Morning):** Resolve CPU-only execution configuration
  - Create CPU-only model variant using Modelfile
  - Test inference with `llama3.2-cpu` model
  - Verify GPU usage remains 0-5% during inference
  
- [ ] **Oct 29 (Afternoon):** Complete initial validation
  - Run 5-10 sample queries
  - Confirm profiling data collection works
  - Document baseline performance metrics

**Phase 1B - Code Modifications:**
- [ ] **Oct 30:** Implement `llm_local_client.py`
  - Create Ollama API wrapper class
  - Add retry logic and error handling
  - Test with sample medical queries

- [ ] **Oct 31:** Integrate profiling instrumentation
  - Modify `customization_pipeline.py` to use local LLM
  - Add per-layer timing hooks
  - Implement `WorkloadProfiler` class for metrics collection
  - Conduct end-to-end integration test

### 📅 Week 2 (Nov 1-3): Finalize Instrumentation
- [ ] **Nov 1-2:** Add CPU and memory monitoring
  - Integrate psutil for real-time resource tracking
  - Implement per-core CPU utilization logging
  - Add memory allocation tracking

- [ ] **Nov 3:** Validation testing
  - Run 10-query validation set
  - Verify data quality and consistency
  - Adjust profiling parameters if needed

### 📅 Weeks 3-4 (Nov 4-17): Data Collection & Analysis
- [ ] **Nov 4-10:** Primary data collection
  - Execute 100 queries × 10 runs = 1000 data points
  - Monitor for anomalies
  - Store results in JSON format

- [ ] **Nov 11-17:** Validation runs and analysis
  - Additional edge case testing
  - Statistical analysis (p50, p95)
  - Emergency vs treatment comparison
  - Bottleneck identification

### 📅 Weeks 5-6 (Nov 18 - Dec 9): Report & Presentation
- [ ] **Nov 18-20:** Final experiments before code freeze
- [ ] **Nov 21-30:** Analysis and visualization
- [ ] **Dec 1-9:** Final report and presentation preparation

---

## 6. Blocking Issues & Challenges

### ⚠️ Current Blocker: CPU-Only Execution Verification

**Issue Description:**  
Ollama 0.12.6 on macOS defaults to Metal (GPU) acceleration for the M2 Pro. Despite setting environment variables (`OLLAMA_NUM_GPU=0`, `OLLAMA_NO_METAL=1`), server logs show:
```
library=Metal layers.offload=29
load_tensors: offloaded 29/29 layers to GPU
Metal_Mapped model buffer size = 1918.35 MiB
CPU_Mapped model buffer size = 308.23 MiB
```

**Evidence:**
- All 29 model layers offloaded to GPU
- 1.9 GB allocated on GPU vs 308 MB on CPU
- Metal inference caused memory assertion failure during initial test

**Impact on Research:**  
CPU-only execution is **critical** to the research question. Using GPU would:
- Fundamentally change workload characteristics
- Invalidate CPU profiling data
- Undermine the entire study's validity

**Solution Identified:**  
Create a custom model variant using Ollama's Modelfile system:
1. Export model configuration: `ollama show llama3.2:3b --modelfile > Modelfile-cpu`
2. Add CPU-only parameter: `PARAMETER num_gpu 0`
3. Create new model: `ollama create llama3.2-cpu -f Modelfile-cpu`
4. Use in all project code: `model="llama3.2-cpu"`

**Timeline Impact:**  
- Blocker Duration: ~2 hours of troubleshooting (Oct 28)
- Resolution Time: 10-15 minutes (Oct 29 morning)
- Project Delay: Minimal (< 1 day)
- Confidence: High - solution is well-documented and straightforward

**Verification Plan:**  
Post-resolution, CPU-only execution will be verified by:
- Activity Monitor: GPU usage 0-10% during inference
- Ollama logs: No "Metal" or "GPU offload" messages
- Inference speed: Slower than GPU (confirming CPU execution)
- CPU utilization: 50-80% across multiple cores

### 📋 Other Considerations (Not Blockers)

**Challenge: ARM Core Scheduling Dynamics**  
The M2 Pro's heterogeneous architecture (6 P-cores + 4 E-cores) may introduce measurement variability due to dynamic scheduling.

**Mitigation:**
- Implement warm-up runs to stabilize on P-cores
- Report median (p50) and p95 across multiple runs
- Document core allocation behavior as part of ARM characterization
- Consider this variability as an inherent characteristic of ARM workloads

**Status:** Under observation - will validate during initial testing phase.

---

## 7. Next Immediate Actions (Oct 29)

**Priority 1:** Implement CPU-only model configuration (30 minutes)  
**Priority 2:** Verify CPU-only execution via Activity Monitor (15 minutes)  
**Priority 3:** Run initial profiled queries (1 hour)  
**Priority 4:** Begin llm_local_client.py implementation (2-3 hours)

**Expected Milestone by Oct 31:**  
Functional local LLM deployment with integrated profiling capability, demonstrated on 5-10 sample medical queries with validated CPU-only execution.

---

## 8. Summary & Outlook

**Current Progress:** On track for Week 1-2 deliverables. Environment setup (Phase 1A) is 85% complete, with only CPU-only configuration remaining. The blocking issue has been diagnosed with a clear solution path.

**Confidence Level:** High. The project timeline includes buffer time for unexpected issues, and the CPU-only blocker has a straightforward resolution. Data collection phase timing will be validated once per-query inference time is measured during initial testing.

**Key Achievement:** Successfully established the foundational infrastructure for ARM-based medical RAG characterization, with profiling tools validated and ready for integration.

---

## References

[1] W. Jiang et al., "RAGO: Systematic performance optimization for retrieval-augmented generation serving," in *Proc. ISCA*, 2025.

[2] S. Na et al., "Understanding performance implications of LLM inference on CPUs," in *Proc. IISWC*, 2024.

[3] M. Li et al., "BiomedRAG: A retrieval-augmented large language model for biomedicine," *J. Biomed. Inform.*, vol. 162, 2025.
