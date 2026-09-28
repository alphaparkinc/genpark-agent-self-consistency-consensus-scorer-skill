import sys, json
from client import AgentSelfConsistencyConsensusScorer

def handle_mcp():
    scorer = AgentSelfConsistencyConsensusScorer()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps(scorer.run_consensus_benchmark(), indent=2))
        return

    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")
            
            if method == "initialize":
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "genpark-agent-self-consistency-consensus-scorer-skill", "version": "1.0.0"},
                    "capabilities": {"tools": {}}
                }}
            elif method == "tools/list":
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": [
                    {"name": "evaluate_consensus_vote", "description": "Evaluate multi-path reasoning paths and perform majority vote.", "inputSchema": {"type": "object", "properties": {"trajectories": {"type": "array", "items": {"type": "string"}}}}},
                    {"name": "calculate_trajectory_entropy", "description": "Compute Shannon entropy for vote distribution.", "inputSchema": {"type": "object", "properties": {"distribution": {"type": "object"}}}},
                    {"name": "run_consensus_benchmark", "description": "Run self-consistency consensus benchmark.", "inputSchema": {"type": "object"}}
                ]}}
            elif method == "tools/call":
                tname = req.get("params", {}).get("name")
                args = req.get("params", {}).get("arguments", {})
                if tname == "evaluate_consensus_vote":
                    res = scorer.evaluate_consensus_vote(args.get("trajectories", []))
                elif tname == "calculate_trajectory_entropy":
                    res = scorer.calculate_trajectory_entropy(args.get("distribution", {}))
                else:
                    res = scorer.run_consensus_benchmark()
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}
            
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "error": {"code": -32000, "message": str(e)}}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    handle_mcp()
