#!/bin/bash
# Question 1: Run randomly-generated MLFQ problems
# - Two jobs (-j 2)
# - Two queues (-n 2)
# - Limited job length (-m 20)
# - No I/Os (-M 0)
# - Show execution trace (-c)

echo "============================================"
echo "Question 1: MLFQ with 2 Jobs, 2 Queues, No I/O"
echo "============================================"
echo ""

# Run with different random seeds to generate different problems
for seed in 1 2 3 4 5
do
    echo "================================================"
    echo "*** Running with seed $seed ***"
    echo "================================================"
    python3 mlfq.py -s $seed -j 2 -n 2 -m 20 -M 0 -c
    echo ""
    echo ""
done

echo "============================================"
echo "All simulations completed!"
echo "============================================"
