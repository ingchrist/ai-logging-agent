from .log_reader import read_log_file, list_log_files, search_logs


def get_log_tools():
    """Return all log analysis tools"""
    return [read_log_file, list_log_files, search_logs]
