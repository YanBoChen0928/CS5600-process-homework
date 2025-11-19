"""
Profiling module for Medical RAG workload characterization

This module provides tools for collecting CPU, memory, and latency metrics
during RAG pipeline execution on ARM (M2 Pro) and x86 (RTX 4090) systems.

Author: Yan-Bo Chen
Date: November 18, 2025
"""

from .workload_profiler import WorkloadProfiler

__all__ = ['WorkloadProfiler']
