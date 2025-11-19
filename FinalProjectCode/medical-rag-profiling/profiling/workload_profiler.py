"""
Workload Profiler for Medical RAG System
Cross-platform profiling for ARM (M2 Pro) and x86 (RTX 4090)

Author: Yan-Bo Chen
Date: November 18, 2025
Purpose: CS5600 Project - CPU Workload Characterization
"""

import psutil
import time
import json
import platform
import logging
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger(__name__)

class WorkloadProfiler:
    """
    Cross-platform workload profiler for RAG pipeline
    Collects CPU, memory, and latency metrics with timeline sampling
    """
    
    def __init__(self, output_dir: str = "profiling_data"):
        """
        Initialize profiler
        
        Args:
            output_dir: Directory to save profiling results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect system information (one-time)
        self.system_info = self._get_system_info()
        
        # Save system info to file
        system_info_path = self.output_dir / "system_info.json"
        with open(system_info_path, 'w') as f:
            json.dump(self.system_info, f, indent=2)
        
        logger.info(f"WorkloadProfiler initialized")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"System: {self.system_info['platform']} {self.system_info['architecture']}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """
        Collect system information (one-time at initialization)
        
        Returns:
            Dict with platform, CPU, and memory details
        """
        cpu_count_physical = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        total_memory = psutil.virtual_memory().total / (1024**3)
        
        system_info = {
            "platform": platform.system(),  # "Darwin" or "Linux"
            "architecture": platform.machine(),  # "arm64" or "x86_64"
            "cpu_count_physical": cpu_count_physical,
            "cpu_count_logical": cpu_count_logical,
            "total_memory_gb": round(total_memory, 2),
            "python_version": platform.python_version(),
            "timestamp": datetime.now().isoformat()
        }
        
        # ARM-specific: Identify P-cores and E-cores using CPU brand detection
        if system_info["architecture"] == "arm64" and system_info["platform"] == "Darwin":
            try:
                import subprocess
                cpu_brand = subprocess.check_output(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    text=True
                ).strip()
            except Exception:
                cpu_brand = "Unknown"
            
            # M2 Pro: 6P + 4E (10 cores)
            if "M2 Pro" in cpu_brand and cpu_count_physical == 10:
                system_info["p_cores"] = list(range(0, 6))     # 0-5
                system_info["e_cores"] = list(range(6, 10))    # 6-9
                system_info["note"] = "M2 Pro (10-core): 6 P-cores + 4 E-cores"
            
            # M2 Pro: 6P + 6E (12 cores) - Higher-end configuration
            elif "M2 Pro" in cpu_brand and cpu_count_physical == 12:
                system_info["p_cores"] = list(range(0, 6))     # 0-5
                system_info["e_cores"] = list(range(6, 12))    # 6-11
                system_info["note"] = "M2 Pro (12-core): 6 P-cores + 6 E-cores"
            
            # M2 Max: 8P + 4E (12 cores)
            elif "M2 Max" in cpu_brand and cpu_count_physical == 12:
                system_info["p_cores"] = list(range(0, 8))     # 0-7
                system_info["e_cores"] = list(range(8, 12))    # 8-11
                system_info["note"] = "M2 Max (12-core): 8 P-cores + 4 E-cores"
            
            # M2 Max: 10P + 4E (14 cores)
            elif "M2 Max" in cpu_brand and cpu_count_physical == 14:
                system_info["p_cores"] = list(range(0, 10))    # 0-9
                system_info["e_cores"] = list(range(10, 14))   # 10-13
                system_info["note"] = "M2 Max (14-core): 10 P-cores + 4 E-cores"
            
            # Unknown ARM layout
            else:
                system_info["p_cores"] = None
                system_info["e_cores"] = None
                system_info["note"] = f"ARM: Unknown core split (physical={cpu_count_physical}, brand={cpu_brand})"
        else:
            # x86 / Linux (homogeneous cores)
            system_info["p_cores"] = None
            system_info["e_cores"] = None
            system_info["note"] = "Homogeneous core architecture"
        
        return system_info
    
    def save_result(self, metrics: Dict[str, Any]) -> None:
        """
        Save profiling result to JSON file
        
        Args:
            metrics: Profiling metrics dictionary
        """
        # Generate filename from metadata
        query_id = metrics["metadata"]["query_id"]
        run_id = metrics["metadata"]["run_id"]
        filename = f"query_{query_id:03d}_run_{run_id:02d}.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(metrics, f, indent=2)
            logger.debug(f"Saved result to: {filepath}")
            
        except OSError as e:
            logger.error(f"Failed to save result: {e}")
            # Try backup location
            backup_path = Path("profiling_backup") / filename
            backup_path.parent.mkdir(exist_ok=True)
            with open(backup_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            logger.warning(f"Saved to backup location: {backup_path}")
    
    def profile_query(
        self, 
        query: str, 
        query_id: int, 
        run_id: int,
        rag_function: Callable[[str], str]
    ) -> Dict[str, Any]:
        """
        Profile a single RAG query execution
        
        Args:
            query: Medical query string
            query_id: Query identifier (0-99)
            run_id: Run number (0-4 for 5 runs)
            rag_function: Function to execute (takes query, returns response)
        
        Returns:
            Dictionary with complete profiling metrics
        """
        logger.info(f"Profiling query {query_id}, run {run_id}: {query[:50]}...")
        
        # Initialize metrics dict
        metrics = {
            "metadata": {
                "query_id": query_id,
                "run_id": run_id,
                "timestamp": datetime.now().isoformat(),
                "query_text": query,
                "system": self.system_info["platform"],
                "architecture": self.system_info["architecture"]
            }
        }
        
        # Start timeline sampling (Segment 3)
        self._start_sampling_thread()
        
        # Pre-execution snapshot
        start_time = time.perf_counter()
        cpu_before = psutil.cpu_percent(interval=0.1, percpu=True)
        mem_before = psutil.virtual_memory()
        
        # Execute RAG query with error handling
        try:
            logger.debug(f"Executing RAG function for query {query_id}...")
            response = rag_function(query)
            success = True
            error = None
            response_length = len(response) if response else 0
            
            # NEW: Save response text to separate file
            response_filename = f"query_{query_id:03d}_run_{run_id:02d}.txt"
            response_filepath = self.output_dir / response_filename
            with open(response_filepath, 'w', encoding='utf-8') as f:
                f.write(response if response else "")
            logger.debug(f"Saved response text to: {response_filename}")
            
        except subprocess.TimeoutExpired as e:
            logger.error(f"Query {query_id} timed out: {e}")
            response = None
            success = False
            error = f"Timeout: {str(e)}"
            response_length = 0
            
        except Exception as e:
            logger.error(f"Query {query_id} failed: {type(e).__name__}: {e}")
            response = None
            success = False
            error = f"{type(e).__name__}: {str(e)}"
            response_length = 0
        
        # Post-execution snapshot
        end_time = time.perf_counter()
        cpu_after = psutil.cpu_percent(interval=0.1, percpu=True)
        mem_after = psutil.virtual_memory()
        
        # Calculate metrics
        total_latency_ms = (end_time - start_time) * 1000
        
        # CPU metrics
        cpu_total_avg = sum(cpu_after) / len(cpu_after)
        cpu_peak = max(cpu_after)
        
        # ARM-specific: P-cores vs E-cores breakdown
        if self.system_info["p_cores"] is not None:
            p_cores_usage = [cpu_after[i] for i in self.system_info["p_cores"]]
            e_cores_usage = [cpu_after[i] for i in self.system_info["e_cores"]]
            p_cores_avg = sum(p_cores_usage) / len(p_cores_usage)
            e_cores_avg = sum(e_cores_usage) / len(e_cores_usage)
        else:
            p_cores_avg = None
            e_cores_avg = None
        
        # Memory metrics
        memory_used_gb = mem_after.used / (1024**3)
        memory_percent = mem_after.percent
        memory_available_gb = mem_after.available / (1024**3)
        
        # Stop timeline sampling and collect data (Segment 3)
        timeline = self._stop_sampling_thread()
        timeline_metrics = self._calculate_timeline_metrics(timeline)
        
        # Build complete metrics dictionary
        metrics["success"] = success
        metrics["error"] = error
        
        metrics["latency"] = {
            "total_ms": round(total_latency_ms, 2)
            # Note: Retrieval/generation breakdown requires instrumentation
            # in RAG pipeline. Keeping simple per intentional design choice
            # to focus on overall CPU-intensive generation workload.
        }
        
        metrics["cpu"] = {
            "peak_percent": round(cpu_peak, 2),
            "average_percent": round(cpu_total_avg, 2),
            "per_core": [round(x, 2) for x in cpu_after],
            "p_cores_average": round(p_cores_avg, 2) if p_cores_avg is not None else None,
            "e_cores_average": round(e_cores_avg, 2) if e_cores_avg is not None else None
        }
        
        metrics["memory"] = {
            "used_gb": round(memory_used_gb, 2),
            "percent": round(memory_percent, 2),
            "available_gb": round(memory_available_gb, 2)
        }
        
        metrics["response"] = {
            "length_chars": response_length,
            "text_file": f"query_{query_id:03d}_run_{run_id:02d}.txt"
        }
        
        # Timeline data (Segment 3)
        metrics["timeline"] = timeline
        metrics["timeline_summary"] = timeline_metrics
        
        logger.info(f"✓ Query {query_id} profiled: {total_latency_ms:.0f}ms, "
                   f"CPU avg {cpu_total_avg:.1f}%, Memory {memory_used_gb:.2f}GB, "
                   f"Timeline samples: {timeline_metrics['num_samples']}")
        
        return metrics
    
    def _start_sampling_thread(self) -> None:
        """
        Start background thread for timeline sampling
        Samples CPU and memory every 0.5 seconds during query execution
        """
        # Warm up psutil baseline (prevents 0.0% or spike in first sample)
        psutil.cpu_percent(interval=None, percpu=True)
        
        self.sampling_active = True
        self.timeline_data = []
        self.sampling_start_time = time.perf_counter()
        
        def sample_metrics():
            """Background sampling function"""
            while self.sampling_active:
                try:
                    # Calculate elapsed time
                    current_time = time.perf_counter() - self.sampling_start_time
                    
                    # Sample CPU per-core (primary metric)
                    cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
                    
                    # Calculate total from cores (sum of all cores)
                    # Example: 12 cores × 25% avg = 300% total
                    cpu_total = sum(cpu_per_core)
                    
                    # Sample memory
                    mem = psutil.virtual_memory()
                    
                    # Create sample
                    sample = {
                        "t": round(current_time, 2),
                        "cpu_total": round(cpu_total, 2),
                        "cpu_cores": [round(x, 2) for x in cpu_per_core],
                        "memory_gb": round(mem.used / (1024**3), 2),
                        "memory_percent": round(mem.percent, 2)
                    }
                    
                    self.timeline_data.append(sample)
                    
                    # Sleep until next sample (0.5s interval)
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"Timeline sampling error: {e}")
                    # Continue sampling despite errors
        
        # Start background daemon thread
        self.sampling_thread = threading.Thread(target=sample_metrics, daemon=True)
        self.sampling_thread.start()
        logger.debug("Timeline sampling thread started")
    
    def _stop_sampling_thread(self) -> list:
        """
        Stop background sampling thread and return collected data
        
        Returns:
            List of timeline samples with CPU/memory over time
        """
        self.sampling_active = False
        
        # Wait for thread to finish (max 1 second)
        if hasattr(self, 'sampling_thread') and self.sampling_thread.is_alive():
            self.sampling_thread.join(timeout=1.0)
        
        # Return collected timeline data
        timeline = self.timeline_data if hasattr(self, 'timeline_data') else []
        
        num_samples = len(timeline)
        if num_samples > 0:
            duration = timeline[-1]['t'] if timeline else 0
            logger.debug(f"Timeline sampling stopped: {num_samples} samples over {duration:.1f}s")
        else:
            logger.warning("Timeline sampling collected no data")
        
        return timeline
    
    def _calculate_timeline_metrics(self, timeline: list) -> Dict[str, Any]:
        """
        Calculate peak and average metrics from timeline data
        More accurate than single-point sampling
        
        Args:
            timeline: List of timeline samples
        
        Returns:
            Dict with peak/average CPU and memory from entire execution
        """
        if not timeline:
            return {
                "cpu_peak_from_timeline": None,
                "cpu_avg_from_timeline": None,
                "memory_peak_from_timeline": None,
                "num_samples": 0
            }
        
        # Extract CPU totals from all samples
        cpu_totals = [sample['cpu_total'] for sample in timeline]
        
        # Extract memory values from all samples  
        memory_values = [sample['memory_gb'] for sample in timeline]
        
        # Calculate peak and average across entire execution
        cpu_peak = max(cpu_totals) if cpu_totals else None
        cpu_avg = sum(cpu_totals) / len(cpu_totals) if cpu_totals else None
        mem_peak = max(memory_values) if memory_values else None
        
        return {
            "cpu_peak_from_timeline": round(cpu_peak, 2) if cpu_peak else None,
            "cpu_avg_from_timeline": round(cpu_avg, 2) if cpu_avg else None,
            "memory_peak_from_timeline": round(mem_peak, 2) if mem_peak else None,
            "num_samples": len(timeline)
        }
