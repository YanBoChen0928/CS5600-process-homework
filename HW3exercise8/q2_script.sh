#!/bin/bash
# Question 2: Reproduce examples from Chapter 8
# This script recreates all figures shown in the MLFQ chapter

echo "============================================"
echo "Question 2: Reproducing Chapter 8 Examples"
echo "============================================"
echo ""

# Figure 8.2: Single Long-Running Job Over Time
# Shows priority degradation as a 200ms job moves down through 3 queues
echo "================================================"
echo "*** Figure 8.2: Single Long-Running Job ***"
echo "A single 200ms job enters at highest priority"
echo "and gradually demotes through all 3 queues"
echo "================================================"
python3 mlfq.py --jlist 0,200,0 -n 3 -q 10 -c
echo ""
echo ""

# Figure 8.3 Left: Along Came A Short Job
# Long job A runs, then short job B arrives at T=100
# Shows how MLFQ approximates SJF for short jobs
echo "================================================"
echo "*** Figure 8.3 (Left): Along Came A Short Job ***"
echo "Job A: long-running (180ms), starts at T=0"
echo "Job B: short job (20ms), arrives at T=100"
echo "================================================"
python3 mlfq.py --jlist 0,180,0:100,20,0 -n 3 -q 10 -c
echo ""
echo ""

# Figure 8.3 Right: Interactive Job with I/O
# Long job A competes with interactive job B that does I/O
# Job B stays at high priority due to frequent I/O
echo "================================================"
echo "*** Figure 8.3 (Right): Interactive Job with I/O ***"
echo "Job A: long-running CPU-bound (180ms)"
echo "Job B: interactive, does I/O every 1ms"
echo "================================================"
python3 mlfq.py --jlist 0,180,0:100,20,1 -n 3 -q 10 -i 5 -c
echo ""
echo ""

# Figure 8.4: Priority Boost Mechanism
# Demonstrates starvation without boost vs. progress with boost
echo "================================================"echo "*** Figure 8.4: Priority Boost ***"
echo "Without boost (-B 0): Long job starves when short jobs arrive"
echo "With boost (-B 50): Long job makes progress via periodic boost"
echo ""
echo "--- WITHOUT Priority Boost ---"
python3 mlfq.py --jlist 0,180,0:100,20,0:120,20,0 -n 3 -q 10 -B 0 -c
echo ""
echo "--- WITH Priority Boost (every 50ms) ---"
python3 mlfq.py --jlist 0,180,0:100,20,0:120,20,0 -n 3 -q 10 -B 50 -c
echo ""
echo ""

# Figure 8.5: Gaming Attack Prevention
# Old rules (4a/4b) allow gaming vs. new Rule 4 prevents it
echo "================================================"
echo "*** Figure 8.5: Gaming Attack Prevention ***"
echo "Job tries to game scheduler by doing I/O before quantum expires"
echo "Old rules (-S flag): Gaming succeeds, job dominates CPU"
echo "New rules: Gaming fails, job demotes normally"
echo ""
echo "--- WITH Gaming (Old Rules 4a/4b, using -S flag) ---"
python3 mlfq.py --jlist 0,200,9:0,200,0 -n 3 -q 10 -S -c
echo ""
echo "--- WITHOUT Gaming (New Rule 4, better accounting) ---"
python3 mlfq.py --jlist 0,200,9:0,200,0 -n 3 -q 10 -c
echo ""
echo ""

echo "============================================"
echo "All Chapter 8 examples completed!"
echo "============================================"
