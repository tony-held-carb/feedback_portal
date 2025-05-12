import arb.__get_logger as get_logger

__version__ = "1.0.0"

logger, pp_log = get_logger.get_logger(__name__, __file__, force_command_line=True)
