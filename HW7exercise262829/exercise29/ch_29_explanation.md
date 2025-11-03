# OSTEP Chapter 29 – Lock-Based Concurrent Data Structures

**Course:** CS 5600 – Operating Systems  
**Instructor:** Logan Schmidt  
**Student:** _(Your Name)_

---

## 🧭 Overview

This homework explores how to make basic data structures thread-safe using locks,  
and how lock granularity affects both **correctness** and **performance**.

Each question builds on the previous one to teach:

- How to measure timing
- How to add locks safely
- How to scale data structures across threads
- How to trade accuracy for performance

---

## Q1 – Timer Accuracy with `gettimeofday()`

### 🌟 Purpose

Verify how precisely `gettimeofday()` measures time on your system.  
This establishes your baseline for later performance comparisons.

### 🧩 What to Do

Run:

```bash
./ch29 q1 200000
```

It samples timestamps many times and reports:

- The number of zero-delta samples
- The smallest measurable non-zero time difference (microseconds)

### 🧠 Expected Discussion

- The minimal non-zero delta shows the clock granularity.
- Most systems give 1–10 microseconds accuracy.
- This tells you how small your benchmark operations can be before noise dominates.

---

## Q2 – Simple Concurrent Counter (Single Lock)

### 🌟 Purpose

Implement the simplest possible **thread-safe counter** using one global mutex.

### 🧩 What to Do

Run:

```bash
./ch29 q2 4 1000000
```

Each thread increments the same shared counter 1M times.

### 🧠 Expected Discussion

- It works correctly (no race conditions).
- But performance degrades sharply as threads increase.
- Demonstrates **coarse-grained locking** and its scalability problem.

---

## Q3 – Approximate Counter (Per-CPU + Global)

### 🌟 Purpose

Improve scalability by allowing each thread/core to update its own **local counter**,  
and only occasionally merge it to a global counter (using a threshold).

### 🧩 What to Do

Run:

```bash
./ch29 q3 4 1000000 1024
```

Vary the threshold (e.g., 1, 16, 1024, 10000).

### 🧠 Expected Discussion

- Small threshold → more accurate but slower (frequent global locking).
- Large threshold → less accurate but faster.
- Trade-off between **accuracy and performance**.
- Same idea used in Linux kernel “sloppy counters”.

---

## Q4 – Concurrent Linked List (Single Lock vs. Hand-over-hand)

### 🌟 Purpose

Compare a linked list with:

1. **Single global lock**
2. **Hand-over-hand locking** (lock per node)

### 🧩 What to Do

Run:

```bash
./ch29 q4 4 200000
```

It builds two lists and measures concurrent lookups on each.

### 🧠 Expected Discussion

- Hand-over-hand allows more concurrency in theory.
- But locking/unlocking each node adds heavy overhead.
- Usually slower than single-lock unless the list is very large and threads rarely overlap.

---

## Q5 – Concurrent Hash Table (Global Lock)

### 🌟 Purpose

Make a hash table using **one global lock** to protect all buckets.

### 🧩 What to Do

Run:

```bash
./ch29 q5 4 200000 101
```

### 🧠 Expected Discussion

- Correct but not scalable.
- Every insert or lookup locks the entire structure.
- Becomes a bottleneck when many threads operate in parallel.

---

## Q6 – Concurrent Hash Table (Per-bucket Locks)

### 🌟 Purpose

Add **a lock per bucket** to increase concurrency.

### 🧩 What to Do

Run:

```bash
./ch29 q6 4 200000 101
```

### 🧠 Expected Discussion

- Each thread can work on different buckets concurrently.
- Much better scalability with multiple threads.
- Demonstrates **fine-grained locking** principle.
- Mirrors real-world concurrent hash map design.

---

## 🗾 Summary Table

| Question | Concept     | Lock Type            | Main Goal                         | Key Insight                |
| -------- | ----------- | -------------------- | --------------------------------- | -------------------------- |
| Q1       | Timer       | –                    | Measure baseline timing precision | System timer granularity   |
| Q2       | Counter     | Single global lock   | Ensure correctness                | Safe but not scalable      |
| Q3       | Counter     | Local + global       | Balance accuracy vs speed         | Approximate counting works |
| Q4       | Linked List | Per-list vs per-node | Test lock granularity             | More locks ≠ always faster |
| Q5       | Hash Table  | Global lock          | Baseline correctness              | Coarse-grained bottleneck  |
| Q6       | Hash Table  | Per-bucket locks     | Improve concurrency               | Fine-grained scalability   |

---

## 📈 Optional Extension

You can log results to CSV and plot threads vs. time using Python or Excel.  
That visualizes the scaling curve — it should look like:

- Steep increase for Q2
- Flat or near-perfect scaling for Q3/Q6 (large threshold / per-bucket)

---

## 💬 Final Note

When explaining this in interview or oral defense:

> “I verified correctness using mutual exclusion, then progressively refined lock granularity to improve scalability while preserving thread safety.”

This demonstrates both **systems reasoning** and **performance thinking**.
