import sys
import json
from pathlib import Path
import argparse

def build_reversed_dict(path: Path, extra_indent: int = 0, reverse: bool = True) -> None:
    text = path.read_text(encoding="utf-8")
    names = [line.strip() for line in text.splitlines() if line.strip()]
    if reverse:
        names.reverse()
    prefix = " " * max(0, int(extra_indent))
    print(f"{prefix}self.name_to_index = {{")
    for idx, name in enumerate(names):
        # keep the original 4-space indent for each entry and prepend the extra prefix
        print(f"{prefix}    {json.dumps(name)}: {idx},")
    print(f"{prefix}}}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build reversed station dict")
    parser.add_argument("file", nargs="?", default="red.txt", help="input file (one station per line)")
    parser.add_argument("-i", "--indent", type=int, default=0, help="additional spaces to prepend to each output line")
    parser.add_argument("--no-reverse", action="store_true", help="do not reverse the station list (keep original order)")
    args = parser.parse_args()

    p = Path(args.file)
    if not p.exists():
        print(f"File not found: {p}")
        sys.exit(1)
    build_reversed_dict(p, extra_indent=args.indent, reverse=not args.no_reverse)