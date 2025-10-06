#!/bin/bash
# Question 6: Testing the -I (iobump) flag effect
# -I flag: Jobs finishing I/O go to FRONT of queue (not back)

echo "============================================"
echo "Question 6: I/O Bump Flag Analysis"
echo "============================================"
echo ""

# Workload: Multiple jobs with I/O operations
# Job 0: I/O every 5ms
# Job 1: I/O every 10ms
# Job 2: No I/O (CPU-bound)

echo "*** Scenario: 3 jobs, some with I/O ***"
echo "Job 0: runTime=50, I/O every 5ms"
echo "Job 1: runTime=50, I/O every 10ms"
echo "Job 2: runTime=50, no I/O"
echo ""

echo "================================================"
echo "Test 1: WITHOUT -I flag (default behavior)"
echo "I/O jobs go to BACK of queue after I/O completes"
echo "================================================"
python3 mlfq.py --jlist 0,50,5:0,50,10:0,50,0 -q 10 -n 2 -c
echo ""
echo ""

echo "================================================"
echo "Test 2: WITH -I flag"
echo "I/O jobs go to FRONT of queue after I/O completes"
echo "================================================"
python3 mlfq.py --jlist 0,50,5:0,50,10:0,50,0 -q 10 -n 2 -I -c
echo ""

echo "============================================"
echo "Analysis:"
echo "With -I flag:"
echo "- Interactive jobs (with I/O) get better response time"
echo "- I/O-bound jobs jump ahead of CPU-bound jobs"
echo "- More realistic for interactive workloads"
echo "============================================"
