"""ADK Observability and debugging features for re-frame agents."""

import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AgentExecutionMetrics(BaseModel):
    """Metrics for agent execution."""
    
    agent_name: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    model_calls: int = 0
    tool_calls: int = 0
    tool_names: List[str] = []


class WorkflowExecutionTrace(BaseModel):
    """Trace for complete workflow execution."""
    
    workflow_id: str
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    stages_completed: List[str] = []
    agent_metrics: List[AgentExecutionMetrics] = []
    user_input: str
    final_response: Optional[str] = None
    crisis_flag: bool = False


class ADKObservabilityManager:
    """Manager for ADK agent observability and debugging."""
    
    def __init__(self):
        """Initialize observability manager."""
        self.execution_traces: Dict[str, WorkflowExecutionTrace] = {}
        self.agent_metrics: Dict[str, List[AgentExecutionMetrics]] = {}
        self.debug_mode = False
        
        logger.info("Initialized ADK Observability Manager")
    
    def enable_debug_mode(self):
        """Enable debug mode for detailed logging."""
        self.debug_mode = True
        logging.getLogger("agents").setLevel(logging.DEBUG)
        logger.info("Debug mode enabled for ADK agents")
    
    def disable_debug_mode(self):
        """Disable debug mode."""
        self.debug_mode = False
        logging.getLogger("agents").setLevel(logging.INFO)
        logger.info("Debug mode disabled for ADK agents")
    
    def start_workflow_trace(
        self, 
        workflow_id: str, 
        session_id: str, 
        user_input: str
    ) -> WorkflowExecutionTrace:
        """Start tracing a workflow execution."""
        trace = WorkflowExecutionTrace(
            workflow_id=workflow_id,
            session_id=session_id,
            start_time=datetime.utcnow(),
            user_input=user_input
        )
        
        self.execution_traces[workflow_id] = trace
        
        if self.debug_mode:
            logger.debug(f"Started workflow trace: {workflow_id}")
        
        return trace
    
    def end_workflow_trace(
        self, 
        workflow_id: str, 
        success: bool = True, 
        error: str = None,
        final_response: str = None,
        crisis_flag: bool = False
    ):
        """End a workflow trace."""
        if workflow_id not in self.execution_traces:
            logger.warning(f"No workflow trace found for ID: {workflow_id}")
            return
        
        trace = self.execution_traces[workflow_id]
        trace.end_time = datetime.utcnow()
        trace.duration_seconds = (trace.end_time - trace.start_time).total_seconds()
        trace.success = success
        trace.error = error
        trace.final_response = final_response
        trace.crisis_flag = crisis_flag
        
        if self.debug_mode:
            logger.debug(f"Ended workflow trace: {workflow_id}, success: {success}")
        
        # Log performance metrics
        self._log_workflow_performance(trace)
    
    def start_agent_execution(
        self, 
        agent_name: str, 
        execution_id: str
    ) -> AgentExecutionMetrics:
        """Start tracking an agent execution."""
        metrics = AgentExecutionMetrics(
            agent_name=agent_name,
            execution_id=execution_id,
            start_time=datetime.utcnow()
        )
        
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = []
        
        self.agent_metrics[agent_name].append(metrics)
        
        if self.debug_mode:
            logger.debug(f"Started agent execution: {agent_name} ({execution_id})")
        
        return metrics
    
    def end_agent_execution(
        self,
        execution_id: str,
        success: bool = True,
        error: str = None,
        token_usage: Dict[str, int] = None,
        tool_calls: List[str] = None
    ):
        """End an agent execution and record metrics."""
        # Find the metrics object
        metrics = None
        for agent_metrics_list in self.agent_metrics.values():
            for m in agent_metrics_list:
                if m.execution_id == execution_id:
                    metrics = m
                    break
            if metrics:
                break
        
        if not metrics:
            logger.warning(f"No agent execution found for ID: {execution_id}")
            return
        
        metrics.end_time = datetime.utcnow()
        metrics.duration_seconds = (metrics.end_time - metrics.start_time).total_seconds()
        metrics.success = success
        metrics.error = error
        
        if token_usage:
            metrics.input_tokens = token_usage.get("input_tokens", 0)
            metrics.output_tokens = token_usage.get("output_tokens", 0)
            metrics.total_tokens = token_usage.get("total_tokens", 0)
        
        if tool_calls:
            metrics.tool_calls = len(tool_calls)
            metrics.tool_names = tool_calls
        
        if self.debug_mode:
            logger.debug(f"Ended agent execution: {metrics.agent_name} ({execution_id}), success: {success}")
        
        # Add to workflow trace if available
        self._add_agent_metrics_to_workflow(metrics)
    
    def record_stage_completion(self, workflow_id: str, stage_name: str):
        """Record completion of a workflow stage."""
        if workflow_id in self.execution_traces:
            self.execution_traces[workflow_id].stages_completed.append(stage_name)
            
            if self.debug_mode:
                logger.debug(f"Completed stage '{stage_name}' in workflow {workflow_id}")
    
    def get_workflow_trace(self, workflow_id: str) -> Optional[WorkflowExecutionTrace]:
        """Get workflow trace by ID."""
        return self.execution_traces.get(workflow_id)
    
    def get_agent_metrics(self, agent_name: str) -> List[AgentExecutionMetrics]:
        """Get all metrics for a specific agent."""
        return self.agent_metrics.get(agent_name, [])
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary across all agents and workflows."""
        total_workflows = len(self.execution_traces)
        successful_workflows = sum(1 for trace in self.execution_traces.values() if trace.success)
        
        agent_stats = {}
        for agent_name, metrics_list in self.agent_metrics.items():
            successful_executions = sum(1 for m in metrics_list if m.success)
            avg_duration = sum(m.duration_seconds or 0 for m in metrics_list) / len(metrics_list) if metrics_list else 0
            total_tokens = sum(m.total_tokens or 0 for m in metrics_list)
            
            agent_stats[agent_name] = {
                "total_executions": len(metrics_list),
                "successful_executions": successful_executions,
                "success_rate": successful_executions / len(metrics_list) if metrics_list else 0,
                "average_duration_seconds": avg_duration,
                "total_tokens_used": total_tokens,
            }
        
        return {
            "total_workflows": total_workflows,
            "successful_workflows": successful_workflows,
            "workflow_success_rate": successful_workflows / total_workflows if total_workflows else 0,
            "agent_statistics": agent_stats,
            "crisis_flags": sum(1 for trace in self.execution_traces.values() if trace.crisis_flag),
        }
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """Get error analysis across all executions."""
        workflow_errors = [
            {"id": trace.workflow_id, "error": trace.error, "timestamp": trace.start_time}
            for trace in self.execution_traces.values()
            if not trace.success and trace.error
        ]
        
        agent_errors = []
        for agent_name, metrics_list in self.agent_metrics.items():
            for metrics in metrics_list:
                if not metrics.success and metrics.error:
                    agent_errors.append({
                        "agent": agent_name,
                        "execution_id": metrics.execution_id,
                        "error": metrics.error,
                        "timestamp": metrics.start_time
                    })
        
        # Categorize errors
        error_categories = {}
        all_errors = workflow_errors + agent_errors
        for error_record in all_errors:
            error_msg = error_record["error"].lower()
            if "rate limit" in error_msg or "quota" in error_msg:
                category = "rate_limiting"
            elif "timeout" in error_msg:
                category = "timeout"
            elif "auth" in error_msg:
                category = "authentication"
            elif "network" in error_msg:
                category = "network"
            else:
                category = "other"
            
            if category not in error_categories:
                error_categories[category] = 0
            error_categories[category] += 1
        
        return {
            "workflow_errors": workflow_errors,
            "agent_errors": agent_errors,
            "error_categories": error_categories,
            "total_errors": len(all_errors),
        }
    
    def export_traces(self, format: str = "json") -> str:
        """Export all traces in specified format."""
        if format == "json":
            export_data = {
                "workflow_traces": [trace.dict() for trace in self.execution_traces.values()],
                "agent_metrics": {
                    agent_name: [metrics.dict() for metrics in metrics_list]
                    for agent_name, metrics_list in self.agent_metrics.items()
                },
                "export_timestamp": datetime.utcnow().isoformat(),
                "performance_summary": self.get_performance_summary(),
            }
            return json.dumps(export_data, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def cleanup_old_traces(self, max_age_hours: int = 24):
        """Clean up traces older than specified hours."""
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        # Clean workflow traces
        old_workflow_ids = [
            wf_id for wf_id, trace in self.execution_traces.items()
            if trace.start_time < cutoff_time
        ]
        for wf_id in old_workflow_ids:
            del self.execution_traces[wf_id]
        
        # Clean agent metrics
        for agent_name in self.agent_metrics:
            self.agent_metrics[agent_name] = [
                metrics for metrics in self.agent_metrics[agent_name]
                if metrics.start_time >= cutoff_time
            ]
        
        logger.info(f"Cleaned up {len(old_workflow_ids)} old workflow traces")
    
    def _log_workflow_performance(self, trace: WorkflowExecutionTrace):
        """Log workflow performance metrics."""
        if trace.duration_seconds:
            if trace.duration_seconds > 10:  # Log slow workflows
                logger.warning(
                    f"Slow workflow detected: {trace.workflow_id} took {trace.duration_seconds:.2f}s"
                )
            elif self.debug_mode:
                logger.debug(
                    f"Workflow {trace.workflow_id} completed in {trace.duration_seconds:.2f}s"
                )
    
    def _add_agent_metrics_to_workflow(self, metrics: AgentExecutionMetrics):
        """Add agent metrics to workflow trace if applicable."""
        # Find workflow trace that contains this agent execution
        for trace in self.execution_traces.values():
            if trace.end_time is None:  # Still running
                trace.agent_metrics.append(metrics)
                break


# Global observability manager instance
observability_manager = ADKObservabilityManager()