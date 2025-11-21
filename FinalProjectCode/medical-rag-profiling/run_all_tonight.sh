#!/bin/bash
# Auto-run all remaining experiments tonight
# Author: Yan-Bo Chen
# Date: November 19, 2025

echo ""
echo "================================================================================"
echo "   TONIGHT'S BATCH EXPERIMENTS - ARM M2 Pro Data Collection"
echo "================================================================================"
echo ""
echo "Experiments to run:"
echo "  1. Cardio      (27×5 = 135 profiles, ~27 min)"
echo "  2. Infection   (31×5 = 155 profiles, ~31 min)"
echo "  3. Trauma      (22×5 = 110 profiles, ~22 min)"
echo "  4. Full 100×5  (100×5 = 500 profiles, ~100 min)"
echo ""
echo "Total estimated time: ~3 hours"
echo "================================================================================"
echo ""

# Log start time
START_TIME=$(date +%s)
echo "Start time: $(date)"
echo ""

# ==============================================================================
# Experiment 1: Cardio
# ==============================================================================
echo "================================================================================"
echo "[1/4] Starting Cardio Experiment"
echo "================================================================================"
./medrag run --dataset cardio --runs 5
echo ""
echo "✓ Cardio complete"
echo ""

# ==============================================================================
# Experiment 2: Infection
# ==============================================================================
echo "================================================================================"
echo "[2/4] Starting Infection Experiment"
echo "================================================================================"
./medrag run --dataset infection --runs 5
echo ""
echo "✓ Infection complete"
echo ""

# ==============================================================================
# Experiment 3: Trauma
# ==============================================================================
echo "================================================================================"
echo "[3/4] Starting Trauma Experiment"
echo "================================================================================"
./medrag run --dataset trauma --runs 5
echo ""
echo "✓ Trauma complete"
echo ""

# ==============================================================================
# Experiment 4: Full 100×5
# ==============================================================================
echo "================================================================================"
echo "[4/4] Starting Full 100×5 Experiment"
echo "================================================================================"
./medrag run --dataset 100 --runs 5
echo ""
echo "✓ 100×5 complete"
echo ""

# ==============================================================================
# Summary
# ==============================================================================
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
HOURS=$((DURATION / 3600))
MINUTES=$(((DURATION % 3600) / 60))

echo ""
echo "================================================================================"
echo "   ALL EXPERIMENTS COMPLETE!"
echo "================================================================================"
echo ""
echo "End time: $(date)"
echo "Total duration: ${HOURS}h ${MINUTES}m"
echo ""
echo "Generated datasets:"
echo "  ✓ profiling_cardio/"
echo "  ✓ profiling_infection/"
echo "  ✓ profiling_trauma/"
echo "  ✓ profiling_data_100/"
echo ""
echo "Next steps (tomorrow):"
echo "  ./medrag analyze --output profiling_cardio"
echo "  ./medrag analyze --output profiling_infection"
echo "  ./medrag analyze --output profiling_trauma"
echo "  ./medrag analyze --output profiling_data_100"
echo ""
echo "  ./medrag visualize --output profiling_cardio"
echo "  ./medrag visualize --output profiling_infection"
echo "  ./medrag visualize --output profiling_trauma"
echo "  ./medrag visualize --output profiling_data_100"
echo ""
echo "================================================================================"
echo "Good night! 😴"
echo "================================================================================"
