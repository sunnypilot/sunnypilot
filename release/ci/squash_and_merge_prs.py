#!/usr/bin/env python3

import subprocess
import sys
import os
import argparse
import json


def setup_argument_parser():
    parser = argparse.ArgumentParser(description='Process and squash GitHub PRs')
    parser.add_argument('--pr-data', type=str, help='PR data in JSON format')
    parser.add_argument('--target-branch', type=str, default='master-dev-c3-new-test',
                        help='Target branch for merging')
    parser.add_argument('--squash-script-path', type=str, required=True,
                        help='Path to the squash_and_merge.py script')
    return parser


def validate_squash_script(script_path):
    if not os.path.isfile(script_path):
        raise FileNotFoundError(f"Squash script not found at: {script_path}")
    if not os.access(script_path, os.X_OK):
        raise PermissionError(f"Squash script is not executable: {script_path}")


def process_pr(pr_data, target_branch, squash_script_path):
    nodes = pr_data.get('data', {}).get('search', {}).get('nodes', [])
    if not nodes:
        print("No PRs to squash")
        return 0

    success_count = 0
    for pr in nodes:
        pr_number = pr.get('number', 'UNKNOWN')
        branch = pr.get('headRefName', '')
        title = pr.get('title', '')

        if not branch:
            print(f"Warning: Missing branch name for PR #{pr_number}, skipping")
            continue

        print(f"Processing PR #{pr_number} ({branch}): {title}")

        try:
            # Fetch PR branch
            subprocess.run(['git', 'fetch', 'origin', branch], check=True)
            # Delete branch if it exists (ignore errors if it doesn't)
            subprocess.run(['git', 'branch', '-D', branch], check=False)
            # Create new branch pointing to origin's branch
            subprocess.run(['git', 'branch', branch, f'origin/{branch}'], check=True)

            # Run squash script with proper error handling
            result = subprocess.run([squash_script_path, '--target', target_branch, '--source', branch, '--title', f"{title} (#{pr_number})"], check=True)

            print(f"Successfully processed PR #{pr_number}")
            success_count += 1

        except subprocess.CalledProcessError as e:
            print(f"Error processing PR #{pr_number}:")
            print(f"Command failed with exit code {e.returncode}")
            print(f"Error output: {e.stderr}")
            continue
        except Exception as e:
            print(f"Unexpected error processing PR #{pr_number}: {str(e)}")
            continue

    return success_count


def main():
    parser = setup_argument_parser()
    try:
        args = parser.parse_args()
        validate_squash_script(args.squash_script_path)
        pr_data_json = json.loads(args.pr_data)

        # Then process the PRs
        success_count = process_pr(pr_data_json, args.target_branch, args.squash_script_path)
        print(f"Successfully processed {success_count} PRs")

    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
