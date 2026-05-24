"""
handler.py — Webhook event routing and dispatch.

Responsibilities:
- Load and expose runtime environment configuration (RuntimeEnv singleton)
- Validate incoming webhook payloads (PayloadValidator)
- Dispatch payloads to the correct event processor (sync or async)
- Provide a default fallback handler for unknown event types
"""

import os
import logging
import importlib
import inspect
from functools import lru_cache

from src.exceptions import InvalidPayloadExceptionError
from src.wxtask import event_to_wx

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Event routing map
# ----------------------------------------------------------------------
EVENT_MAP = {
    "motion_alert":      "src.motionAlert",
    "sensor_alert":      "src.sensorAlert",
    "settings_changed":  "src.settingsChanged",
    "mi_alert":          "src.miAlert",
    "sensor_automation": "src.sensorAutomation",
}


# ----------------------------------------------------------------------
# Runtime Environment Loader (singleton, secret-aware)
# ----------------------------------------------------------------------
class RuntimeEnv:
    """
    Loads runtime configuration from environment variables.

    Use `get_runtime_env()` to obtain the shared singleton instance.
    Secrets are stored on private attributes and accessed via properties
    to make accidental leakage less likely.
    """

    # Required env keys for the app to function
    REQUIRED_ENV_KEYS = (
        "MERAKI_API_URL",
        "M_API_KEY",
        "WX_TOKEN",
        "M_WEBHOOK_SHARED_SECRET",
    )

    def __init__(self):
        # --- Public, non-sensitive config ---
        self.TZ_OFFSET: int = int(os.getenv("TZ_OFFSET", "0"))
        self.MERAKI_API_URL: str = os.getenv("MERAKI_API_URL", "")
        self.M_ORG_ID: str = os.getenv("M_ORG_ID", "")
        self.WX_API_URL: str = os.getenv("WX_API_URL", "")
        self.WX_ROOM_ID: str = str(os.getenv("WX_ROOM_ID", ""))

        # --- Private, sensitive config ---
        self._M_API_KEY: str = os.getenv("M_API_KEY", "")
        self._WX_TOKEN: str = os.getenv("WX_TOKEN", "")
        self._WH_SHAREDSECRET: str = os.getenv("M_WEBHOOK_SHARED_SECRET", "")

        # Validate immediately so misconfiguration fails fast at startup
        self._validate()

    # --- Controlled access to secrets via properties ---
    @property
    def meraki_api_key(self) -> str:
        return self._M_API_KEY

    @property
    def webex_token(self) -> str:
        return self._WX_TOKEN

    @property
    def webhook_shared_secret(self) -> str:
        return self._WH_SHAREDSECRET
    
    # Temporary backward-compat aliases — remove after migration complete
    @property
    def M_API_KEY(self) -> str:
        return self._M_API_KEY

    @property
    def WX_TOKEN(self) -> str:
        return self._WX_TOKEN

    @property
    def WH_SHAREDSECRET(self) -> str:
        return self._WH_SHAREDSECRET

    # --- Backward-compatible attribute access (preserve existing call sites) ---
    # NOTE: This `__getitem__` keeps existing code like `runtime_env["MERAKI_API_URL"]` working.
    # Prefer the property access (e.g., runtime_env.meraki_api_key) in new code.
    def __getitem__(self, item: str):
        # Map legacy keys to their property/attribute names if needed
        legacy_map = {
            "M_API_KEY": "meraki_api_key",
            "WX_TOKEN": "webex_token",
            "WH_SHAREDSECRET": "webhook_shared_secret",
        }
        attr_name = legacy_map.get(item, item)
        if hasattr(self, attr_name):
            return getattr(self, attr_name)
        raise KeyError(f"RuntimeEnv has no key '{item}'")

    # --- Security: prevent accidental secret leakage ---
    def __repr__(self) -> str:
        return (
            f"<RuntimeEnv configured "
            f"org={self.M_ORG_ID or 'unset'} "
            f"meraki_api={'set' if self.MERAKI_API_URL else 'unset'} "
            f"secrets={'loaded' if self._has_all_secrets() else 'missing'}>"
        )

    __str__ = __repr__

    def __reduce__(self):
        # Prevent pickling/serialization (which would expose secrets)
        raise TypeError("RuntimeEnv instances cannot be serialized")

    def _has_all_secrets(self) -> bool:
        return all((self._M_API_KEY, self._WX_TOKEN, self._WH_SHAREDSECRET))

    def _validate(self) -> None:
        """Fail fast if required env vars are missing."""
        missing = [
            key for key in self.REQUIRED_ENV_KEYS
            if not os.getenv(key)
        ]
        if missing:
            logger.error(f"Missing required environment variables: {missing}")
            raise EnvironmentError(
                f"RuntimeEnv: missing required env vars: {missing}"
            )
        logger.info("RuntimeEnv: all required environment variables loaded")

    def env_check(self) -> str:
        """Public health-check method (returns a safe summary string)."""
        valid = self._has_all_secrets()
        return f"Env keys valid: {valid}"


@lru_cache(maxsize=1)
def get_runtime_env() -> RuntimeEnv:
    """
    Return a single shared RuntimeEnv instance for the lifetime of the process.

    Lazily instantiated on first call; subsequent calls return the cached instance.
    """
    return RuntimeEnv()


# ----------------------------------------------------------------------
# Payload Validator (stateless, per-request)
# ----------------------------------------------------------------------
class PayloadValidator:
    """
    Stateless validator for incoming webhook payloads.

    Use the class method `validate()` directly — no instantiation required.
    """

    REQUIRED_KEYS = ("alertType", "occurredAt", "networkName", "alertData")

    @classmethod
    def validate(cls, payload: dict) -> str:
        """
        Validate that required keys are present and non-empty.

        Returns a status string on success.
        Raises InvalidPayloadExceptionError on failure.
        """
        if not isinstance(payload, dict):
            raise InvalidPayloadExceptionError(
                "Invalid Payload: expected a dict"
            )

        missing = [
            key for key in cls.REQUIRED_KEYS
            if not payload.get(key)
        ]
        if missing:
            logger.error(f"Invalid Payload: missing keys {missing}")
            raise InvalidPayloadExceptionError(
                f"Error: Invalid Payload - Missing keys: {missing}"
            )

        return "Payload valid: True"


# ----------------------------------------------------------------------
# Default fallback handler
# ----------------------------------------------------------------------
def default_event_handler(payload: dict):
    """Handle event types that aren't in EVENT_MAP."""
    logger.info(f'Using default event handler for: {payload.get("alertTypeId")}')
    try:
        return event_to_wx(payload)
    except KeyError:
        logger.error("event_to_wx failed: Invalid Key Error!")
        raise
    except Exception as e:
        logger.warning(f"event_to_wx failed: Processing error! {e}")
        return e


# ----------------------------------------------------------------------
# Async-aware dispatcher
# ----------------------------------------------------------------------
async def dispatch_event(payload: dict):
    """
    Dispatch payload to the correct event_processor.

    Supports both sync and async processors during gradual async migration.
    """
    alert_type = payload.get("alertTypeId")
    module_name = EVENT_MAP.get(alert_type)

    if not module_name:
        logger.info(f"Event Type '{alert_type}' undefined, using default handler")
        return default_event_handler(payload)

    try:
        logger.info(f"{alert_type} event trigger...")
        module = importlib.import_module(module_name)
        processor = module.event_processor

        # Detect async vs sync processor and call appropriately
        if inspect.iscoroutinefunction(processor):
            return await processor(payload)
        return processor(payload)

    except Exception as e:
        logger.error(f"Failed to process event '{alert_type}': {e}")
        return default_event_handler(payload)


# ----------------------------------------------------------------------
# Entry point: validation + dispatch
# ----------------------------------------------------------------------
async def webhook_triage(payload: dict):
    """Top-level entry point for processing an incoming webhook."""
    logger.info("Webhook Triage")

    runtime_env = get_runtime_env()   # Singleton — one instance per process
    payload_status = PayloadValidator.validate(payload)
    logger.info(f"{runtime_env.env_check()} | {payload_status}")

    return await dispatch_event(payload)