#!/usr/bin/env python3

import matplotlib.pyplot as plt

# Read data from tlb_results.txt
pages = []
times = []

with open('tlb_results.txt', 'r') as f:
    for line in f:
        p, t = line.strip().split()
        pages.append(int(p))
        times.append(float(t))

# Create plot
plt.figure(figsize=(10, 6))
plt.plot(pages, times, 'o-', color='orange', linewidth=2, markersize=8)

plt.xlabel('Number Of Pages', fontsize=14)
plt.ylabel('Time Per Access (ns)', fontsize=14)
plt.title('TLB Size Measurement', fontsize=16)

# Use log scale for x-axis to better show the pattern
plt.xscale('log')
plt.xticks([1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048], 
           ['1', '2', '4', '8', '16', '32', '64', '128', '256', '512', '1024', '2048'])

plt.grid(True, alpha=0.3)
plt.tight_layout()

# Save and show
plt.savefig('tlb_graph.png', dpi=300)
print("Graph saved to tlb_graph.png")
plt.show()
