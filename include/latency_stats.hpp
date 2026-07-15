#pragma once

#include <algorithm>
#include <cmath>
#include <numeric>
#include <stdexcept>
#include <vector>

namespace md {

class LatencyStats {
public:
    void add(double value_ns) {
        samples_.push_back(value_ns);
    }

    size_t size() const {
        return samples_.size();
    }

    bool empty() const {
        return samples_.empty();
    }

    double min() const;
    double max() const;
    double mean() const;
    double median() const;
    double percentile(double p) const;
    double stddev() const;

private:
    std::vector<double> samples_;
};

} // namespace md