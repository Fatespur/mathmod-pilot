import argparse
import sys
import json
import os

def main():
    parser = argparse.ArgumentParser(
        description="CUMCM Modeling Skills Toolkit - Unified CLI Helper"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: list
    list_parser = subparsers.add_parser("list", help="List all registered skills")
    list_parser.add_argument("--category", type=str, help="Filter by category")

    # Command: info
    info_parser = subparsers.add_parser("info", help="Show details of a specific skill")
    info_parser.add_argument("name", type=str, help="Skill name")

    # Command: workflow
    wf_parser = subparsers.add_parser("workflow", help="Display modeling pipeline stages and DAG")

    args = parser.parse_args()

    reg_path = os.path.join(os.path.dirname(__file__), "..", "registry", "skills.json")
    if not os.path.exists(reg_path):
        print("Registry not found at:", reg_path)
        sys.exit(1)

    with open(reg_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    skills = data.get("skills", [])

    if args.command == "list":
        print(f"{'Stage':<8} {'Category':<28} {'Skill Name':<30}")
        print("-" * 70)
        for s in skills:
            if args.category and args.category.lower() not in s["category"].lower():
                continue
            print(f"{s['stage']:<8} {s['category']:<28} {s['name']:<30}")
    elif args.command == "info":
        found = [s for s in skills if s["name"] == args.name]
        if not found:
            print(f"Skill '{args.name}' not found.")
            sys.exit(1)
        s = found[0]
        print(f"Title:        {s['title']}")
        print(f"Name:         {s['name']}")
        print(f"Category:     {s['category']}")
        print(f"Stage:        {s['stage']} ({s['stage_name']})")
        print(f"Description:  {s['description']}")
        print(f"Dependencies: {', '.join(s['dependencies']) if s['dependencies'] else 'None'}")
        print(f"Inputs:       {', '.join(s['inputs'])}")
        print(f"Outputs:      {', '.join(s['outputs'])}")
        print(f"Path:         {s['path']}")
    elif args.command == "workflow":
        wf_path = os.path.join(os.path.dirname(__file__), "..", "registry", "workflow.json")
        with open(wf_path, "r", encoding="utf-8") as fp:
            wf = json.load(fp)
        print(f"Workflow: {wf['name']}")
        print("Stages:")
        for st in wf.get("stages", []):
            print(f"  [{st['id']}] {st['name']} (Owner: {st['owner_skill']})")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
