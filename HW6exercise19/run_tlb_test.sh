#!/bin/bash

# Bash script to test TLB size by running tlb program with increasing page counts

# Output file for results
OUTPUT="tlb_results.txt"

# Number of trials per test (adjust based on Q1 findings)
TRIALS=1000000

# Clear previous results
> $OUTPUT

echo "Testing TLB size..."
echo "Results will be saved to $OUTPUT"
echo ""

# Test with increasing number of pages (powers of 2)
for PAGES in 1 2 4 8 16 32 64 128 256 512 1024 2048
do
    echo "Testing $PAGES pages..."
    ./tlb $PAGES $TRIALS >> $OUTPUT
done

echo ""
echo "Testing complete! Results:"
cat $OUTPUT

# Optional: Create a simple visualization
echo ""
echo "Look for jumps in access time to identify TLB sizes"