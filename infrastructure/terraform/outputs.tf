output "cloud_run_url" {
  description = "URL of the Cloud Run service"
  value       = module.cloud_run.service_url
}

output "firebase_hosting_url" {
  description = "Firebase Hosting URL"
  value       = module.firebase.hosting_url
}

output "firebase_web_app_id" {
  description = "Firebase Web App ID"
  value       = module.firebase.web_app_id
}

output "firebase_config" {
  description = "Firebase SDK configuration for frontend"
  value       = module.firebase.firebase_config
  sensitive   = true
}

output "firestore_database_name" {
  description = "Firestore database name"
  value       = module.firestore.database_name
}

output "cloud_armor_policy_name" {
  description = "Cloud Armor security policy name"
  value       = module.cloud_armor.policy_name
}

output "estimated_monthly_cost" {
  description = "Estimated monthly cost based on minimal usage"
  value = {
    cloud_run     = "$0-5 (with scale to zero)"
    firestore     = "$0-10 (minimal usage)"
    firebase_auth = "$0 (free tier)"
    hosting       = "$0 (free tier)"
    total         = "< $15/month"
  }
}

# DNS Configuration Instructions
output "dns_configuration" {
  description = "DNS configuration instructions for name.com"
  value = {
    instructions = "Configure these DNS records in name.com:"
    a_records = [
      "Type: A | Name: @ | Value: 151.101.1.195",
      "Type: A | Name: @ | Value: 151.101.65.195"
    ]
    cname_records = [
      "Type: CNAME | Name: www | Value: ${var.firebase_hosting_site_id}.web.app",
      "Type: CNAME | Name: api | Value: ${replace(module.cloud_run.service_url, "https://", "")}"
    ]
    verification = "Add Firebase verification TXT record when prompted in Firebase Console"
    note         = "DNS propagation can take up to 48 hours"
  }
}

# Optional: Cloud DNS nameservers (if using Google Cloud DNS)
# output "cloud_dns_nameservers" {
#   description = "Cloud DNS nameservers (if enabled)"
#   value       = var.enable_cloud_dns ? module.cloud_dns[0].name_servers : ["Using name.com DNS"]
# }