resource "google_firebase_project" "default" {
  provider = google-beta
  project  = var.project_id
}

# Firebase Auth configuration
resource "google_identity_platform_config" "default" {
  project = var.project_id
  
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
      quota_duration = "86400s"  # 24 hours
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

# Firebase Hosting
resource "google_firebase_hosting_site" "default" {
  provider = google-beta
  project  = var.project_id
  site_id  = var.hosting_site_id
  
  depends_on = [google_firebase_project.default]
}

# Firebase Hosting configuration
resource "google_firebase_hosting_version" "default" {
  provider = google-beta
  project  = var.project_id
  site_id  = google_firebase_hosting_site.default.site_id
  
  config {
    rewrites {
      glob = "**"
      path = "/index.html"
    }
    
    headers {
      glob = "**/*.@(js|css|woff2)"
      headers = {
        "Cache-Control" = "max-age=31536000"
      }
    }
    
    headers {
      glob = "**"
      headers = {
        "X-Frame-Options"        = "DENY"
        "X-Content-Type-Options" = "nosniff"
        "X-XSS-Protection"       = "1; mode=block"
        "Referrer-Policy"        = "strict-origin-when-cross-origin"
        "Permissions-Policy"     = "geolocation=(), microphone=(), camera=()"
        "Content-Security-Policy" = join(" ", [
          "default-src 'self';",
          "script-src 'self' 'unsafe-inline' https://*.googleapis.com https://*.firebaseapp.com;",
          "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;",
          "font-src 'self' https://fonts.gstatic.com;",
          "img-src 'self' data: https:;",
          "connect-src 'self' https://*.googleapis.com https://*.firebaseapp.com ${var.project_id}.web.app;",
          "frame-src 'none';",
          "object-src 'none';",
          "base-uri 'self';",
          "form-action 'self';"
        ])
      }
    }
  }
}

# Firebase Hosting release (will be updated by CI/CD)
resource "google_firebase_hosting_release" "default" {
  provider     = google-beta
  project      = var.project_id
  site_id      = google_firebase_hosting_site.default.site_id
  version_name = google_firebase_hosting_version.default.version_name
  
  message = "Initial release"
}