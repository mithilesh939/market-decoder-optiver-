#pragma once

#include <chrono>
#include <iostream>
#include <string>

namespace md {

class ScopedProfiler {
public:
    explicit ScopedProfiler(const std::string& name)
        : name_(name),
          start_(std::chrono::steady_clock::now()) {}

    ~ScopedProfiler() {
        auto end = std::chrono::steady_clock::now();

        double us =
            std::chrono::duration<double, std::micro>(end - start_).count();

        std::cout
            << "[PROFILE] "
            << name_
            << " : "
            << us
            << " us"
            << std::endl;
    }

private:
    std::string name_;

    std::chrono::steady_clock::time_point start_;
};

}

#define PROFILE_SCOPE(name) md::ScopedProfiler profiler_##__LINE__(name)