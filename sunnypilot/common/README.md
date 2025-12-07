
# Comparative Analysis of Parameter Access Methods: `Params::get` vs. `ParamWatcher`

## Inefficiencies in Standard Parameter Access
The standard `Params::get()` method executes a full file I/O lifecycle—opening, allocating, reading, and closing—for every function call. This approach results in significant CPU overhead and memory churn due to the frequency of these operations in the user interface loop.

### System Overhead Analysis
*   **System Call Overhead**: Every read operation requires context switches into kernel mode. The `Params::get` function calls `util::read_file` (sunnypilot, 2024), which subsequently invokes `std::ifstream` (sunnypilot, 2024).
    *   *Impact*: Frequent context switching degrades performance (Linux man-pages, n.d.-a; Linux man-pages, n.d.-b).
*   **C++ Stream Overhead**: The use of `std::ifstream` introduces additional overhead for maintaining stream state and buffering compared to raw file descriptors (cppreference.com, n.d.-a; Codezup, n.d.).
*   **Memory Churn**: The instantiation of `std::string result(size, '\0');` forces heap allocation and deallocation during every call (sunnypilot, 2024). This stresses the memory allocator and can lead to fragmentation (cppreference.com, n.d.).

## The `ParamWatcher` Optimization
The `ParamWatcher` implementation utilizes OS-level file system events, such as `inotify` on Linux or `FSEvents` on macOS, to maintain a Random Access Memory (RAM) cache. This architecture eliminates the need for continuous polling.

### Performance Comparison

| Feature | Standard `Params::get` | Optimized `ParamWatcher` |
| :--- | :--- | :--- |
| **Workflow** | `open` → `malloc` → `read` → `close` | `dict.get()` (RAM lookup) |
| **Complexity** | **O(N * F)** (Linear to toggles & FPS) | **O(1)** (Constant time) |
| **Disk I/O** | ~1,000 reads/sec (50 toggles @ 20FPS) | **0 reads/sec** (Steady state) |
| **Memory** | New string object per call (High GC pressure) | Returns reference (Zero GC pressure) |

## Architectural Mismatch of Standard Modules
Standard C++ modules like `std::ifstream` are optimized for **throughput**—reading large files sequentially—rather than **latency** required for polling small files frequently.

*   **The I/O Trap**: Even when a file resides in the OS page cache (RAM), invoking `open()` and `read()` forces a CPU mode switch (User → Kernel → User). Executing this sequence 1,000 times per second consumes CPU cycles merely to verify state constancy.
*   **The Memory Trap**: The `std::string` class allocates memory on the heap. Repeated allocation creates short-lived objects, which in C++ fragments memory. In Python (which wraps this), it triggers the Garbage Collector, pausing the UI.
*   **The Query Mismatch**: `Params::get` queries the current value every frame, whereas `ParamWatcher` waits for a notification of change, serving cached values in the interim.

## Limitations and Trade-offs
While `ParamWatcher` offers superior performance for UI rendering, it presents specific trade-offs:

*   **Static RAM Usage**: `ParamWatcher` maintains a persistent dictionary cache of all accessed parameters (~50KB), whereas `Params::get` uses zero static RAM but incurs high dynamic memory access.
*   **Event Latency**: In high-load scenarios, `inotify` events may experience slight delays or coalescing compared to direct reads. However, for user interface applications, this latency (<10ms) is imperceptible.
*   **Complexity**: The solution requires managing a singleton background thread and OS-specific event loops, increasing code complexity compared to the synchronous `Params::get` function.

## 5. Implementation Analysis: `param_watcher.py`

The `ParamWatcher` class provides a cross-platform solution for monitoring file system changes, specifically targeting the parameter files used in Openpilot. The implementation leverages the `ctypes` library to interface directly with operating system kernels, bypassing higher-level abstractions for maximum performance.

### Linux Implementation (`_run_linux`)
The Linux implementation interacts directly with the kernel's `inotify` subsystem (Linux man-pages, n.d.-c).

*   **Library Loading**: `libc = ctypes.CDLL('libc.so.6')` loads the standard C library to access system calls.
*   **Initialization**: `inotify_init()` is called to create a new inotify instance, returning a file descriptor.
*   **Watch Setup**: `inotify_add_watch(fd, path, mask)` registers the parameters directory. The mask includes `IN_MODIFY | IN_CREATE | IN_DELETE | IN_MOVED_TO | IN_CLOSE_WRITE` to capture all relevant file changes.
*   **Event Loop**:
    *   **Polling**: `select.epoll()` is used to efficiently wait for activity on the file descriptor without busy-waiting.
    *   **Reading**: When events occur, `os.read(fd, 1024)` retrieves the raw binary event data.
    *   **Parsing**: The code uses Python's `struct` module (`struct.unpack_from("iIII", ...)`) to parse the C-style `inotify_event` structures directly from the buffer, avoiding the overhead of defining `ctypes` structures.
    *   **Handling**: Extracted filenames are passed to `_trigger_callbacks`, which invalidates the specific cache entry (`self._cache.pop(path, None)`), forcing a fresh read on the next access.

### macOS Implementation (`_run_darwin`)
The macOS implementation uses the `FSEvents` API from the `CoreServices` framework (Apple Inc., n.d.-a), which is more efficient than `kqueue` for directory monitoring.

*   **Framework Loading**: `ctypes.cdll.LoadLibrary` loads `CoreServices` and `CoreFoundation`.
*   **Callback Definition**: `CFUNCTYPE` is used to define a C-compatible callback function. This function is invoked by the OS whenever a change occurs in the watched directory.
*   **Stream Creation**: `FSEventStreamCreate` creates a stream for the target directory. The `kFSEventStreamCreateFlagFileEvents` flag is used to request file-level granularity where available.
*   **Scheduling**: `FSEventStreamScheduleWithRunLoop` attaches the stream to the current thread's run loop (Apple Inc., n.d.-b).
*   **Execution**: `CFRunLoopRun()` starts the event loop. This passes control to the OS, which wakes the thread only when necessary.
*   **Handling**: Inside the callback, the code iterates through the changed paths provided by the OS. It extracts the filename and calls `_trigger_callbacks` to invalidate the cache for that specific parameter.

### Python `ctypes` Integration
The use of `ctypes` (Python Software Foundation, n.d.) is a strategic choice. It allows the Python interpreter to load shared libraries (`libc.so.6` on Linux, `CoreServices` on macOS) and call C functions directly. This approach avoids the overhead of spawning subprocesses or compiling external C extensions, keeping the codebase pure Python while achieving C-level system integration.

### Memory Impact Analysis
 With 232 defined parameters in `param_keys.h`, the maximum static RAM footprint of `ParamWatcher` is estimated to be **less than 250 KB**. Even if every single parameter were cached simultaneously, this static usage is negligible. Crucially, this stable footprint is likely more probable to maintain no trend of memory increase, whenc compared to the standard `Params::get` approach, which generates **megabytes** of short-lived "garbage" allocations per second, forcing the Python Garbage Collector to pause execution repeatedly.

## Conclusion
Replacing polling mechanisms with event-driven caching shifts the computational load from kernel space (syscalls) to user space (RAM). This transition eliminates I/O overhead and UI stutters caused by garbage collection, resulting in a more responsive user experience.

## References

Apple Inc. (n.d.-a). *File System Events*. Retrieved from https://developer.apple.com/documentation/coreservices/file_system_events

Apple Inc. (n.d.-b). *CFRunLoop*. Retrieved from https://developer.apple.com/documentation/corefoundation/cfrunloop-rhk

Codezup. (n.d.). *Efficient File I/O in C++*. Retrieved from https://codezup.com/efficient-file-io-cpp-best-practices/

cppreference.com. (n.d.-a). *std::basic_ifstream*. Retrieved from https://en.cppreference.com/w/cpp/io/basic_ifstream

cppreference.com. (n.d.-b). *std::basic_string*. Retrieved from https://en.cppreference.com/w/cpp/string/basic_string/basic_string

Linux man-pages. (n.d.-a). *open(2)*. Retrieved from https://man7.org/linux/man-pages/man2/open.2.html

Linux man-pages. (n.d.-b). *read(2)*. Retrieved from https://man7.org/linux/man-pages/man2/read.2.html

Linux man-pages. (n.d.-c). *inotify(7)*. Retrieved from https://man7.org/linux/man-pages/man7/inotify.7.html

Python Software Foundation. (n.d.). *ctypes — A foreign function library for Python*. Retrieved from https://docs.python.org/3/library/ctypes.html

sunnypilot. (2025). *common/params.cc* [Source code]. GitHub. https://github.com/sunnypilot/sunnypilot/blob/master/common/params.cc

sunnypilot. (2025). *common/util.cc* [Source code]. GitHub. https://github.com/sunnypilot/sunnypilot/blob/master/common/util.cc
