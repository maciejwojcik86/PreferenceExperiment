import sys
import asyncio
from experiment import ExperimentRunner
from analysis import analyze_results

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [generate|rate|analyze]")
        return

    command = sys.argv[1].lower()
    runner = ExperimentRunner()

    if command == "generate":
        asyncio.run(runner.run_generation())
    elif command == "rate":
        asyncio.run(runner.run_rating())
    elif command == "analyze":
        analyze_results()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
