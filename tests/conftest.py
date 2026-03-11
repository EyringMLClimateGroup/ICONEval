from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

import iconeval._dependencies
import iconeval._job

pytest.register_assert_rewrite("tests.integration")


@pytest.fixture
def expected_output_dir() -> Path:
    return Path(__file__).absolute().parent / "expected_output"


@dataclass
class PatchedProcess:
    returncode: int


class PatchedPopen:
    def __init__(
        self,
        returncode: int,
        stdout: str = "STDOUT",
        stderr: str = "STDERR",
    ) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def poll(self) -> int:
        return self.returncode

    def communicate(self) -> tuple[str, str]:
        return (self.stdout, self.stderr)


class PatchedSubprocess:
    PIPE = "PatchedPIPE"

    def __init__(self, returncode: int) -> None:
        self.returncode = returncode

    def run(self, *_: Any, **__: Any) -> PatchedProcess:
        return PatchedProcess(returncode=self.returncode)

    def Popen(self, *_: Any, **__: Any) -> PatchedPopen:  # noqa: N802
        return PatchedPopen(self.returncode)


@pytest.fixture
def patched_subprocess_return_0(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(iconeval._dependencies, "subprocess", PatchedSubprocess(0))
    monkeypatch.setattr(iconeval._job, "subprocess", PatchedSubprocess(0))


@pytest.fixture
def patched_subprocess_return_1(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(iconeval._dependencies, "subprocess", PatchedSubprocess(1))
    monkeypatch.setattr(iconeval._job, "subprocess", PatchedSubprocess(1))


@pytest.fixture
def sample_data_path() -> Path:
    return Path(__file__).absolute().parent / "sample_data"
