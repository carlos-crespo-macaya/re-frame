output "hosting_url" {
  description = "Firebase Hosting URL"
  value       = "https://${var.hosting_site_id}.web.app"
}

output "site_id" {
  description = "Firebase Hosting site ID"
  value       = google_firebase_hosting_site.default.site_id
}

output "auth_domain" {
  description = "Firebase Auth domain"
  value       = var.auth_domain
}

output "web_app_id" {
  description = "Firebase Web App ID"
  value       = google_firebase_web_app.default.app_id
}

output "firebase_config" {
  description = "Firebase SDK configuration"
  value = {
    projectId     = var.project_id
    appId         = google_firebase_web_app.default.app_id
    authDomain    = var.auth_domain
    storageBucket = "${var.project_id}.appspot.com"
  }
  sensitive = true
}