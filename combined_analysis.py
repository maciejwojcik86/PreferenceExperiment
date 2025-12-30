import os
import sys
import glob
import argparse
from collections import defaultdict
from config import MODELS, DATA_DIR
from storage import Storage
from analysis import get_matches, calculate_bias_uncertainty, calculate_elo

class ReportLogger:
    def __init__(self, filename="combined_analysis_report.txt", output_dir=None):
        out_dir = output_dir if output_dir else DATA_DIR
        self.filepath = os.path.join(out_dir, filename)
        self.buffer = []

    def log(self, msg=""):
        print(msg)
        self.buffer.append(str(msg))

    def save(self):
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.buffer))
            print(f"[INFO] Report saved to {self.filepath}")
        except Exception as e:
            print(f"[ERR] Failed to save report: {e}")

def get_matches_for_run(run_path):
    """
    Creates a Storage instance pointing to the specific run directory
    and returns the matches found in that run.
    """
    if not os.path.exists(run_path):
        print(f"[WARN] Run directory not found: {run_path}")
        return []
    
    # Initialize storage and override paths to point to the specific run directory
    storage = Storage()
    storage.data_dir = run_path
    storage.gen_path = os.path.join(run_path, "generations.json")
    storage.ratings_path = os.path.join(run_path, "ratings.json") 
    
    # Verify files exist before trying to load
    if not os.path.exists(storage.gen_path) or not os.path.exists(storage.ratings_path):
         # Try singular 'rating.json' just in case? No, stick to config standard or what we see.
         # Current repo seems to have 'ratings.json'.
         pass

    matches = get_matches(storage)
    print(f"Loaded {len(matches)} matches from {run_path}")
    return matches

def run_combined_analysis(run_dirs=None, output_file="combined_analysis_report.txt"):
    if not run_dirs:
        # Default to finding all results/run* directories
        base_dir = os.path.join(os.getcwd(), DATA_DIR)
        run_dirs = glob.glob(os.path.join(base_dir, "run*"))
        run_dirs = [d for d in run_dirs if os.path.isdir(d)]
        print(f"Auto-detected runs in {base_dir}: {run_dirs}")
    
    all_matches = []
    
    for path in run_dirs:
        all_matches.extend(get_matches_for_run(path))
        
    if not all_matches:
        print("No matches found in any run directories.")
        return

    logger = ReportLogger(filename=output_file)
    
    logger.log("\n--- Combined Analysis Report ---\n")
    logger.log(f"Runs Included: {len(run_dirs)}")
    for r in run_dirs:
        logger.log(f" - {r}")
    logger.log(f"Total Matches Analyzed: {len(all_matches)}")
    
    # --- 1. Bias Analysis (Relative) ---
    logger.log("\n## Relative Self-Preference Bias")
    logger.log("Bias Score = (Win Rate when Self is Judge) - (Win Rate when Others are Judge)")
    
    # win_counts[judge][candidate] = [wins, attempts]
    win_stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    
    for m in all_matches:
        win_stats[m.judge][m.model_a][1] += 1
        if m.winner == "A":
            win_stats[m.judge][m.model_a][0] += 1
            
        win_stats[m.judge][m.model_b][1] += 1
        if m.winner == "B":
            win_stats[m.judge][m.model_b][0] += 1

    for model in MODELS:
        self_stats = win_stats[model][model] 
        self_win_rate = 0
        if self_stats[1] > 0:
            self_win_rate = (self_stats[0] / self_stats[1]) * 100
            
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
        
        logger.log(f"[{model}]")
        logger.log(f"  Self-Judge Win Rate: {self_win_rate:.1f}% ({self_stats[0]}/{self_stats[1]})")
        logger.log(f"  Other-Judge Win Rate: {other_win_rate:.1f}% ({other_wins}/{other_attempts})")
        logger.log(f"  > Bias Score: {bias:+.1f} ± {uncertainty:.1f} points")
        if abs(bias) > 25:
             logger.log("  *** HIGH BIAS DETECTED ***")
        if abs(bias) - uncertainty > 0:
             logger.log("  (Statistically Significant at 95% CL)")
        logger.log("")

    # --- 2. ELO Leaderboard ---
    logger.log("## Model ELO Leaderboard")
    elo_ratings = calculate_elo(all_matches)
    sorted_elo = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)
    
    for rank, (model, rating) in enumerate(sorted_elo, 1):
        logger.log(f"{rank}. {model:<40} ELO: {rating:.0f}")

    logger.save()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine and analyze results from multiple experiment runs.")
    parser.add_argument("runs", nargs="*", help="Paths to run directories (e.g., results/run1 results/run2). If empty, auto-detects 'run*' in results dir.")
    parser.add_argument("--output", default="combined_analysis_report.txt", help="Output filename for the report.")
    
    args = parser.parse_args()
    
    run_combined_analysis(run_dirs=args.runs, output_file=args.output)
