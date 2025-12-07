# X86 Setup Guide (Intel + RTX 4090)

Author: Yan-Bo Chen  
Device: University Lab Workstation (x86_64, Linux, RTX 4090)  
Purpose: Medical RAG Profiling Experiments  
Last Updated: 2025-11-20

---

# 🧪 1. Pre-Experiment 30-Second Checklist (x86)

### ✔️ (A) Verify you're in the correct directory
```bash
pwd
```

### ✔️ (B) Check if experiment package exists
```bash
ls medical-rag-profiling
```

### ✔️ (C) Activate virtual environment
```bash
source venv_profiling/bin/activate
```

### ✔️ (D) Verify model is downloaded in WSL (not PowerShell)
```bash
# IMPORTANT: Execute in WSL, NOT in Windows PowerShell
ollama pull llama3.2:3b
ollama list  # Confirm llama3.2:3b is present
```

**Reason**: Models are stored in `~/.ollama/models` (WSL Linux path).  
Downloading via PowerShell will cause WSL to fail to access the model.

### ✔️ (E) Check Ollama availability
```bash
ollama list
ollama serve   # Run in Terminal 1
```

### ✔️ (F) Close unnecessary GPU usage (e.g., browser, VS Code)

### ✔️ (G) Start monitoring (Terminal 3)
```bash
htop
# OR for GPU monitoring:
watch -n 1 nvidia-smi
```

---

# 📂 2. Directory Structure (x86)

```
medical-rag-profiling/
├── profiling/
├── run_experiment.py
├── rag_wrapper.py
├── queries/
├── profiling_data/
├── logs/
└── checkpoints/
```

---

# ⚙️ 3. Environment Setup (x86)

## 📌 Step 0: Download Ollama Model (Execute in WSL)

⚠️ **CRITICAL**: Must download within WSL, NOT in Windows PowerShell

```bash
ollama pull llama3.2:3b
```

**GPU + CUDA Configuration**:
- x86 workstation uses RTX 4090 + CUDA
- Ollama automatically detects GPU acceleration
- **DO NOT** set `num_gpu=0` (that's for ARM CPU-only mode)
- **DO NOT** specify `num_threads` (GPU mode doesn't use CPU threads)

---

## 📌 Step 1: Navigate to working directory
```bash
cd ~/medical-rag-profiling
```

## 📌 Step 2: Activate virtual environment
```bash
source venv_profiling/bin/activate
```

## 📌 Step 3: Test profiler import
```bash
python -c "import profiling; print('✓ profiling module OK')"
```

## 📌 Step 4: Start Ollama (Terminal 1)
```bash
ollama serve
```

---

# 🔥 4. Three-Terminal Configuration (x86)

### 🖥 Terminal 1 — Ollama Server
```bash
ollama serve
```

### 🖥 Terminal 2 — Experiment Runner
```bash
source venv_profiling/bin/activate
python run_experiment.py --queries queries/medical_queries_100.json --runs 5
```

### 🖥 Terminal 3 — System Monitoring (htop Guide)

```bash
htop
```

**Key Metrics to Monitor**:

1. **CPU Core Usage**:
   - Individual core fluctuations are normal
   - GPU mode consumes minimal CPU resources

2. **Memory Usage**:
   - Orange (cache/buffer) = reclaimable
   - Green (active) = actual usage
   - 5–7% usage = normal

3. **Load Average** (three numbers):
   - First: Past 1 minute
   - Second: Past 5 minutes
   - Third: Past 15 minutes
   - Load < 10 (on 16-core / 32 threads system) = healthy system

4. **Tasks / Threads**:
   - Example: "38, 59 thr" = normal
   - Indicates 38 active processes, 59 threads

**GPU Monitoring** (alternative):
```bash
watch -n 1 nvidia-smi
```

---

# 🚀 5. Running Experiments (x86)

### 📌 Small Test (10 queries × 5 runs)
```bash
python run_experiment.py --queries queries/medical_queries_10.json --runs 5
```

### 📌 Medium Test (25 queries × 5 runs)
```bash
python run_experiment.py --queries queries/medical_queries_25.json --runs 5
```

### 📌 Full Experiment (100 queries × 5 runs)
```bash
python run_experiment.py --queries queries/medical_queries_100.json --runs 5
```

---

# 📊 6. Post-Experiment Validation

### ✔ (1) File Count Verification (Example: 25×5)

```bash
ls profiling_data | wc -l
```

Expected output:
- JSON files = 125
- TXT files = 125
- experiment_config.json = 1
- system_info.json = 1

### ✔ (2) JSON Health Check

```bash
cat profiling_data/query_001_run_00.json
```

**Must see**:
```json
"success": true,
"error": null    // This is a field name, NOT an error!
```

**CPU timeline must show variations**:
```json
"cpu_total": 80.0
"cpu_total": 20.2
"cpu_total": 109.1
```

**Memory should show range changes** (normally 1.0–1.6GB)

⚠️ **Don't Misinterpret Errors**:  
- `"error": null` is a field name, not an error
- Actual errors look like: `"error": "TimeoutError: ..."`

### ✔ (3) Log Completeness

```bash
tail -50 logs/experiment.log
```

---

# 📦 7. Exporting Experiment Results

## Method 1: tar Compression (Recommended)

### Compress:
```bash
tar -czf x86_results.tar.gz results/
```

### Parameter Explanation:
- `c` = create (create archive)
- `z` = gzip (compress)
- `f` = file (specify filename)
- `x` = extract (for decompression)

### Why use tar?
- Preserves Linux file permissions (zip destroys permissions)
- Preserves timestamps
- Ideal for large collections of json/txt/log files
- Cross-platform compatible (ARM Mac, Linux, WSL)

### Decompress (on ARM):
```bash
tar -xzf x86_results.tar.gz
```

---

## Method 2: Manual Renaming (When prefix Doesn't Work)

**Issue**: `medrag.py batch --all --prefix results/x86_all` didn't work

**Reasons**:
- medrag.py still uses old CPU version names in model field
- batch mode doesn't fully handle prefix parameter

**Safe Alternative**:

```bash
# After completing full batch run
mv test_25x5 results/x86_25/
mv profiling_cardio results/x86_cardio/
mv profiling_infection results/x86_infection/
mv profiling_trauma results/x86_trauma/
mv test_100x5 results/x86_100/
```

This is completely safe and facilitates ARM vs x86 comparison.

---

# 🔧 8. Advanced Notes and Troubleshooting

## 8.1 Windows + L Screen Lock (Safe, Won't Interrupt Computation)

WSL + GPU training is system-level computation and won't be interrupted by screen locking.

**Safe Operation**:
```
Windows + L
```

**Features**:
- Locks screen (prevents unauthorized access)
- ✅ Does NOT stop WSL
- ✅ Does NOT stop GPU
- ✅ Does NOT put WSL to sleep
- ✅ Computation continues running

⚠️ **Important**:  
Do NOT let Windows enter sleep/hibernate mode.  
Configure in power management:
- "Never sleep when plugged in"

---

## 8.2 GPU vs CPU Mode Differences

### x86 (GPU + CUDA):
- Nvidia driver + CUDA automatically enabled
- Ollama auto-detects RTX 4090
- **DO NOT** use `num_gpu=0`
- **DO NOT** specify `num_threads`

### ARM (CPU-only):
- Requires `num_gpu=0` (disable GPU)
- Requires `num_threads=8` (specify CPU cores)

---

## 8.3 prefix Issue and Manual Workaround

**Problem**: `medrag.py batch --all --prefix results/x86_all` doesn't take effect

**Causes**:
- medrag.py still uses old CPU version names in model field
- batch mode incomplete handling of prefix parameter

**Safe Workaround**:
1. Complete full `batch all` run
2. Results output to default folders
3. Manually `mv` rename (see Section 7)

---

## 8.4 Safely Transfer Data Back to ARM (Recommended Workflow)

### Step 1: Package
```bash
tar -czf x86_results.tar.gz results/
```

### Step 2: Transfer to ARM
Options:
- OneDrive
- USB drive
- scp
- Teams / Slack file upload

### Step 3: Extract on ARM
```bash
tar -xzf x86_results.tar.gz
```

### Step 4: Integrate into Final results Directory
Unified structure:
```
results/
├── ARM_25/
├── x86_25/
├── ARM_100/
├── x86_100/
├── ARM_cardio/
├── x86_cardio/
├── ARM_infection/
├── x86_infection/
├── ARM_trauma/
└── x86_trauma/
```

### Step 5: Formal Comparison (Compare / Report / LaTeX)
```bash
python3 medrag.py compare --all
python3 medrag.py report --all
python3 medrag.py latex --all
```

---

# 🎉 Complete

You have successfully completed the comprehensive x86 experiment guide (basic + advanced).

This document covers all x86-specific operations including WSL model management, GPU/CUDA configuration, system monitoring, experiment validation, and ARM data integration workflow.
