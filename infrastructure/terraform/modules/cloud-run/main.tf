# Service account for Cloud Run with minimal permissions
resource "google_service_account" "cloud_run" {
  account_id   = "${var.service_name}-sa"
  display_name = "Service Account for ${var.service_name}"
  description  = "Service account for Cloud Run service with minimal permissions"
}

# Grant necessary permissions to the service account
resource "google_project_iam_member" "cloud_run_permissions" {
  for_each = toset([
    "roles/firestore.dataUser",           # Access Firestore
    "roles/logging.logWriter",            # Write logs
    "roles/cloudtrace.agent",             # Send traces
    "roles/monitoring.metricWriter",      # Write metrics
    "roles/secretmanager.secretAccessor", # Access secrets
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Grant Container Registry access to pull images
resource "google_storage_bucket_iam_member" "cloud_run_gcr_access" {
  bucket = "artifacts.${var.project_id}.appspot.com"
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_cloud_run_service" "backend" {
  name     = var.service_name
  location = var.region

  template {
    spec {
      # Use the dedicated service account
      service_account_name = google_service_account.cloud_run.email

      containers {
        image = var.image_url

        # Cost-saving: minimal resources
        resources {
          limits = {
            cpu    = var.cpu
            memory = var.memory
          }
        }

        # Environment variables
        dynamic "env" {
          for_each = var.environment_variables
          content {
            name  = env.key
            value = env.value
          }
        }

        # Secret environment variables from Secret Manager
        dynamic "env" {
          for_each = var.secret_environment_variables
          content {
            name = env.key
            value_from {
              secret_key_ref {
                name = env.value.secret_name
                key  = env.value.secret_version
              }
            }
          }
        }

        # Health check endpoint
        startup_probe {
          http_get {
            path = "/health"
          }
          initial_delay_seconds = 10
          timeout_seconds       = 3
          period_seconds        = 10
          failure_threshold     = 3
        }
      }

      # Concurrency limit per instance
      container_concurrency = 80

      # Request timeout
      timeout_seconds = 300
    }

    metadata {
      annotations = {
        # Scale to zero when not in use
        "autoscaling.knative.dev/minScale" = tostring(var.min_instances)
        "autoscaling.knative.dev/maxScale" = tostring(var.max_instances)

        # CPU allocation during request processing only
        "run.googleapis.com/cpu-throttling" = "true"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true
}

# IAM policy to allow public access
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.backend.name
  location = google_cloud_run_service.backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}