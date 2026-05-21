"""
Handler for Meraki 'settings_changed' webhook events.
Parses the payload and converts it into a Webex-friendly markdown diff view.
"""

import json
import logging
from src.wxSender import outbox_str_only
from src.converters import utc_iso_to_tz_offset
from src.handler import RuntimeLoader

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------

def _safe_json_loads(value):
    """Try to parse a JSON string. Return original value if parsing fails."""
    if not value:
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def _diff_dicts(old: dict, new: dict, prefix: str = "") -> list[str]:
    """
    Recursively compare two dicts and return markdown-formatted diff lines.
    Only changed fields are returned.
    """
    diffs = []
    all_keys = set(old.keys()) | set(new.keys())

    for key in sorted(all_keys):
        full_key = f"{prefix}.{key}" if prefix else key
        old_val = old.get(key)
        new_val = new.get(key)

        if old_val == new_val:
            continue   # Skip unchanged fields

        # Recurse into nested dicts
        if isinstance(old_val, dict) and isinstance(new_val, dict):
            diffs.extend(_diff_dicts(old_val, new_val, full_key))
        # Handle nested lists of dicts
        elif isinstance(old_val, list) and isinstance(new_val, list):
            diffs.extend(_diff_lists(old_val, new_val, full_key))
        # Leaf values: show the change
        else:
            diffs.append(f"- **`{full_key}`**: `{old_val}` → `{new_val}`")

    return diffs


def _diff_lists(old: list, new: list, prefix: str = "") -> list[str]:
    """Compare two lists element by element and return diff lines."""
    diffs = []
    max_len = max(len(old), len(new))

    for i in range(max_len):
        old_item = old[i] if i < len(old) else None
        new_item = new[i] if i < len(new) else None

        if old_item == new_item:
            continue

        entry_prefix = f"{prefix}[{i}]"

        if isinstance(old_item, dict) and isinstance(new_item, dict):
            diffs.extend(_diff_dicts(old_item, new_item, entry_prefix))
        elif old_item is None:
            diffs.append(f"- ➕ **Added** `{entry_prefix}`: `{new_item}`")
        elif new_item is None:
            diffs.append(f"- ➖ **Removed** `{entry_prefix}`: `{old_item}`")
        else:
            diffs.append(f"- **`{entry_prefix}`**: `{old_item}` → `{new_item}`")

    return diffs


def _extract_changes(payload: dict) -> list[dict]:
    """Pull out and parse all changes from the payload."""
    alert_data = payload.get("alertData", {})
    changes = alert_data.get("changes", {})

    extracted = []
    for change_key, details in changes.items():
        extracted.append({
            "key": change_key,
            "label": details.get("label", change_key),
            "old": _safe_json_loads(details.get("oldText", "")),
            "new": _safe_json_loads(details.get("newText", "")),
            "changed_by": details.get("changedBy", "Unknown"),
        })
    return extracted


# ----------------------------------------------------------------------
# Markdown builder
# ----------------------------------------------------------------------

def build_markdown(payload: dict) -> str:
    """Build a Webex-friendly markdown message showing only what changed."""

    # Header info
    org_name      = payload.get("organizationName", "N/A")
    network_name  = payload.get("networkName", "N/A")
    network_url   = payload.get("networkUrl", "")
    alert_type    = payload.get("alertType", "N/A")
    occurred_at   = payload.get("occurredAt", "N/A")
    setting_name  = payload.get("alertData", {}).get("name", "N/A")
    setting_url   = payload.get("alertData", {}).get("url", "")
    tz_offset     = RuntimeLoader().TZ_OFFSET

    # Build setting link if URL fragment exists
    setting_link = (
        f"[{setting_name}]({network_url.rstrip('/')})"
        if setting_url else setting_name
    )

    md = [
        f"### 🔔 {alert_type}: {setting_link}",
        "",
        #f"- **Organization:** {org_name}",
        f"- **Network:** [{network_name}]({network_url})",
        f"- **Occurred At:** `{(utc_iso_to_tz_offset(occurred_at, tz_offset))}`",
        "",
        "---",
        "",
    ]

    changes = _extract_changes(payload)

    if not changes:
        md.append("_No changes detected in payload._")
        return "\n".join(md)

    for change in changes:
        md.append(f"#### 🔧 {change['label']}")
        md.append(f"*Changed by:* `{change['changed_by']}`")
        md.append("")

        old, new = change["old"], change["new"]

        # Determine the structure and produce diff lines
        if isinstance(old, list) and isinstance(new, list):
            diff_lines = _diff_lists(old, new)
        elif isinstance(old, dict) and isinstance(new, dict):
            diff_lines = _diff_dicts(old, new)
        else:
            diff_lines = [f"- `{old}` → `{new}`"]

        if diff_lines:
            md.extend(diff_lines)
        else:
            md.append("_No field-level changes detected._")

        md.append("")

    return "\n".join(md)


# ----------------------------------------------------------------------
# Event processor (entry point called by dispatch_event)
# ----------------------------------------------------------------------

def event_processor(payload: dict):
    """Main entry point for settings_changed events."""
    logger.info(f"Processing settings_changed event for: {payload.get('networkName')}")

    try:
        markdown_body = build_markdown(payload)
        logger.debug(f"Generated markdown:\n{markdown_body}")

        # Forward to Webex
        return outbox_str_only(markdown_body)

    except Exception as e:
        logger.error(f"Failed to process settings_changed event: {e}")
        raise