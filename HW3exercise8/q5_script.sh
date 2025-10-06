#!/bin/bash
# Question 5: Finding boost interval for 5% CPU guarantee
# Scenario: Long job gets starved by arriving short jobs

echo "============================================"
echo "Question 5: Priority Boost Analysis"
echo "============================================"
echo ""
echo "Workload: Long job (1000ms) vs two short jobs (200ms each)"
echo "Short jobs arrive at T=50 and T=100, starving the long job"
echo ""

# Test 1: No boost - long job starves
echo "=========================================="
echo "Test 1: No boost (B=0)"
echo "=========================================="
python3 mlfq.py --jlist 0,1000,0:50,200,0:100,200,0 -q 10 -n 3 -B 0 -c | grep -A 5 "Final statistics"
echo ""

# Test 2: Boost every 200ms
echo "=========================================="
echo "Test 2: Boost every 200ms"
echo "=========================================="
python3 mlfq.py --jlist 0,1000,0:50,200,0:100,200,0 -q 10 -n 3 -B 200 -c | grep -A 5 "Final statistics"
echo ""

# Test 3: Boost every 100ms
echo "=========================================="
echo "Test 3: Boost every 100ms"
echo "=========================================="
python3 mlfq.py --jlist 0,1000,0:50,200,0:100,200,0 -q 10 -n 3 -B 100 -c | grep -A 5 "Final statistics"
echo ""

# Test 4: Boost every 50ms
echo "=========================================="
echo "Test 4: Boost every 50ms"
echo "=========================================="
python3 mlfq.py --jlist 0,1000,0:50,200,0:100,200,0 -q 10 -n 3 -B 50 -c | grep -A 5 "Final statistics"
echo ""

echo "============================================"
echo "Answer: Boost every 200ms"
echo "Calculation: quantum / target_cpu = 10ms / 0.05 = 200ms"
echo "============================================"
