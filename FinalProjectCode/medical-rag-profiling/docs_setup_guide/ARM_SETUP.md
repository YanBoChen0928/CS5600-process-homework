# ARM Setup Guide (Apple M2 Pro)

**Author:** Yan-Bo Chen  
**Device:** MacBook Pro M2 Pro (ARM, macOS)  
**Purpose:** Medical RAG Profiling Experiments  
**Last Updated:** November 21, 2025

---

## Quick Start Checklist

### Step 1: Check Ollama Status
```bash
ollama list
```

If no models are shown, start Ollama server:
```bash
ollama serve
```

### Step 2: Activate Virtual Environment
```bash
source venv_cs5600Project/bin/activate
```

You should see `(venv_cs5600Project)` in your terminal prompt.

### Step 3: Verify Current Directory
```bash
pwd
```

Should display: `.../medical-rag-profiling`

### Step 4: Close Unnecessary Applications
- Chrome (especially 20+ tabs)
- VS Code (if not debugging)
- Zoom / Teams / Slack
- Xcode / Docker / Simulator
- Background backup services (Google Drive / OneDrive)

**Reason:** CPU profiling requires minimal background interference.

---

## Directory Structure

```
medical-rag-profiling/
├── profiling/
│   ├── workload_profiler.py
│   └── __init__.py
├── run_experiment.py
├── rag_wrapper.py
├── queries/
│   ├── medical_queries_100.json
│   ├── medical_queries_25.json
│   └── medical_queries_10.json
├── profiling_data/
├── logs/
└── checkpoints/
```

---

## Environment Setup

### Install Ollama Model (CPU-Only Mode)
```bash
# Create CPU-only model
ollama create llama3.2-cpu -f Modelfile-cpu
```

**Modelfile-cpu contents:**
```
FROM llama3.2:3b
PARAMETER num_gpu 0
PARAMETER num_threads 8
```

### Navigate to Project Directory
```bash
cd ~/Desktop/medical-rag-profiling
```

### Activate Virtual Environment
```bash
source venv_cs5600Project/bin/activate
```

### Test Profiler Import
```bash
python -c "import profiling; print('Profiler OK')"
```

### Verify Ollama Model
```bash
ollama list | grep llama
```

Should show: `llama3.2-cpu`

---

## Three-Terminal Configuration

```
┌──────────────────┐
│ Terminal 1       │
│ (Ollama Server)  │
│------------------│
│ ollama serve     │
└──────────────────┘

┌──────────────────┐
│ Terminal 2       │
│ (Experiment)     │
│------------------│
│ ./medrag.py run  │
└──────────────────┘

┌──────────────────┐
│ Terminal 3       │
│ (Monitoring)     │
│------------------│
│ Activity Monitor │
└──────────────────┘
```

**Purpose:**
- Terminal 1: Ollama logs (CPU/GPU usage patterns)
- Terminal 2: Profiling experiment execution
- Terminal 3: External resource monitoring

---

## Running Experiments

### Terminal 1 — Start Ollama Server
```bash
ollama serve
```

Keep this terminal open.

### Terminal 2 — Run Profiling Experiment
```bash
cd ~/Desktop/medical-rag-profiling
source venv_cs5600Project/bin/activate

# Quick test (10 queries × 1 run)
./medrag.py run --dataset 10 --runs 1

# Full experiment (100 queries × 5 runs)
./medrag.py run --dataset 100 --runs 5
```

### Terminal 3 — Monitor CPU
macOS:
```bash
top -o cpu
```

Or open Activity Monitor application.

**Monitor:**
- `ollama` CPU usage (should be 100%–600%)
- Python + RAG process behavior

---

## Post-Experiment Validation

### Check Generated Files
```bash
ls results/ARM_100/*.json | wc -l
```

Expected: 500 files (100 queries × 5 runs)

### Verify JSON Structure
```bash
cat results/ARM_100/query_000_run_00.json | python -m json.tool
```

### Check Timeline Data
```bash
grep -R "timeline" results/ARM_100/query_000_run_00.json
```

---

## Important Notes

✓ ARM CPU-only mode is stable  
✓ If thermal throttling occurs, wait 5 minutes  
✓ Avoid running VS Code indexer (pollutes CPU measurements)  
✓ Ensure sufficient disk space (≥ 2GB)

---

## Related Documentation

- Main README: ../README.md
- CLI Reference: CLI_REFERENCE.md
- x86 Setup Guide: X86_SETUP.md
- Analysis Guide: ANALYSIS_GUIDE.md

---

**For complete workflow and data integration, see CLI_REFERENCE.md**
