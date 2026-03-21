from sklearn.metrics import cohen_kappa_score

class MetricEvaluator:
    @staticmethod
    def calculate_kappa(ai_scores, human_scores):
        # Quantize AI scores (0.0-1.0) to Binary (0 or 1)
        ai_binary = [1 if x > 0.5 else 0 for x in ai_scores]
        
        # Ensure lengths match
        min_len = min(len(ai_binary), len(human_scores))
        return cohen_kappa_score(ai_binary[:min_len], human_scores[:min_len])