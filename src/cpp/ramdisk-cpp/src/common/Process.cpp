#include "ramdisk/Process.hpp"
#include "ramdisk/Logger.hpp"

#include <sstream>
#include <cstring>
#include <algorithm>
#include <chrono>

#ifdef _WIN32
#  ifndef NOMINMAX
#    define NOMINMAX
#  endif
#  define WIN32_LEAN_AND_MEAN
#  include <windows.h>
#else
#  include <unistd.h>
#  include <sys/wait.h>
#  include <sys/select.h>
#  include <fcntl.h>
#  include <signal.h>
#  include <errno.h>
#  include <poll.h>
#endif

namespace ramdisk {

// =============================================================================
// Process – move / lifetime
// =============================================================================

Process::~Process() {
    if (started_ && !waited_) {
        kill(true);
        wait(1000);
    }
    reset();
}

Process::Process(Process&& o) noexcept {
    *this = std::move(o);
}

Process& Process::operator=(Process&& o) noexcept {
    if (this == &o) return *this;
    reset();
#ifdef _WIN32
    processHandle_ = o.processHandle_; o.processHandle_ = nullptr;
    threadHandle_  = o.threadHandle_;  o.threadHandle_  = nullptr;
    stdinWrite_    = o.stdinWrite_;    o.stdinWrite_    = nullptr;
    stdoutRead_    = o.stdoutRead_;    o.stdoutRead_    = nullptr;
    stderrRead_    = o.stderrRead_;    o.stderrRead_    = nullptr;
#else
    pid_        = o.pid_;        o.pid_        = -1;
    stdinWrite_ = o.stdinWrite_; o.stdinWrite_ = -1;
    stdoutRead_ = o.stdoutRead_; o.stdoutRead_ = -1;
    stderrRead_ = o.stderrRead_; o.stderrRead_ = -1;
#endif
    started_  = o.started_;  o.started_  = false;
    waited_   = o.waited_;   o.waited_   = false;
    exitCode_ = o.exitCode_;
    return *this;
}

void Process::reset() {
#ifdef _WIN32
    if (stdinWrite_)  { CloseHandle(static_cast<HANDLE>(stdinWrite_));  stdinWrite_  = nullptr; }
    if (stdoutRead_)  { CloseHandle(static_cast<HANDLE>(stdoutRead_));  stdoutRead_  = nullptr; }
    if (stderrRead_)  { CloseHandle(static_cast<HANDLE>(stderrRead_));  stderrRead_  = nullptr; }
    if (threadHandle_){ CloseHandle(static_cast<HANDLE>(threadHandle_));threadHandle_ = nullptr; }
    if (processHandle_){CloseHandle(static_cast<HANDLE>(processHandle_));processHandle_ = nullptr; }
#else
    if (stdinWrite_ >= 0) { ::close(stdinWrite_); stdinWrite_ = -1; }
    if (stdoutRead_ >= 0) { ::close(stdoutRead_); stdoutRead_ = -1; }
    if (stderrRead_ >= 0) { ::close(stderrRead_); stderrRead_ = -1; }
    pid_ = -1;
#endif
    started_ = false;
    waited_  = false;
    exitCode_ = -1;
}

// =============================================================================
// POSIX implementation
// =============================================================================
#ifndef _WIN32

bool Process::setupPipes(bool /*capture*/) {
    // Pipes are created inside spawn for the parent/child split.
    return true;
}

void Process::closePipeEnds(bool /*parentSide*/) {}

bool Process::spawn(const std::vector<std::string>& args, bool captureOutput) {
    if (args.empty()) return false;
    reset();

    int inPipe[2]  = {-1, -1};
    int outPipe[2] = {-1, -1};
    int errPipe[2] = {-1, -1};

    if (captureOutput) {
        if (pipe(inPipe)  != 0 ||
            pipe(outPipe) != 0 ||
            pipe(errPipe) != 0) {
            RD_LOG_ERROR("pipe() failed");
            return false;
        }
    }

    pid_t child = fork();
    if (child < 0) {
        RD_LOG_ERROR("fork() failed");
        if (captureOutput) {
            ::close(inPipe[0]);  ::close(inPipe[1]);
            ::close(outPipe[0]); ::close(outPipe[1]);
            ::close(errPipe[0]); ::close(errPipe[1]);
        }
        return false;
    }

    if (child == 0) {
        // ----- child -----
        if (captureOutput) {
            ::close(inPipe[1]);
            ::close(outPipe[0]);
            ::close(errPipe[0]);
            dup2(inPipe[0],  STDIN_FILENO);
            dup2(outPipe[1], STDOUT_FILENO);
            dup2(errPipe[1], STDERR_FILENO);
            ::close(inPipe[0]);
            ::close(outPipe[1]);
            ::close(errPipe[1]);
        }

        std::vector<char*> argv;
        argv.reserve(args.size() + 1);
        for (const auto& a : args)
            argv.push_back(const_cast<char*>(a.c_str()));
        argv.push_back(nullptr);

        execvp(argv[0], argv.data());
        // exec failed
        _exit(127);
    }

    // ----- parent -----
    if (captureOutput) {
        ::close(inPipe[0]);
        ::close(outPipe[1]);
        ::close(errPipe[1]);
        stdinWrite_ = inPipe[1];
        stdoutRead_ = outPipe[0];
        stderrRead_ = errPipe[0];

        // Non-blocking reads make communicate() with timeout easier
        fcntl(stdoutRead_, F_SETFL, fcntl(stdoutRead_, F_GETFL) | O_NONBLOCK);
        fcntl(stderrRead_, F_SETFL, fcntl(stderrRead_, F_GETFL) | O_NONBLOCK);
    }

    pid_     = static_cast<int>(child);
    started_ = true;
    waited_  = false;
    return true;
}

bool Process::spawnShell(const std::string& command, bool captureOutput) {
    return spawn({"/bin/sh", "-c", command}, captureOutput);
}

std::int64_t Process::pid() const {
    return started_ ? static_cast<std::int64_t>(pid_) : 0;
}

bool Process::running() const {
    if (!started_ || waited_) return false;
    // Non-destructive check
    int status = 0;
    pid_t r = waitpid(pid_, &status, WNOHANG);
    if (r == 0) return true;          // still running
    // reaped (or error) – treat as not running; exit code filled in wait()
    return false;
}

std::optional<int> Process::wait(int timeout_ms) {
    if (!started_) return std::nullopt;
    if (waited_)   return exitCode_;

    if (timeout_ms <= 0) {
        int status = 0;
        if (waitpid(pid_, &status, 0) < 0) return std::nullopt;
        exitCode_ = WIFEXITED(status) ? WEXITSTATUS(status) : -1;
        waited_ = true;
        return exitCode_;
    }

    // Poll with timeout
    auto deadline = std::chrono::steady_clock::now() +
                    std::chrono::milliseconds(timeout_ms);
    while (std::chrono::steady_clock::now() < deadline) {
        int status = 0;
        pid_t r = waitpid(pid_, &status, WNOHANG);
        if (r == pid_) {
            exitCode_ = WIFEXITED(status) ? WEXITSTATUS(status) : -1;
            waited_ = true;
            return exitCode_;
        }
        if (r < 0 && errno != EINTR) return std::nullopt;
        usleep(10 * 1000); // 10 ms
    }
    return std::nullopt; // timeout
}

static std::string readFdAvailable(int fd) {
    std::string out;
    char buf[4096];
    for (;;) {
        ssize_t n = ::read(fd, buf, sizeof(buf));
        if (n > 0) {
            out.append(buf, static_cast<size_t>(n));
        } else if (n == 0) {
            break; // EOF
        } else {
            if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR)
                break;
            break;
        }
    }
    return out;
}

ProcessResult Process::communicate(int timeout_ms, const std::string& stdinData) {
    ProcessResult res;
    if (!started_) {
        res.exitCode = -1;
        res.stderrStr = "process not started";
        return res;
    }

    if (!stdinData.empty()) {
        writeStdin(stdinData);
    }
    // Close stdin so the child sees EOF if it was reading
    closeStdin();

    auto deadline = (timeout_ms > 0)
        ? std::chrono::steady_clock::now() + std::chrono::milliseconds(timeout_ms)
        : (std::chrono::steady_clock::time_point::max)();

    std::string out, err;
    while (!waited_) {
        if (stdoutRead_ >= 0) out += readFdAvailable(stdoutRead_);
        if (stderrRead_ >= 0) err += readFdAvailable(stderrRead_);

        int status = 0;
        pid_t r = waitpid(pid_, &status, WNOHANG);
        if (r == pid_) {
            exitCode_ = WIFEXITED(status) ? WEXITSTATUS(status) : -1;
            waited_ = true;
            break;
        }
        if (std::chrono::steady_clock::now() >= deadline) {
            res.stdoutStr = std::move(out);
            res.stderrStr = std::move(err);
            res.exitCode  = -1;
            return res; // timeout – caller may kill()
        }
        // Small sleep to avoid busy-spin when pipes are empty
        usleep(5 * 1000);
    }

    // Drain remaining data after exit
    if (stdoutRead_ >= 0) {
        // Switch back to blocking for final drain
        fcntl(stdoutRead_, F_SETFL, fcntl(stdoutRead_, F_GETFL) & ~O_NONBLOCK);
        out += readFdAvailable(stdoutRead_);
        ::close(stdoutRead_); stdoutRead_ = -1;
    }
    if (stderrRead_ >= 0) {
        fcntl(stderrRead_, F_SETFL, fcntl(stderrRead_, F_GETFL) & ~O_NONBLOCK);
        err += readFdAvailable(stderrRead_);
        ::close(stderrRead_); stderrRead_ = -1;
    }

    res.stdoutStr = std::move(out);
    res.stderrStr = std::move(err);
    res.exitCode  = exitCode_;
    return res;
}

bool Process::kill(bool force) {
    if (!started_ || waited_) return false;
    int sig = force ? SIGKILL : SIGTERM;
    if (::kill(pid_, sig) != 0) return false;
    return true;
}

bool Process::writeStdin(const std::string& data) {
    if (stdinWrite_ < 0) return false;
    const char* p = data.data();
    size_t left = data.size();
    while (left > 0) {
        ssize_t n = ::write(stdinWrite_, p, left);
        if (n < 0) {
            if (errno == EINTR) continue;
            return false;
        }
        p += n;
        left -= static_cast<size_t>(n);
    }
    return true;
}

void Process::closeStdin() {
    if (stdinWrite_ >= 0) {
        ::close(stdinWrite_);
        stdinWrite_ = -1;
    }
}

#endif // !_WIN32

// =============================================================================
// Windows implementation
// =============================================================================
#ifdef _WIN32

bool Process::spawn(const std::vector<std::string>& args, bool captureOutput) {
    if (args.empty()) return false;
    reset();

    // Build command line with simple quoting
    std::ostringstream oss;
    for (size_t i = 0; i < args.size(); ++i) {
        if (i) oss << ' ';
        if (args[i].find_first_of(" \t\"") != std::string::npos)
            oss << '"' << args[i] << '"';
        else
            oss << args[i];
    }
    return spawnShell(oss.str(), captureOutput);
}

bool Process::spawnShell(const std::string& command, bool captureOutput) {
    reset();

    SECURITY_ATTRIBUTES sa{};
    sa.nLength = sizeof(sa);
    sa.bInheritHandle = TRUE;

    HANDLE hInR = nullptr, hInW = nullptr;
    HANDLE hOutR = nullptr, hOutW = nullptr;
    HANDLE hErrR = nullptr, hErrW = nullptr;

    if (captureOutput) {
        if (!CreatePipe(&hInR,  &hInW,  &sa, 0) ||
            !CreatePipe(&hOutR, &hOutW, &sa, 0) ||
            !CreatePipe(&hErrR, &hErrW, &sa, 0)) {
            return false;
        }
        SetHandleInformation(hInW,  HANDLE_FLAG_INHERIT, 0);
        SetHandleInformation(hOutR, HANDLE_FLAG_INHERIT, 0);
        SetHandleInformation(hErrR, HANDLE_FLAG_INHERIT, 0);
    }

    STARTUPINFOA si{};
    si.cb = sizeof(si);
    if (captureOutput) {
        si.dwFlags |= STARTF_USESTDHANDLES;
        si.hStdInput  = hInR;
        si.hStdOutput = hOutW;
        si.hStdError  = hErrW;
    }

    PROCESS_INFORMATION pi{};
    std::string cmdLine = "cmd.exe /c " + command;

    BOOL ok = CreateProcessA(
        nullptr, cmdLine.data(),
        nullptr, nullptr, TRUE,
        0, nullptr, nullptr,
        &si, &pi);

    if (captureOutput) {
        CloseHandle(hInR);
        CloseHandle(hOutW);
        CloseHandle(hErrW);
    }

    if (!ok) {
        if (captureOutput) {
            CloseHandle(hInW);
            CloseHandle(hOutR);
            CloseHandle(hErrR);
        }
        return false;
    }

    processHandle_ = pi.hProcess;
    threadHandle_  = pi.hThread;
    if (captureOutput) {
        stdinWrite_ = hInW;
        stdoutRead_ = hOutR;
        stderrRead_ = hErrR;
    }
    started_ = true;
    waited_  = false;
    return true;
}

std::int64_t Process::pid() const {
    if (!started_ || !processHandle_) return 0;
    return static_cast<std::int64_t>(GetProcessId(static_cast<HANDLE>(processHandle_)));
}

bool Process::running() const {
    if (!started_ || waited_ || !processHandle_) return false;
    DWORD code = 0;
    if (!GetExitCodeProcess(static_cast<HANDLE>(processHandle_), &code))
        return false;
    return code == STILL_ACTIVE;
}

std::optional<int> Process::wait(int timeout_ms) {
    if (!started_ || !processHandle_) return std::nullopt;
    if (waited_) return exitCode_;

    DWORD ms = (timeout_ms <= 0) ? INFINITE : static_cast<DWORD>(timeout_ms);
    DWORD r = WaitForSingleObject(static_cast<HANDLE>(processHandle_), ms);
    if (r == WAIT_TIMEOUT) return std::nullopt;
    if (r != WAIT_OBJECT_0) return std::nullopt;

    DWORD code = 0;
    GetExitCodeProcess(static_cast<HANDLE>(processHandle_), &code);
    exitCode_ = static_cast<int>(code);
    waited_ = true;
    return exitCode_;
}

static std::string readHandleAvailable(HANDLE h) {
    std::string out;
    char buf[4096];
    DWORD n = 0;
    // Peek so we don't block forever
    DWORD avail = 0;
    while (PeekNamedPipe(h, nullptr, 0, nullptr, &avail, nullptr) && avail > 0) {
        if (!ReadFile(h, buf, sizeof(buf), &n, nullptr) || n == 0) break;
        out.append(buf, n);
    }
    return out;
}

ProcessResult Process::communicate(int timeout_ms, const std::string& stdinData) {
    ProcessResult res;
    if (!started_) {
        res.exitCode = -1;
        res.stderrStr = "process not started";
        return res;
    }
    if (!stdinData.empty()) {
        writeStdin(stdinData);
    }
    closeStdin();

    auto deadline = (timeout_ms > 0)
        ? std::chrono::steady_clock::now() + std::chrono::milliseconds(timeout_ms)
        : (std::chrono::steady_clock::time_point::max)();

    std::string out, err;
    while (!waited_) {
        if (stdoutRead_) out += readHandleAvailable(static_cast<HANDLE>(stdoutRead_));
        if (stderrRead_) err += readHandleAvailable(static_cast<HANDLE>(stderrRead_));

        DWORD code = 0;
        if (GetExitCodeProcess(static_cast<HANDLE>(processHandle_), &code) &&
            code != STILL_ACTIVE) {
            exitCode_ = static_cast<int>(code);
            waited_ = true;
            break;
        }
        if (std::chrono::steady_clock::now() >= deadline) {
            res.stdoutStr = std::move(out);
            res.stderrStr = std::move(err);
            res.exitCode  = -1;
            return res;
        }
        Sleep(5);
    }

    // Final blocking drain
    if (stdoutRead_) {
        char buf[4096];
        DWORD n = 0;
        while (ReadFile(static_cast<HANDLE>(stdoutRead_), buf, sizeof(buf), &n, nullptr) && n > 0)
            out.append(buf, n);
        CloseHandle(static_cast<HANDLE>(stdoutRead_));
        stdoutRead_ = nullptr;
    }
    if (stderrRead_) {
        char buf[4096];
        DWORD n = 0;
        while (ReadFile(static_cast<HANDLE>(stderrRead_), buf, sizeof(buf), &n, nullptr) && n > 0)
            err.append(buf, n);
        CloseHandle(static_cast<HANDLE>(stderrRead_));
        stderrRead_ = nullptr;
    }

    res.stdoutStr = std::move(out);
    res.stderrStr = std::move(err);
    res.exitCode  = exitCode_;
    return res;
}

bool Process::kill(bool /*force*/) {
    if (!started_ || waited_ || !processHandle_) return false;
    return TerminateProcess(static_cast<HANDLE>(processHandle_), 1) != 0;
}

bool Process::writeStdin(const std::string& data) {
    if (!stdinWrite_) return false;
    DWORD written = 0;
    return WriteFile(static_cast<HANDLE>(stdinWrite_),
                     data.data(), static_cast<DWORD>(data.size()),
                     &written, nullptr) != 0;
}

void Process::closeStdin() {
    if (stdinWrite_) {
        CloseHandle(static_cast<HANDLE>(stdinWrite_));
        stdinWrite_ = nullptr;
    }
}

#endif // _WIN32

// =============================================================================
// Convenience wrappers (unchanged API)
// =============================================================================

ProcessResult runCommand(const std::vector<std::string>& args, bool captureOutput) {
    Process p;
    if (!p.spawn(args, captureOutput)) {
        return {-1, "", "spawn failed"};
    }
    return p.communicate();
}

ProcessResult runShell(const std::string& command, bool captureOutput) {
    Process p;
    if (!p.spawnShell(command, captureOutput)) {
        return {-1, "", "spawn failed"};
    }
    return p.communicate();
}

ProcessResult runShellSudo(const std::string& command,
                           const std::string& password,
                           bool captureOutput) {
#ifdef _WIN32
    (void)password;
    return runShell(command, captureOutput);
#else
    // sudo -S reads password from stdin; -p '' suppresses the prompt text
    Process p;
    if (!p.spawn({"sudo", "-S", "-p", "", "/bin/sh", "-c", command}, captureOutput)) {
        return {-1, "", "sudo spawn failed"};
    }
    // Password must end with newline for sudo -S
    return p.communicate(0, password + "\n");
#endif
}

} // namespace ramdisk