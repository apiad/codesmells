from typing import List, Dict, Tuple, Optional
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

        # Backpointers
        # H_ptr: 0=Stop, 1=Match, 2=E, 3=F
        H_ptr = [[0] * (m + 1) for _ in range(n + 1)]
        # E_ptr: 1=H, 2=E
        E_ptr = [[0] * (m + 1) for _ in range(n + 1)]
        # F_ptr: 1=H, 2=F
        F_ptr = [[0] * (m + 1) for _ in range(n + 1)]
        
        gamma = self.gap_open
        epsilon = self.gap_extend
        
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                tc = candidate[i-1]
                te = template[j-1]
                
                # E[i][j] = gap in template (insertion in candidate)
                h_open = H[i-1][j] + gamma + epsilon
                e_ext = E[i-1][j] + epsilon
                if h_open >= e_ext:
                    E[i][j] = h_open
                    E_ptr[i][j] = 1
                else:
                    E[i][j] = e_ext
                    E_ptr[i][j] = 2
                
                # F[i][j] = gap in candidate (deletion in template)
                h_open_f = H[i][j-1] + gamma + epsilon
                f_ext = F[i][j-1] + epsilon
                if h_open_f >= f_ext:
                    F[i][j] = h_open_f
                    F_ptr[i][j] = 1
                else:
                    F[i][j] = f_ext
                    F_ptr[i][j] = 2
                
                # Match score
                match = self.score_match(tc, te)
                h_match = H[i-1][j-1] + match
                
                # H[i][j]
                if h_match >= E[i][j] and h_match >= F[i][j] and h_match > 0:
                    H[i][j] = h_match
                    H_ptr[i][j] = 1
                elif E[i][j] >= F[i][j] and E[i][j] > 0:
                    H[i][j] = E[i][j]
                    H_ptr[i][j] = 2
                elif F[i][j] > 0:
                    H[i][j] = F[i][j]
                    H_ptr[i][j] = 3
                else:
                    H[i][j] = 0.0
                    H_ptr[i][j] = 0

        # Collect all potential starting points for traceback, sorted by score descending
        all_cells = []
        for i in range(n + 1):
            for j in range(m + 1):
                if H[i][j] > 0:
                    all_cells.append((H[i][j], i, j))
        
        all_cells.sort(key=lambda x: x[0], reverse=True)
        
        template_weight_sum = sum(te.weight for te in template)
        
        for score, si, sj in all_cells:
            matches = self.traceback(H_ptr, E_ptr, F_ptr, si, sj)
            bindings = self.solve_csp(matches, candidate, template)
            if bindings is not None:
                if template_weight_sum == 0:
                    normalized_score = 1.0 if score >= 0 else 0.0
                else:
                    normalized_score = score / template_weight_sum
                return normalized_score, bindings

        return 0.0, {}

    def traceback(self, H_ptr: List[List[int]], E_ptr: List[List[int]], F_ptr: List[List[int]], i: int, j: int) -> List[Tuple[int, int]]:
        """
        Performs traceback from (i, j) and returns a list of matched (candidate_idx, template_idx) pairs.
        """
        matches = []
        curr_i, curr_j = i, j
        curr_matrix = 'H'
        
        while curr_i > 0 or curr_j > 0:
            if curr_matrix == 'H':
                ptr = H_ptr[curr_i][curr_j]
                if ptr == 0:
                    break
                if ptr == 1:
                    matches.append((curr_i-1, curr_j-1))
                    curr_i -= 1
                    curr_j -= 1
                elif ptr == 2:
                    curr_matrix = 'E'
                elif ptr == 3:
                    curr_matrix = 'F'
            elif curr_matrix == 'E':
                ptr = E_ptr[curr_i][curr_j]
                curr_i -= 1
                if ptr == 1:
                    curr_matrix = 'H'
                else:
                    curr_matrix = 'E'
            elif curr_matrix == 'F':
                ptr = F_ptr[curr_i][curr_j]
                curr_j -= 1
                if ptr == 1:
                    curr_matrix = 'H'
                else:
                    curr_matrix = 'F'
        return matches

    def solve_csp(self, matches: List[Tuple[int, int]], candidate: List[Token], template: List[Token]) -> Optional[Dict[str, str]]:
        """
        Validates SIGIL bindings (CSP) from a list of matched indices.
        
        Returns bindings dict if valid, else None.
        """
        bindings = {}
        for ci, ti in matches:
            tc = candidate[ci]
            te = template[ti]
            if te.token_class == TokenClass.SIGIL and tc.token_class == TokenClass.IDENTIFIER:
                if te.value in bindings and bindings[te.value] != tc.value:
                    return None
                bindings[te.value] = tc.value
        return bindings
