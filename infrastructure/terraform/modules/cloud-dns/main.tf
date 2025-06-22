terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Create DNS zone
resource "google_dns_managed_zone" "main" {
  name        = "${replace(var.domain, ".", "-")}-zone"
  dns_name    = "${var.domain}."
  description = "DNS zone for ${var.domain}"
  project     = var.project_id

  dnssec_config {
    state = "on"
  }

  lifecycle {
    prevent_destroy = true
  }
}

# A records for root domain (Firebase Hosting)
resource "google_dns_record_set" "root_a" {
  count = var.enable_firebase ? 1 : 0

  name         = google_dns_managed_zone.main.dns_name
  type         = "A"
  ttl          = var.ttl
  managed_zone = google_dns_managed_zone.main.name
  project      = var.project_id

  rrdatas = var.firebase_hosting_ips
}

# CNAME for www subdomain (Firebase Hosting)
resource "google_dns_record_set" "www_cname" {
  count = var.enable_firebase ? 1 : 0

  name         = "www.${google_dns_managed_zone.main.dns_name}"
  type         = "CNAME"
  ttl          = var.ttl
  managed_zone = google_dns_managed_zone.main.name
  project      = var.project_id

  rrdatas = ["${var.firebase_site_id}.web.app."]
}

# CNAME for api subdomain (Cloud Run)
resource "google_dns_record_set" "api_cname" {
  count = var.cloud_run_url != "" ? 1 : 0

  name         = "api.${google_dns_managed_zone.main.dns_name}"
  type         = "CNAME"
  ttl          = var.ttl
  managed_zone = google_dns_managed_zone.main.name
  project      = var.project_id

  rrdatas = ["${replace(var.cloud_run_url, "https://", "")}"]
}

# MX records for email forwarding
resource "google_dns_record_set" "mx" {
  count = var.enable_email ? 1 : 0

  name         = google_dns_managed_zone.main.dns_name
  type         = "MX"
  ttl          = var.ttl
  managed_zone = google_dns_managed_zone.main.name
  project      = var.project_id

  rrdatas = var.mx_records
}

# SPF TXT record
resource "google_dns_record_set" "spf" {
  count = var.enable_email ? 1 : 0

  name         = google_dns_managed_zone.main.dns_name
  type         = "TXT"
  ttl          = var.ttl
  managed_zone = google_dns_managed_zone.main.name
  project      = var.project_id

  rrdatas = [var.spf_record]
}

# Domain verification TXT record (if provided)
resource "google_dns_record_set" "domain_verification" {
  count = var.domain_verification_record != "" ? 1 : 0

  name         = google_dns_managed_zone.main.dns_name
  type         = "TXT"
  ttl          = 300 # Keep low for verification
  managed_zone = google_dns_managed_zone.main.name
  project      = var.project_id

  rrdatas = [var.domain_verification_record]
}