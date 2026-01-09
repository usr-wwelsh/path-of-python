import pstats
import sys

if __name__ == "__main__":
    profile_file = "profile_output.prof"
    if len(sys.argv) > 1:
        profile_file = sys.argv[1]

    try:
        p = pstats.Stats(profile_file)
        p.strip_dirs().sort_stats("cumulative").print_stats(20) # Print top 20 cumulative time entries
        print("\n" + "="*50 + "\n")
        p.sort_stats("time").print_stats(20) # Print top 20 time entries
    except FileNotFoundError:
        print(f"Error: Profile file '{profile_file}' not found.")
    except Exception as e:
        print(f"An error occurred while processing the profile file: {e}")