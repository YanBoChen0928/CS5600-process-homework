import subprocess
import matplotlib.pyplot as plt

# Set parameters
address_space_size = 1024
limit_values = [0, 128, 256, 384, 512, 640, 768, 896, 1024]
seeds = [0, 1, 2]  # Use multiple seeds for verification
n_addresses = 1000  # Generate 1000 addresses

# Collect data
fractions = []

for limit in limit_values:
    valid_counts = []
    
    for seed in seeds:
        # Execute command
        cmd = f"python3 relocation.py -s {seed} -n {n_addresses} -l {limit} -c"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Count number of VALID addresses
        valid_count = result.stdout.count("VALID")
        valid_counts.append(valid_count)
    
    # Calculate average fraction
    avg_fraction = sum(valid_counts) / len(valid_counts) / n_addresses
    fractions.append(avg_fraction * 100)  # Convert to percentage
    print(f"Limit = {limit}: {avg_fraction*100:.1f}% valid")

# Create plot
plt.figure(figsize=(10, 6))
plt.plot(limit_values, fractions, marker='o', linewidth=2, markersize=8, label='Experimental')
plt.xlabel('Limit (bytes)', fontsize=12)
plt.ylabel('Valid Address Fraction (%)', fontsize=12)
plt.title('Valid Address Fraction vs Limit Register Value', fontsize=14)
plt.grid(True, alpha=0.3)
plt.xlim(-50, 1100)
plt.ylim(-5, 105)

# Add theoretical line
theoretical = [(l / address_space_size * 100) for l in limit_values]
plt.plot(limit_values, theoretical, 'r--', label='Theoretical (Limit/1024)', alpha=0.7)
plt.legend()

plt.savefig('question5_graph.png', dpi=300, bbox_inches='tight')
print("\nGraph saved as question5_graph.png")
plt.show()