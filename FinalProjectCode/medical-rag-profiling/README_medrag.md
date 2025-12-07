# medrag CLI - User Guide

**Medical RAG Profiling - Unified Command-Line Interface**

---

## 🎯 Overview

`medrag` is a unified CLI tool for running, monitoring, analyzing, and visualizing Medical RAG profiling experiments on CPU-based systems.

**Key Features**:
- ✅ Single command to run experiments
- ✅ Real-time monitoring with Timeline CPU metrics
- ✅ Automated statistical analysis
- ✅ Publication-quality visualizations
- ✅ Hardware-adaptive (ARM vs x86)

---

## 📦 Installation

### Prerequisites
```bash
# Ensure you're in the project directory
cd medical-rag-profiling

# Activate virtual environment
source venv_cs5600Project/bin/activate

# Verify Ollama is running
ollama serve  # In a separate terminal
```

### Setup
```bash
# Make CLI executable
chmod +x medrag.py

# Create convenient shortcut (optional)
ln -s medrag.py medrag
```

---

## 🚀 Quick Start

### Basic Usage
```bash
# Run 25 queries × 5 runs
./medrag run --dataset 25 --runs 5

# Analyze results
./medrag analyze --output test_25x5

# Generate visualizations
./medrag visualize --output test_25x5
```

### With Monitoring
```bash
# Terminal 1: Ollama service
ollama serve

# Terminal 2: Run experiment
./medrag run --dataset 100 --runs 5

# Terminal 3: Monitor in real-time
./medrag monitor --output profiling_data_100
```

---

## 📚 Commands Reference

### `run` - Execute Profiling Experiment

**Syntax**:
```bash
./medrag run --dataset DATASET --runs RUNS [--model MODEL] [--prefix PREFIX]
```

**Parameters**:
- `--dataset`: Dataset to use
  - Numeric: `10`, `25`, `100` (test datasets)
  - Categories: `cardio`, `infection`, `trauma`
- `--runs`: Number of runs per query (default: 1)
- `--model`: Ollama model name (default: `llama3.2-cpu`)
- `--prefix`: Custom output directory prefix (optional)

**Examples**:
```bash
# Small test (10 queries × 1 run)
./medrag run --dataset 10 --runs 1

# Medium test (25 queries × 5 runs)
./medrag run --dataset 25 --runs 5

# Full experiment (100 queries × 5 runs)
./medrag run --dataset 100 --runs 5

# Category-specific
./medrag run --dataset cardio --runs 5
./medrag run --dataset infection --runs 5
./medrag run --dataset trauma --runs 5

# Custom output directory
./medrag run --dataset 25 --runs 3 --prefix my_test
```

**Output Directories**:
- Numeric datasets: `test_{N}x{R}` (e.g., `test_25x5`)
- Categories: `profiling_{category}` (e.g., `profiling_cardio`)
- Custom: Uses `--prefix` value

---

### `monitor` - Real-Time Monitoring

**Syntax**:
```bash
./medrag monitor --output OUTPUT_DIR
```

**Parameters**:
- `--output`: Directory to monitor

**Example**:
```bash
# Monitor ongoing experiment
./medrag monitor --output test_25x5
```

**Display**:
- Latest completed query info
- Timeline CPU usage (all cores total)
- Per-core average CPU usage
- Memory usage
- Latency
- Progress percentage

**Refresh Rate**: Every 2 seconds

**Stop Monitoring**: Press `Ctrl+C`

---

### `analyze` - Statistical Analysis

**Syntax**:
```bash
./medrag analyze --output OUTPUT_DIR
```

**Parameters**:
- `--output`: Directory containing experiment results

**Example**:
```bash
./medrag analyze --output test_25x5
./medrag analyze --output profiling_cardio
```

**Output Sections**:
1. **Latency Analysis**: Min/Max/Median/Mean/StdDev
2. **CPU Usage**: Timeline-based metrics (all cores total)
3. **Memory Analysis**: Usage patterns and stability check
4. **Response Quality**: Character length statistics
5. **Timeline Sampling**: Sample counts per query
6. **System Characterization**: High-level summary

---

### `visualize` - Generate Plots

**Syntax**:
```bash
./medrag visualize --output OUTPUT_DIR
```

**Parameters**:
- `--output`: Directory containing experiment results

**Example**:
```bash
./medrag visualize --output test_25x5
./medrag visualize --output profiling_data_100
```

**Generated Plots** (PNG format):
1. `cpu_heatmap.png` - Core-by-core CPU utilization heatmap
2. `latency_distribution.png` - Response time histogram
3. `memory_timeline.png` - Memory usage across queries
4. `core_utilization_comparison.png` - P-cores vs E-cores (ARM) or unified view (x86)
5. `cpu_timeline_aggregate.png` - Aggregate CPU timeline

**Resolution**: 300 DPI (publication-quality)

---

## 📊 Typical Workflows

### Workflow 1: Quick Test (10-15 minutes)
```bash
# 1. Run small experiment
./medrag run --dataset 10 --runs 1

# 2. Analyze
./medrag analyze --output test_10x1

# 3. Visualize
./medrag visualize --output test_10x1
```

### Workflow 2: Full Experiment with Monitoring (2-3 hours)
```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: Run experiment
./medrag run --dataset 100 --runs 5

# Terminal 3: Monitor
./medrag monitor --output profiling_data_100

# After completion (Terminal 2):
./medrag analyze --output profiling_data_100
./medrag visualize --output profiling_data_100
```

### Workflow 3: Category-Specific Analysis
```bash
# Run all categories
./medrag run --dataset cardio --runs 5
./medrag run --dataset infection --runs 5
./medrag run --dataset trauma --runs 5

# Analyze each
./medrag analyze --output profiling_cardio
./medrag analyze --output profiling_infection
./medrag analyze --output profiling_trauma

# Visualize each
./medrag visualize --output profiling_cardio
./medrag visualize --output profiling_infection
./medrag visualize --output profiling_trauma
```

---

## 📁 File Structure

### Query Files
```
queries/
├── medical_queries_10.json      # 10 queries (quick test)
├── medical_queries_25.json      # 25 queries (stress test)
├── medical_queries_100.json     # 100 queries (full experiment)
├── cardio_queries.json          # 27 cardiovascular queries
├── infection_queries.json       # 31 infectious disease queries
└── trauma_queries.json          # 22 trauma queries
```

### Output Structure
```
test_25x5/  (or profiling_cardio/, etc.)
├── query_001_run_00.json        # Metrics (CPU, memory, latency)
├── query_001_run_00.txt         # Response text
├── query_001_run_01.json
├── query_001_run_01.txt
├── ...
├── experiment_config.json       # Experiment metadata
├── system_info.json             # System configuration
├── cpu_heatmap.png              # Visualization (after visualize command)
├── latency_distribution.png
├── memory_timeline.png
├── core_utilization_comparison.png
└── cpu_timeline_aggregate.png
```

---

## ⚙️ Configuration

### Default Settings
```python
Model: llama3.2-cpu
Timeout: 300 seconds per query
Timeline Sampling: 0.5 second intervals
```

### Pre-Flight Checks
Before running experiments:
1. ✅ Ollama service running
2. ✅ Model available (`ollama list`)
3. ✅ Query file exists
4. ✅ Output directory doesn't exist (to avoid overwriting)

### System Requirements
- **CPU**: Multi-core processor (tested on ARM M2 Pro 12-core)
- **Memory**: ≥6 GB available
- **Disk**: ~500 MB for 100×5 experiment
- **Python**: 3.11+
- **Ollama**: Running and accessible

---

## 🖥️ Hardware Adaptation

### ARM (M1/M2/M3)
```
Detected: ARM architecture
Cores: 12 (8 P-cores + 4 E-cores)
Visualizations: Separate P-core and E-core analysis
Heatmap: Shows P/E core labels and divider line
```

### x86 (Intel/AMD)
```
Detected: x86 architecture
Cores: Variable (8/16/24)
Visualizations: Unified core analysis
Heatmap: All cores treated equally
```

**Auto-detection**: CLI automatically detects CPU architecture and adjusts visualizations accordingly.

---

## 🔧 Troubleshooting

### Issue: "No module named 'matplotlib'"
```bash
# Install visualization dependencies
pip install matplotlib seaborn numpy
```

### Issue: "Ollama is not running"
```bash
# Terminal 1: Start Ollama
ollama serve

# Verify
curl http://localhost:11434/api/tags
```

### Issue: "Model not available"
```bash
# Check available models
ollama list

# Pull model if needed
ollama pull llama3.2:3b
```

### Issue: "Permission denied"
```bash
# Make CLI executable
chmod +x medrag.py
```

### Issue: "Output directory already exists"
```bash
# Remove old directory or use different prefix
rm -rf test_25x5

# Or use custom prefix
./medrag run --dataset 25 --runs 5 --prefix test_25x5_v2
```

---

## 📊 Understanding Metrics

### Timeline CPU Total
- **Range**: 0% to 1200% (12 cores × 100%)
- **Meaning**: Sum of all CPU cores' usage
- **Example**: 831% = ~8.3 cores actively used
- **Usage**: Primary metric for CPU-intensive workload characterization

### Per-Core Average
- **Calculation**: Timeline CPU Total ÷ Number of Cores
- **Example**: 831% ÷ 12 = 69.3% per core
- **Usage**: Comparable to system-level metrics (e.g., `top`)

### Memory Stability
- **Threshold**: 0.5 GB range
- **Stable**: Range < 0.5 GB (no memory leaks)
- **Unstable**: Range > 0.5 GB (potential memory growth)

---

## 📈 Performance Expectations

### Latency (per query)
- **Fast queries**: 8-12 seconds
- **Average queries**: 13-17 seconds
- **Slow queries**: 18-25 seconds

### CPU Usage (Timeline)
- **Peak**: 900-1200% (9-12 cores)
- **Average**: 700-900% (7-9 cores)
- **Per-core avg**: 60-75%

### Memory
- **Typical**: 6.5-7.5 GB
- **Stable**: ±0.2-0.3 GB variation

### Experiment Duration
- **10×1**: ~3-5 minutes
- **25×5**: ~30-40 minutes
- **100×5**: ~2-3 hours
- **Categories**: ~25-35 minutes each

---

## 🎯 Best Practices

### Before Running
1. ✅ Close unnecessary applications (Chrome, VSCode, etc.)
2. ✅ Verify Ollama is running
3. ✅ Check available disk space
4. ✅ Ensure stable power supply (for laptops)

### During Experiment
1. ✅ Let it run uninterrupted
2. ✅ Monitor progress in Terminal 3
3. ✅ Don't start other heavy processes
4. ✅ Keep laptop awake (disable sleep mode)

### After Completion
1. ✅ Run analysis immediately
2. ✅ Generate visualizations
3. ✅ Back up output directory
4. ✅ Document any anomalies

---

## 📚 Related Documentation

- `DOCS/20251119_Phase4_Analysis_Tools.md` - Analysis tools documentation
- `DOCS/20251119_Phase4_Hardware_Adaptive_Patch.md` - Hardware adaptation details
- `DOCS/20251119_Phase3_Stress_Test_Plan.md` - Stress testing methodology
- `README.md` - Project overview

---

## 🆘 Support

### Issues
If you encounter problems:
1. Check Pre-flight requirements
2. Verify Ollama service status
3. Check available disk space and memory
4. Review error messages in Terminal output

### Contact
- **Author**: Yan-Bo Chen
- **Project**: CS5600 Final Project - Medical RAG Profiling
- **Institution**: Northeastern University

---

## 📝 Examples Summary

```bash
# Quick test
./medrag run --dataset 10 --runs 1
./medrag analyze --output test_10x1

# Stress test
./medrag run --dataset 25 --runs 5
./medrag visualize --output test_25x5

# Full experiment with monitoring
./medrag run --dataset 100 --runs 5  # Terminal 2
./medrag monitor --output profiling_data_100  # Terminal 3

# Category analysis
./medrag run --dataset cardio --runs 5
./medrag analyze --output profiling_cardio
./medrag visualize --output profiling_cardio
```

---

## ✅ Version

**CLI Version**: 1.0  
**Last Updated**: November 19, 2025  
**Python Version**: 3.11+  
**Tested On**: macOS ARM (M2 Pro)

---

**Ready to profile your Medical RAG system? Start with `./medrag run --dataset 10 --runs 1` for a quick test!** 🚀
