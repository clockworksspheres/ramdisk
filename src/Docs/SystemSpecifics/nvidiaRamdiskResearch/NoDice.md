# Summary:

There is no cross platform way to create or access vram as a ramdisk.  One would have to write a low level driver in each operating system to access the graphics card hardware to create a ramdisk driver for each OS.

# on macOS

Without writing a low level GPU Memory driver, this is not possible on macOS.  Please see the copilot documentation.

# on Linux

This is has a better chance of success as Linux does expose GPU-side block device abstraction.  One still has to write low level driver for something close to a ramdisk to work.  There is an experimental FUSE filesystem called vramfs.  Note, it is not stable.  What is fully supported and stable on linux is CUDA/OpenCL/Vulkan/HIP GPU memory allocation.  

# on Windows

It appears This OS is somwthat of a middle ground between the two above - still requires writing a low level ramdisk driver.

# Comparison Table

|Feature|Windows|Linux|macOS|
|---|---|---|---|
|NVIDIA CUDA|✔️ Full|✔️ Full|❌ None|
|Direct GPU VRAM allocation|✔️ CUDA/D3D12/Vulkan|✔️ CUDA/Vulkan/OpenCL|✔️ Metal only|
|OS‑level VRAM filesystem|❌ No|⚠️ Experimental (`` `vramfs` ``)|❌ No|
|Build your own GPU‑side RAM disk|✔️ Yes|✔️ Yes|✔️ Yes|
|Best platform for GPU VRAM experiments|**Windows or Linux**|**Linux**|macOS (limited)|

# References:

See the "copilotNvidiaRamdiskResearch" document.

