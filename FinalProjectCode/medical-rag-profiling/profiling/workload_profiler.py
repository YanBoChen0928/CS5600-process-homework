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
        # Generate filename
        query_id = metrics.get('query_id', 0)
        run_id = metrics.get('run_id', 0)
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
