#pragma once

#include <string>
#include <iostream>
#include <mutex>
#include <fstream>
#include <chrono>
#include <iomanip>
#include <sstream>

namespace ramdisk {

enum class LogLevel {
    DEBUG = 0,
    INFO  = 1,
    WARNING = 2,
    ERROR = 3
};

class Logger {
public:
    static Logger& instance() {
        static Logger inst;
        return inst;
    }

    void setLevel(LogLevel level) { level_ = level; }

    void log(LogLevel level, const std::string& msg) {
        if (level < level_) return;
        std::lock_guard<std::mutex> lock(mutex_);
        auto now = std::chrono::system_clock::now();
        auto t   = std::chrono::system_clock::to_time_t(now);
        std::ostringstream oss;
        oss << std::put_time(std::localtime(&t), "%Y-%m-%d %H:%M:%S")
            << " [" << levelToString(level) << "] " << msg << '\n';
        std::cerr << oss.str();
        if (file_.is_open()) {
            file_ << oss.str();
            file_.flush();
        }
    }

    void debug  (const std::string& m) { log(LogLevel::DEBUG,   m); }
    void info   (const std::string& m) { log(LogLevel::INFO,    m); }
    void warning(const std::string& m) { log(LogLevel::WARNING, m); }
    void error  (const std::string& m) { log(LogLevel::ERROR,   m); }

    void setLogFile(const std::string& path) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (file_.is_open()) file_.close();
        file_.open(path, std::ios::app);
    }

private:
    Logger() = default;
    ~Logger() { if (file_.is_open()) file_.close(); }

    static const char* levelToString(LogLevel l) {
        switch (l) {
            case LogLevel::DEBUG:   return "DEBUG";
            case LogLevel::INFO:    return "INFO";
            case LogLevel::WARNING: return "WARN";
            case LogLevel::ERROR:   return "ERROR";
        }
        return "UNKNOWN";
    }

    LogLevel          level_ = LogLevel::INFO;
    std::mutex        mutex_;
    std::ofstream     file_;
};

// Convenience macros
#define RD_LOG_DEBUG(msg)   ::ramdisk::Logger::instance().debug(msg)
#define RD_LOG_INFO(msg)    ::ramdisk::Logger::instance().info(msg)
#define RD_LOG_WARN(msg)    ::ramdisk::Logger::instance().warning(msg)
#define RD_LOG_ERROR(msg)   ::ramdisk::Logger::instance().error(msg)

} // namespace ramdisk