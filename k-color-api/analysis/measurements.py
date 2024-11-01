import time
import tracemalloc

def measure_runtime(func, graph):
    """
    Measures the runtime of a function in seconds.

    :param func: The function to measure.
    :param args: Positional arguments for the function.
    :param kwargs: Keyword arguments for the function.
    :return: Time taken in seconds.
    """
    start_time = time.perf_counter()
    result = func(graph)
    end_time = time.perf_counter()
    runtime = end_time - start_time
    return result, runtime

def measure_memory(func, graph):
    """
    Measures the peak memory usage of a function in megabytes (MB).

    :param func: The function to measure.
    :param args: Positional arguments for the function.
    :param kwargs: Keyword arguments for the function.
    :return: Peak memory usage in MB.
    """
    tracemalloc.start()
    result = func(graph)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    memory_usage = peak / (1024 * 1024)  # Convert to MB
    return result, memory_usage
