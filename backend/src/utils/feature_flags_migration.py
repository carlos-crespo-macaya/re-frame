"""Migration utilities for transitioning from environment-based to ConfigCat feature flags."""

from typing import Any

from src.utils.configcat_flags import get_configcat_flags
from src.utils.feature_flags import get_feature_flags as get_old_flags
from src.utils.logging import get_logger

logger = get_logger(__name__)


class FeatureFlagsMigration:
    """Handles migration from old feature flags to ConfigCat."""

    def __init__(self):
        self.old_flags = get_old_flags()
        self.new_flags = get_configcat_flags()

    def is_enabled(self, flag_name: str, user: dict[str, Any] | None = None) -> bool:
        """
        Check if a feature is enabled, with fallback to old system.

        This method provides backward compatibility during migration.
        """
        try:
            # Try ConfigCat first
            configcat_value = self.new_flags.is_enabled(flag_name, user)

            # If flag exists in old system, log any discrepancies
            if flag_name in self.old_flags.get_all_flags():
                old_value = self.old_flags.is_enabled(flag_name)
                if old_value != configcat_value:
                    logger.warning(
                        "feature_flag_discrepancy",
                        flag=flag_name,
                        old_value=old_value,
                        new_value=configcat_value,
                        message="Feature flag values differ between systems",
                    )

            return bool(configcat_value)

        except Exception as e:
            logger.error(
                "configcat_fallback_to_old",
                flag=flag_name,
                error=str(e),
                message="Falling back to old feature flag system",
            )
            # Fall back to old system
            return bool(self.old_flags.is_enabled(flag_name))

    def migrate_reactive_greeting(self, user: dict[str, Any] | None = None) -> bool:
        """
        Special migration for reactive_greeting flag.

        Maps old reactive_greeting to new system while maintaining compatibility.
        """
        # Check if reactive_greeting exists in ConfigCat
        # If not, use the old flag value
        try:
            return bool(self.new_flags.is_enabled("reactive_greeting", user))
        except Exception:
            return bool(self.old_flags.is_enabled("reactive_greeting"))

    def get_migration_status(self) -> dict[str, Any]:
        """Get status of feature flag migration."""
        old_flags = self.old_flags.get_all_flags()
        new_flags = self.new_flags.get_all_flags()

        status = {
            "old_flags": old_flags,
            "new_flags": new_flags,
            "migrated_flags": [],
            "pending_flags": list(old_flags.keys()),
            "new_only_flags": [k for k in new_flags if k not in old_flags],
        }

        # Check which flags have been migrated (exist in both systems)
        for flag in old_flags:
            if flag in new_flags:
                status["migrated_flags"].append(flag)
                status["pending_flags"].remove(flag)

        return status


# Singleton instance
_migration: FeatureFlagsMigration | None = None


def get_migration() -> FeatureFlagsMigration:
    """Get the singleton migration instance."""
    global _migration
    if _migration is None:
        _migration = FeatureFlagsMigration()
    return _migration


def is_feature_enabled_with_migration(
    flag_name: str, user: dict[str, Any] | None = None
) -> bool:
    """
    Check if a feature is enabled using migration logic.

    This is the main function to use during the migration period.
    """
    return get_migration().is_enabled(flag_name, user)
