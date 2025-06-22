#!/bin/bash
# DNS Verification Script for re-frame.social

set -e

DOMAIN="re-frame.social"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 DNS Verification for ${DOMAIN}"
echo "================================"

# Function to check DNS record
check_dns() {
    local record_type=$1
    local subdomain=$2
    local expected=$3
    local domain_to_check="${subdomain}${DOMAIN}"
    
    if [ -z "$subdomain" ]; then
        domain_to_check="${DOMAIN}"
    fi
    
    echo -n "Checking ${record_type} record for ${domain_to_check}... "
    
    result=$(dig +short ${domain_to_check} ${record_type} 2>/dev/null)
    
    if [ -z "$result" ]; then
        echo -e "${RED}❌ No ${record_type} record found${NC}"
        return 1
    else
        echo -e "${GREEN}✓ Found: ${result}${NC}"
        if [ ! -z "$expected" ] && [[ ! "$result" =~ "$expected" ]]; then
            echo -e "${YELLOW}  ⚠️  Expected to contain: ${expected}${NC}"
        fi
        return 0
    fi
}

# Check A records for root domain
echo -e "\n${YELLOW}1. Root Domain A Records:${NC}"
check_dns "A" "" "151.101"

# Check CNAME for www
echo -e "\n${YELLOW}2. WWW Subdomain:${NC}"
check_dns "CNAME" "www." "web.app"

# Check CNAME for api
echo -e "\n${YELLOW}3. API Subdomain:${NC}"
check_dns "CNAME" "api." "run.app"

# Check TXT records (for domain verification)
echo -e "\n${YELLOW}4. TXT Records:${NC}"
check_dns "TXT" "" ""

# Check from different DNS servers
echo -e "\n${YELLOW}5. Checking from different DNS servers:${NC}"
for server in "8.8.8.8" "1.1.1.1"; do
    echo -e "\n  Using DNS server ${server}:"
    echo -n "  Root domain: "
    dig +short @${server} ${DOMAIN} A | head -n1 || echo -e "${RED}Failed${NC}"
    echo -n "  WWW: "
    dig +short @${server} www.${DOMAIN} CNAME | head -n1 || echo -e "${RED}Failed${NC}"
    echo -n "  API: "
    dig +short @${server} api.${DOMAIN} CNAME | head -n1 || echo -e "${RED}Failed${NC}"
done

# Check HTTPS connectivity
echo -e "\n${YELLOW}6. HTTPS Connectivity:${NC}"
for url in "https://${DOMAIN}" "https://www.${DOMAIN}" "https://api.${DOMAIN}"; do
    echo -n "Testing ${url}... "
    if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "${url}" | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✓ Reachable${NC}"
    else
        echo -e "${RED}❌ Not reachable or certificate issue${NC}"
    fi
done

echo -e "\n${YELLOW}7. SSL Certificate Check:${NC}"
for domain in "${DOMAIN}" "www.${DOMAIN}" "api.${DOMAIN}"; do
    echo -n "Checking SSL for ${domain}... "
    if echo | openssl s_client -servername ${domain} -connect ${domain}:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null; then
        echo -e "${GREEN}✓ Valid SSL certificate${NC}"
    else
        echo -e "${YELLOW}⚠️  SSL certificate not yet provisioned${NC}"
    fi
done

echo -e "\n================================"
echo "📝 Notes:"
echo "- DNS propagation can take up to 48 hours"
echo "- SSL certificates are auto-provisioned after domain verification"
echo "- Use 'terraform output dns_configuration' for setup instructions"