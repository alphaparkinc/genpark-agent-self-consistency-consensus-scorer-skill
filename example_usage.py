from client import AgentSelfConsistencyConsensusScorer
import json

scorer = AgentSelfConsistencyConsensusScorer()
print("=== AGENT SELF-CONSISTENCY CONSENSUS SCORER BENCHMARK ===")
res = scorer.run_consensus_benchmark()
print(json.dumps(res, indent=2))
