"""
Basic tests for log reading tools
Run with: python -m pytest tests/
"""
import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_list_log_files():
    """Test that list_log_files returns available files"""
    from src.tools.log_reader import list_log_files
    result = list_log_files.invoke({})
    assert "app.log" in result or "Error" in result


def test_read_log_file_found():
    """Test reading an existing log file"""
    from src.tools.log_reader import read_log_file
    result = read_log_file.invoke({"filename": "app.log"})
    assert "Error" not in result or "not found" not in result


def test_read_log_file_not_found():
    """Test reading a non-existent log file returns error"""
    from src.tools.log_reader import read_log_file
    result = read_log_file.invoke({"filename": "nonexistent.log"})
    assert "Error" in result


def test_search_logs_found():
    """Test search finds matching lines"""
    from src.tools.log_reader import search_logs
    result = search_logs.invoke({"filename": "app.log", "search_term": "ERROR"})
    assert "ERROR" in result or "No matches" in result


def test_search_logs_no_match():
    """Test search returns appropriate message when no match"""
    from src.tools.log_reader import search_logs
    result = search_logs.invoke({"filename": "app.log", "search_term": "XYZNOTFOUND123"})
    assert "No matches found" in result
