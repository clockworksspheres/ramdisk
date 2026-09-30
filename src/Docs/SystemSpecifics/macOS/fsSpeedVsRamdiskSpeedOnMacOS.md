# why is filesystem access faster than ramdisk on macos?


It usually **isn't** — a RAM disk still wins on raw sequential throughput. But for many real-world workloads, native APFS on NVMe can be *comparable* or even *faster*. Here's why:

### 1. The page cache makes "filesystem access" already hit RAM

macOS aggressively caches file data in the **buffer cache** (a portion of physical RAM). After the first read, subsequent reads are served from RAM — you're already getting "RAM disk" speeds without the virtual disk layer.

```
App → VFS → APFS → [page cache hit] → done (no SSD access)
```

So "filesystem access" in practice is often already a RAM access.

### 2. The RAM disk *steals* memory from the page cache

A `hdiutil ram://` disk **pre-allocates** a fixed chunk of RAM. That memory is no longer available for the kernel's buffer cache. If your working set is larger than the RAM disk, you get page-outs and the whole system slows down.

### 3. Virtual block device overhead

The I/O path for a RAM disk has **more software layers** than native storage:

```
Native:  App → VFS → APFS → NVMe driver → SSD controller
RAM disk: App → VFS → APFS → IOKit virtual disk → RAM
```

The virtual disk driver adds locking, block translation, and context switches. On older DDR3 Macs this overhead was negligible (NVMe was slower), but on modern Apple Silicon with 7 GB/s NVMe, the virtual disk layer can become the bottleneck.

### 4. NVMe is fast enough to close the gap

| | Throughput |
|---|---|
| Apple NVMe (M-series) | 3–7 GB/s |
| DDR4-3200 RAM (theoretical) | ~50 GB/s |
| RAM disk *effective* (through virtual disk + FS) | ~1.5–4 GB/s (varies by FS, queue depth) |

The gap between "theoretical RAM speed" and "effective RAM disk speed" is where the virtual disk layer and filesystem overhead eat the advantage.

### 5. APFS is optimized for the native path

Copy-on-write, inline compression, and clone semantics are tuned for the NVMe storage stack. A RAM disk running APFS still pays the COW metadata cost but doesn't benefit from SSD-level parallelism.

### When a RAM disk *does* win

- **Write-heavy workloads** where you want to avoid SSD wear (limited practical benefit on modern SSDs)
- **Latency-sensitive random I/O** with high queue depth (the virtual disk still avoids SSD controller latency)
- **Memory is plentiful** and your working set fits comfortably in the RAM disk

### TL;DR

The "filesystem is faster than RAM disk" observation is usually the **page cache** doing its job — your data is already in RAM, just through the normal VFS path rather than a virtual block device. The RAM disk adds a software layer *on top of* RAM while simultaneously *removing* RAM from the cache that would have served you anyway.




