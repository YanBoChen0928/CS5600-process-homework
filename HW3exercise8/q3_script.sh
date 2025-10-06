#!/bin/bash
# Question 3: Configure MLFQ to behave like a round-robin scheduler
# Round-robin means: all jobs at same priority, rotating equally

echo "============================================"
echo "Question 3: MLFQ as Round-Robin Scheduler"
echo "============================================"
echo ""

# Strategy: Use only 1 queue (no priority levels)
# All jobs stay at same priority, rotate with time quantum

echo "*** Configuration: Single queue (-n 1) ***"
echo "All jobs stay at same priority level"
echo ""

python3 mlfq.py -j 3 -n 1 -q 10 -m 30 -M 0 -c

echo ""
echo "============================================"
echo "This behaves like round-robin because:"
echo "- Only 1 queue = no priority degradation"
echo "- Jobs rotate in order with equal time slices"
echo "============================================"
