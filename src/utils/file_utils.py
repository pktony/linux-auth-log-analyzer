"""
File utilities for log file processing
"""
import os
import gzip
from typing import List, Callable, TextIO, Iterator
from pathlib import Path


class FileProcessor:
    """Handles file processing operations"""
    
    @staticmethod
    def get_log_files(log_dir: str, prefix: str) -> List[str]:
        """Get list of log files with given prefix"""
        if not os.path.exists(log_dir):
            return []
            
        files = []
        for fname in os.listdir(log_dir):
            if fname.startswith(prefix):
                files.append(os.path.join(log_dir, fname))
        
        return sorted(files)
    
    @staticmethod
    def open_log_file(filepath: str) -> TextIO:
        """Open log file (supports both plain text and gzip)"""
        if filepath.endswith('.gz'):
            return gzip.open(filepath, 'rt', encoding='utf-8', errors='ignore')
        return open(filepath, 'rt', encoding='utf-8', errors='ignore')
    
    @staticmethod
    def process_log_file(filepath: str, line_processor: Callable[[str], None]) -> None:
        """Process a log file line by line"""
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return
            
        try:
            with FileProcessor.open_log_file(filepath) as f:
                for line in f:
                    line_processor(line)
        except Exception as e:
            print(f"Error processing file {filepath}: {e}")
    
    @staticmethod
    def iterate_log_files(log_dir: str, prefix: str) -> Iterator[tuple[str, TextIO]]:
        """Iterate through log files and yield (filepath, file_handle) pairs"""
        files = FileProcessor.get_log_files(log_dir, prefix)
        
        for filepath in files:
            try:
                with FileProcessor.open_log_file(filepath) as f:
                    yield filepath, f
            except Exception as e:
                print(f"Error opening file {filepath}: {e}")
                continue 