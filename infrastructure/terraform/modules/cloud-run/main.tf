resource "google_cloud_run_service" "backend" {
  name     = var.service_name
  location = var.region

  template {
    spec {
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