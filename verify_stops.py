import argparse
import csv
from pathlib import Path
from typing import List

def load_stop_names(stops_path: Path) -> List[dict]:
    out = []
    with stops_path.open("r", encoding="utf-8", errors="ignore", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            # only include stops with numeric stop_id in the 40000-49999 range
            sid = (row.get("stop_id") or "").strip()
            try:
                sid_int = int(sid)
            except ValueError:
                continue
            if not (40000 <= sid_int <= 49999):
                continue
            out.append({"stop_id": sid_int, "stop_name": (row.get("stop_name") or "").strip()})
    return out

def normalize(s: str) -> str:
    return (s or "").strip().lower()

def find_matches(name: str, stops: List[dict]):
    n = normalize(name)
    # exact matches (case-insensitive)
    exact = [s for s in stops if normalize(s["stop_name"]) == n]
    if exact:
        return "exact", exact
    # substring matches
    subs = [s for s in stops if n in normalize(s["stop_name"])]
    if subs:
        return "substring", subs
    return "none", []

def main():
    p = argparse.ArgumentParser(description="Verify station names against CTA stops.txt")
    p.add_argument("names_file", nargs="?", default="red.txt", help="file with one station name per line")
    p.add_argument("--stops", "-s", default=r"C:\Users\Chen\Downloads\cta_google_transit\stops.txt", help="path to stops.txt")
    p.add_argument("--show-all", action="store_true", help="show all matching stop rows (default: show up to 5)")
    args = p.parse_args()

    names_path = Path(args.names_file)
    stops_path = Path(args.stops)

    if not names_path.exists():
        print(f"Names file not found: {names_path}")
        raise SystemExit(1)
    if not stops_path.exists():
        print(f"stops.txt not found: {stops_path}")
        raise SystemExit(1)

    stops = load_stop_names(stops_path)

    names = [line.strip() for line in names_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    for name in names:
        kind, matches = find_matches(name, stops)
        if kind == "exact":
            print(f"{name}: FOUND (exact) — {len(matches)} match(es)")
            for m in (matches if args.show_all else matches[:5]):
                print(f"    {m['stop_id']}: {m['stop_name']}")
        elif kind == "substring":
            print(f"{name}: FOUND (substring) — {len(matches)} match(es)")
            for m in (matches if args.show_all else matches[:5]):
                print(f"    {m['stop_id']}: {m['stop_name']}")
        else:
            print(f"{name}: NOT FOUND")

if __name__ == "__main__":
    main()