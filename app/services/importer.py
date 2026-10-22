from __future__ import annotations

import logging

from app.core.config import Settings
from app.utils.subprocess import CommandResult, run_exec

logger = logging.getLogger(__name__)


class Importer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def import_incoming(self) -> CommandResult:
        env = {}
        if self.settings.beets_config_path:
            env["BEETSDIR"] = str(self.settings.beets_config_path.parent)
        result = await run_exec(self.settings.beet_bin, "import", "-q", str(self.settings.incoming_dir), env=env)
        logger.info("beet import finished rc=%s stdout=%s stderr=%s", result.returncode, result.stdout, result.stderr)
        return result
