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