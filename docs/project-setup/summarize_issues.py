#!/usr/bin/env python3
"""
Summarize the GitHub issues by epic and team.
"""

import json
from collections import defaultdict

def main():
    with open("github_issues.json", "r") as f:
        data = json.load(f)
    
    # Group by epic and team
    epic_summary = defaultdict(lambda: {"teams": defaultdict(int), "total": 0, "points": 0})
    
    for issue in data["issues"]:
        # Find epic
        epic = next((l for l in issue["labels"] if "epic-" in l), "unknown")
        team = next((l for l in issue["labels"] if "team-" in l), "unknown")
        points = int(next((l.replace("size-", "") for l in issue["labels"] if "size-" in l), "0"))
        
        epic_summary[epic]["teams"][team] += 1
        epic_summary[epic]["total"] += 1
        epic_summary[epic]["points"] += points
    
    print("\n=== GitHub Issues Summary ===\n")
    
    # Epic 0: Migration
    print("📦 Epic 0: Monorepo Migration")
    epic = epic_summary["epic-0-migration"]
    print(f"   Total Issues: {epic['total']}")
    print(f"   Story Points: {epic['points']}")
    for team, count in epic["teams"].items():
        print(f"   - {team.replace('team-', '').title()}: {count} issues")
    
    # Epic 1: Local Docker
    print("\n🐳 Epic 1: Local Docker Deployment")
    epic = epic_summary["epic-1-local"]
    print(f"   Total Issues: {epic['total']}")
    print(f"   Story Points: {epic['points']}")
    for team, count in epic["teams"].items():
        print(f"   - {team.replace('team-', '').title()}: {count} issues")
    
    # Epic 2: Cloud Run
    print("\n☁️  Epic 2: Cloud Run Production")
    epic = epic_summary["epic-2-production"]
    print(f"   Total Issues: {epic['total']}")
    print(f"   Story Points: {epic['points']}")
    for team, count in epic["teams"].items():
        print(f"   - {team.replace('team-', '').title()}: {count} issues")
    
    # Grand total
    total_issues = sum(e["total"] for e in epic_summary.values())
    total_points = sum(e["points"] for e in epic_summary.values())
    
    print(f"\n📊 Grand Total: {total_issues} issues, {total_points} story points")
    
    print("\n=== Deployment Flow ===")
    print("1️⃣  Epic 0: Migrate to monorepo structure")
    print("2️⃣  Epic 1: Local Docker deployment + integration testing")
    print("3️⃣  TEST LOCALLY: Verify everything works before proceeding!")
    print("4️⃣  Epic 2: Cloud Run deployment (only after local success)")

if __name__ == "__main__":
    main()