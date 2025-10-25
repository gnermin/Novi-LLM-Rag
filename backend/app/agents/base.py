from abc import ABC, abstractmethod
from typing import Optional
from app.agents.types import ProcessingContext, AgentResult, AgentStatus


class BaseAgent(ABC):
    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
    
    async def execute(self, context: ProcessingContext) -> ProcessingContext:
        if not self.enabled:
            result = AgentResult(
                agent_name=self.name,
                status=AgentStatus.SKIPPED,
                message=f"{self.name} is disabled"
            )
            context.add_result(result)
            return context
        
        try:
            result = AgentResult(
                agent_name=self.name,
                status=AgentStatus.PROCESSING,
                message=f"Starting {self.name}"
            )
            context.add_result(result)
            
            context = await self.process(context)
            
            result = AgentResult(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                message=f"{self.name} completed successfully"
            )
            context.add_result(result)
            
        except Exception as e:
            result = AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                message=f"{self.name} failed",
                error=str(e)
            )
            context.add_result(result)
        
        return context
    
    @abstractmethod
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        pass
