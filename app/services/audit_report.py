from typing import List, Dict, Any

class AuditReport:
    def __init__(self, rule_results: List[Dict[str, Any]]):
        self.rule_results = rule_results
        self.score = self._calculate_score()
        self.summary = self._generate_summary()

    def _calculate_score(self) -> int:
        total = 0
        count = 0
        for result in self.rule_results:
            if result['score'] is not None:
                total += result['score']
                count += 1
        return int(total / count) if count > 0 else 0

    def _generate_summary(self) -> Dict[str, List[str]]:
        strengths = []
        improvements = []
        for result in self.rule_results:
            if result['passed']:
                strengths.append(result['justification'])
            else:
                improvements.append(result['justification'])
        return {'strengths': strengths, 'improvements': improvements}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'score': self.score,
            'rules': self.rule_results,
            'summary': self.summary
        } 