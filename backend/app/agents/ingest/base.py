from abc import ABC, abstractmethod
from typing import List, Optional
from .types import IngestContext, AgentResult
import time


class IngestAgent(ABC):
    """Bazna klasa za sve ingest agente"""
    
    def __init__(self, name: str, dependencies: Optional[List[str]] = None):
        self.name = name
        self.dependencies = dependencies or []
    
    async def execute(self, context: IngestContext) -> AgentResult:
        """Izvršava agenta i vraća rezultat"""
        start_time = time.time()
        
        try:
            # Pre-execution check
            if not self.should_execute(context):
                return AgentResult(
                    agent_name=self.name,
                    status="skipped",
                    message=f"{self.name} preskočen",
                    duration_ms=0
                )
            
            # Execute agent logic
            await self.process(context)
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Log success
            context.add_log(
                self.name,
                "success",
                f"{self.name} uspješno izvršen",
                duration_ms=duration_ms
            )
            
            return AgentResult(
                agent_name=self.name,
                status="success",
                message=f"{self.name} uspješno izvršen",
                duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = f"{self.name} greška: {str(e)}"
            
            context.add_error(error_msg)
            context.add_log(
                self.name,
                "failed",
                error_msg,
                duration_ms=duration_ms,
                error=str(e)
            )
            
            return AgentResult(
                agent_name=self.name,
                status="failed",
                message=error_msg,
                duration_ms=duration_ms,
                metadata={"error": str(e)}
            )
    
    def should_execute(self, context: IngestContext) -> bool:
        """Provjeri da li agent treba da se izvršava"""
        return True
    
    @abstractmethod
    async def process(self, context: IngestContext):
        """Glavni processing logic - MORA biti implementiran u svakom agentu"""
        pass
