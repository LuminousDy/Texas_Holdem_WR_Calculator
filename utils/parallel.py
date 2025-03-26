import multiprocessing
import numpy as np
from concurrent.futures import ProcessPoolExecutor

def split_workload(total_items, num_workers):
    """
    Split workload evenly among workers.
    
    Args:
        total_items (int): Total number of items to process
        num_workers (int): Number of workers
    
    Returns:
        list: List of (start, end) tuples for each worker
    """
    items_per_worker = total_items // num_workers
    remaining = total_items % num_workers
    
    workloads = []
    start = 0
    
    for i in range(num_workers):
        extra = 1 if i < remaining else 0
        end = start + items_per_worker + extra
        workloads.append((start, end))
        start = end
    
    return workloads

def parallel_map(func, items, num_workers=None):
    """
    Apply a function to each item in parallel.
    
    Args:
        func (callable): Function to apply to each item
        items (iterable): Items to process
        num_workers (int, optional): Number of workers. Default is CPU count.
    
    Returns:
        list: Results from applying func to each item
    """
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(func, items))
    
    return results

def parallel_execute(func, args_list, num_workers=None):
    """
    Execute a function with different arguments in parallel.
    
    Args:
        func (callable): Function to execute
        args_list (list): List of argument tuples for each function call
        num_workers (int, optional): Number of workers. Default is CPU count.
    
    Returns:
        list: Results from each function call
    """
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(func, *args) for args in args_list]
        results = [future.result() for future in futures]
    
    return results

# Try to use GPU acceleration if available
try:
    import numba
    has_gpu = numba.cuda.is_available()
except (ImportError, AttributeError):
    has_gpu = False

def get_computation_device():
    """
    Check if GPU acceleration is available.
    
    Returns:
        str: 'gpu' if available, otherwise 'cpu'
    """
    return 'gpu' if has_gpu else 'cpu'
