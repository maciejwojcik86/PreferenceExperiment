from storage import Storage
from config import MODELS
import hashlib
from collections import defaultdict
import math

def _get_rating_key(text_a: str, text_b: str) -> str:
    combined = f"{text_a}||{text_b}"
    return hashlib.md5(combined.encode()).hexdigest()

class Match:
    def __init__(self, judge, model_a, model_b, winner):
        self.judge = judge
        self.model_a = model_a
        self.model_b = model_b
        self.winner = winner # "A" or "B"

    @property
    def winner_model(self):
        return self.model_a if self.winner == "A" else self.model_b
    
    @property
    def loser_model(self):
        return self.model_b if self.winner == "A" else self.model_a

def calculate_bias_uncertainty(wins1, attempts1, wins2, attempts2):
    """
    Calculates the 95% Margin of Error for the difference between two proportions
    using the Agresti-Caffo method (adding 1 success and 1 failure to each group).
    
    Returns:
        float: The margin of error (half-width of the 95% CI) in percentage points.
    """
    # Agresti-Caffo adjustment: add 1 success and 1 failure (so n increases by 2)
    n1 = attempts1 + 2
    p1 = (wins1 + 1) / n1
    
    n2 = attempts2 + 2
    p2 = (wins2 + 1) / n2
    
    # Standard Error of the difference
    se_diff = math.sqrt((p1 * (1 - p1) / n1) + (p2 * (1 - p2) / n2))
    
    # 95% Confidence Interval is approx +/- 1.96 * SE
    margin_of_error = 1.96 * se_diff
    
    return margin_of_error * 100  # Convert to percentage

def get_matches(storage):
    generations = storage.load_generations()
    ratings = storage.load_ratings()
    matches = []
    
    # Pre-compute hash map for all pairs to avoid O(N^4) lookups
    # Map: key -> (model_A, model_B)
    key_map = {}
    for m1 in MODELS:
        for m2 in MODELS:
            if m1 == m2: continue
            
            t1 = generations.get(m1)
            t2 = generations.get(m2)
            if not t1 or not t2: continue
            
            key = _get_rating_key(t1, t2)
            key_map[key] = (m1, m2)
    
    for judge, j_ratings in ratings.items():
        for key, winner in j_ratings.items():
            if key in key_map:
                m1, m2 = key_map[key]
                matches.append(Match(judge, m1, m2, winner))
                
    return matches

def calculate_elo(matches, k=32, initial=1000):
    elo = {model: initial for model in MODELS}
    
    for match in matches:
        ra = elo[match.model_a]
        rb = elo[match.model_b]
        
        ea = 1 / (1 + 10 ** ((rb - ra) / 400))
        eb = 1 / (1 + 10 ** ((ra - rb) / 400))
        
        sa = 1 if match.winner == "A" else 0
        sb = 1 if match.winner == "B" else 0
        
        elo[match.model_a] = ra + k * (sa - ea)
        elo[match.model_b] = rb + k * (sb - eb)
        
    return elo

def analyze_results():
    storage = Storage()
    matches = get_matches(storage)
    
    if not matches:
        print("No matches found to analyze.")
        return

    print("\n--- Extended Analysis Report ---\n")
    
    # --- 1. Bias Analysis (Relative) ---
    print("## Relative Self-Preference Bias")
    print("Bias Score = (Win Rate when Self is Judge) - (Win Rate when Others are Judge)")
    
    # win_counts[judge][candidate] = [wins, attempts]
    win_stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    
    for m in matches:
        # Looking at match from 'm.judge' perspective
        # Candidate A
        win_stats[m.judge][m.model_a][1] += 1
        if m.winner == "A":
            win_stats[m.judge][m.model_a][0] += 1
            
        # Candidate B
        win_stats[m.judge][m.model_b][1] += 1
        if m.winner == "B":
            win_stats[m.judge][m.model_b][0] += 1

    for model in MODELS:
        # Calculate Self Score
        self_stats = win_stats[model][model] # When 'model' judged 'model'
        self_win_rate = 0
        if self_stats[1] > 0:
            self_win_rate = (self_stats[0] / self_stats[1]) * 100
            
        # Calculate Others Score
        other_wins = 0
        other_attempts = 0
        for other_judge in MODELS:
            if other_judge == model: continue
            stats = win_stats[other_judge][model]
            other_wins += stats[0]
            other_attempts += stats[1]
            
        other_win_rate = 0
        if other_attempts > 0:
            other_win_rate = (other_wins / other_attempts) * 100
            
        bias = self_win_rate - other_win_rate
        uncertainty = calculate_bias_uncertainty(
            self_stats[0], self_stats[1],
            other_wins, other_attempts
        )
        
        print(f"[{model}]")
        print(f"  Self-Judge Win Rate: {self_win_rate:.1f}% ({self_stats[0]}/{self_stats[1]})")
        print(f"  Other-Judge Win Rate: {other_win_rate:.1f}% ({other_wins}/{other_attempts})")
        print(f"  > Bias Score: {bias:+.1f} ± {uncertainty:.1f} points")
        if abs(bias) > 25:
             print("  *** HIGH BIAS DETECTED ***")
        if abs(bias) - uncertainty > 0:
             print("  (Statistically Significant at 95% CL)")
        print()

    # --- 2. ELO Leaderboard ---
    print("## Model ELO Leaderboard")
    elo_ratings = calculate_elo(matches)
    sorted_elo = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)
    
    for rank, (model, rating) in enumerate(sorted_elo, 1):
        print(f"{rank}. {model:<40} ELO: {rating:.0f}")

if __name__ == "__main__":
    analyze_results()
