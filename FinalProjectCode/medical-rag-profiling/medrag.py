#!/usr/bin/env python3
"""
medrag CLI - Unified command-line interface for Medical RAG Profiling
Supports: run, monitor, analyze, visualize
Author: Yan-Bo Chen
"""

import argparse
import subprocess
import sys
from pathlib import Path
import platform
import psutil

# ==== Helper: detect CPU architecture ======================================
def detect_arch():
    machine = platform.machine()
    if machine == "arm64":
        return "ARM"
    if machine in ["x86_64", "AMD64"]:
        return "x86"
    return "Unknown"

# ==== Helper: maps dataset names to files ==================================
QUERY_MAP = {
    "10": "queries/medical_queries_10.json",
    "25": "queries/medical_queries_25.json",
    "100": "queries/medical_queries_100.json",

    # category queries
    "cardio": "queries/cardio_queries.json",
    "infection": "queries/infection_queries.json",
    "trauma": "queries/trauma_queries.json",
}

# ============================================================================    
#                               COMMAND: RUN
# ============================================================================    
def cmd_run(args):
    dataset = args.dataset.lower()

    if dataset not in QUERY_MAP:
        print(f"❌ Unknown dataset '{dataset}'. Available: {list(QUERY_MAP.keys())}")
        sys.exit(1)

    query_file = QUERY_MAP[dataset]

    # Output folder name: smart naming based on dataset type
    if args.prefix:
        output_dir = args.prefix
    elif dataset in ["10", "25", "100"]:
        # Numeric sets: test_25x5, test_100x5
        output_dir = f"test_{dataset}x{args.runs}"
    else:
        # Category sets: profiling_cardio, profiling_infection
        output_dir = f"profiling_{dataset}"

    arch = detect_arch()
    
    cmd = [
        sys.executable,
        "run_experiment.py",
        "--queries", query_file,
        "--runs", str(args.runs),
        "--model", args.model,
        "--output", output_dir
    ]

    print("=" * 80)
    print(" MEDICAL RAG PROFILING - EXPERIMENT RUNNER".center(80))
    print("=" * 80)
    print(f" Dataset:      {dataset}")
    print(f" Query File:   {query_file}")
    print(f" Runs:         {args.runs}")
    print(f" Model:        {args.model}")
    print(f" Architecture: {arch}")
    print(f" Output Dir:   {output_dir}")
    print("=" * 80)
    print()

    subprocess.run(cmd)

# ============================================================================    
#                           COMMAND: MONITOR
# ============================================================================    
def cmd_monitor(args):
    cmd = [
        sys.executable,
        "monitor_experiment.py",
        args.output
    ]
    subprocess.run(cmd)

# ============================================================================    
#                           COMMAND: ANALYZE
# ============================================================================    
def cmd_analyze(args):
    cmd = [
        sys.executable,
        "analyze_results.py",
        args.output
    ]
    subprocess.run(cmd)

# ============================================================================    
#                         COMMAND: VISUALIZE
# ============================================================================    
def cmd_visualize(args):
    cmd = [
        sys.executable,
        "visualize_results.py",
        args.output
    ]
    subprocess.run(cmd)

# ============================================================================    
#                              MAIN CLI
# ============================================================================    
def main():
    parser = argparse.ArgumentParser(
        prog="medrag",
        description="Unified CLI for Medical RAG Profiling"
    )

    subparsers = parser.add_subparsers(dest="command")

    # ----- run --------------------------------------------------------------
    p_run = subparsers.add_parser("run", help="Run RAG profiling experiment")
    p_run.add_argument("--dataset",
                       required=True,
                       help="10 / 25 / 100 / cardio / infection / trauma")
    p_run.add_argument("--runs",
                       type=int,
                       default=1,
                       help="How many runs per query")
    p_run.add_argument("--model",
                       default="llama3.2-cpu",
                       help="Model name used by RAG wrapper")
    p_run.add_argument("--prefix",
                       default=None,
                       help="Optional output prefix")
    p_run.set_defaults(func=cmd_run)

    # ----- monitor ----------------------------------------------------------
    p_monitor = subparsers.add_parser("monitor", help="Monitor experiment (real-time)")
    p_monitor.add_argument("--output",
                           required=True,
                           help="Output directory to monitor")
    p_monitor.set_defaults(func=cmd_monitor)

    # ----- analyze ----------------------------------------------------------
    p_analyze = subparsers.add_parser("analyze", help="Analyze finished experiment")
    p_analyze.add_argument("--output",
                           required=True,
                           help="Output directory")
    p_analyze.set_defaults(func=cmd_analyze)

    # ----- visualize --------------------------------------------------------
    p_visual = subparsers.add_parser("visualize", help="Generate plots & heatmaps")
    p_visual.add_argument("--output",
                          required=True,
                          help="Output directory")
    p_visual.set_defaults(func=cmd_visualize)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
