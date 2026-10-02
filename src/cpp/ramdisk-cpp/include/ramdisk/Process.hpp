#pragma once

/**
 * Process spawning and command execution.
 *
 * Two layers:
 *   1. Process  – spawn a child (fork/exec or CreateProcess), keep the handle,
 *                 communicate, wait, kill. Closest to Python subprocess.Popen /
 *                 the original RunWith class.
 *   2. runCommand / runShell – convenience “run to completion and return output”.
 */

#include <string>
#include <vector>
#include <optional>
#include <chrono>
#include <cstdint>

namespace ramdisk {

struct ProcessResult {
    int         exitCode = -1;
    std::string stdoutStr;
    std::string stderrStr;

    bool ok() const { return exitCode == 0; }
};

/**
 * Spawned child process.
 *
 * Typical use:
 *   Process p;
 *   p.spawn({"hdiutil", "attach", "-nomount", "ram://2048"});
 *   auto res = p.communicate();          // wait + read stdout/stderr
 *   // or
 *   p.wait();
 *   p.kill();
 */
class Process {
public:
    Process() = default;
    ~Process();

    Process(const Process&) = delete;
    Process& operator=(const Process&) = delete;
    Process(Process&& other) noexcept;
    Process& operator=(Process&& other) noexcept;

    /**
     * Spawn a new process with the given argument vector (argv[0] = executable).
     * Returns true if the process was started successfully.
     *
     * On POSIX this is fork + execvp.
     * On Windows this is CreateProcess.
     */
    bool spawn(const std::vector<std::string>& args, bool captureOutput = true);

    /**
     * Spawn via the shell (/bin/sh -c or cmd.exe /c).
     */
    bool spawnShell(const std::string& command, bool captureOutput = true);

    /** Process id of the child (0 if not running / not started). */
    std::int64_t pid() const;

    /** True if a child was started and has not been waited on yet. */
    bool running() const;

    /**
     * Block until the child exits (or until timeout).
     * Returns the exit code, or nullopt on timeout.
     * timeout_ms == 0 means wait forever.
     */
    std::optional<int> wait(int timeout_ms = 0);

    /**
     * Read remaining stdout/stderr and wait for exit.
     * Equivalent to Python Popen.communicate().
     */
    ProcessResult communicate(int timeout_ms = 0);

    /**
     * Send SIGTERM (POSIX) or TerminateProcess (Windows).
     * If force is true, uses SIGKILL / immediate terminate.
     */
    bool kill(bool force = false);

    /** Write to the child’s stdin (only if spawn was called with capture). */
    bool writeStdin(const std::string& data);

    /** Close the write end of stdin (sends EOF to the child). */
    void closeStdin();

private:
    void reset();
    bool setupPipes(bool capture);
    void closePipeEnds(bool parentSide);

#ifdef _WIN32
    void* processHandle_ = nullptr;   // HANDLE
    void* threadHandle_  = nullptr;
    void* stdinWrite_    = nullptr;
    void* stdoutRead_    = nullptr;
    void* stderrRead_    = nullptr;
#else
    int   pid_         = -1;
    int   stdinWrite_  = -1;
    int   stdoutRead_  = -1;
    int   stderrRead_  = -1;
#endif
    bool  started_     = false;
    bool  waited_      = false;
    int   exitCode_    = -1;
};

// ---------------------------------------------------------------------------
// Convenience: run to completion
// ---------------------------------------------------------------------------

/** Run argv and wait; capture stdout/stderr. */
ProcessResult runCommand(const std::vector<std::string>& args,
                         bool captureOutput = true);

/** Run a shell string and wait. */
ProcessResult runShell(const std::string& command, bool captureOutput = true);

} // namespace ramdisk