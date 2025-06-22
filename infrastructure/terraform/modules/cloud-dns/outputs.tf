output "zone_name" {
  description = "The name of the DNS zone"
  value       = google_dns_managed_zone.main.name
}

output "zone_dns_name" {
  description = "The DNS name of the zone"
  value       = google_dns_managed_zone.main.dns_name
}

output "name_servers" {
  description = "The name servers for the DNS zone"
  value       = google_dns_managed_zone.main.name_servers
}

output "dns_records" {
  description = "Summary of configured DNS records"
  value = {
    root_domain = var.enable_firebase ? "A records -> Firebase Hosting" : "Not configured"
    www         = var.enable_firebase ? "CNAME -> ${var.firebase_site_id}.web.app" : "Not configured"
    api         = var.cloud_run_url != "" ? "CNAME -> ${var.cloud_run_url}" : "Not configured"
    email       = var.enable_email ? "MX records configured" : "Not configured"
  }
}