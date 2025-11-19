"""
Experiment Runner for Medical RAG Profiling
Executes batch profiling experiments with multiple queries and runs

Author: Yan-Bo Chen
Date: November 19, 2025
Purpose: CS5600 Final Project - Workload Characterization
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from profiling.workload_profiler import WorkloadProfiler
from rag_wrapper import rag_query, check_ollama_running

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Run profiling experiments on medical RAG queries'
    )
    
    # Required arguments
    parser.add_argument(
        '--queries',
        type=str,
        required=True,
        help='Path to query JSON file (e.g., medical_queries_100.json)'
    )
    parser.add_argument(
        '--runs',
        type=int,
        required=True,
        help='Number of runs per query (typically 5)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--model',
        type=str,
        default='llama3.2-cpu',
        help='Ollama model to use (default: llama3.2-cpu)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='profiling_data',
        help='Output directory for results (default: profiling_data)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='Timeout per query in seconds (default: 300)'
    )
    
    return parser.parse_args()


def load_queries(query_file: str) -> List[Dict[str, Any]]:
    """
    Load queries from JSON file
    
    Args:
        query_file: Path to JSON file with queries
        
    Returns:
        List of query dictionaries with 'id' and 'query' fields
    """
    query_path = Path(query_file)
    
    if not query_path.exists():
        raise FileNotFoundError(f"Query file not found: {query_file}")
    
    with open(query_path, 'r') as f:
        queries = json.load(f)
    
    logger.info(f"Loaded {len(queries)} queries from {query_file}")
    
    return queries



def mock_rag_function(query: str) -> str:
    """
    Mock RAG function for Phase 1 testing
    DEPRECATED: Use real RAG in Phase 2
    
    Args:
        query: Medical query string
        
    Returns:
        Mock response string
    """
    import random
    time.sleep(random.uniform(1, 3))  # Simulate inference time
    return f"Mock response to: {query[:50]}..."


def create_rag_function(model: str, timeout: int):
    """
    Create RAG function with model and timeout parameters bound
    
    Args:
        model: Ollama model name
        timeout: Query timeout in seconds
        
    Returns:
        Function that takes query string and returns response
    """
    def rag_function(query: str) -> str:
        return rag_query(query, model=model, timeout=timeout)
    
    return rag_function


def generate_experiment_config(
    args,
    queries: List[Dict],
    profiler: WorkloadProfiler
) -> Dict[str, Any]:
    """
    Generate initial experiment configuration
    
    Args:
        args: Command-line arguments
        queries: List of queries
        profiler: WorkloadProfiler instance (for system info)
        
    Returns:
        Configuration dictionary
    """
    config = {
        "experiment_metadata": {
            "query_file": args.queries,
            "num_queries": len(queries),
            "runs_per_query": args.runs,
            "total_profiles": len(queries) * args.runs,
            "model": args.model,
            "output_dir": args.output,
            "timeout": args.timeout
        },
        "system_info": profiler.system_info,
        "execution_info": {
            "timestamp_start": datetime.now().isoformat(),
            "command": " ".join(sys.argv)
        },
        "results_summary": {
            "total_attempted": 0,
            "successful": 0,
            "failed": 0,
            "success_rate": 0.0,
            "failed_queries": []
        }
    }
    
    return config


def save_experiment_config(config: Dict, output_dir: Path):
    """Save experiment configuration to JSON file"""
    config_path = output_dir / "experiment_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    logger.debug(f"Saved experiment config to {config_path}")


def update_experiment_config(
    config: Dict,
    output_dir: Path,
    successful: int,
    failed: int,
    failed_list: List[Dict]
):
    """
    Update experiment configuration with final results
    
    Args:
        config: Configuration dictionary
        output_dir: Output directory
        successful: Number of successful queries
        failed: Number of failed queries
        failed_list: List of failed query details
    """
    total = successful + failed
    
    config["execution_info"]["timestamp_end"] = datetime.now().isoformat()
    
    # Calculate duration
    start = datetime.fromisoformat(config["execution_info"]["timestamp_start"])
    end = datetime.fromisoformat(config["execution_info"]["timestamp_end"])
    duration = (end - start).total_seconds()
    
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)
    
    config["execution_info"]["duration_seconds"] = int(duration)
    config["execution_info"]["duration_human"] = f"{hours}h {minutes}m {seconds}s"
    
    # Update results
    config["results_summary"]["total_attempted"] = total
    config["results_summary"]["successful"] = successful
    config["results_summary"]["failed"] = failed
    config["results_summary"]["success_rate"] = (successful / total * 100) if total > 0 else 0.0
    config["results_summary"]["failed_queries"] = failed_list
    
    # Save updated config
    save_experiment_config(config, output_dir)



def main():
    """Main experiment execution"""
    # Parse arguments
    args = parse_arguments()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load queries
    try:
        queries = load_queries(args.queries)
    except Exception as e:
        logger.error(f"Failed to load queries: {e}")
        sys.exit(1)
    
    # Initialize profiler
    profiler = WorkloadProfiler(output_dir=str(output_dir))
    
    # ============================================================
    # CRITICAL: Check Ollama BEFORE starting experiment
    # Fail fast to avoid wasting hours of profiling
    # ============================================================
    logger.info("")
    logger.info("=" * 70)
    logger.info("PRE-FLIGHT CHECKS")
    logger.info("=" * 70)
    
    # Check 1: Ollama service running
    logger.info("[1/2] Checking Ollama service...")
    if not check_ollama_running():
        logger.error("✗ Ollama is NOT running!")
        logger.error("")
        logger.error("  Please start Ollama first:")
        logger.error("  $ ollama serve")
        logger.error("")
        logger.error("  Then re-run this experiment.")
        sys.exit(1)
    logger.info("✓ Ollama is running")
    
    # Check 2: Model available (FAIL FAST if not found)
    logger.info(f"[2/2] Checking model '{args.model}'...")
    from rag_wrapper import check_model_available
    if not check_model_available(args.model):
        logger.error(f"✗ Model '{args.model}' NOT found!")
        logger.error("")
        logger.error("  Available models:")
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        logger.error(result.stdout)
        logger.error("")
        logger.error(f"  To download the model:")
        logger.error(f"  $ ollama pull {args.model}")
        logger.error("")
        logger.error("  Then re-run this experiment.")
        sys.exit(1)
    logger.info(f"✓ Model '{args.model}' is available")
    
    logger.info("=" * 70)
    logger.info("✓ All pre-flight checks passed")
    logger.info("=" * 70)
    logger.info("")
    
    # Create RAG function with model and timeout
    rag_function = create_rag_function(args.model, args.timeout)
    logger.info(f"RAG function initialized with model: {args.model}, timeout: {args.timeout}s")
    
    # Generate and save initial experiment config
    config = generate_experiment_config(args, queries, profiler)
    save_experiment_config(config, output_dir)
    
    # Print experiment header
    logger.info("=" * 70)
    logger.info("MEDICAL RAG PROFILING EXPERIMENT")
    logger.info("=" * 70)
    logger.info(f"Query file: {args.queries}")
    logger.info(f"Queries: {len(queries)}")
    logger.info(f"Runs per query: {args.runs}")
    logger.info(f"Total profiles: {len(queries) * args.runs}")
    logger.info(f"Model: {args.model}")
    logger.info(f"Output: {output_dir}")
    logger.info(f"System: {profiler.system_info['platform']} {profiler.system_info['architecture']}")
    logger.info(f"CPU: {profiler.system_info['cpu_count_physical']} cores")
    logger.info(f"Memory: {profiler.system_info['total_memory_gb']}GB")
    logger.info("=" * 70)
    logger.info("")
    
    # Track results
    successful_count = 0
    failed_count = 0
    failed_list = []
    
    total_queries = len(queries) * args.runs
    current_count = 0
    
    # Start time
    experiment_start = time.time()
    
    # Main execution loop
    for query_obj in queries:
        query_text = query_obj['query']
        query_id = query_obj['id']
        
        for run_id in range(args.runs):
            current_count += 1
            
            # Progress display
            logger.info(f"[{current_count}/{total_queries}] Query {query_id}, Run {run_id + 1}/{args.runs}")
            logger.info(f"  Query: {query_text[:60]}...")
            
            try:
                # Profile query with real RAG (Phase 2)
                metrics = profiler.profile_query(
                    query=query_text,
                    query_id=query_id,
                    run_id=run_id,
                    rag_function=rag_function
                )
                
                # Save result
                profiler.save_result(metrics)
                
                successful_count += 1
                
                # Brief result summary
                logger.info(f"  ✓ Success: {metrics['latency']['total_ms']:.0f}ms, "
                           f"CPU {metrics['cpu']['average_percent']:.1f}%, "
                           f"Memory {metrics['memory']['used_gb']:.2f}GB")
                
            except Exception as e:
                failed_count += 1
                error_msg = f"{type(e).__name__}: {str(e)}"
                
                failed_list.append({
                    "query_id": query_id,
                    "run_id": run_id,
                    "error": error_msg
                })
                
                logger.error(f"  ✗ Failed: {error_msg}")
            
            # Progress percentage
            progress = (current_count / total_queries) * 100
            elapsed = time.time() - experiment_start
            
            if current_count > 0:
                avg_time = elapsed / current_count
                remaining = (total_queries - current_count) * avg_time
                eta_mins = int(remaining / 60)
                logger.info(f"  Progress: {progress:.1f}% | ETA: ~{eta_mins} minutes")
            
            logger.info("")
    
    # Update config with final results
    update_experiment_config(
        config, output_dir,
        successful_count, failed_count, failed_list
    )
    
    # Final summary
    logger.info("=" * 70)
    logger.info("EXPERIMENT COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Total queries: {len(queries)}")
    logger.info(f"Runs per query: {args.runs}")
    logger.info(f"Total profiles: {total_queries}")
    logger.info(f"Successful: {successful_count} ({successful_count/total_queries*100:.1f}%)")
    logger.info(f"Failed: {failed_count} ({failed_count/total_queries*100:.1f}%)")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Configuration: {output_dir / 'experiment_config.json'}")
    
    duration = time.time() - experiment_start
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)
    logger.info(f"Duration: {hours}h {minutes}m {seconds}s")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
