from collections import Counter
import threading

_lock = threading.Lock()
http_requests_total = Counter()
http_requests_by_path_total = Counter()
http_requests_by_method_total = Counter()

def track_request(path: str, method: str) -> None:
    """Tracks a request and increments the appropriate metrics."""
    with _lock:
        http_requests_total['total'] += 1
        http_requests_by_path_total[path] += 1
        http_requests_by_method_total[method] += 1

def generate_metrics() -> str:
    """Generates a string of all metrics in Prometheus format."""
    with _lock:
        metrics = []
        metrics.append(f'# HELP http_requests_total Total number of HTTP requests.')
        metrics.append(f'# TYPE http_requests_total counter')
        metrics.append(f'http_requests_total {http_requests_total["total"]}')

        metrics.append(f'\n# HELP http_requests_by_path_total Total number of HTTP requests by path.')
        metrics.append(f'# TYPE http_requests_by_path_total counter')
        for path, count in http_requests_by_path_total.items():
            metrics.append(f'http_requests_by_path_total{{path="{path}"}} {count}')

        metrics.append(f'\n# HELP http_requests_by_method_total Total number of HTTP requests by method.')
        metrics.append(f'# TYPE http_requests_by_method_total counter')
        for method, count in http_requests_by_method_total.items():
            metrics.append(f'http_requests_by_method_total{{method="{method}"}} {count}')

        return "\n".join(metrics)

def reset_metrics() -> None:
    """Resets all metrics to their initial state."""
    with _lock:
        http_requests_total.clear()
        http_requests_by_path_total.clear()
        http_requests_by_method_total.clear()