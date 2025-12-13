<center>

# Comparative Analysis of Parameter Getter Methods: Params vs. ParamWatcher

James (sunnypilot Developer) <br>
December 13, 2025

</center>


## <br><br> Abstract

This research report examines the inefficiencies in standard parameter access methods within sunnypilot and proposes an optimized alternative, ParamWatcher. The standard `Params::get()` method incurs significant CPU and memory overhead due to repeated file I/O operations (sunnypilot, 2025). ParamWatcher utilizes OS-level file system events (inotify on Linux, FSEvents on macOS) to maintain an in-memory cache, reducing I/O to near zero (Linux man-pages, 2025-c; Apple Inc., n.d.-a). Empirical benchmarks with ~10 million parameter accesses demonstrate a 14.5x CPU speedup and flat memory usage (514.7 KB vs. 497.7 KB for base Params, with only 17 KB overhead). The implementation employs a process-local singleton pattern for efficiency in multi-process architectures (Gamma et al., 1994). Results indicate ParamWatcher eliminates UI stutters and GC pauses, enhancing system responsiveness without compromising data freshness.

**Keywords:** parameter access, file I/O optimization, event-driven caching, autonomous driving systems, performance benchmarking

## Introduction

In sunnypilot, efficient parameter management is important for real-time system access. The standard `Params::get()` method, implemented in C++ and wrapped in Python, performs full file I/O cycles for each access, leading to high CPU overhead and memory churn (sunnypilot, 2025). This is particularly problematic in UI loops where parameters are queried frequently (e.g., 50 toggles at 20 FPS equates to ~1,000 reads/second).

This inefficiency stems from architectural mismatches: C++ streams are designed for throughput, not latency (cppreference.com, n.d.-a). Each call triggers kernel mode switches, heap allocations, and garbage collection in Python, causing UI stutters (Linux man-pages, 2025-a; Linux man-pages, 2025-b).

### Inefficiencies in Standard Parameter Access
The standard `Params::get()` method executes a full file I/O lifecycle—opening, allocating, reading, and closing—for every function call. This results in significant CPU overhead and memory churn due to the frequency of these operations in the user interface loop.

#### System Overhead Analysis
- **System Call Overhead**: Every read operation requires context switches into kernel mode. The `Params::get` function calls `util::read_file` (sunnypilot, 2025), which subsequently invokes `std::ifstream` (sunnypilot, 2025).
- **Impact**: Frequent context switching degrades performance (Linux man-pages, 2025-a; Linux man-pages, 2025-b).
- **C++ Stream Overhead**: The use of `std::ifstream` introduces additional overhead for maintaining stream state and buffering compared to raw file descriptors (cppreference.com, n.d.-a; Codezup, 2025).
- **Memory Churn**: The instantiation of `std::string result(size, '\0');` forces heap allocation and deallocation during every call (sunnypilot, 2025). This stresses the memory allocator and can lead to fragmentation (cppreference.com, n.d.-b).

This report introduces ParamWatcher, an event-driven caching solution using OS file system events. It shifts from polling to notifications, caching converted values in static RAM. I propose that ParamWatcher achieves minimum 10x+ CPU gains with bounded non increasing memory, improving sunnypilot's performance both on latency and responsiveness.

## Method

### Materials
- **System:** sunnypilot, running on macOS, Ubuntu/Linux, comma 3x, and comma four.
- **Parameters:** 231 defined keys in `param_keys.h`.
- **Tools:** Python 3, tracemalloc for memory profiling, time.perf_counter for CPU timing, ctypes for OS integration (Python Software Foundation, 2025).

### Implementation Details
ParamWatcher provides cross-platform file system monitoring using ctypes for direct OS integration (Python Software Foundation, 2025).

#### Linux Implementation
On Linux, ParamWatcher uses the inotify subsystem for efficient file change detection (Linux man-pages, 2025-c). It loads `libc.so.6` to access system calls, initializes an inotify instance, and watches the parameters directory for events like `IN_MODIFY` and `IN_CLOSE_WRITE` (Linux Kernel Organization, 2005). Events are polled with `select.epoll()` and parsed using `struct.unpack_from()` to avoid ctypes overhead. Filenames are extracted and passed to cache invalidation, ensuring real-time updates without polling (Codezup, 2025).

- **Library Loading**: `libc = ctypes.CDLL('libc.so.6')` loads the standard C library to access system calls.
- **Initialization**: `inotify_init()` is called to create a new inotify instance, returning a file descriptor.
- **Watch Setup**: `inotify_add_watch(fd, path, mask)` registers the parameters directory. The mask includes `IN_MODIFY | IN_CREATE | IN_DELETE | IN_MOVED_TO | IN_CLOSE_WRITE` (Linux Kernel Organization, 2005) to capture all relevant file changes.
- **Event Loop**:
  - **Polling**: `select.epoll()` is used to efficiently wait for activity on the file descriptor without busy-waiting.
  - **Reading**: When events occur, `os.read(fd, 1024)` retrieves the raw binary event data.
  - **Parsing**: The code uses Python's `struct` module (`struct.unpack_from("iIII", ...)`) to parse the C-style `inotify_event` structures directly from the buffer, avoiding the overhead of defining `ctypes` structures.
  - **Handling**: Extracted filenames are passed to `_trigger_callbacks`, which invalidates the specific cache entry (`self._cache.pop(path, None)`), forcing a fresh read on the next access.

#### macOS Implementation
On macOS, ParamWatcher leverages FSEvents from CoreServices for directory monitoring (Apple Inc., n.d.-a). It defines a C-compatible callback using `CFUNCTYPE`, creates an `FSEventStream` with `kFSEventStreamCreateFlagFileEvents`, and schedules it on the run loop (Apple Inc., n.d.-b). Events are filtered for modifications, creations, and renames (Apple Inc., n.d.-c), triggering cache invalidation for affected parameters.

- **Framework Loading**: `ctypes.cdll.LoadLibrary` loads `CoreServices` and `CoreFoundation`.
- **Callback Definition**: `CFUNCTYPE` is used to define a C-compatible callback function. This function is invoked by the OS whenever a change occurs in the watched directory.
- **Stream Creation**: `FSEventStreamCreate` creates a stream for the target directory. The `kFSEventStreamCreateFlagFileEvents` flag is used to request file-level granularity where available.
- **Event Filtering**: The callback filters events using flags such as `kFSEventStreamEventFlagItemCreated` and `kFSEventStreamEventFlagItemModified` to ensure only relevant file changes trigger updates (Apple Inc., n.d.-c).
- **Scheduling**: `FSEventStreamScheduleWithRunLoop` attaches the stream to the current thread's run loop (Apple Inc., n.d.-b).
- **Execution**: `CFRunLoopRun()` starts the event loop. This passes control to the OS, which wakes the thread only when necessary.
- **Handling**: Inside the callback, the code iterates through the changed paths provided by the OS. It extracts the filename and calls `_trigger_callbacks` to invalidate the cache for that specific parameter.

### Procedure
Benchmarks simulated heavy load:
- **Memory Test:** ~10 million gets (43,290 loops over 231 keys), measured with tracemalloc.
- **CPU Test:** Same load, timed with perf_counter.
- Comparisons: Base Params vs. ParamWatcher.

## Results

### Memory Usage
Using tracemalloc for peak memory measurement during ~10 million parameter accesses (43,290 loops over 231 keys), base Params peaked at 497.7 KB, while ParamWatcher peaked at 514.7 KB (17 KB overhead). ParamWatcher's memory remained flat post-initialization, preventing churn.

| Condition | Memory (KB) | Overhead |
|-----------|-------------|----------|
| Base Params | 497.7 | - |
| ParamWatcher | 514.7 | 17 KB |
### CPU Performance
ParamWatcher was 14.5x faster: 4.52s vs. 65.43s to complete ~10 million param gets.

| Condition | Time (s) | Speedup |
|-----------|----------|---------|
| Base Params | 65.43 | 1x |
| ParamWatcher | 4.52 | 14.5x |

### Scalability
No degradation at scale; cache invalidation maintained freshness.

See Appendix A for visual graphs of memory usage over a 30-minute time span, captured on comma four. These two routes are of equal conditions: each route started completely unplugged to two minutes offroad, followed by onroad state, with ambient temperature at 75 degrees fahrenheit. These routes are direct comparisons of pre-ParamWatcher and ParamWatcher implementations. Appendix A also includes I/O capture graphs for those 30-minute routes, demonstrating reductions in file system activity post-ParamWatcher.

## Discussion

ParamWatcher successfully optimizes parameter access, delivering substantial CPU gains with minimal memory overhead. The event-driven approach eliminates I/O bottlenecks, reducing GC pressure and UI stutters (cppreference.com, n.d.-b). The 17 KB memory overhead is negligible compared to the megabytes of churn from base Params, ensuring bounded usage in multi-process environments via the singleton pattern (Gamma et al., 1994).

Results demonstrate scalability without degradation, with cache invalidation maintaining data freshness. This optimization enhances system responsiveness.
Limitations include potential event latency in high-load scenarios (<10 ms, imperceptible for UI) and increased complexity from background threads.
Trade-offs: Static RAM (~17 KB) vs. dynamic churn; benefits outweigh costs for param-heavy workloads.

## <br> Appendix A: Memory Usage Graphs

### Base Params Memory Usage
![Base Params Memory Usage](https://github.com/sunnyhaibin/sunnypilot/blob/paramwatcher/sunnypilot/common/assets/memory_usage_pre_paramwatcher.png)

### ParamWatcher Memory Usage
![ParamWatcher Memory Usage](https://github.com/sunnyhaibin/sunnypilot/blob/paramwatcher/sunnypilot/common/assets/memory_usage_00000025--d50a4a3471.png)

### Base Params IO Usage
![Base Params IO Usage](https://github.com/sunnyhaibin/sunnypilot/blob/paramwatcher/sunnypilot/common/assets/io_usage_pre_paramwatcher.png)

### ParamWatcher IO Usage
![ParamWatcher IO Usage](https://github.com/sunnyhaibin/sunnypilot/blob/paramwatcher/sunnypilot/common/assets/io_usage_param_watcher.png)


## <br>References

Apple Inc. (n.d.-a). *File System Events*. Retrieved from https://developer.apple.com/documentation/coreservices/file_system_events

Apple Inc. (n.d.-b). *CFRunLoop*. Retrieved from https://developer.apple.com/documentation/corefoundation/cfrunloop

Apple Inc. (n.d.-c). *FSEventStreamEventFlags*. Retrieved from https://developer.apple.com/documentation/coreservices/1455361-fseventstreameventflags

Codezup. (2025). *Efficient File I/O in C++*. Retrieved from https://codezup.com/efficient-file-io-cpp-best-practices/

cppreference.com. (n.d.-a). *std::basic_ifstream*. Retrieved from https://en.cppreference.com/w/cpp/io/basic_ifstream

cppreference.com. (n.d.-b). *std::basic_string*. Retrieved from https://en.cppreference.com/w/cpp/string/basic_string/basic_string

Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley.

Linux Kernel Organization. (2005). *include/uapi/linux/inotify.h*. Retrieved from https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/include/uapi/linux/inotify.h

Linux man-pages. (2025-a). *open(2)*. Retrieved from https://man7.org/linux/man-pages/man2/open.2.html

Linux man-pages. (2025-b). *read(2)*. Retrieved from https://man7.org/linux/man-pages/man2/read.2.html

Linux man-pages. (2025-c). *inotify(7)*. Retrieved from https://man7.org/linux/man-pages/man7/inotify.7.html

Python Software Foundation. (2025). *ctypes — A foreign function library for Python*. Retrieved from https://docs.python.org/3/library/ctypes.html

sunnypilot. (2025). *common/params.cc* [Source code]. GitHub. https://github.com/sunnypilot/sunnypilot/blob/master/common/params.cc#L180C1-L206C2

sunnypilot. (2025). *common/util.cc* [Source code]. GitHub. https://github.com/sunnypilot/sunnypilot/blob/master/common/util.cc#L79C1-L117C2
