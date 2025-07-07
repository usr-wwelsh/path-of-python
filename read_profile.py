import pstats
import sys

try:
    p = pstats.Stats('profile.out')
    p.strip_dirs().sort_stats('cumulative').print_stats()
except Exception as e:
    print(f"Error reading profile.out: {e}", file=sys.stderr)
    sys.exit(1)