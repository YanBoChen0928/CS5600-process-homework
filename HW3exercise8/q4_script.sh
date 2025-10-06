#!/bin/bash
# Question 4: Gaming the scheduler with old Rules 4a and 4b
# One job takes advantage of -S flag to get 99% CPU time

echo "============================================"
echo "Question 4: Gaming the Scheduler"
echo "============================================"
echo ""

# Strategy:
# Job 0: Issues I/O just before quantum expires (every 9ms, quantum=10ms)
#        With -S flag, it stays at high priority
# Job 1: Pure CPU job, gets demoted to low priority quickly

echo "*** Workload Design ***"
echo "Job 0: Runs 200ms, does I/O every 9ms (games the system)"
echo "Job 1: Runs 200ms, no I/O (victim job)"
echo ""

python3 mlfq.py --jlist 0,200,9:0,200,0 -q 10 -n 3 -S -c

echo ""
echo "============================================"
echo "Result Analysis:"
echo "- Job 0 issues I/O at 9ms (before 10ms quantum ends)"
echo "- With -S flag, Job 0 stays at highest priority"
echo "- Job 1 gets demoted and starves"
echo "- Job 0 achieves ~99% CPU utilization"
echo "============================================"
