output "cloud_run_url" {
  description = "URL of the Cloud Run service"
  value       = module.cloud_run.service_url
}

output "firebase_hosting_url" {
  description = "Firebase Hosting URL"
  value       = module.firebase.hosting_url
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