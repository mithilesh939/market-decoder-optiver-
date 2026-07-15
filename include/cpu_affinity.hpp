#pragma once

#ifdef __linux__

#include <pthread.h>
#include <sched.h>
#include <stdexcept>

namespace md {

inline void pin_current_thread(int cpu_id)
{
    cpu_set_t cpuset;

    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);

    int rc = pthread_setaffinity_np(
        pthread_self(),
        sizeof(cpu_set_t),
        &cpuset);

    if (rc != 0)
        throw std::runtime_error("Failed to pin thread");
}

}

#else

namespace md {

inline void pin_current_thread(int)
{
}

}

#endif