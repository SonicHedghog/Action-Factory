import tempfile
import subprocess
import os
from typing import Tuple

PYTEST_TIMEOUT = 12  # seconds

def run_property_test(func_code: str, test_code: str) -> Tuple[bool, str]:
    """
    Writes func_code and test_code to a temp dir, runs pytest on the test file.
    Returns (passed, combined_stdout_stderr).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        func_path = os.path.join(tmpdir, "tool.py")
        test_path = os.path.join(tmpdir, "test_tool.py")
        with open(func_path, "w", encoding="utf-8") as f:
            f.write(func_code + "\n")
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("from tool import *\n\n" + test_code + "\n")
        try:
            proc = subprocess.run(
                ["pytest", "-q", test_path],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=PYTEST_TIMEOUT
            )
            output = proc.stdout + "\n" + proc.stderr
            return (proc.returncode == 0, output)
        except subprocess.TimeoutExpired:
            return (False, "pytest timed out")