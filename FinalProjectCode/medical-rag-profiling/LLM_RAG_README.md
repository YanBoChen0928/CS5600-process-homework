---
title: OnCall.ai - Medical Emergency Assistant
emoji: 🏥
colorFrom: red
colorTo: blue
sdk: gradio
sdk_version: "5.38.0"
app_file: app.py
python_version: "3.11"
pinned: false
license: mit
tags:
  - medical
  - healthcare
  - RAG
  - emergency
  - clinical-guidance
  - gradio
---

# 🏥 Medical RAG System - Technical Documentation

A RAG-based medical assistant system that provides **evidence-based clinical guidance** for emergency medical situations using real medical guidelines and language models.

> **Note**: This document describes the Medical RAG workload used in the CS5600 performance characterization study. For the main project documentation, see README.md in the root directory.

---

## 🎯 What This System Does

The Medical RAG system helps process medical queries by:
- **Processing medical queries** through multi-level validation system
- **Retrieving relevant medical guidelines** from curated emergency medicine datasets
- **Generating evidence-based clinical advice** using Llama 3.2 (3B parameters)
- **Providing transparent, traceable medical guidance** with source attribution

---

## 🏗️ System Architecture

### Multi-Level Query Processing Pipeline

1. **Level 1**: Predefined medical condition mapping (instant response)
2. **Level 2**: LLM-based condition extraction (Llama 3.2:3B via Ollama)
3. **Level 3**: Semantic search fallback
4. **Level 4**: Medical query validation (100% non-medical rejection)
5. **Level 5**: Generic medical search for rare conditions

### Dual-Index Retrieval System

- **Emergency Guidelines Index**: Fast retrieval for critical conditions
- **Treatment Protocols Index**: Comprehensive clinical procedures
- **Semantic Search**: Vector-based similarity matching using sentence transformers

---

## 📋 Technical Details

### Key Features

- **Complete RAG Pipeline**: Query → Condition Extraction → Retrieval → Generation
- **Multi-level fallback validation** for robust query processing
- **Evidence-based medical advice** with transparent source attribution
- **CPU-only and GPU-accelerated modes** for architecture comparison
- **Real-time profiling** of CPU, memory, and latency metrics

### Models Used

- **Medical LLM**: Llama 3.2:3B (via Ollama)
  - ARM: CPU-only execution (forced with `num_gpu=0`, `num_threads=8`)
  - x86: GPU-accelerated execution (CUDA, RTX 4090)
- **Embedding Model**: Sentence Transformers for semantic search
- **Retrieval**: Annoy index for fast approximate nearest neighbor search

### Dataset

- Curated medical guidelines and emergency protocols
- Treatment procedures and clinical decision trees
- Evidence-based medical knowledge base
- Query datasets:
  - General medical queries: 10, 25, 100 queries
  - Category-specific: cardio, infection, trauma

---

## 🔧 System Configuration

### ARM (M2 Pro) Configuration

**CPU-only Mode:**
```python
# Ollama Modelfile configuration
FROM llama3.2:3b
PARAMETER num_gpu 0
PARAMETER num_threads 8
```

**Environment:**
- macOS 14.x
- ARM64 architecture
- Unified memory architecture
- 12 cores (6 performance + 6 efficiency)

### x86 (Intel + RTX 4090) Configuration

**GPU-accelerated Mode:**
```python
# Ollama automatically detects CUDA
# No explicit configuration needed
```

**Environment:**
- WSL2 (Ubuntu)
- CUDA 12.x
- Discrete GPU: RTX 4090 (24GB VRAM)
- CPU: Intel i9 (32 cores)

---

## 📊 Performance Characteristics

### Workload Properties

**Computational Intensity:**
- LLM inference: Token generation (CPU/GPU intensive)
- Retrieval: Vector similarity search (memory intensive)
- Embedding: Sentence encoding (moderate CPU)

**Memory Footprint:**
- Model size: ~2GB (Llama 3.2:3B)
- Embedding index: ~500MB
- Runtime memory: 3-5GB

**I/O Characteristics:**
- Model loading: One-time cost
- Query processing: Minimal I/O
- Index retrieval: In-memory operations

### Expected Performance Metrics

**Latency (per query):**
- ARM (CPU-only): 10-15 seconds
- x86 (GPU): 6-10 seconds
- Speedup: 1.3-1.6×

**CPU Utilization:**
- ARM: 400-800% (4-8 cores active)
- x86: 600-1200% (6-12 cores active)

**Memory Usage:**
- ARM: 3.0-3.5 GB
- x86: 3.5-4.5 GB

---

## 🎓 Usage in CS5600 Project

This Medical RAG system serves as the **benchmark workload** for characterizing performance differences between ARM and x86 architectures.

### Why Medical RAG as a Workload?

1. **Representative of Modern AI Workloads**
   - LLM inference (compute-intensive)
   - Vector search (memory-intensive)
   - Real-world application scenario

2. **Measurable Performance Metrics**
   - Clear start/end points (query → response)
   - Reproducible execution
   - Quantifiable resource usage

3. **Architecture-Relevant Characteristics**
   - Benefits from GPU acceleration (x86)
   - Tests CPU efficiency (ARM)
   - Memory architecture differences

### Profiling Integration

The system is instrumented with:
- **Real-time CPU monitoring** (per-core and total)
- **Memory tracking** (used, available, peak)
- **Latency measurement** (retrieval, generation, total)
- **Timeline recording** (500ms sampling interval)

See medrag.py for the complete profiling CLI.

---

## ⚠️ Important Disclaimers

🚨 **This tool is for educational and research purposes only.**

- **Not a substitute for professional medical advice**
- **Not for use in actual medical emergencies**
- **Always consult qualified healthcare professionals**
- **Verify all information with authoritative medical sources**

---

## 📁 Project Structure

```
medical-rag-profiling/
├── app.py                      # Gradio interface (original)
├── medrag.py                   # Unified CLI for profiling
├── run_experiment.py           # Experiment runner
├── analyze_results.py          # Statistical analysis
├── visualize_results.py        # Plot generation
├── rag_wrapper.py              # RAG pipeline interface
├── src/                        # Core RAG modules
│   ├── user_prompt.py          # Query processing
│   ├── retrieval.py            # Retrieval system
│   ├── generation.py           # Response generation
│   ├── llm_clients.py          # Ollama interface
│   └── medical_conditions.py   # Condition mapping
├── profiling/                  # Profiling modules
│   ├── workload_profiler.py    # CPU, memory, latency tracking
│   └── __init__.py
├── queries/                    # Query datasets
│   ├── medical_queries_10.json
│   ├── medical_queries_25.json
│   ├── medical_queries_100.json
│   ├── cardio_queries.json
│   ├── infection_queries.json
│   └── trauma_queries.json
├── models/                     # Pre-trained models
│   ├── embeddings/             # Vector embeddings
│   └── indices/                # Search indices
├── results/                    # Profiling results (gitignored)
│   ├── ARM_*/
│   └── x86_*/
├── final_report/               # Analysis outputs (gitignored)
└── requirements.txt
```

---

## 🔗 Related Documentation

- **Main Project README**: README.md
- **ARM Setup Guide**: docs_setup_guide/README_ARM.md
- **x86 Setup Guide**: docs_setup_guide/README_X86.md
- **CLI Reference**: docs_setup_guide/README_medrag.md
- **Data Analysis Guide**: docs_setup_guide/Data_Analysis_Guide_ARM_vs_x86.md

---

## 📚 Technical References

### RAG Pipeline

1. **Query Processing**: Multi-level condition extraction
2. **Retrieval**: Dual-index system (emergency guidelines + treatment protocols)
3. **Generation**: LLM-based response synthesis with source attribution
4. **Validation**: Medical query filtering and safety checks

### Model Details

**Llama 3.2:3B**
- Parameters: 3 billion
- Context window: 4096 tokens
- Quantization: FP16 (ARM), FP16/BF16 (x86 GPU)
- Inference framework: Ollama

**Embedding Model**
- Architecture: Sentence Transformers
- Dimension: 384 (or 768 depending on model variant)
- Index type: Annoy (approximate nearest neighbor)

---

## 🔧 Development Notes

### Version History

- **v0.9.0** (2025-07-31): Initial OnCall.ai application
- **v1.0.0** (2025-11-17): Integration with CS5600 profiling system
- **v1.1.0** (2025-11-20): Unified medrag.py CLI with compare/report/latex

### Known Limitations

1. **CPU-only mode on ARM**: Requires custom Ollama Modelfile
2. **WSL Ollama setup**: Must download models in WSL, not PowerShell
3. **Memory usage**: Increases with index size and model quantization
4. **Latency variance**: Depends on query complexity and context length

---

## 🎯 Summary

This Medical RAG system provides a **realistic, reproducible workload** for characterizing the performance of modern AI inference across different hardware architectures. It combines:

- **Compute-intensive** LLM inference
- **Memory-intensive** vector retrieval
- **Real-world** application scenario
- **Comprehensive** profiling instrumentation

For the complete performance study and comparative analysis, see the main README.md and related documentation in the docs_setup_guide and academic directories.

---

**Last Updated**: November 21, 2025  
**Author**: Yan-Bo Chen  
**Project**: CS5600 Computer Systems Final Project  
**Institution**: Northeastern University

