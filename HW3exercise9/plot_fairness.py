import matplotlib.pyplot as plt

# my data files
files = [
    ("R=10", "out_R10_s1.txt"),
    ("R=100", "out_R100_s1.txt"),
    ("R=1000", "out_R1000_s1.txt")
]

R_values = []
F_values = []

for label, filename in files:
    with open(filename) as f:
        lines = [line.strip() for line in f if "--> JOB" in line]
        if len(lines) >= 2:
            time1 = int(lines[0].split("time")[-1])
            time2 = int(lines[1].split("time")[-1])
            F = min(time1, time2) / max(time1, time2)
            R_values.append(int(label.split('=')[-1]))
            F_values.append(F)
            print(f"{label}: Job times = {time1}, {time2}, Fairness F = {F:.3f}")

# Plotting the results
plt.figure(figsize=(6, 4))
plt.plot(R_values, F_values, marker='o')
plt.xscale('log')
plt.ylim(0.8, 1.02)
plt.xlabel("Job Length (R)")
plt.ylabel("Fairness Ratio (F)")
plt.title("Fairness vs. Job Length (Lottery Scheduling)")
plt.grid(True)
plt.show()
