"""Command-line interface for SnippetVault."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from snippetvault.vault import VaultService

# ANSI color codes
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
DIM = "\033[2m"
RED = "\033[31m"
RESET = "\033[0m"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="snippetvault",
        description="Intelligent Terminal Command and Code Snippet Vault CLI.",
    )
    parser.add_argument("--db", help="Custom SQLite database file path.")
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # add
    p_add = subparsers.add_parser("add", help="Add a new command or snippet to vault.")
    p_add.add_argument("command", help="The exact shell command or code snippet.")
    p_add.add_argument("-t", "--title", required=True, help="Short, memorable title.")
    p_add.add_argument("--tags", default="", help="Comma-separated tags (e.g. 'docker,prod').")
    p_add.add_argument("-d", "--desc", default="", help="Detailed description or context.")
    p_add.add_argument("--lang", default="bash", help="Language syntax (default: bash).")

    # list
    p_list = subparsers.add_parser("list", help="List stored snippets.")
    p_list.add_argument("-t", "--tag", help="Filter by tag.")
    p_list.add_argument("--json", action="store_true", help="Output as JSON.")

    # find
    p_find = subparsers.add_parser("find", help="Fuzzy search snippets by keyword.")
    p_find.add_argument("query", help="Search keyword.")
    p_find.add_argument("--limit", type=int, default=10, help="Max results to return.")
    p_find.add_argument("--json", action="store_true", help="Output as JSON.")

    # get / show
    p_get = subparsers.add_parser("get", help="Show snippet details by ID.")
    p_get.add_argument("id", type=int, help="Snippet ID.")

    # copy
    p_copy = subparsers.add_parser("copy", help="Copy snippet command to system clipboard.")
    p_copy.add_argument("id", type=int, help="Snippet ID to copy.")

    # run
    p_run = subparsers.add_parser("run", help="Execute snippet command in terminal.")
    p_run.add_argument("id", type=int, help="Snippet ID to execute.")
    p_run.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt.")

    # delete
    p_del = subparsers.add_parser("delete", help="Delete snippet from vault.")
    p_del.add_argument("id", type=int, help="Snippet ID to delete.")

    # export
    p_exp = subparsers.add_parser("export", help="Export snippets to JSON file or stdout.")
    p_exp.add_argument("-o", "--output", help="Target output file path.")

    # import
    p_imp = subparsers.add_parser("import", help="Import snippets from JSON file.")
    p_imp.add_argument("file", help="Path to JSON file to import.")
    p_imp.add_argument("--overwrite", action="store_true", help="Overwrite existing snippets by title.")

    # stats
    subparsers.add_parser("stats", help="Display vault usage statistics.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.subcommand:
        parser.print_help()
        return 0

    from snippetvault.db import Database
    db = Database(args.db) if args.db else Database()
    service = VaultService(db)

    if args.subcommand == "add":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        try:
            s = service.add_snippet(
                title=args.title,
                command=args.command,
                tags=tags,
                description=args.desc,
                language=args.lang,
            )
            print(f"{GREEN}✓ Snippet #{s.id} saved successfully!{RESET}")
            print(f"{BOLD}{s.title}{RESET} ({CYAN}{', '.join(s.tags) or 'no tags'}{RESET})")
            print(f"{DIM}$ {s.command}{RESET}")
            return 0
        except ValueError as err:
            print(f"{RED}Error:{RESET} {err}", file=sys.stderr)
            return 1

    if args.subcommand == "list":
        snippets = service.list_snippets(tag=args.tag)
        if args.json:
            print(json.dumps([s.to_dict() for s in snippets], indent=2))
            return 0
        if not snippets:
            filter_msg = f" with tag '{args.tag}'" if args.tag else ""
            print(f"{YELLOW}No snippets found{filter_msg}. Use 'snippetvault add' to create one.{RESET}")
            return 0

        print(f"\n{BOLD}SnippetVault — {len(snippets)} Stored Snippets{RESET}")
        print("=" * 70)
        for s in snippets:
            tag_str = f" [{CYAN}{', '.join(s.tags)}{RESET}]" if s.tags else ""
            print(f"{GREEN}#{s.id:<3}{RESET} {BOLD}{s.title}{RESET}{tag_str}")
            print(f"     {DIM}$ {s.command}{RESET}")
            if s.description:
                print(f"     {DIM}ℹ {s.description}{RESET}")
        print("=" * 70)
        return 0

    if args.subcommand == "find":
        matches = service.search(args.query, limit=args.limit)
        if args.json:
            print(json.dumps([{"score": m.score, "snippet": m.snippet.to_dict()} for m in matches], indent=2))
            return 0
        if not matches:
            print(f"{YELLOW}No matches found for query: '{args.query}'{RESET}")
            return 0

        print(f"\n{BOLD}Search Results for '{args.query}' ({len(matches)} matches){RESET}")
        print("-" * 70)
        for m in matches:
            s = m.snippet
            tag_str = f" [{CYAN}{', '.join(s.tags)}{RESET}]" if s.tags else ""
            print(f"{GREEN}#{s.id:<3}{RESET} {BOLD}{s.title}{RESET}{tag_str} {DIM}(score: {m.score:.2f}){RESET}")
            print(f"     {DIM}$ {s.command}{RESET}")
        print("-" * 70)
        return 0

    if args.subcommand == "get":
        s = service.get_by_id(args.id)
        if not s:
            print(f"{RED}Error: Snippet #{args.id} not found.{RESET}", file=sys.stderr)
            return 1
        print(f"\n{BOLD}Snippet #{s.id}: {s.title}{RESET}")
        print(f"Language:    {s.language}")
        print(f"Tags:        {', '.join(s.tags) or 'None'}")
        print(f"Times Used:  {s.times_used}")
        print(f"Created At:  {s.created_at}")
        if s.description:
            print(f"Description: {s.description}")
        print(f"\n{BOLD}Command:{RESET}\n{CYAN}{s.command}{RESET}\n")
        return 0

    if args.subcommand == "copy":
        ok, s = service.copy_snippet(args.id)
        if not s:
            print(f"{RED}Error: Snippet #{args.id} not found.{RESET}", file=sys.stderr)
            return 1
        if ok:
            print(f"{GREEN}✓ Snippet #{s.id} copied to clipboard!{RESET}")
            print(f"{DIM}$ {s.command}{RESET}")
        else:
            print(f"{YELLOW}Copied to stdout (clipboard tool unavailable):{RESET}")
            print(s.command)
        return 0

    if args.subcommand == "run":
        s = service.get_by_id(args.id)
        if not s:
            print(f"{RED}Error: Snippet #{args.id} not found.{RESET}", file=sys.stderr)
            return 1

        print(f"{BOLD}Ready to execute snippet #{s.id}:{RESET}")
        print(f"{CYAN}$ {s.command}{RESET}")

        if not args.yes:
            try:
                ans = input(f"{YELLOW}Execute this command? [y/N]: {RESET}").strip().lower()
                if ans not in ("y", "yes"):
                    print(f"{DIM}Execution cancelled.{RESET}")
                    return 0
            except (KeyboardInterrupt, EOFError):
                print(f"\n{DIM}Cancelled.{RESET}")
                return 0

        code, out, err = service.run_snippet(args.id)
        if out:
            print(out, end="")
        if err:
            print(err, end="", file=sys.stderr)
        return code

    if args.subcommand == "delete":
        if service.delete_snippet(args.id):
            print(f"{GREEN}✓ Snippet #{args.id} deleted.{RESET}")
            return 0
        print(f"{RED}Error: Snippet #{args.id} not found.{RESET}", file=sys.stderr)
        return 1

    if args.subcommand == "export":
        data = service.export_snippets()
        content = json.dumps(data, indent=2)
        if args.output:
            Path(args.output).write_text(content, encoding="utf-8")
            print(f"{GREEN}✓ Exported {len(data)} snippets to {args.output}{RESET}")
        else:
            print(content)
        return 0

    if args.subcommand == "import":
        p = Path(args.file)
        if not p.exists():
            print(f"{RED}Error: File {args.file} not found.{RESET}", file=sys.stderr)
            return 1
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            count = service.import_snippets(data, overwrite=args.overwrite)
            print(f"{GREEN}✓ Successfully imported {count} snippets.{RESET}")
            return 0
        except Exception as exc:
            print(f"{RED}Error importing snippets:{RESET} {exc}", file=sys.stderr)
            return 1

    if args.subcommand == "stats":
        stats = service.get_stats()
        print(f"\n{BOLD}SnippetVault Statistics{RESET}")
        print("=" * 40)
        print(f"Total Snippets: {stats['total_snippets']}")
        print(f"Total Tags:     {stats['total_tags']}")
        print(f"\n{BOLD}Top Tags:{RESET}")
        for t, count in stats["top_tags"]:
            print(f"  • {CYAN}{t:<15}{RESET} ({count} snippets)")
        print(f"\n{BOLD}Most Used Snippets:{RESET}")
        for s in stats["most_used"]:
            print(f"  • #{s['id']:<3} {s['title']:<25} ({s['uses']} runs/copies)")
        print("=" * 40)
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
