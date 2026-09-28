import sys, json, math, re
from collections import Counter

class AgentSelfConsistencyConsensusScorer:
    """
    Self-Consistency & Majority Voting Consensus Scorer for Multi-Path Agent Reasoning.
    Extracts answers from chain-of-thought outputs, normalizes candidate values,
    computes Shannon entropy of consensus distribution, and selects confident winning answers.
    """
    def _extract_candidate_answer(self, text):
        # Look for explicit markdown tags or answer indicators
        patterns = [
            r"<answer>\s*([^<]+?)\s*</answer>",
            r"(?:final answer|answer is|result:)\s*[:=]?\s*([\$]?[0-9a-zA-Z\.,\-\s%]+)",
            r"####\s*([\$]?[0-9a-zA-Z\.,\-\s%]+)",
            r"\b([0-9]+(?:\.[0-9]+)?)\b"
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                raw = m.group(1).strip()
                # Clean currency, punctuation, trailing dots
                cleaned = re.sub(r"^[\$\€\£\s]+|[\.\,\s]+$", "", raw)
                return cleaned.lower()
        return text.strip().lower()

    def evaluate_consensus_vote(self, trajectories, answer_key=None):
        """
        Takes a list of trajectories (strings or dicts) and calculates majority consensus.
        """
        parsed_answers = []
        for idx, item in enumerate(trajectories):
            raw_text = item.get("text", "") if isinstance(item, dict) else str(item)
            ans = self._extract_candidate_answer(raw_text)
            parsed_answers.append({"index": idx, "answer": ans, "raw": raw_text[:120]})

        if not parsed_answers:
            return {"consensus": None, "confidence": 0.0, "distribution": {}}

        counts = Counter(p["answer"] for p in parsed_answers)
        total = len(parsed_answers)
        most_common_answer, highest_count = counts.most_common(1)[0]
        confidence = round(highest_count / total, 4)
        
        # Calculate Shannon entropy
        entropy = 0.0
        for count in counts.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        entropy = round(entropy, 4)

        return {
            "dominant_answer": most_common_answer,
            "confidence_ratio": confidence,
            "shannon_entropy": entropy,
            "total_paths": total,
            "vote_distribution": dict(counts),
            "consensus_verdict": "STRONG_CONSENSUS" if confidence >= 0.7 else ("MODERATE_CONSENSUS" if confidence >= 0.5 else "HIGH_DISAGREEMENT")
        }

    def calculate_trajectory_entropy(self, distribution_dict):
        """Compute Shannon cognitive entropy for a distribution."""
        total = sum(distribution_dict.values())
        if total <= 0: return 0.0
        entropy = 0.0
        for count in distribution_dict.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        return round(entropy, 4)

    def cluster_reasoning_paths(self, trajectories):
        """Cluster reasoning paths based on word-overlap jaccard similarity."""
        clusters = []
        for traj in trajectories:
            text = traj.get("text", "") if isinstance(traj, dict) else str(traj)
            tokens = set(re.findall(r"\b\w{3,}\b", text.lower()))
            assigned = False
            for c in clusters:
                overlap = len(tokens & c["tokens"]) / max(1, len(tokens | c["tokens"]))
                if overlap > 0.4:
                    c["members"].append(text[:100])
                    assigned = True
                    break
            if not assigned:
                clusters.append({"tokens": tokens, "members": [text[:100]]})
        
        return {
            "cluster_count": len(clusters),
            "clusters": [{"size": len(c["members"]), "samples": c["members"][:2]} for c in clusters]
        }

    def run_consensus_benchmark(self):
        sample_paths = [
            "Step 1: Calculate 15 * 4 = 60. Step 2: Add 12 to 60 = 72. Step 3: Divide by 2 = 36. <answer>36</answer>",
            "Let's compute the total. 15 * 4 is 60. Then 60 + 12 gives 72. Half of 72 is 36. Final Answer: 36",
            "First 15 * 4 = 60. Then add 12 to get 72. 72 / 2 = 36. Therefore the answer is 36.",
            "15 times 4 equals 60. 60 + 12 = 72. 72 divided by 2 is 36. #### 36",
            "Hallucinated branch: 15 * 4 = 60, add 10 = 70, divided by 2 = 35. <answer>35</answer>"
        ]
        
        consensus = self.evaluate_consensus_vote(sample_paths)
        clusters = self.cluster_reasoning_paths(sample_paths)

        return {
            "suite": "Self-Consistency Majority Scorer Benchmark",
            "consensus_analysis": consensus,
            "trajectory_clustering": clusters,
            "status": "DETERMINISTIC_CONSENSUS_REACHED"
        }
