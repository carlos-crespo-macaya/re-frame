"""ADK Configuration management for re-frame agents."""

import logging
from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from config.settings import get_settings

logger = logging.getLogger(__name__)


class AgentConfiguration(BaseModel):
    """Configuration for individual agents."""

    name: str
    model_name: str = Field(default="gemini-1.5-flash")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, gt=0)
    timeout_seconds: int = Field(default=30, gt=0)
    retry_attempts: int = Field(default=3, ge=0)
    enable_tools: bool = Field(default=True)
    enable_observability: bool = Field(default=True)
    custom_instructions: str | None = None


class WorkflowConfiguration(BaseModel):
    """Configuration for multi-agent workflows."""

    name: str
    enabled_agents: list[str] = Field(default=["intake", "cbt", "synthesis"])
    max_workflow_duration_seconds: int = Field(default=60, gt=0)
    enable_crisis_detection: bool = Field(default=True)
    crisis_escalation_threshold: str = Field(default="high")
    transparency_level: str = Field(
        default="detailed", regex="^(minimal|standard|detailed|educational)$"
    )
    session_timeout_hours: int = Field(default=24, gt=0)
    enable_session_persistence: bool = Field(default=True)


class ADKSettings(BaseSettings):
    """ADK-specific settings for re-frame."""

    # Model settings
    adk_model_provider: str = Field(
        default="gemini", description="Model provider (gemini, openai, etc.)"
    )
    adk_model_name: str = Field(default="gemini-1.5-flash", description="Model name to use")
    adk_model_temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Model temperature"
    )
    adk_model_max_tokens: int = Field(default=2048, gt=0, description="Maximum tokens per response")

    # Performance settings
    adk_timeout_seconds: int = Field(default=30, gt=0, description="Request timeout in seconds")
    adk_retry_attempts: int = Field(default=3, ge=0, description="Number of retry attempts")
    adk_concurrent_requests: int = Field(default=5, gt=0, description="Max concurrent requests")

    # Observability settings
    adk_enable_observability: bool = Field(
        default=True, description="Enable observability features"
    )
    adk_enable_debug_mode: bool = Field(default=False, description="Enable debug mode")
    adk_log_level: str = Field(default="INFO", description="Logging level")
    adk_trace_retention_hours: int = Field(default=24, gt=0, description="How long to keep traces")

    # Session settings
    adk_session_timeout_hours: int = Field(default=24, gt=0, description="Session timeout")
    adk_max_sessions: int = Field(default=1000, gt=0, description="Maximum concurrent sessions")
    adk_enable_session_persistence: bool = Field(
        default=True, description="Enable session persistence"
    )

    # Safety settings
    adk_enable_crisis_detection: bool = Field(default=True, description="Enable crisis detection")
    adk_crisis_escalation_threshold: str = Field(
        default="high", description="Crisis escalation threshold"
    )
    adk_content_filtering_enabled: bool = Field(
        default=True, description="Enable content filtering"
    )

    # Tool settings
    adk_enable_tools: bool = Field(default=True, description="Enable tool usage")
    adk_tool_timeout_seconds: int = Field(default=10, gt=0, description="Tool execution timeout")

    class Config:
        env_prefix = "ADK_"
        case_sensitive = False


class ADKConfigurationManager:
    """Manager for ADK configuration."""

    def __init__(self):
        """Initialize configuration manager."""
        self.settings = ADKSettings()
        self.agent_configs: dict[str, AgentConfiguration] = {}
        self.workflow_configs: dict[str, WorkflowConfiguration] = {}

        # Initialize default configurations
        self._initialize_default_configs()

        logger.info("Initialized ADK Configuration Manager")

    def _initialize_default_configs(self):
        """Initialize default agent and workflow configurations."""
        # Default agent configurations
        self.agent_configs = {
            "intake": AgentConfiguration(
                name="ADKIntakeAgent",
                model_name=self.settings.adk_model_name,
                temperature=0.3,  # Lower temperature for more consistent validation
                max_tokens=1024,  # Smaller responses for intake
                timeout_seconds=self.settings.adk_timeout_seconds,
                retry_attempts=self.settings.adk_retry_attempts,
            ),
            "cbt": AgentConfiguration(
                name="ADKCBTFrameworkAgent",
                model_name=self.settings.adk_model_name,
                temperature=self.settings.adk_model_temperature,
                max_tokens=self.settings.adk_model_max_tokens,
                timeout_seconds=self.settings.adk_timeout_seconds,
                retry_attempts=self.settings.adk_retry_attempts,
            ),
            "synthesis": AgentConfiguration(
                name="ADKSynthesisAgent",
                model_name=self.settings.adk_model_name,
                temperature=0.8,  # Higher temperature for more creative synthesis
                max_tokens=self.settings.adk_model_max_tokens,
                timeout_seconds=self.settings.adk_timeout_seconds,
                retry_attempts=self.settings.adk_retry_attempts,
            ),
        }

        # Default workflow configuration
        self.workflow_configs["default"] = WorkflowConfiguration(
            name="default_reframe_workflow",
            enabled_agents=["intake", "cbt", "synthesis"],
            max_workflow_duration_seconds=60,
            enable_crisis_detection=self.settings.adk_enable_crisis_detection,
            crisis_escalation_threshold=self.settings.adk_crisis_escalation_threshold,
            transparency_level="detailed",
            session_timeout_hours=self.settings.adk_session_timeout_hours,
            enable_session_persistence=self.settings.adk_enable_session_persistence,
        )

    def get_agent_config(self, agent_name: str) -> AgentConfiguration | None:
        """Get configuration for a specific agent."""
        return self.agent_configs.get(agent_name)

    def set_agent_config(self, agent_name: str, config: AgentConfiguration):
        """Set configuration for a specific agent."""
        self.agent_configs[agent_name] = config
        logger.info(f"Updated configuration for agent: {agent_name}")

    def get_workflow_config(
        self, workflow_name: str = "default"
    ) -> WorkflowConfiguration | None:
        """Get workflow configuration."""
        return self.workflow_configs.get(workflow_name)

    def set_workflow_config(self, workflow_name: str, config: WorkflowConfiguration):
        """Set workflow configuration."""
        self.workflow_configs[workflow_name] = config
        logger.info(f"Updated workflow configuration: {workflow_name}")

    def get_model_config(self) -> dict[str, Any]:
        """Get model configuration for ADK agents."""
        base_settings = get_settings()

        return {
            "provider": self.settings.adk_model_provider,
            "model_name": self.settings.adk_model_name,
            "temperature": self.settings.adk_model_temperature,
            "max_tokens": self.settings.adk_model_max_tokens,
            "api_key": base_settings.google_ai_api_key,
            "timeout": self.settings.adk_timeout_seconds,
        }

    def get_observability_config(self) -> dict[str, Any]:
        """Get observability configuration."""
        return {
            "enabled": self.settings.adk_enable_observability,
            "debug_mode": self.settings.adk_enable_debug_mode,
            "log_level": self.settings.adk_log_level,
            "trace_retention_hours": self.settings.adk_trace_retention_hours,
        }

    def get_session_config(self) -> dict[str, Any]:
        """Get session management configuration."""
        return {
            "timeout_hours": self.settings.adk_session_timeout_hours,
            "max_sessions": self.settings.adk_max_sessions,
            "enable_persistence": self.settings.adk_enable_session_persistence,
        }

    def get_safety_config(self) -> dict[str, Any]:
        """Get safety and crisis detection configuration."""
        return {
            "enable_crisis_detection": self.settings.adk_enable_crisis_detection,
            "crisis_threshold": self.settings.adk_crisis_escalation_threshold,
            "content_filtering": self.settings.adk_content_filtering_enabled,
        }

    def get_tool_config(self) -> dict[str, Any]:
        """Get tool configuration."""
        return {
            "enabled": self.settings.adk_enable_tools,
            "timeout_seconds": self.settings.adk_tool_timeout_seconds,
        }

    def update_from_dict(self, config_dict: dict[str, Any]):
        """Update configuration from dictionary."""
        for key, value in config_dict.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
                logger.info(f"Updated setting: {key} = {value}")

    def validate_configuration(self) -> dict[str, Any]:
        """Validate current configuration and return any issues."""
        issues = []
        warnings = []

        # Validate model settings
        if self.settings.adk_model_temperature < 0 or self.settings.adk_model_temperature > 2:
            issues.append("Model temperature must be between 0 and 2")

        if self.settings.adk_model_max_tokens <= 0:
            issues.append("Max tokens must be greater than 0")

        # Validate performance settings
        if self.settings.adk_timeout_seconds <= 0:
            issues.append("Timeout must be greater than 0 seconds")

        if self.settings.adk_concurrent_requests <= 0:
            issues.append("Concurrent requests must be greater than 0")

        # Validate agent configurations
        for agent_name, config in self.agent_configs.items():
            if config.temperature < 0 or config.temperature > 2:
                issues.append(f"Agent {agent_name}: temperature must be between 0 and 2")

            if config.max_tokens <= 0:
                issues.append(f"Agent {agent_name}: max_tokens must be greater than 0")

        # Warnings for potentially problematic settings
        if self.settings.adk_model_temperature > 1.5:
            warnings.append("High temperature (>1.5) may result in inconsistent responses")

        if self.settings.adk_timeout_seconds < 10:
            warnings.append("Very low timeout (<10s) may cause frequent timeouts")

        if not self.settings.adk_enable_crisis_detection:
            warnings.append("Crisis detection is disabled - this may be unsafe for production")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
        }

    def export_configuration(self) -> dict[str, Any]:
        """Export current configuration."""
        return {
            "adk_settings": self.settings.dict(),
            "agent_configs": {name: config.dict() for name, config in self.agent_configs.items()},
            "workflow_configs": {
                name: config.dict() for name, config in self.workflow_configs.items()
            },
            "validation": self.validate_configuration(),
        }

    def import_configuration(self, config_data: dict[str, Any]):
        """Import configuration from exported data."""
        try:
            # Update ADK settings
            if "adk_settings" in config_data:
                for key, value in config_data["adk_settings"].items():
                    if hasattr(self.settings, key):
                        setattr(self.settings, key, value)

            # Update agent configs
            if "agent_configs" in config_data:
                for agent_name, config_dict in config_data["agent_configs"].items():
                    self.agent_configs[agent_name] = AgentConfiguration(**config_dict)

            # Update workflow configs
            if "workflow_configs" in config_data:
                for workflow_name, config_dict in config_data["workflow_configs"].items():
                    self.workflow_configs[workflow_name] = WorkflowConfiguration(**config_dict)

            logger.info("Successfully imported configuration")

        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            raise


# Global configuration manager instance
config_manager = ADKConfigurationManager()
