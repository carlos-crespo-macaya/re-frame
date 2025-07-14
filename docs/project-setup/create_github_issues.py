#!/usr/bin/env python3
"""
Create GitHub issues for the CBT Assistant POC project.

Usage:
    python scripts/create_github_issues.py --token YOUR_GITHUB_TOKEN --repo owner/repo-name

Example:
    python scripts/create_github_issues.py --token ghp_xxxx --repo myorg/re-frame
"""

import json
import argparse
import sys
from typing import Dict, List, Optional
from github import Github, GithubException
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

def load_issues_data(filename: str = "github_issues.json") -> dict:
    """Load issues data from JSON file."""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Error: {filename} not found[/red]")
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]Error parsing JSON: {e}[/red]")
        sys.exit(1)

def create_labels(repo, labels_data: List[Dict]) -> Dict[str, any]:
    """Create labels in the repository."""
    console.print("\n[bold cyan]Creating Labels...[/bold cyan]")
    existing_labels = {label.name: label for label in repo.get_labels()}
    created_labels = {}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Creating labels...", total=len(labels_data))
        
        for label_data in labels_data:
            name = label_data["name"]
            
            if name in existing_labels:
                # Update existing label
                try:
                    label = existing_labels[name]
                    label.edit(
                        name=name,
                        color=label_data["color"],
                        description=label_data.get("description", "")
                    )
                    console.print(f"  ✓ Updated label: [yellow]{name}[/yellow]")
                except GithubException as e:
                    console.print(f"  ✗ Failed to update label {name}: {e}")
            else:
                # Create new label
                try:
                    label = repo.create_label(
                        name=name,
                        color=label_data["color"],
                        description=label_data.get("description", "")
                    )
                    console.print(f"  ✓ Created label: [green]{name}[/green]")
                except GithubException as e:
                    console.print(f"  ✗ Failed to create label {name}: {e}")
            
            created_labels[name] = repo.get_label(name)
            progress.update(task, advance=1)
    
    return created_labels

def create_milestones(repo, milestones_data: List[Dict]) -> Dict[str, any]:
    """Create milestones in the repository."""
    console.print("\n[bold cyan]Creating Milestones...[/bold cyan]")
    existing_milestones = {m.title: m for m in repo.get_milestones(state="all")}
    created_milestones = {}
    
    for milestone_data in milestones_data:
        title = milestone_data["title"]
        
        if title in existing_milestones:
            console.print(f"  ℹ Milestone already exists: [yellow]{title}[/yellow]")
            created_milestones[title] = existing_milestones[title]
        else:
            try:
                milestone = repo.create_milestone(
                    title=title,
                    description=milestone_data.get("description", ""),
                    due_on=milestone_data.get("due_on")
                )
                console.print(f"  ✓ Created milestone: [green]{title}[/green]")
                created_milestones[title] = milestone
            except GithubException as e:
                console.print(f"  ✗ Failed to create milestone {title}: {e}")
    
    return created_milestones

def create_issues(repo, issues_data: List[Dict], labels_map: Dict, milestones_map: Dict, dry_run: bool = False):
    """Create issues in the repository."""
    console.print(f"\n[bold cyan]Creating Issues {'(DRY RUN)' if dry_run else ''}...[/bold cyan]")
    
    # Create summary table
    summary_table = Table(title="Issues to Create")
    summary_table.add_column("Epic", style="cyan")
    summary_table.add_column("Team", style="green")
    summary_table.add_column("Priority", style="yellow")
    summary_table.add_column("Points", style="magenta")
    summary_table.add_column("Count", style="white")
    
    # Group issues by epic and team
    epic_summary = {}
    for issue in issues_data:
        epic = issue["labels"][0] if issue["labels"] else "unknown"
        team = next((l for l in issue["labels"] if "team-" in l), "unknown")
        priority = next((l for l in issue["labels"] if "priority-" in l), "unknown")
        points = next((l.replace("size-", "") for l in issue["labels"] if "size-" in l), "0")
        
        key = f"{epic}|{team}"
        if key not in epic_summary:
            epic_summary[key] = {"count": 0, "points": 0, "priority": priority}
        epic_summary[key]["count"] += 1
        epic_summary[key]["points"] += int(points)
    
    for key, data in epic_summary.items():
        epic, team = key.split("|")
        summary_table.add_row(
            epic.replace("epic-", "Epic ").title(),
            team.replace("team-", "").title(),
            data["priority"].replace("priority-", ""),
            str(data["points"]),
            str(data["count"])
        )
    
    console.print(summary_table)
    
    if dry_run:
        console.print("\n[yellow]DRY RUN: No issues will be created[/yellow]")
        return
    
    # Create issues
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Creating issues...", total=len(issues_data))
        
        for issue_data in issues_data:
            title = issue_data["title"]
            
            # Check if issue already exists
            existing_issues = repo.get_issues(state="all")
            issue_exists = any(issue.title == title for issue in existing_issues)
            
            if issue_exists:
                console.print(f"  ℹ Issue already exists: [yellow]{title}[/yellow]")
                progress.update(task, advance=1)
                continue
            
            try:
                # Get label objects
                label_objects = []
                for label_name in issue_data.get("labels", []):
                    if label_name in labels_map:
                        label_objects.append(labels_map[label_name])
                
                # Get milestone object
                milestone_name = issue_data.get("milestone")
                milestone_object = milestones_map.get(milestone_name) if milestone_name else None
                
                # Add dependencies to body if present
                body = issue_data["body"]
                if "Dependencies" in body and "depends_on" in issue_data:
                    deps = ", ".join(issue_data["depends_on"])
                    body = body.replace("**Dependencies**:", f"**Dependencies**: {deps}")
                
                # Create issue
                assignee = issue_data.get("assignee")
                if assignee is None:
                    issue = repo.create_issue(
                        title=title,
                        body=body,
                        labels=label_objects,
                        milestone=milestone_object
                    )
                else:
                    issue = repo.create_issue(
                        title=title,
                        body=body,
                        labels=label_objects,
                        milestone=milestone_object,
                        assignee=assignee
                    )
                
                console.print(f"  ✓ Created issue: [green]{title}[/green]")
                
            except GithubException as e:
                console.print(f"  ✗ Failed to create issue {title}: {e}")
            
            progress.update(task, advance=1)

def main():
    parser = argparse.ArgumentParser(description="Create GitHub issues for CBT Assistant POC")
    parser.add_argument("--token", required=True, help="GitHub personal access token")
    parser.add_argument("--repo", required=True, help="Repository in format owner/repo")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created without creating")
    parser.add_argument("--issues-file", default="github_issues.json", help="JSON file with issues data")
    
    args = parser.parse_args()
    
    # Load issues data
    data = load_issues_data(args.issues_file)
    
    # Initialize GitHub client
    try:
        g = Github(args.token)
        repo = g.get_repo(args.repo)
        console.print(f"\n[bold green]Connected to repository: {repo.full_name}[/bold green]")
    except GithubException as e:
        console.print(f"[red]Failed to connect to repository: {e}[/red]")
        sys.exit(1)
    
    # Create labels
    labels_map = create_labels(repo, data["labels"])
    
    # Create milestones
    milestones_map = create_milestones(repo, data["milestones"])
    
    # Create issues
    create_issues(repo, data["issues"], labels_map, milestones_map, args.dry_run)
    
    # Summary
    console.print("\n[bold green]✓ Issue creation complete![/bold green]")
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  - Labels: {len(data['labels'])}")
    console.print(f"  - Milestones: {len(data['milestones'])}")
    console.print(f"  - Issues: {len(data['issues'])}")
    
    # Next steps
    console.print("\n[bold cyan]Next Steps:[/bold cyan]")
    console.print("  1. Create a GitHub Project Board")
    console.print("  2. Add all issues to the project board")
    console.print("  3. Configure automation rules")
    console.print("  4. Assign team members to issues")

if __name__ == "__main__":
    main()