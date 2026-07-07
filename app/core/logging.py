import logging
import re

SENSITIVE_PATTERNS = [
    re.compile(r"(password|secret|token|key|auth)\s*[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"X-Auth-Mock\s*[=:]\s*\S+", re.IGNORECASE),
]

MASK_VALUE = "[REDACTED]"


class SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern in SENSITIVE_PATTERNS:
                record.msg = pattern.sub(r"\1=" + MASK_VALUE, record.msg)
        if record.args and isinstance(record.args, dict):
            record.args = {
                k: MASK_VALUE
                if any(p.search(str(k)) for p in SENSITIVE_PATTERNS)
                else v
                for k, v in record.args.items()
            }
        return True


def setup_log_masking() -> None:
    root_logger = logging.getLogger()
    root_logger.addFilter(SensitiveDataFilter())
