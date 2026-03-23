from typing import List, Dict, Tuple
from codesmells.models import Token, TokenClass

class FuzzyAlignmentEngine:
    """
    Core algorithmic engine for computing similarity between candidate code and templates.
    """
    def __init__(self, gap_open: float = -2.0, gap_extend: float = -0.1):
        self.gap_open = gap_open
        self.gap_extend = gap_extend

    def score_match(self, tc: Token, te: Token) -> float:
        """
        Computes the substitution score M(tc, te) between a candidate token and a template token.

        Args:
            tc: The candidate token.
            te: The template token.

        Returns:
            The substitution score:
            - 0.0 if te is a GAP.
            - tc.weight if te is a SIGIL.
            - tc.weight * 2.0 if values match.
            - -infinity otherwise.
        """
        if te.token_class == TokenClass.GAP:
            return 0.0
        if te.token_class == TokenClass.SIGIL:
            return tc.weight
        if tc.value == te.value:
            return tc.weight * 2.0
        return float('-inf')

    def align(self, candidate: List[Token], template: List[Token]) -> Tuple[float, Dict[str, str]]:
        """
        Computes the best alignment score between a candidate and a template.
        Uses Smith-Waterman with affine gap penalties.
        
        Args:
            candidate: List of tokens from the source code.
            template: List of tokens from the template rule.
            
        Returns:
            A tuple (normalized_score, bindings).
        """
        n = len(candidate)
        m = len(template)
        
        if m == 0:
            return 0.0, {}

        # H[i][j] = max score ending at candidate[i-1] and template[j-1]
        # E[i][j] = max score ending with gap in template
        # F[i][j] = max score ending with gap in candidate
        H = [[0.0] * (m + 1) for _ in range(n + 1)]
        E = [[float('-inf')] * (m + 1) for _ in range(n + 1)]
        F = [[float('-inf')] * (m + 1) for _ in range(n + 1)]
        
        gamma = self.gap_open
        epsilon = self.gap_extend
        
        max_score = 0.0
        
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                tc = candidate[i-1]
                te = template[j-1]
                
                # E[i][j] = gap in template (insertion in candidate)
                # We come from H[i-1][j] (opening a gap) or E[i-1][j] (extending)
                E[i][j] = max(H[i-1][j] + gamma + epsilon, E[i-1][j] + epsilon)
                
                # F[i][j] = gap in candidate (deletion in template)
                F[i][j] = max(H[i][j-1] + gamma + epsilon, F[i][j-1] + epsilon)
                
                # Match score
                match = self.score_match(tc, te)
                
                # H[i][j]
                H[i][j] = max(0.0, H[i-1][j-1] + match, E[i][j], F[i][j])
                
                if H[i][j] > max_score:
                    max_score = H[i][j]

        # Normalization
        template_weight_sum = sum(te.weight for te in template)
        if template_weight_sum == 0:
            normalized_score = 1.0 if max_score >= 0 else 0.0
        else:
            normalized_score = max_score / template_weight_sum
            
        return normalized_score, {}
