# CS5600 HW6 Exercise 19 - TLB Measurement

## 實驗概述

測量 Translation Lookaside Buffer (TLB) 的大小和訪問成本，通過觀察不同頁數訪問時間的"跳躍點"來推測 TLB 層級結構。

---

## Q1: 計時器精度測試

### 問題

How precise is `gettimeofday()`? How long does an operation take to time it precisely?

### 答案

The timer has microsecond precision (typically 1-10 μs on modern systems). For TLB measurement where each access takes 5-70 nanoseconds, a single access is too fast to measure accurately. We need to repeat the operation approximately 200,000+ times to accumulate at least 10 milliseconds of total time, ensuring measurement error stays below 1%.

### 實測結果

```
Minimum detectable time: 1 microseconds
This is approximately: 1000 nanoseconds
Recommended iterations: 200000
```

### 關鍵代碼

```c
struct timeval start, end;
gettimeofday(&start, NULL);
// ... operations ...
gettimeofday(&end, NULL);

long elapsed_usec = (end.tv_sec - start.tv_sec) * 1000000L +
                    (end.tv_usec - start.tv_usec);
```

---

## Q2: 寫測量程序 tlb.c

### 問題

Write the program that can measure the cost of accessing each page.

### 答案

The program measures average TLB access time by accessing one integer per page in a jump pattern (stride = PAGESIZE). It repeats the access pattern many times to accumulate measurable time, then calculates nanoseconds per access. Output format: `<num_pages> <ns_per_access>`.

### 核心邏輯

```c
int jump = PAGESIZE / sizeof(int);  // 每次跳一頁

// 跳躍式訪問
for (int t = 0; t < trials; t++) {
    for (int i = 0; i < NUMPAGES * jump; i += jump) {
        a[i] += 1;  // 訪問：a[0], a[1024], a[2048]...
    }
}

// 計算平均時間
double total_accesses = (double)trials * (double)NUMPAGES;
double ns_per_access = (elapsed_usec * 1000.0) / total_accesses;
```

### 關鍵設計

- **跳躍式訪問**：每次訪問不同的頁面（隔離 TLB 效果）
- **預熱初始化**：避免 demand zeroing 干擾
- **雙精度計算**：防止大數溢出

---

## Q3: 自動化測試腳本

### 問題

Write a script to run the program with varying number of pages. How many trials are needed?

### 答案

We used 1,000,000 trials based on Q1's timer precision analysis. However, the results show measurement instability without CPU pinning. After implementing CPU pinning on Linux, stable results emerged with clear TLB transitions at 8-16 pages (2.66ns → 7.28ns).

### 測試腳本

```bash
#!/bin/bash
OUTPUT="tlb_results.txt"
TRIALS=1000000

for PAGES in 1 2 4 8 16 32 64 128 256 512 1024 2048
do
    echo "Testing $PAGES pages..."
    ./tlb $PAGES $TRIALS >> $OUTPUT
done
```

### Linux 實測結果

```
Pages   Time(ns)
1-8     2.66-2.99 ns  (L1 TLB hit)
16-32   7.28-9.00 ns  (跳躍！)
64-2048 8.98-9.46 ns  (L2 TLB hit)
```

---

## Q4: 數據視覺化

### 問題

Why does visualization make the data easier to digest?

### 答案

The graph immediately reveals what the raw numbers obscure. Our visualization shows a **dramatic visual jump between 8 pages (~2.6ns) and 32 pages (~9.2ns), with a transition zone at 16 pages (~7.3ns)**. The data then plateaus stably at ~9ns through 2048 pages. This pattern indicates **L1 TLB holds approximately 8 entries, with a gradual transition to L2 TLB usage between 8-32 pages**, followed by consistent L2 TLB hits (L2 size >2048 entries).

The jump pattern specifically isolates TLB effects because total access time = TLB time + Data Cache time + Memory time. Our **strided access pattern (jumping by PAGESIZE = 4096 bytes) ensures every access hits a different cache line**, making Data Cache consistently miss and contributing a constant overhead. Since our **total dataset (8KB) fits entirely in cache**, memory access time is negligible. Therefore, the observed time variations (2.6ns → 9ns) directly reflect TLB hierarchy transitions, not cache effects.

The human visual system excels at pattern recognition - **the steep slope between pages 8-32 immediately draws the eye**, while scanning columns of numbers requires mental calculation to notice the 3.5x increase.

### 圖表代碼

```python
#!/usr/bin/env python3
import matplotlib.pyplot as plt

pages = []
times = []

with open('tlb_results.txt', 'r') as f:
    for line in f:
        p, t = line.strip().split()
        pages.append(int(p))
        times.append(float(t))

plt.figure(figsize=(10, 6))
plt.plot(pages, times, 'o-', color='orange', linewidth=2, markersize=8)
plt.xscale('log')
plt.savefig('tlb_graph.png', dpi=300)
```

---

## Q5: 防止編譯器優化

### 問題

How can you ensure the compiler does not remove the main loop?

### 答案

Use the `-O0` compiler flag: `gcc -o tlb tlb.c -O0`. This disables compiler optimizations and ensures the loop executes exactly as written. Our testing confirmed that `-O0` alone is sufficient - adding `volatile` keywords actually introduced measurement artifacts (inconsistent timing, some values decreased unexpectedly at 256+ pages). The clean results with just `-O0` (stable 2.6ns → 9ns transition at 8-16 pages) prove the compiler is not optimizing away our memory accesses.

### 為什麼 -O0 還不是 100% 安全？

```
-O0 仍會做：
✅ 不優化：函數內聯、循環展開
❌ 可能優化：明顯的死代碼消除

但對我們的實驗：
-O0 已經足夠！
```

### 如果需要更強保護

```c
// 方法 1: volatile
volatile int *a;

// 方法 2: 編譯選項
gcc -O0 -fno-inline -fno-builtin
```

---

## Q6: CPU Pinning（綁核）

### 問題

How can you pin your code to one CPU? What happens if you don't?

### 答案

**On Linux**, use `sched_setaffinity()` to bind the process to a specific CPU core:

```c
#define _GNU_SOURCE
#include <sched.h>

void pin_to_core(int core_id) {
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(core_id, &set);
    sched_setaffinity(0, sizeof(set), &set);
}

int main() {
    pin_to_core(0);  // Pin to core 0
    // ... measurement code ...
}
```

**Without CPU pinning**, the OS scheduler can migrate the process between cores. Each CPU core has its own independent TLB, so when the process moves from Core 0 to Core 1, all TLB entries are lost and must be rebuilt. This causes:

- Inconsistent measurements (times fluctuate randomly)
- Unable to detect TLB size (no clear jumps in access time)
- Data shows noise instead of the true TLB hierarchy signal

### 對比結果

```
沒綁核（macOS）：
1-8 頁浮動在 1.19-4.84 ns（不穩定）

有綁核（Linux）：
1-8 頁穩定在 2.66-2.99 ns
16+ 頁清楚跳到 7-9 ns
```

### 為什麼每個核心有自己的 TLB？

```
硬件結構：
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Core 0  │  │ Core 1  │  │ Core 2  │
│ ┌─────┐ │  │ ┌─────┐ │  │ ┌─────┐ │
│ │ TLB │ │  │ │ TLB │ │  │ │ TLB │ │ ← 各自獨立
│ └─────┘ │  │ └─────┘ │  │ └─────┘ │
└─────────┘  └─────────┘  └─────────┘

換核 = TLB 清空 = 測量失效
```

---

## Q7: 初始化問題

### 問題

Will initialization affect timing? What can you do to counterbalance these costs?

### 答案

Yes, without initialization, the first access to each page triggers **demand zeroing** - the OS allocates a physical page and zeros it for security, causing a page fault (~microseconds). This would skew the first iteration's timing.

We prevent this by **pre-warming the array** before timing begins:

```c
// Initialize array to avoid demand zeroing overhead
for (int i = 0; i < array_size; i += jump) {
    a[i] = 0;  // Touch each page once
}

gettimeofday(&start, NULL);  // Start timing AFTER initialization
// ... measurement loop ...
```

By accessing each page once before measurement, all physical pages are allocated and zeroed. The actual measurement loop then only measures TLB behavior without page fault interference.

### Demand Zeroing 詳解

```
什麼是 Demand Zeroing？
┌─────────────────────────────┐
│ malloc() 時：               │
│   只分配 virtual address    │
│   不分配 physical memory    │
└─────────────────────────────┘
         ↓ 第一次訪問
┌─────────────────────────────┐
│ Page Fault!                 │
│ OS 才分配 physical page：   │
│   1. 找空閒 page            │
│   2. 清零 4096 bytes ← 慢！│
│   3. 映射到 virtual addr    │
└─────────────────────────────┘

代價：~1-5 微秒（vs 正常 2-9 納秒）
```

### 為什麼要清零？

```
安全性：防止讀到前一個程序的數據
時機：按需（demand）- 第一次訪問時才做
```

---

## 核心概念總結

### TLB 的作用

```
Virtual Address → TLB 查詢 → Physical Address
                    ↓ miss
              Page Table (RAM)

TLB = 地址翻譯的緩存
目的：加速 virtual → physical 轉換
```

### 實驗原理

```
訪問頁數 ≤ TLB 大小 → TLB hit → 快
訪問頁數 > TLB 大小 → TLB miss → 慢

觀察"跳躍點" → 推測 TLB 大小
```

### 為什麼跳躍式訪問？

```
連續訪問：a[0], a[1], a[2] → 都在同一頁
跳躍訪問：a[0], a[1024], a[2048] → 每次不同頁

效果：
1. 每次觸發不同的地址翻譯（測 TLB）
2. Data Cache 每次 miss（排除 cache 干擾）
3. 時間變化主要來自 TLB
```

### 實驗設計的隔離技巧

```
總時間 = TLB時間 + Data Cache時間 + Memory時間

我們的設計：
1. 跳躍訪問 → Data Cache = 常數（每次 miss）
2. 數據量小 → Memory時間 = 0（都在 cache）
3. 結果：時間變化 ≈ 只反映 TLB

這就是為什麼能測到 TLB！
```

---

## 實驗結果（Linux x86_64 服務器）

### 測量數據

```
Pages   Time(ns)   TLB狀態
1       2.99       L1 TLB hit
2       2.81       L1 TLB hit
4       2.76       L1 TLB hit
8       2.66       L1 TLB hit
16      7.28       L1 miss, L2 hit (跳躍!)
32      9.00       L2 TLB hit
64      9.06       L2 TLB hit
128     9.21       L2 TLB hit
256     9.31       L2 TLB hit
512     8.98       L2 TLB hit
1024    9.42       L2 TLB hit
2048    9.46       L2 TLB hit
```

### 結論

- **L1 TLB**: 約 8-12 entries
- **L2 TLB**: > 2048 entries
- **TLB miss 代價**: 2.66ns → 9ns（約 3.4 倍）

---

## 關鍵技術點

### 1. 計時精度

```c
// 單次太快測不到 → 重複很多次
for (int t = 0; t < 1000000; t++) {
    // 訪問操作
}
// 總時間 ÷ 次數 = 平均時間
```

### 2. 跳躍訪問模式

```c
int jump = PAGESIZE / sizeof(int);  // 1024 (4096/4)
for (i = 0; i < NUMPAGES * jump; i += jump) {
    a[i] += 1;  // 跳過一整頁
}
```

### 3. CPU Pinning (Linux)

```c
#define _GNU_SOURCE
#include <sched.h>

void pin_to_core(int core_id) {
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(core_id, &set);
    sched_setaffinity(0, sizeof(set), &set);
}
```

### 4. 避免溢出

```c
// ❌ 可能溢出
double result = (elapsed * 1000.0) / (trials * NUMPAGES);

// ✅ 安全
double total = (double)trials * (double)NUMPAGES;
double result = (elapsed * 1000.0) / total;
```

### 5. 預熱初始化

```c
// 測量前先訪問一遍，觸發所有 demand zeroing
for (int i = 0; i < array_size; i += jump) {
    a[i] = 0;
}

// 然後才開始計時
gettimeofday(&start, NULL);
```

---

## 實驗中遇到的問題與解決

### 問題 1: macOS 無法綁核

```
現象：Warning: Failed to pin to core 0
原因：macOS 限制用戶程序綁核
解決：切換到 Linux 服務器
```

### 問題 2: 負數時間

```
現象：256 頁 → -9.29 ns
原因：int 溢出（trials * NUMPAGES）
解決：強制用 double 計算
```

### 問題 3: volatile 增加額外開銷

```
現象：加 volatile 後數據變混亂
原因：dummy += a[i] 增加太多操作
解決：只用 -O0，不用 volatile
```

### 問題 4: 數據不穩定

```
現象：時間在 1-7 ns 浮動
原因：程序在多核間跳躍
解決：CPU pinning
```

---

## 重要概念複習

### TLB 是什麼？

```
TLB = Translation Lookaside Buffer
作用：緩存虛擬地址到物理地址的翻譯

位置：CPU 內部（MMU）
結構：
  L1 TLB（小而快）
  L2 TLB（大而慢）
     ↓ miss
  Page Table (RAM)

每次內存訪問：
1. 查 TLB（快，幾納秒）
2. Miss → 查 Page Table（慢，幾十納秒）
```

### TLB vs Data Cache

```
┌─────────────────┬──────────────┬──────────────┐
│                 │ TLB          │ Data Cache   │
├─────────────────┼──────────────┼──────────────┤
│ 緩存什麼        │ 地址翻譯     │ 數據本身     │
│ 在哪裡          │ CPU (MMU)    │ CPU          │
│ 大小            │ 幾十到幾百   │ KB-MB 級     │
│ Miss 代價       │ ~幾十 ns     │ ~幾十 ns     │
│ 這個實驗        │ ✅ 測這個    │ 被排除       │
└─────────────────┴──────────────┴──────────────┘
```

### PLRU (Pseudo-LRU)

```
TLB 的替換策略：

真正 LRU：
- 完全準確知道誰最久沒用
- 硬件成本高（需要記錄所有訪問順序）

PLRU：
- 用二叉樹近似記錄
- 硬件成本低（只需要 n-1 個 bits）
- 命中率 ≈ 95% of LRU

例子（4 entries）：
        bit0
       /    \
     bit1   bit2
     / \    / \
   [0][1] [2][3]

只需 3 個 bits，但接近完整 LRU 效果
```

### Demand Zeroing

```
過程：
1. malloc() → 只預留 virtual address
2. 第一次訪問 → Page Fault!
3. OS 分配 physical page
4. 清零整個頁面（4096 bytes）
5. 建立映射
6. 繼續執行

為什麼清零？
安全性 - 防止讀到前一個程序的數據

代價：
~1-5 微秒（比正常訪問慢 1000 倍）
```

---

## 關鍵命令

### 編譯

```bash
# Linux 版本（有綁核）
gcc -o tlb tlb.c -O0

# macOS 版本（無綁核）
gcc -o tlb_mac tlb_mac.c -O0
```

### 運行單次測試

```bash
./tlb <num_pages> <num_trials>
# 例如：./tlb 10 1000000
```

### 批量測試

```bash
./run_tlb_test.sh
```

### 畫圖

```bash
python3 plot_tlb.py
```

### 查看系統信息

```bash
uname -a              # 系統信息
sysctl -n hw.ncpu     # CPU 核心數（macOS）
lscpu                 # CPU 信息（Linux）
```

---

## 實驗心得

### 成功的關鍵

1. ✅ **CPU Pinning 最重要**（比 trials 數量更重要）
2. ✅ **-O0 足夠**（不需要 volatile）
3. ✅ **預熱初始化**（避免 demand zeroing）
4. ✅ **雙精度計算**（避免溢出）

### 平台差異

```
macOS：
- 不支持可靠的 CPU pinning
- 數據不穩定
- 適合學習理解

Linux：
- 完整支持 sched_setaffinity()
- 數據穩定清晰
- 適合正式測量
```

### TLB 性能影響

```
L1 TLB hit:  ~2.7 ns
L2 TLB hit:  ~9 ns   (慢 3.4 倍)
Complete miss: ~70 ns (慢 26 倍，教材數據)

結論：
TLB 對性能影響巨大！
這就是為什麼 locality 很重要
```

---

## 檔案清單

```
tlb.c              - Linux 版本（有 CPU pinning）
tlb_mac.c          - macOS 版本（無 CPU pinning）
timer_test.c       - Q1 計時器精度測試
run_tlb_test.sh    - 自動化測試腳本
plot_tlb.py        - 畫圖腳本
tlb_results.txt    - 測試結果數據
tlb_graph.png      - 結果圖表
README.md          - 本文檔
```

---

## 參考資料

- OSTEP Chapter 19: Paging - Faster Translations (TLBs)
- Saavedra-Barrera, "CPU Performance Evaluation" (1992)
- 課程：CS5600 Operating Systems, Northeastern University

---

_Created: October 27, 2025_  
_Author: YanBo Chen_  
_Platform: Linux x86_64 (login-students server)_
