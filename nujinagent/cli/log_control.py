from loguru import logger

__all__ = ["_set_nujinagent_logs"]


def _set_nujinagent_logs(enabled: bool) -> None:
    if enabled:
        logger.enable("nujinagent")
    else:
        logger.disable("nujinagent")
