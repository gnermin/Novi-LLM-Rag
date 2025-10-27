from typing import List, Dict
from .types import IngestContext, AgentResult
from .base import IngestAgent
import asyncio


class IngestDAG:
    """DAG orchestrator za ingest pipeline"""
    
    def __init__(self):
        self.agents: List[IngestAgent] = []
        self.dependency_graph: Dict[str, List[str]] = {}
    
    def add_agent(self, agent: IngestAgent):
        """Dodaj agenta u DAG"""
        self.agents.append(agent)
        self.dependency_graph[agent.name] = agent.dependencies
    
    async def execute(self, context: IngestContext) -> IngestContext:
        """Izvršava sve agente po dependency order-u"""
        executed = set()
        results = []
        
        # Topological sort + execution
        while len(executed) < len(self.agents):
            ready_agents = [
                agent for agent in self.agents
                if agent.name not in executed and
                all(dep in executed for dep in agent.dependencies)
            ]
            
            if not ready_agents:
                # Circular dependency or error
                context.add_error("DAG execution stuck - možda ima circular dependencies")
                break
            
            # Execute ready agents in parallel
            tasks = [agent.execute(context) for agent in ready_agents]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for agent, result in zip(ready_agents, batch_results):
                if isinstance(result, Exception):
                    context.add_error(f"{agent.name} exception: {str(result)}")
                    result = AgentResult(
                        agent_name=agent.name,
                        status="failed",
                        message=str(result),
                        duration_ms=0
                    )
                
                results.append(result)
                executed.add(agent.name)
                
                # Stop on critical failure
                if hasattr(result, 'status') and result.status == "failed" and agent.name in ["ExtractAgent", "IndexAgent"]:
                    context.add_error(f"Kritična greška u {agent.name}, zaustavljam pipeline")
                    return context
        
        return context
