#\!/bin/bash

# First, get the field and option IDs
echo "Getting field and option IDs..."

FIELD_DATA=$(gh api graphql -f query='
{
  user(login: "macayaven") {
    projectV2(number: 7) {
      id
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue {
              number
              title
            }
          }
        }
      }
      field(name: "Status") {
        ... on ProjectV2SingleSelectField {
          id
          options {
            id
            name
          }
        }
      }
    }
  }
}')

# Extract the field ID and option IDs
FIELD_ID=$(echo "$FIELD_DATA"  < /dev/null |  jq -r '.data.user.projectV2.field.id')
BACKLOG_ID=$(echo "$FIELD_DATA" | jq -r '.data.user.projectV2.field.options[] | select(.name == "Backlog") | .id')
READY_ID=$(echo "$FIELD_DATA" | jq -r '.data.user.projectV2.field.options[] | select(.name == "Ready") | .id')

echo "Field ID: $FIELD_ID"
echo "Backlog ID: $BACKLOG_ID"
echo "Ready ID: $READY_ID"

# Move all items to Backlog first
echo "Moving all items to Backlog..."
echo "$FIELD_DATA" | jq -r '.data.user.projectV2.items.nodes[] | .id' | while read -r item_id; do
  gh api graphql -f query="
    mutation {
      updateProjectV2ItemFieldValue(
        input: {
          projectId: \"PVT_kwHOAEkav84A92u5\"
          itemId: \"$item_id\"
          fieldId: \"$FIELD_ID\"
          value: { singleSelectOptionId: \"$BACKLOG_ID\" }
        }
      ) {
        projectV2Item {
          id
        }
      }
    }"
done

# Move Epic 0 issues (135-139) to Ready
echo "Moving Epic 0 issues to Ready..."
for issue_num in {135..139}; do
  ITEM_ID=$(echo "$FIELD_DATA" | jq -r ".data.user.projectV2.items.nodes[] | select(.content.number == $issue_num) | .id" | head -n1)
  if [ \! -z "$ITEM_ID" ]; then
    echo "Moving issue #$issue_num to Ready..."
    gh api graphql -f query="
      mutation {
        updateProjectV2ItemFieldValue(
          input: {
            projectId: \"PVT_kwHOAEkav84A92u5\"
            itemId: \"$ITEM_ID\"
            fieldId: \"$FIELD_ID\"
            value: { singleSelectOptionId: \"$READY_ID\" }
          }
        ) {
          projectV2Item {
            id
          }
        }
      }"
  fi
done

echo "Project board organized\!"
