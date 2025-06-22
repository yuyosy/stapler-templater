import subprocess
import sys
from pathlib import Path

MAIN_PATH = Path(__file__).parent.parent / "src" / "main.py"
TEST_DATA_PATH = Path(Path.cwd() / "tests" / "data")


def test_main_integration():
    config_path = TEST_DATA_PATH / "config.yaml"
    cmd = [
        sys.executable,
        str(MAIN_PATH),
        "--config",
        str(config_path),
        "--input",
        str(TEST_DATA_PATH),
        "--recipes",
        "r1",
        "r2",
    ]
    result = subprocess.run(cmd, cwd=TEST_DATA_PATH, capture_output=True, text=True)
    assert result.returncode == 0, f"STDERR: {result.stderr}"
    assert (TEST_DATA_PATH / "output.txt").exists(), "output.txt not found"
    assert (TEST_DATA_PATH / "fsm_output.txt").exists(), "fsm_output.txt not found"
    with (TEST_DATA_PATH / "expected_output.txt").open("r", encoding="utf-8") as f:
        expected_output = f.read()
    with (TEST_DATA_PATH / "output.txt").open("r", encoding="utf-8") as f:
        output = f.read()
    assert output == expected_output, "Output does not match expected output"
    with (TEST_DATA_PATH / "expected_fsm_output.txt").open("r", encoding="utf-8") as f:
        expected_fsm_output = f.read()
    with (TEST_DATA_PATH / "fsm_output.txt").open("r", encoding="utf-8") as f:
        fsm_output = f.read()
    assert fsm_output == expected_fsm_output, (
        "FSM output does not match expected FSM output"
    )
