#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ID="gen-lang-client-0105778560"
REGION="europe-west1"
FRONTEND_SERVICE="re-frame-frontend"
BACKEND_SERVICE="re-frame-backend"

echo -e "${YELLOW}Fixing Frontend Authentication Issues${NC}"
echo "========================================="

# Set project
gcloud config set project ${PROJECT_ID}

# Get the backend public URL
echo -e "\n${GREEN}1. Getting backend public URL...${NC}"
BACKEND_PUBLIC_URL=$(gcloud run services describe ${BACKEND_SERVICE} \
  --region=${REGION} \
  --format="value(status.url)")

echo "   Backend public URL: ${BACKEND_PUBLIC_URL}"

# Update frontend environment variables
echo -e "\n${GREEN}2. Updating frontend environment variables...${NC}"
gcloud run services update ${FRONTEND_SERVICE} \
  --region=${REGION} \
  --update-env-vars="BACKEND_PUBLIC_URL=${BACKEND_PUBLIC_URL}" \
  --no-traffic

echo -e "\n${GREEN}3. Verifying service account permissions...${NC}"

# Get frontend service account
FRONTEND_SA=$(gcloud run services describe ${FRONTEND_SERVICE} \
  --region=${REGION} \
  --format="value(spec.template.spec.serviceAccountName)")

echo "   Frontend service account: ${FRONTEND_SA}"

# Check if frontend SA can invoke backend
echo -e "\n${GREEN}4. Checking IAM bindings on backend service...${NC}"
BINDINGS=$(gcloud run services get-iam-policy ${BACKEND_SERVICE} \
  --region=${REGION} \
  --format="value(bindings[0].members)" | grep "${FRONTEND_SA}" || true)

if [ -z "${BINDINGS}" ]; then
  echo -e "   ${YELLOW}Frontend SA doesn't have invoke permissions. Adding...${NC}"
  gcloud run services add-iam-policy-binding ${BACKEND_SERVICE} \
    --region=${REGION} \
    --member="serviceAccount:${FRONTEND_SA}" \
    --role="roles/run.invoker"
else
  echo "   ✓ Frontend SA already has invoke permissions"
fi

# Verify ingress settings
echo -e "\n${GREEN}5. Verifying ingress settings...${NC}"
BACKEND_INGRESS=$(gcloud run services describe ${BACKEND_SERVICE} \
  --region=${REGION} \
  --format="value(metadata.annotations.'run.googleapis.com/ingress')")

echo "   Backend ingress: ${BACKEND_INGRESS}"

if [ "${BACKEND_INGRESS}" != "internal" ]; then
  echo -e "   ${YELLOW}WARNING: Backend ingress is not set to 'internal'${NC}"
  echo "   Consider running: gcloud run services update ${BACKEND_SERVICE} --region=${REGION} --ingress=internal"
fi

# Check VPC connector
echo -e "\n${GREEN}6. Checking VPC connector on frontend...${NC}"
VPC_CONNECTOR=$(gcloud run services describe ${FRONTEND_SERVICE} \
  --region=${REGION} \
  --format="value(metadata.annotations.'run.googleREDACTED')" || echo "none")

if [ "${VPC_CONNECTOR}" == "none" ] || [ -z "${VPC_CONNECTOR}" ]; then
  echo -e "   ${RED}ERROR: Frontend is not using a VPC connector${NC}"
  echo "   This is required for internal traffic routing"
else
  echo "   ✓ VPC connector: ${VPC_CONNECTOR}"
fi

# Deploy the changes with traffic
echo -e "\n${GREEN}7. Routing traffic to updated revision...${NC}"
gcloud run services update-traffic ${FRONTEND_SERVICE} \
  --region=${REGION} \
  --to-latest

echo -e "\n${GREEN}8. Testing the configuration...${NC}"
FRONTEND_URL=$(gcloud run services describe ${FRONTEND_SERVICE} \
  --region=${REGION} \
  --format="value(status.url)")

echo "   Frontend URL: ${FRONTEND_URL}"
echo -e "\n${GREEN}Testing health endpoint...${NC}"
curl -s "${FRONTEND_URL}/api/health" | jq . || echo "Health check failed"

echo -e "\n${GREEN}Summary:${NC}"
echo "========================================="
echo "Frontend service: ${FRONTEND_SERVICE}"
echo "Backend service: ${BACKEND_SERVICE}"
echo "Backend public URL: ${BACKEND_PUBLIC_URL}"
echo "Frontend SA: ${FRONTEND_SA}"
echo "VPC Connector: ${VPC_CONNECTOR}"
echo ""
echo -e "${GREEN}✓ Configuration updated successfully!${NC}"
echo ""
echo "To test the proxy, try:"
echo "  curl ${FRONTEND_URL}/api/proxy/health"
