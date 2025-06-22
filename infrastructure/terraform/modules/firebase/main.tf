terraform {
  required_providers {
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

resource "google_firebase_project" "default" {
  provider = google-beta
  project  = var.project_id
}

# Firebase Auth configuration
resource "google_identity_platform_config" "default" {
  provider = google-beta
  project  = var.project_id

  # Enable anonymous auth for alpha phase
  sign_in {
    allow_duplicate_emails = false
    anonymous {
      enabled = true
    }
    email {
      enabled           = true
      password_required = true
    }
  }

  # Rate limiting for auth
  quota {
    sign_up_quota_config {
      quota          = 100
      quota_duration = "86400s" # 24 hours
    }
  }

  # Authorized domains
  authorized_domains = [
    "localhost",
    var.auth_domain,
    "${var.project_id}.web.app",
    "${var.project_id}.firebaseapp.com"
  ]
}

# Firebase Web App
resource "google_firebase_web_app" "default" {
  provider     = google-beta
  project      = var.project_id
  display_name = "re-frame Web App"

  depends_on = [google_firebase_project.default]
}

# Firebase Hosting
resource "google_firebase_hosting_site" "default" {
  provider = google-beta
  project  = var.project_id
  site_id  = var.hosting_site_id

  depends_on = [google_firebase_project.default]
}

# Firebase Hosting custom domain
# Note: This creates the custom domain mapping but requires manual DNS verification
resource "google_firebase_hosting_custom_domain" "main" {
  provider      = google-beta
  project       = var.project_id
  site_id       = google_firebase_hosting_site.default.site_id
  custom_domain = var.custom_domain

  count = var.custom_domain != "" ? 1 : 0

  # Wait for manual DNS verification before creating
  # DNS records must be added to your domain registrar
  wait_dns_verification = false

  depends_on = [google_firebase_hosting_site.default]
}

resource "google_firebase_hosting_custom_domain" "www" {
  provider      = google-beta
  project       = var.project_id
  site_id       = google_firebase_hosting_site.default.site_id
  custom_domain = "www.${var.custom_domain}"

  count = var.custom_domain != "" ? 1 : 0

  wait_dns_verification = false

  depends_on = [google_firebase_hosting_site.default]
}

# Firebase Hosting deployment notes
# Note: Firebase Hosting configuration will be managed via Firebase CLI
# due to limitations in Terraform provider v5.x
# 
# The firebase.json file in the frontend directory defines:
# - Hosting rewrites and headers
# - Security headers (CSP, X-Frame-Options, etc.)
# - Cache control settings
#
# Deployment will be handled by CI/CD using:
# firebase deploy --only hosting