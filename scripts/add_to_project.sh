#\!/bin/bash

PROJECT_NUMBER=7
OWNER="macayaven"
REPO="macayaven/re-frame"

echo "Adding issues to project board..."

# Add all issues from #135 to #166
for issue_num in {135..166}; do
  echo "Adding issue #$issue_num..."
  gh project item-add $PROJECT_NUMBER --owner $OWNER --url https://github.com/$REPO/issues/$issue_num || true
done

echo "All issues added to project board\!"
