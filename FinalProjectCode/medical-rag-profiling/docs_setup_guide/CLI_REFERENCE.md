# CLI Reference & Data Integration Guide

**Author:** Yan-Bo Chen  
**Project:** Medical RAG Workload Characterization on ARM and x86  
**Last Updated:** November 21, 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [CLI Command Reference](#cli-command-reference)
4. [Complete Workflow: ARM + x86 Data Integration](#complete-workflow-arm--x86-data-integration)
5. [Directory Structure](#directory-structure)
6. [Data Transfer Methods](#data-transfer-methods)
7. [Troubleshooting](#troubleshooting)
8. [Appendix: Command Cheat Sheet](#appendix-command-cheat-sheet)

---

## 🎯 Overview

`medrag.py` is a unified command-line interface (CLI) for running Medical RAG profiling experiments on both **ARM (M2 Pro, CPU-only)** and **x86 (Intel + RTX 4090, GPU-accelerated)** architectures.

### Key Features

- ✅ **Automatic architecture detection** (ARM vs x86)
- ✅ **Standardized output directories** (`results/ARM_*`, `results/x86_*`)
- ✅ **Batch experiment execution** (run multiple datasets sequentially)
- ✅ **Cross-platform comparison** (ARM vs x86 performance analysis)
- ✅ **Automated report generation** (Markdown, CSV, LaTeX tables)
- ✅ **Publication-ready visualizations** (300 DPI, multi-panel figures)

### Supported Commands

| Command | Purpose | Typical Usage |
|---------|---------|---------------|
| `run` | Run a single experiment | `./medrag.py run --dataset 100 --runs 5` |
| `monitor` | Real-time experiment monitoring | `./medrag.py monitor --output test_100x5` |
| `analyze` | Analyze experiment results | `./medrag.py analyze --output results/ARM_100` |
| `visualize` | Generate visualizations | `./medrag.py visualize --output results/ARM_100` |
| `batch` | Run multiple experiments | `./medrag.py batch --all` |
| `compare` | Compare ARM vs x86 | `./medrag.py compare --dataset 100` |
| `report` | Generate summary reports | `./medrag.py report --all` |
| `latex` | Generate LaTeX tables | `./medrag.py latex --all` |

---

## 🚀 Quick Start

### Prerequisites

**On ARM (MacBook M2 Pro):**
```bash
cd FinalProjectCode/medical-rag-profiling
source venv_cs5600Project/bin/activate
ollama serve  # In a separate terminal
```

**On x86 (Lab Workstation):**
```bash
cd medical-rag-profiling
source venv_x86/bin/activate
ollama serve  # In WSL, not PowerShell
```

---

### Run Your First Experiment

**Small test (10 queries × 1 run):**
```bash
./medrag.py run --dataset 10 --runs 1
```

**Production experiment (100 queries × 5 runs):**
```bash
./medrag.py run --dataset 100 --runs 5
```

**Output location:**
- On ARM: `results/ARM_100/`
- On x86: `results/x86_100/`

---

### Run All Experiments (Batch Mode)

**Most common use case:**
```bash
./medrag.py batch --all
```

**This will run:**
- 25 queries × 5 runs
- 100 queries × 5 runs
- cardio queries × 5 runs
- infection queries × 5 runs
- trauma queries × 5 runs

**Expected time:**
- ARM (CPU-only): ~4-6 hours
- x86 (GPU-accelerated): ~2-3 hours

---

## 📖 CLI Command Reference

### 1. `run` — Run a Single Experiment

**Syntax:**
```bash
./medrag.py run --dataset <name> --runs <number> [--model <model>] [--prefix <output_dir>]
```

**Arguments:**
- `--dataset`: Dataset name (required)
  - `10`, `25`, `100`: General medical queries
  - `cardio`, `infection`, `trauma`: Category-specific queries
- `--runs`: Number of runs per query (default: 1)
- `--model`: Model name (default: `llama3.2-cpu`)
- `--prefix`: Custom output directory prefix (optional)

**Examples:**
```bash
# Run 100 queries, 5 runs each
./medrag.py run --dataset 100 --runs 5

# Run cardio queries, 5 runs each
./medrag.py run --dataset cardio --runs 5

# Custom output directory
./medrag.py run --dataset 100 --runs 5 --prefix my_experiment
```

**Output Structure:**
```
results/
  └── ARM_100/  (or x86_100/)
      ├── query_000_run_00.json
      ├── query_000_run_01.json
      ├── ...
      ├── query_099_run_04.json
      ├── system_info.json
      └── experiment_log.txt
```

---

### 2. `batch` — Run Multiple Experiments Sequentially

**Syntax:**
```bash
./medrag.py batch {--all | --categories} [--model <model>]
```

**Arguments:**
- `--all`: Run all experiments (25, 100, cardio, infection, trauma)
- `--categories`: Run only category experiments (cardio, infection, trauma)
- `--model`: Model name (default: `llama3.2-cpu`)

**Examples:**
```bash
# Run all experiments
./medrag.py batch --all

# Run only category experiments
./medrag.py batch --categories
```

**Progress Tracking:**
- The CLI will display progress for each dataset
- Estimated time for completion
- Summary of generated datasets at the end

**Background Execution (Recommended):**
```bash
# Run in background with logging
nohup ./medrag.py batch --all > batch_log.txt 2>&1 &

# Monitor progress
tail -f batch_log.txt
```

---

### 3. `analyze` — Analyze Experiment Results

**Syntax:**
```bash
./medrag.py analyze --output <directory>
```

**Arguments:**
- `--output`: Output directory to analyze (required)

**Examples:**
```bash
# Analyze ARM 100-query experiment
./medrag.py analyze --output results/ARM_100

# Analyze x86 cardio experiment
./medrag.py analyze --output results/x86_cardio
```

**Output Example:**
```
================================================================================
                MEDICAL RAG PROFILING - ANALYSIS REPORT                      
================================================================================

📁 Dataset: results/ARM_100
📊 Total Queries Analyzed: 500

⏱️  LATENCY ANALYSIS (seconds)
--------------------------------------------------------------------------------
   Minimum:         8.45s
   Maximum:        18.32s
   Median:         12.34s
   Mean:           12.56s
   Std Deviation:   2.15s

⚡ CPU USAGE ANALYSIS (Timeline - All Cores Total %)
--------------------------------------------------------------------------------
   Peak Load (Mean):       823.4%
   Average Load (Mean):    543.2%
   Per-Core Average:       45.3%
   Interpretation:         ~5.4 cores actively running on average

💾 MEMORY USAGE ANALYSIS (GB)
--------------------------------------------------------------------------------
   Minimum:    3.12 GB
   Maximum:    3.58 GB
   Mean:       3.35 GB
   Range:      0.46 GB
   ✓ Memory stable (range < 0.5 GB) - No memory leaks detected
```

---

### 4. `visualize` — Generate Visualizations

**Syntax:**
```bash
./medrag.py visualize --output <directory>
```

**Arguments:**
- `--output`: Output directory to visualize (required)

**Examples:**
```bash
# Generate all visualizations for ARM 100-query experiment
./medrag.py visualize --output results/ARM_100
```

**Generated Files (saved in the output directory):**

1. **`cpu_heatmap.png`** — CPU core utilization heatmap
   - Shows per-core CPU usage over time
   - Distinguishes P-cores vs E-cores (ARM only)

2. **`latency_distribution.png`** — Latency distribution histogram
   - Shows distribution of query response times
   - Marks median and mean values

3. **`memory_timeline.png`** — Memory usage timeline
   - Tracks memory usage across all queries
   - Useful for detecting memory leaks

4. **`core_utilization_comparison.png`** — Core utilization comparison
   - ARM: P-cores vs E-cores average usage
   - x86: All cores average usage

5. **`cpu_timeline_aggregate.png`** — Aggregated CPU timeline
   - Overlays all query CPU timelines
   - Red line indicates average usage

**Chart Properties:**
- 300 DPI resolution (publication-ready)
- Professional color schemes
- Automatic adaptation to ARM/x86 differences

---

### 5. `compare` — ARM vs x86 Performance Comparison

**Syntax:**
```bash
./medrag.py compare {--dataset <name> | --all}
```

**Arguments:**
- `--dataset <name>`: Compare a specific dataset
- `--all`: Compare all datasets

**Examples:**
```bash
# Compare 100-query experiments
./medrag.py compare --dataset 100

# Compare all datasets
./medrag.py compare --all
```

**Prerequisites:**
- Both ARM and x86 data must exist:
  - `results/ARM_100/` **AND** `results/x86_100/`

**Generated Files (saved in `final_report/`):**

**`comparison_ARM_vs_x86_<dataset>.png`** — Multi-panel comparison figure
- **Panel 1:** Latency distribution (box plots)
  - Shows median, quartiles, outliers
  - Displays speedup annotation (e.g., "Speedup: 1.44×")
- **Panel 2:** CPU peak utilization (bar chart with error bars)
- **Panel 3:** CPU average utilization (bar chart with error bars)
- **Panel 4:** Memory footprint (bar chart with error bars)

**Example Interpretation:**
```
If ARM median latency = 12.3s, x86 median latency = 8.5s
→ Speedup = 12.3 / 8.5 = 1.45×
→ "x86 is 1.45× faster than ARM"
```

---

### 6. `report` — Generate Summary Reports

**Syntax:**
```bash
./medrag.py report {--dataset <name> | --all}
```

**Arguments:**
- `--dataset <name>`: Generate report for a specific dataset
- `--all`: Generate reports for all datasets

**Examples:**
```bash
# Generate report for 100-query experiment
./medrag.py report --dataset 100

# Generate reports for all datasets
./medrag.py report --all
```

**Prerequisites:**
- Both ARM and x86 data must exist

**Generated Files (saved in `final_report/`):**

1. **`summary_ARM_vs_x86_<dataset>.md`** — Markdown report
   - Complete statistical comparison table
   - Key findings summary
   - Deployment recommendations

2. **`summary_ARM_vs_x86_<dataset>.csv`** — CSV report
   - Can be imported into Excel/Google Sheets
   - Suitable for further analysis in Python/R

**Markdown Report Example:**
```markdown
# Performance Comparison: ARM vs x86 (100 Queries)

## Summary Statistics

| Metric                     | ARM M2 Pro | x86 + RTX 4090 | Speedup |
|---------------------------|------------|----------------|---------|
| **Latency (Median)**      | 12.34s     | 8.56s          | 1.44×   |
| **CPU Peak (Total %)**    | 890.2%     | 1245.6%        | -       |
| **Memory Peak (GB)**      | 3.58       | 4.52           | -       |

## Key Findings

- x86 + RTX 4090 is **1.44× faster** than ARM M2 Pro
- ARM shows 20% lower memory usage
```

**CSV Report Example:**
```csv
Metric,ARM_M2_Pro,x86_RTX4090,Speedup
Latency_Median_s,12.34,8.56,1.44
CPU_Peak_Percent,890.2,1245.6,
Memory_Peak_GB,3.58,4.52,
```

---

### 7. `latex` — Generate LaTeX Tables

**Syntax:**
```bash
./medrag.py latex {--dataset <name> | --all}
```

**Arguments:**
- `--dataset <name>`: Generate LaTeX table for a specific dataset
- `--all`: Generate LaTeX tables for all datasets

**Examples:**
```bash
# Generate LaTeX table for 100-query experiment
./medrag.py latex --dataset 100

# Generate LaTeX tables for all datasets
./medrag.py latex --all
```

**Prerequisites:**
- Both ARM and x86 data must exist

**Generated Files (saved in `final_report/`):**
- `table_<dataset>.tex`

**LaTeX Table Example:**
```latex
\begin{table}[htbp]
\centering
\caption{Performance Comparison: ARM M2 Pro vs x86 + RTX 4090 (100 Queries)}
\label{tab:perf_comparison_100}
\begin{tabular}{lrrr}
\toprule
\textbf{Metric} & \textbf{ARM M2 Pro} & \textbf{x86 + RTX 4090} & \textbf{Speedup} \\
\midrule
\multicolumn{4}{l}{\textit{Latency (seconds)}} \\
\quad Median       & 12.34 & 8.56  & 1.44$\times$ \\
\quad Mean         & 12.56 & 8.78  & 1.43$\times$ \\
\bottomrule
\end{tabular}
\end{table}
```

**Usage in LaTeX Paper:**
```latex
% In preamble
\usepackage{booktabs}

% In document
\input{final_report/table_100.tex}
```

---

## 🔄 Complete Workflow: ARM + x86 Data Integration

This section provides a **step-by-step guide** for collecting data on both platforms and integrating them for comparative analysis.

### Overview of Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Data Collection on ARM                           │
│  ├─ Run: ./medrag.py batch --all                          │
│  └─ Output: results/ARM_25, ARM_100, ARM_cardio, etc.     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: Data Collection on x86                           │
│  ├─ Run: ./medrag.py batch --all                          │
│  └─ Output: results/x86_25, x86_100, x86_cardio, etc.     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: Transfer x86 Data to ARM                         │
│  ├─ Package: tar -czf x86_results.tar.gz results/x86_*    │
│  ├─ Transfer: scp / OneDrive / USB                        │
│  └─ Extract: tar -xzf x86_results.tar.gz                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 4: Unified Analysis on ARM                          │
│  ├─ Compare: ./medrag.py compare --all                    │
│  ├─ Report:  ./medrag.py report --all                     │
│  └─ LaTeX:   ./medrag.py latex --all                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 5: Paper Writing                                    │
│  ├─ Use figures: final_report/comparison_*.png            │
│  ├─ Use tables:  final_report/table_*.tex                 │
│  └─ Cite data:   final_report/summary_*.md                │
└─────────────────────────────────────────────────────────────┘
```

---

### Phase 1: Data Collection on ARM (MacBook M2 Pro)

**Environment Setup:**
```bash
cd ~/Desktop/FinalProjectCode/medical-rag-profiling
source venv_cs5600Project/bin/activate
```

**Terminal 1 — Start Ollama Server:**
```bash
ollama serve
```

**Terminal 2 — Run All Experiments:**
```bash
# Run in background with logging
nohup ./medrag.py batch --all > batch_arm_log.txt 2>&1 &

# Monitor progress
tail -f batch_arm_log.txt
```

**Expected Duration:**
- ~4-6 hours (CPU-only)

**Expected Output:**
```
results/
├── ARM_25/
│   ├── query_000_run_00.json
│   ├── ...
│   └── system_info.json
├── ARM_100/
├── ARM_cardio/
├── ARM_infection/
└── ARM_trauma/
```

**Validation Checklist:**
```bash
# Check file counts (example for 25 queries × 5 runs)
ls results/ARM_25/query_*.json | wc -l
# Expected: 125 files

# Check JSON health
cat results/ARM_25/query_000_run_00.json | grep '"success"'
# Expected: "success": true

# Check system info
cat results/ARM_25/system_info.json
# Should show ARM architecture, M2 Pro details
```

---

### Phase 2: Data Collection on x86 (Lab Workstation)

**Environment Setup:**
```bash
# In WSL (NOT PowerShell)
cd ~/medical-rag-profiling
source venv_x86/bin/activate
```

**Terminal 1 — Start Ollama Server (in WSL):**
```bash
# IMPORTANT: Run in WSL, NOT Windows PowerShell
ollama serve
```

**Terminal 2 — Run All Experiments:**
```bash
# Run in background with logging
nohup ./medrag.py batch --all > batch_x86_log.txt 2>&1 &

# Monitor progress
tail -f batch_x86_log.txt
```

**Expected Duration:**
- ~2-3 hours (GPU-accelerated)

**Expected Output:**
```
results/
├── x86_25/
├── x86_100/
├── x86_cardio/
├── x86_infection/
└── x86_trauma/
```

**Validation Checklist:**
```bash
# Check file counts
ls results/x86_100/query_*.json | wc -l
# Expected: 500 files (100 queries × 5 runs)

# Check GPU usage in logs
grep -i "gpu" results/x86_100/system_info.json
# Should show RTX 4090 details
```

---

### Phase 3: Transfer x86 Data to ARM

This is the **critical integration step** that merges data from both platforms.

#### Method 1: tar + scp (Recommended for Lab Network)

**Step 1: Package x86 Data (on x86 machine):**
```bash
cd ~/medical-rag-profiling

# Create compressed archive of all x86 results
tar -czf x86_results.tar.gz results/x86_*

# Verify archive size
ls -lh x86_results.tar.gz
# Expected: ~50-200 MB depending on dataset size
```

**Parameter Explanation:**
- `c` = create archive
- `z` = gzip compression
- `f` = specify filename
- `results/x86_*` = include all x86 result directories

**Step 2: Transfer to ARM (choose one method):**

**Option A: Direct scp (if both machines on same network):**
```bash
# On x86 machine
scp x86_results.tar.gz your_username@arm-macbook-ip:/path/to/FinalProjectCode/medical-rag-profiling/

# Example:
scp x86_results.tar.gz yanboc@192.168.1.100:~/Desktop/FinalProjectCode/medical-rag-profiling/
```

**Option B: Cloud Storage (OneDrive / Google Drive):**
```bash
# On x86 machine
cp x86_results.tar.gz /mnt/c/Users/YourName/OneDrive/

# On ARM machine (after OneDrive sync)
cp ~/OneDrive/x86_results.tar.gz ~/Desktop/FinalProjectCode/medical-rag-profiling/
```

**Option C: USB Drive:**
```bash
# On x86 machine
cp x86_results.tar.gz /media/usb_drive/

# On ARM machine
cp /Volumes/USB_DRIVE/x86_results.tar.gz ~/Desktop/FinalProjectCode/medical-rag-profiling/
```

**Step 3: Extract on ARM (on ARM machine):**
```bash
cd ~/Desktop/FinalProjectCode/medical-rag-profiling

# Extract x86 data
tar -xzf x86_results.tar.gz

# Verify extraction
ls results/
# Should now see both ARM_* and x86_* directories
```

**Expected Final Structure:**
```
results/
├── ARM_25/           ← From Phase 1
├── ARM_100/          ← From Phase 1
├── ARM_cardio/       ← From Phase 1
├── ARM_infection/    ← From Phase 1
├── ARM_trauma/       ← From Phase 1
├── x86_25/           ← From Phase 2 (transferred)
├── x86_100/          ← From Phase 2 (transferred)
├── x86_cardio/       ← From Phase 2 (transferred)
├── x86_infection/    ← From Phase 2 (transferred)
└── x86_trauma/       ← From Phase 2 (transferred)
```

---

#### Method 2: Manual Directory Renaming (If Prefix Fails)

If for some reason the architecture prefixes were not applied correctly during data collection, you can manually rename the directories:

**On x86 (if directories were named incorrectly):**
```bash
# If your x86 results were output as test_25x5, profiling_cardio, etc.
mv test_25x5 results/x86_25/
mv test_100x5 results/x86_100/
mv profiling_cardio results/x86_cardio/
mv profiling_infection results/x86_infection/
mv profiling_trauma results/x86_trauma/

# Then package and transfer
tar -czf x86_results.tar.gz results/x86_*
```

**⚠️ IMPORTANT:** This renaming is safe and does NOT affect data integrity. The architecture information is also stored inside `system_info.json` within each directory.

---

### Phase 4: Unified Analysis on ARM

Once both ARM and x86 data are in the same `results/` directory on the ARM machine, you can perform cross-platform analysis.

**Step 1: Verify Data Integrity:**
```bash
cd ~/Desktop/FinalProjectCode/medical-rag-profiling

# Check all required directories exist
ls results/
# Should show: ARM_25, ARM_100, ARM_cardio, ARM_infection, ARM_trauma
#              x86_25, x86_100, x86_cardio, x86_infection, x86_trauma

# Verify file counts match
ls results/ARM_100/query_*.json | wc -l
ls results/x86_100/query_*.json | wc -l
# Both should show 500 (100 queries × 5 runs)
```

**Step 2: Generate All Comparisons:**
```bash
# Compare all datasets
./medrag.py compare --all
```

**Output:**
```
final_report/
├── comparison_ARM_vs_x86_25.png
├── comparison_ARM_vs_x86_100.png
├── comparison_ARM_vs_x86_cardio.png
├── comparison_ARM_vs_x86_infection.png
└── comparison_ARM_vs_x86_trauma.png
```

**Step 3: Generate All Reports:**
```bash
# Generate Markdown and CSV reports
./medrag.py report --all
```

**Output:**
```
final_report/
├── summary_ARM_vs_x86_25.md
├── summary_ARM_vs_x86_25.csv
├── summary_ARM_vs_x86_100.md
├── summary_ARM_vs_x86_100.csv
├── summary_ARM_vs_x86_cardio.md
├── summary_ARM_vs_x86_cardio.csv
├── ...
```

**Step 4: Generate All LaTeX Tables:**
```bash
# Generate LaTeX tables for paper
./medrag.py latex --all
```

**Output:**
```
final_report/
├── table_25.tex
├── table_100.tex
├── table_cardio.tex
├── table_infection.tex
└── table_trauma.tex
```

**Step 5: Review Generated Files:**
```bash
# Open Markdown report
open final_report/summary_ARM_vs_x86_100.md

# View comparison figure
open final_report/comparison_ARM_vs_x86_100.png

# Check LaTeX table
cat final_report/table_100.tex
```

---

### Phase 5: Paper Writing

**Use Generated Figures in LaTeX:**
```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.9\textwidth]{final_report/comparison_ARM_vs_x86_100.png}
  \caption{Performance comparison between ARM M2 Pro (CPU-only) and x86 + RTX 4090 
           (GPU-accelerated) for 100 medical queries. The x86 configuration achieves 
           1.44× speedup in median latency while consuming higher memory resources.}
  \label{fig:arm_vs_x86_comparison}
\end{figure}
```

**Use Generated Tables in LaTeX:**
```latex
% In preamble
\usepackage{booktabs}

% In Results section
\input{final_report/table_100.tex}
```

**Cite Statistics from Markdown Reports:**
```latex
Our experiments show that the x86 + RTX 4090 configuration achieves a median latency 
of 8.56 seconds compared to 12.34 seconds on ARM M2 Pro, representing a 1.44× speedup. 
However, the ARM platform demonstrates 20\% lower memory footprint (3.58 GB vs 4.52 GB), 
making it more suitable for edge deployment scenarios.
```

---

## 📂 Directory Structure

### Standard Directory Layout

```
medical-rag-profiling/
├── medrag.py                    # Main CLI script
├── run_experiment.py            # Experiment runner
├── analyze_results.py           # Analysis script
├── visualize_results.py         # Visualization script
├── rag_wrapper.py               # RAG interface
├── profiling/                   # Profiling modules
│   ├── workload_profiler.py
│   └── __init__.py
├── queries/                     # Query datasets
│   ├── medical_queries_10.json
│   ├── medical_queries_25.json
│   ├── medical_queries_100.json
│   ├── cardio_queries.json
│   ├── infection_queries.json
│   └── trauma_queries.json
├── results/                     # Experiment results (gitignored)
│   ├── ARM_25/
│   ├── ARM_100/
│   ├── ARM_cardio/
│   ├── ARM_infection/
│   ├── ARM_trauma/
│   ├── x86_25/
│   ├── x86_100/
│   ├── x86_cardio/
│   ├── x86_infection/
│   └── x86_trauma/
├── final_report/                # Analysis outputs (gitignored)
│   ├── comparison_ARM_vs_x86_*.png
│   ├── summary_ARM_vs_x86_*.md
│   ├── summary_ARM_vs_x86_*.csv
│   └── table_*.tex
├── venv_cs5600Project/          # ARM virtual environment
├── venv_x86/                    # x86 virtual environment
└── requirements.txt
```

### Individual Experiment Directory Structure

```
results/ARM_100/
├── query_000_run_00.json        # Query 0, Run 0
├── query_000_run_01.json        # Query 0, Run 1
├── ...
├── query_099_run_04.json        # Query 99, Run 4
├── system_info.json             # Platform information
├── experiment_log.txt           # Execution log
├── cpu_heatmap.png              # Generated by visualize
├── latency_distribution.png     # Generated by visualize
├── memory_timeline.png          # Generated by visualize
├── core_utilization_comparison.png
└── cpu_timeline_aggregate.png
```

### JSON Data Format (Individual Query Result)

```json
{
  "metadata": {
    "query_id": 42,
    "run_id": 3,
    "timestamp": "2025-11-21T14:30:15.123456",
    "query_text": "What are the symptoms of myocardial infarction?",
    "success": true,
    "error": null
  },
  "latency": {
    "total_ms": 12456.78,
    "retrieval_ms": 234.56,
    "generation_ms": 12000.12,
    "overhead_ms": 222.10
  },
  "cpu": {
    "peak_percent": 875.3,
    "average_percent": 543.2,
    "per_core": [85.2, 78.3, 65.1, 54.2, 45.6, 38.9, ...],
    "p_cores_avg": 82.4,
    "e_cores_avg": 45.6
  },
  "memory": {
    "used_gb": 3.45,
    "percent": 21.5,
    "available_gb": 12.55
  },
  "timeline": [
    {"t": 0.0, "cpu_total": 234.5, "cpu_cores": [...], "mem_gb": 3.2},
    {"t": 0.5, "cpu_total": 567.8, "cpu_cores": [...], "mem_gb": 3.4},
    ...
  ],
  "timeline_summary": {
    "cpu_peak_from_timeline": 890.5,
    "cpu_avg_from_timeline": 550.2,
    "memory_peak_from_timeline": 3.5,
    "num_samples": 45
  },
  "response": {
    "length_chars": 1234,
    "content": "Symptoms of myocardial infarction include..."
  }
}
```

---

## 🔧 Data Transfer Methods

### Comparison of Transfer Methods

| Method | Speed | Reliability | Setup Complexity | Use Case |
|--------|-------|-------------|------------------|----------|
| **scp** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Same network, tech-savvy users |
| **OneDrive** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Different networks, auto-sync |
| **Google Drive** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Different networks, web interface |
| **USB Drive** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | No network required |
| **rsync** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | Advanced users, incremental sync |

---

### Detailed Transfer Instructions

#### Method 1: scp (Secure Copy)

**Advantages:**
- Fast, direct network transfer
- Preserves file permissions and timestamps
- Secure (encrypted)

**Requirements:**
- Both machines on same network (or VPN)
- SSH enabled on ARM machine

**Steps:**

**Enable SSH on ARM (macOS):**
```bash
# On ARM Mac
sudo systemsetup -setremotelogin on

# Get your IP address
ipconfig getifaddr en0
# Example output: 192.168.1.100
```

**Transfer from x86 to ARM:**
```bash
# On x86 machine
scp x86_results.tar.gz username@192.168.1.100:~/Desktop/FinalProjectCode/medical-rag-profiling/

# Enter password when prompted
```

**Alternative: Use SSH Key (No Password):**
```bash
# On x86 machine (one-time setup)
ssh-keygen -t rsa -b 4096
ssh-copy-id username@192.168.1.100

# Future transfers won't require password
scp x86_results.tar.gz username@192.168.1.100:~/Desktop/FinalProjectCode/medical-rag-profiling/
```

---

#### Method 2: OneDrive / Google Drive

**Advantages:**
- No network configuration needed
- Works across different networks
- Automatic cloud backup

**Disadvantages:**
- Slower than direct transfer
- Requires cloud storage quota

**Steps:**

**On x86 (Windows WSL):**
```bash
# Copy to Windows OneDrive folder
cp x86_results.tar.gz /mnt/c/Users/YourName/OneDrive/CS5600_Project/

# Wait for OneDrive to sync (check status icon)
```

**On ARM (macOS):**
```bash
# After OneDrive sync completes
cp ~/OneDrive/CS5600_Project/x86_results.tar.gz ~/Desktop/FinalProjectCode/medical-rag-profiling/

# Extract
cd ~/Desktop/FinalProjectCode/medical-rag-profiling/
tar -xzf x86_results.tar.gz
```

---

#### Method 3: USB Drive

**Advantages:**
- No network required
- Fast transfer speed
- Completely offline

**Disadvantages:**
- Requires physical access to both machines

**Steps:**

**On x86:**
```bash
# Plug in USB drive

# In WSL, mount the drive (if not auto-mounted)
sudo mkdir -p /mnt/usb
sudo mount /dev/sdb1 /mnt/usb

# Copy file
cp x86_results.tar.gz /mnt/usb/

# Safely eject
sudo umount /mnt/usb
```

**On ARM:**
```bash
# Plug in USB drive (auto-mounts to /Volumes/)

# Copy from USB
cp /Volumes/USB_DRIVE/x86_results.tar.gz ~/Desktop/FinalProjectCode/medical-rag-profiling/

# Extract
cd ~/Desktop/FinalProjectCode/medical-rag-profiling/
tar -xzf x86_results.tar.gz

# Eject USB (via Finder or command)
diskutil eject /Volumes/USB_DRIVE
```

---

#### Method 4: rsync (Advanced)

**Advantages:**
- Incremental transfer (only changed files)
- Resume capability
- Bandwidth control

**Use Case:**
- Repeatedly transferring updated datasets
- Large datasets with minor changes

**Steps:**

**Initial Transfer:**
```bash
# On x86 machine
rsync -avz --progress results/x86_* username@192.168.1.100:~/Desktop/FinalProjectCode/medical-rag-profiling/results/
```

**Incremental Transfer (only new/changed files):**
```bash
# On x86 machine (after running more experiments)
rsync -avz --progress results/x86_* username@192.168.1.100:~/Desktop/FinalProjectCode/medical-rag-profiling/results/
```

**Parameter Explanation:**
- `-a` = archive mode (preserves permissions, timestamps)
- `-v` = verbose (show progress)
- `-z` = compress during transfer
- `--progress` = show transfer progress

---

## 🔍 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Architecture Prefix Not Applied

**Symptom:**
```bash
# Output directories lack ARM_ or x86_ prefix
results/
├── test_25x5/        # Should be ARM_25 or x86_25
├── test_100x5/       # Should be ARM_100 or x86_100
└── profiling_cardio/ # Should be ARM_cardio or x86_cardio
```

**Cause:**
- Using old version of `medrag.py`
- `detect_arch()` not being called
- Manual `--prefix` override

**Solution:**
```bash
# Manually rename directories (safe operation)
mv test_25x5 results/ARM_25/
mv test_100x5 results/ARM_100/
mv profiling_cardio results/ARM_cardio/
mv profiling_infection results/ARM_infection/
mv profiling_trauma results/ARM_trauma/

# Verify system_info.json still has correct architecture info
cat results/ARM_100/system_info.json | grep architecture
```

---

#### Issue 2: Compare Command Fails

**Symptom:**
```bash
./medrag.py compare --dataset 100
# Output: "⚠️  Warning: ARM data not found: results/ARM_100"
# or: "⚠️  Warning: x86 data not found: results/x86_100"
```

**Cause:**
- Missing data from one platform
- Incorrect directory names

**Solution:**
```bash
# Check which directories exist
ls results/

# If only ARM data exists
# → You need to run experiments on x86 and transfer data

# If directories are named incorrectly
# → Rename as shown in Issue 1

# If x86 data wasn't transferred
# → Follow Phase 3 instructions to transfer data
```

---

#### Issue 3: Incomplete Data Transfer

**Symptom:**
```bash
# After extracting x86_results.tar.gz
ls results/x86_100/query_*.json | wc -l
# Expected: 500, Actual: 245 (incomplete)
```

**Cause:**
- Transfer interrupted
- Insufficient disk space during extraction
- Corrupted archive

**Solution:**
```bash
# Verify archive integrity
tar -tzf x86_results.tar.gz | wc -l
# Should show all expected files

# Check disk space
df -h
# Ensure sufficient space

# Re-transfer if corrupted
# Use md5/sha256 checksum to verify

# On x86:
sha256sum x86_results.tar.gz > x86_results.sha256

# On ARM:
sha256sum -c x86_results.sha256
# Should output: "x86_results.tar.gz: OK"
```

---

#### Issue 4: Permission Errors During Extraction

**Symptom:**
```bash
tar -xzf x86_results.tar.gz
# tar: results/x86_100/query_000_run_00.json: Cannot open: Permission denied
```

**Cause:**
- Extracting to directory without write permissions
- Running as wrong user

**Solution:**
```bash
# Check permissions
ls -ld results/

# Change ownership if needed
sudo chown -R $USER:$USER results/

# Or extract to a different location
mkdir ~/temp_extract
cd ~/temp_extract
tar -xzf ~/Desktop/FinalProjectCode/medical-rag-profiling/x86_results.tar.gz
mv results/x86_* ~/Desktop/FinalProjectCode/medical-rag-profiling/results/
```

---

#### Issue 5: Virtual Environment Not Activated

**Symptom:**
```bash
./medrag.py run --dataset 100 --runs 5
# ModuleNotFoundError: No module named 'psutil'
```

**Cause:**
- Virtual environment not activated
- Packages installed outside venv

**Solution:**
```bash
# ARM:
source venv_cs5600Project/bin/activate

# x86:
source venv_x86/bin/activate

# Verify activation
which python
# Should show path inside venv directory

# Reinstall packages if needed
pip install -r requirements.txt
```

---

#### Issue 6: Ollama Model Not Found in WSL

**Symptom:**
```bash
# In WSL
ollama list
# No models shown (empty list)

# In PowerShell
ollama list
# Models are present
```

**Cause:**
- Model downloaded in PowerShell, but WSL uses separate `~/.ollama/models` path

**Solution:**
```bash
# In WSL (NOT PowerShell)
ollama pull llama3.2:3b

# Verify
ollama list
# Should now show the model
```

---

## 📚 Appendix: Command Cheat Sheet

### Quick Reference: Essential Commands

**Data Collection:**
```bash
# Run all experiments (most common)
./medrag.py batch --all

# Run single experiment
./medrag.py run --dataset 100 --runs 5

# Run in background with logging
nohup ./medrag.py batch --all > batch_log.txt 2>&1 &
```

**Single-Platform Analysis:**
```bash
# Analyze and visualize ARM data
./medrag.py analyze --output results/ARM_100
./medrag.py visualize --output results/ARM_100

# Analyze and visualize x86 data
./medrag.py analyze --output results/x86_100
./medrag.py visualize --output results/x86_100
```

**Cross-Platform Comparison:**
```bash
# Compare all datasets
./medrag.py compare --all
./medrag.py report --all
./medrag.py latex --all

# Compare specific dataset
./medrag.py compare --dataset 100
./medrag.py report --dataset 100
./medrag.py latex --dataset 100
```

**Data Transfer:**
```bash
# Package on x86
tar -czf x86_results.tar.gz results/x86_*

# Transfer via scp
scp x86_results.tar.gz user@arm-ip:~/path/

# Extract on ARM
tar -xzf x86_results.tar.gz
```

**Validation:**
```bash
# Check file counts
ls results/ARM_100/query_*.json | wc -l

# Verify JSON integrity
cat results/ARM_100/query_000_run_00.json | grep '"success"'

# Check architecture
cat results/ARM_100/system_info.json | grep architecture
```

---

### Complete End-to-End Example

**Day 1 (Monday) — ARM Data Collection:**
```bash
# On MacBook M2 Pro
cd ~/Desktop/FinalProjectCode/medical-rag-profiling
source venv_cs5600Project/bin/activate

# Terminal 1
ollama serve

# Terminal 2
nohup ./medrag.py batch --all > batch_arm.log 2>&1 &
tail -f batch_arm.log

# Let run overnight (~4-6 hours)
```

**Day 2 (Tuesday) — x86 Data Collection:**
```bash
# On Lab Workstation (WSL)
cd ~/medical-rag-profiling
source venv_x86/bin/activate

# Terminal 1
ollama serve

# Terminal 2
nohup ./medrag.py batch --all > batch_x86.log 2>&1 &
tail -f batch_x86.log

# Let run (~2-3 hours)
```

**Day 2 (Tuesday Evening) — Transfer Data:**
```bash
# On Lab Workstation
tar -czf x86_results.tar.gz results/x86_*
cp x86_results.tar.gz /mnt/c/Users/YourName/OneDrive/CS5600/

# On MacBook (after OneDrive sync)
cd ~/Desktop/FinalProjectCode/medical-rag-profiling
cp ~/OneDrive/CS5600/x86_results.tar.gz .
tar -xzf x86_results.tar.gz
```

**Day 3 (Wednesday) — Analysis & Paper Writing:**
```bash
# On MacBook M2 Pro
cd ~/Desktop/FinalProjectCode/medical-rag-profiling
source venv_cs5600Project/bin/activate

# Generate all comparisons
./medrag.py compare --all
./medrag.py report --all
./medrag.py latex --all

# Review results
open final_report/comparison_ARM_vs_x86_100.png
open final_report/summary_ARM_vs_x86_100.md
cat final_report/table_100.tex

# Start writing paper using generated figures and tables
```

---

## 🎓 Summary

This document provides a complete reference for using `medrag.py` to:

1. ✅ **Run experiments** on both ARM and x86 architectures
2. ✅ **Transfer data** between platforms using multiple methods
3. ✅ **Integrate data** into a unified directory structure
4. ✅ **Compare performance** across architectures
5. ✅ **Generate reports** in multiple formats (Markdown, CSV, LaTeX)
6. ✅ **Create visualizations** for publication

**Key Takeaways:**
- Architecture detection is automatic (ARM vs x86)
- All output directories follow standardized naming: `results/{ARM,x86}_<dataset>`
- Cross-platform commands (`compare`, `report`, `latex`) require both ARM and x86 data
- Data transfer is straightforward with tar + your preferred method (scp, cloud, USB)
- All analysis can be performed on a single machine (typically ARM) after data integration

**For more details:**
- ARM-specific setup: ARM_SETUP.md
- x86-specific setup: X86_SETUP.md
- Data analysis methodology: ANALYSIS_GUIDE.md

---

**Last Updated:** November 21, 2025  
**Contact:** Yan-Bo Chen  
**Project Repository:** CS5600 Final Project — Medical RAG Workload Characterization

