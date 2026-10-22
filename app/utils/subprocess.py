from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass


@dataclass(slots=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


async def run_exec(*args: str, env: dict[str, str] | None = None) -> CommandResult:
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={**os.environ, **(env or {})},
    )
    stdout, stderr = await process.communicate()
    return CommandResult(
        returncode=process.returncode,
        stdout=stdout.decode("utf-8", errors="replace"),
        stderr=stderr.decode("utf-8", errors="replace"),
    )
