# Medical RAG Workload Characterization on ARM and x86 Architectures

**CS5600 Computer Systems - Final Project**  
**Author:** Yan-Bo Chen  
**Institution:** Northeastern University  
**Term:** Fall 2025

---

## 🎯 Project Overview

This project conducts a **comprehensive performance characterization** of a Medical RAG (Retrieval-Augmented Generation) system across two fundamentally different computing architectures:

| Platform | Architecture | Configuration | Mode |
|----------|-------------|---------------|------|
| **ARM** | Apple M2 Pro | 12 cores (8P+4E), 16GB Unified Memory | CPU-only |
| **x86** | Intel i9 + RTX 4090 | 32 cores, 64GB RAM, 24GB VRAM | GPU-accelerated |

### Key Objectives

1. **Characterize performance** of LLM inference workloads on ARM (CPU-only) vs x86 (GPU)
2. **Quantify resource utilization** (CPU, memory, latency) across architectures
3. **Analyze deployment trade-offs** for edge (ARM) vs cloud/datacenter (x86) scenarios
4. **Provide evidence-based recommendations** for RAG system deployment

### Why This Matters

- **Modern AI workloads** increasingly run on diverse hardware (edge devices, cloud servers)
- **ARM-based systems** (Apple Silicon, AWS Graviton) are gaining popularity for inference
- **GPU acceleration** (CUDA) has been the standard, but CPU-only alternatives are emerging
- **Performance vs cost trade-offs** need empirical data for informed decisions

---

## 🔬 Research Questions

### Primary Questions

1. **Performance Gap**: How much faster is GPU-accelerated x86 compared to CPU-only ARM for LLM inference?
   - Hypothesis: x86 + RTX 4090 achieves 1.3-1.8× speedup

2. **Resource Efficiency**: How do CPU and memory utilization patterns differ between architectures?
   - ARM: Expected higher CPU utilization (all compute on CPU)
   - x86: Expected lower CPU utilization (offloaded to GPU)

3. **Scalability**: How does performance scale with workload complexity?
   - Test datasets: 10, 25, 100 queries
   - Categories: general, cardio, infection, trauma

### Secondary Questions

4. **Memory Architecture**: Does ARM's unified memory provide advantages over discrete x86 memory?
5. **Power Efficiency**: What is the performance-per-watt comparison? (future work)
6. **Cost-Benefit Analysis**: When is ARM deployment preferable to x86?

---

## 🏗️ System Architecture

### Workload: Medical RAG Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     Medical Query Input                         │
│              "What are symptoms of myocardial infarction?"      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Level 1: Condition Extraction (LLM: Llama 3.2:3B)             │
│  ├─ ARM: CPU-only (num_gpu=0, num_threads=8)                   │
│  └─ x86: GPU-accelerated (CUDA, automatic)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Level 2: Retrieval (Vector Search + Dual-Index)               │
│  ├─ Emergency Guidelines Index                                 │
│  └─ Treatment Protocols Index                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Level 3: Generation (LLM: Llama 3.2:3B)                       │
│  └─ Evidence-based response with source attribution            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                Clinical Guidance Output                         │
│         (with latency, CPU, memory metrics captured)            │
└─────────────────────────────────────────────────────────────────┘
```

**Why Medical RAG?**
- ✅ Representative of modern AI workloads (LLM + retrieval)
- ✅ Compute-intensive (token generation)
- ✅ Memory-intensive (vector search, model weights)
- ✅ Real-world application with clear performance requirements
- ✅ Reproducible and measurable

For detailed RAG system documentation, see LLM_RAG_README.md in the root directory.

---

### Profiling System

**Real-time Metrics Collection:**
- **CPU**: Per-core and total utilization (sampled every 500ms)
- **Memory**: Used, available, peak (GB)
- **Latency**: Total, retrieval, generation, overhead (milliseconds)
- **Timeline**: Complete resource usage trace for each query

**Implementation:**
- Python `psutil` for system metrics
- `time.perf_counter()` for high-resolution timing
- JSON output for structured data storage

---

## 🧪 Experimental Setup

### Hardware Platforms

#### ARM (Apple MacBook Pro M2 Pro)

**Specifications:**
- **CPU**: 12 cores (6 performance + 6 efficiency)
- **Memory**: 16 GB unified memory
- **OS**: macOS 14.x
- **Architecture**: ARM64

**Configuration:**
- **LLM Backend**: Ollama (CPU-only mode)
- **Model**: Llama 3.2:3B
- **Forced CPU execution**: `num_gpu=0`, `num_threads=8`

#### x86 (Lab Workstation)

**Specifications:**
- **CPU**: Intel i9 (32 cores)
- **GPU**: NVIDIA RTX 4090 (24GB VRAM)
- **Memory**: 64 GB DDR4
- **OS**: Ubuntu 22.04 (WSL2)
- **Architecture**: x86_64

**Configuration:**
- **LLM Backend**: Ollama (GPU-accelerated)
- **Model**: Llama 3.2:3B
- **CUDA**: Automatic GPU utilization

---

### Datasets

| Dataset | Size | Runs | Total Queries | Description |
|---------|------|------|---------------|-------------|
| **10** | 10 queries | 5 | 50 | Small test set |
| **25** | 25 queries | 5 | 125 | Medium test set |
| **100** | 100 queries | 5 | 500 | Full experiment |
| **cardio** | 30 queries | 5 | 150 | Cardiovascular emergencies |
| **infection** | 25 queries | 5 | 125 | Infectious diseases |
| **trauma** | 20 queries | 5 | 100 | Trauma cases |

**Query Examples:**
- "What are the symptoms of acute myocardial infarction?"
- "How to manage septic shock in emergency settings?"
- "Treatment protocol for severe head trauma?"

---

### Experimental Protocol

**Phase 1: ARM Data Collection**
1. Close all background applications
2. Start Ollama server (CPU-only)
3. Run: `./medrag.py batch --all`
4. Duration: ~4-6 hours
5. Output: `results/ARM_*/`

**Phase 2: x86 Data Collection**
1. Verify GPU availability
2. Start Ollama server (GPU mode)
3. Run: `./medrag.py batch --all`
4. Duration: ~2-3 hours
5. Output: `results/x86_*/`

**Phase 3: Data Integration & Analysis**
1. Transfer x86 data to ARM machine
2. Run: `./medrag.py compare --all`
3. Run: `./medrag.py report --all`
4. Run: `./medrag.py latex --all`
5. Output: `final_report/`

---

## 🚀 Quick Start

### Prerequisites

**On ARM (MacBook M2 Pro):**
```bash
# Install Ollama
brew install ollama

# Clone repository
cd ~/Desktop
git clone <repository-url> FinalProjectCode

# Setup environment
cd FinalProjectCode/medical-rag-profiling
python3 -m venv venv_cs5600Project
source venv_cs5600Project/bin/activate
pip install -r requirements.txt

# Configure CPU-only model
ollama create llama3.2-cpu -f Modelfile-cpu
```

**On x86 (Lab Workstation):**
```bash
# In WSL2 (Ubuntu)
# Install Ollama (see: https://ollama.ai/download/linux)
curl -fsSL https://ollama.com/install.sh | sh

# Clone repository
git clone <repository-url> medical-rag-profiling
cd medical-rag-profiling

# Setup environment
python3 -m venv venv_x86
source venv_x86/bin/activate
pip install -r requirements.txt

# Pull model (GPU will be auto-detected)
ollama pull llama3.2:3b
```

---

### Running Experiments

**Quick Test (10 queries):**
```bash
# Verify system is working
./medrag.py run --dataset 10 --runs 1

# Check output
ls results/ARM_10/  # or x86_10/
cat results/ARM_10/query_000_run_00.json
```

**Full Experiment (All Datasets):**
```bash
# Run in background with logging
nohup ./medrag.py batch --all > batch_log.txt 2>&1 &

# Monitor progress
tail -f batch_log.txt
```

**Analysis:**
```bash
# Single platform analysis
./medrag.py analyze --output results/ARM_100
./medrag.py visualize --output results/ARM_100

# Cross-platform comparison (requires both ARM and x86 data)
./medrag.py compare --dataset 100
./medrag.py report --dataset 100
./medrag.py latex --dataset 100

# Advanced visualizations (p95/p99, CDF, violin, P/E-cores)
python3 visualization_advanced.py --all

# Generate specific visualization type
python3 visualization_advanced.py --type boxplot --dataset 100
python3 visualization_advanced.py --type cdf --dataset cardio
python3 visualization_advanced.py --type violin --platform ARM
python3 visualization_advanced.py --type pecores  # P/E-cores analysis
python3 visualization_advanced.py --report --dataset 100  # Percentile report
```

---

## 📁 Project Structure

```
medical-rag-profiling/
├── README.md                       # Project overview (this file)
├── LLM_RAG_README.md               # RAG system technical documentation
├── medrag.py                       # Unified CLI tool
├── run_experiment.py               # Experiment execution engine
├── analyze_results.py              # Statistical analysis
├── visualize_results.py            # Visualization generator
├── visualization_advanced.py       # Advanced viz (p95/p99, CDF, violin, P/E-cores)
├── rag_wrapper.py                  # RAG pipeline interface
├── Modelfile-cpu                   # Ollama CPU-only configuration
├── requirements.txt                # Python dependencies
│
├── src/                            # RAG system modules
│   ├── user_prompt.py              # Query processing
│   ├── retrieval.py                # Dual-index retrieval
│   ├── generation.py               # LLM response generation
│   ├── llm_clients.py              # Ollama interface
│   └── medical_conditions.py       # Condition mapping
│
├── profiling/                      # Profiling modules
│   ├── workload_profiler.py        # Real-time metrics collection
│   └── __init__.py
│
├── queries/                        # Query datasets
│   ├── medical_queries_10.json
│   ├── medical_queries_25.json
│   ├── medical_queries_100.json
│   ├── cardio_queries.json
│   ├── infection_queries.json
│   └── trauma_queries.json
│
├── models/                         # Pre-trained models and indices
│   ├── embeddings/
│   └── indices/
│
├── docs_setup_guide/               # Setup and usage guides
│   ├── README_ARM.md               # ARM environment setup
│   ├── README_X86.md               # x86 environment setup
│   ├── README_medrag.md            # Complete CLI reference
│   └── Data_Analysis_Guide_ARM_vs_x86.md
│
├── academic/                       # Academic documents
│   ├── YanBoChen_CS5600_Progress_Update_1.md
│   ├── YanBoChen_CS5600_Progress_Update_2.md
│   ├── YanBoChen_CS5600_TwoPage_Project_Proposal.pdf
│   └── SystemDesign.md
│
├── results/                        # Experiment outputs (not in repo)
│   ├── ARM_10/, ARM_25/, ARM_100/
│   ├── ARM_cardio/, ARM_infection/, ARM_trauma/
│   ├── x86_10/, x86_25/, x86_100/
│   └── x86_cardio/, x86_infection/, x86_trauma/
│
└── final_report/                   # Analysis outputs (not in repo)
    ├── comparison_ARM_vs_x86_*.png  # Multi-panel comparisons
    ├── boxplot_*.png                # Latency box plots with p95/p99
    ├── cdf_*.png                    # Cumulative distribution functions
    ├── violin_*.png                 # Domain comparison violin plots
    ├── comparison_matrix_*.png      # 2x2 statistical comparison grids
    ├── pe_cores_*.png               # P-cores vs E-cores analysis (ARM)
    ├── summary_ARM_vs_x86_*.md
    ├── summary_ARM_vs_x86_*.csv
    └── table_*.tex
```

---

## 📚 Documentation

### User Guides

| Document | Description | Audience |
|----------|-------------|----------|
| README.md | **Project overview** (this file) | Everyone |
| LLM_RAG_README.md | RAG system technical details | Developers |
| docs_setup_guide/README_ARM.md | ARM environment setup & execution | ARM users |
| docs_setup_guide/README_X86.md | x86 environment setup & execution | x86 users |
| docs_setup_guide/README_medrag.md | **Complete CLI reference** | All users |
| docs_setup_guide/Data_Analysis_Guide_ARM_vs_x86.md | Analysis methodology | Researchers |

### Academic Documents

- academic/YanBoChen_CS5600_TwoPage_Project_Proposal.pdf — Initial project proposal
- academic/YanBoChen_CS5600_Progress_Update_1.md — First progress update
- academic/YanBoChen_CS5600_Progress_Update_2.md — Second progress update

---

## 📊 Results

### Actual Performance Results (500 queries)

#### Latency (Median Query Response Time)

| Dataset | ARM (CPU) | x86 (GPU) | Speedup |
|---------|-----------|-----------|---------|
| 100 queries | 10.60s | 2.30s | **4.62×** |
| cardio | 10.52s | 2.28s | **4.61×** |
| infection | 10.78s | 2.35s | **4.59×** |
| trauma | 10.45s | 2.31s | **4.52×** |

#### Tail Latency (p95/p99)

| Metric | ARM M2 Pro | x86 + RTX 4090 | Speedup |
|--------|------------|----------------|---------|
| p95 | 14.59s | 2.98s | **4.90×** |
| p99 | 17.35s | 3.25s | **5.34×** |

#### CPU Utilization (Average)

| Platform | Total CPU % | Cores Used | P-cores | E-cores |
|----------|-------------|------------|---------|---------|
| ARM M2 Pro | 759.9% | ~7.6 | 98.5% workload | 1.5% workload |
| x86 i9 | 76.1% | ~0.8 | N/A (GPU) | N/A |

#### Memory Footprint

| Platform | Average | Peak | Architecture |
|----------|---------|------|--------------|
| ARM M2 Pro | 8.02 GB | 8.12 GB | Unified |
| x86 + RTX 4090 | 2.02 GB | 2.15 GB | Discrete (GPU VRAM) |

### Generated Outputs

**Comparison Figures (via medrag.py):**
- Multi-panel performance comparison (latency, CPU, memory)
- Box plots, bar charts with error bars
- 300 DPI resolution (publication-ready)

**Advanced Visualizations (via visualization_advanced.py):**
- Box plots with p95/p99 percentile markers
- CDF (Cumulative Distribution Function) plots
- Violin plots comparing medical domains
- Dataset comparison matrices (2x2 statistical grids)
- P-cores vs E-cores workload distribution (ARM heterogeneous analysis)

**Reports:**
- Markdown summaries with key findings (including P/E-cores analysis)
- CSV data for further analysis
- LaTeX tables for paper integration

**Visualizations:**
- CPU heatmaps (per-core utilization)
- Latency distributions
- Memory timelines
- Core utilization comparisons

**Quick Commands:**
```bash
# Standard analysis
./medrag.py compare --all && ./medrag.py report --all

# Advanced visualizations (p95/p99, CDF, violin, P/E-cores)
python3 visualization_advanced.py --all

# Percentile report only
python3 visualization_advanced.py --report --dataset 100
```

See `final_report/` directory after running analysis commands.

---

## 🎓 Academic Context

### Course Information

**Course:** CS5600 Computer Systems  
**Instructor:** [Instructor Name]  
**Institution:** Northeastern University  
**Term:** Fall 2025

### Learning Objectives Addressed

1. **System Performance Analysis**
   - Profiling techniques (CPU, memory, I/O)
   - Bottleneck identification
   - Resource utilization characterization

2. **Architecture Comparison**
   - ARM vs x86 instruction sets
   - Unified vs discrete memory
   - CPU vs GPU compute paradigms

3. **Empirical Evaluation**
   - Experimental design
   - Data collection methodology
   - Statistical analysis and visualization

4. **Real-World System Design**
   - Performance vs cost trade-offs
   - Edge vs cloud deployment
   - Workload characterization

---

### Related Work

**ARM-based AI Inference:**
- Apple MLX (Metal acceleration on Apple Silicon)
- AWS Graviton instances for ML workloads
- Edge AI deployment on mobile/embedded ARM

**GPU-accelerated LLM Inference:**
- CUDA optimization for transformers
- TensorRT-LLM for production inference
- Multi-GPU scaling techniques

**RAG System Performance:**
- Retrieval latency optimization
- Vector database benchmarks
- LLM inference optimization techniques

---

### Future Work

1. **Power Efficiency Analysis**
   - Measure power consumption on both platforms
   - Calculate performance-per-watt metrics
   - Evaluate total cost of ownership (TCO)

2. **Quantization Impact**
   - Test INT8/INT4 quantization on both platforms
   - Compare accuracy vs performance trade-offs
   - Evaluate ARM's INT8 acceleration capabilities

3. **Batch Inference**
   - Test batch processing performance
   - Evaluate throughput vs latency trade-offs
   - Compare GPU batch efficiency

4. **Multi-GPU Scaling** (x86)
   - Test performance with multiple GPUs
   - Evaluate scaling efficiency
   - Compare to ARM multi-chip modules

5. **Real-Time Inference**
   - Test streaming response generation
   - Evaluate time-to-first-token (TTFT)
   - Compare responsiveness on both platforms

---

## 🔧 Development & Contribution

### Tools & Technologies

**Languages:**
- Python 3.11+

**Frameworks:**
- Ollama (LLM inference)
- Gradio (web interface, optional)
- psutil (system profiling)
- matplotlib/seaborn (visualization)

**Infrastructure:**
- Git (version control)
- WSL2 (x86 Linux environment)
- macOS (ARM native environment)

### Dependencies

See requirements.txt for complete list.

**Key Dependencies:**
- `psutil` — System metrics
- `requests` — Ollama API client
- `numpy`, `pandas` — Data analysis
- `matplotlib`, `seaborn` — Visualization
- `scipy` — Statistical tests

---

## 📞 Contact

**Author:** Yan-Bo Chen  
**Email:** [Your Email]  
**GitHub:** [Your GitHub Profile]

**Project Repository:** [GitHub Link]

---

## 📄 License

This project is developed for academic purposes as part of CS5600 Computer Systems at Northeastern University.

The Medical RAG system uses the Llama 3.2 model under Meta's Community License Agreement.

---

## ⚠️ Disclaimers

### Medical AI System

🚨 **This Medical RAG system is for educational and research purposes only.**

- **Not a substitute for professional medical advice**
- **Not for use in actual medical emergencies**
- **Always consult qualified healthcare professionals**
- **Verify all information with authoritative medical sources**

### Performance Results

- Results are specific to the tested hardware configurations
- Performance may vary with different:
  - Model versions
  - Quantization settings
  - System load
  - Temperature/thermal throttling
- Use results as relative comparison, not absolute benchmarks

---

## 🙏 Acknowledgments

- **Course Staff:** CS5600 teaching team for guidance and support
- **Meta AI:** Llama 3.2 model and community license
- **Ollama Team:** Excellent local LLM inference platform
- **Medical Data Sources:** Curated emergency medicine guidelines

---

## 📈 Project Status

**Current Phase:** Paper Writing & Final Polish  
**Completion:** ~95%

**Milestones:**
- ✅ ARM data collection complete (500+ queries)
- ✅ x86 data collection complete (500+ queries)
- ✅ Cross-platform analysis complete
- ✅ Advanced visualizations (p95/p99, CDF, violin, P/E-cores)
- ✅ P-cores vs E-cores heterogeneous core analysis
- 🔄 Final paper writing in progress

**Key Findings:**
- GPU speedup: **4.6×** (median), **4.9×** (p95), **5.3×** (p99)
- ARM P-cores handle **98.5%** of LLM inference workload
- Cardio queries show **21.2%** E-core utilization (14× higher than others)

---

**Last Updated:** December 6, 2025  
**Version:** 2.0.0
