terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "firestore.googleapis.com",
    "firebase.googleapis.com",
    "firebaserules.googleapis.com",
    "firebasehosting.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com",
    "compute.googleapis.com",
    "cloudarmor.googleapis.com"
  ])

  service            = each.value
  disable_on_destroy = false
}

# Cloud Run Module
module "cloud_run" {
  source = "./modules/cloud-run"

  project_id   = var.project_id
  region       = var.region
  service_name = var.cloud_run_service_name
  image_url    = var.backend_image_url

  # Cost-saving measures
  min_instances = 0 # Scale to zero
  max_instances = var.cloud_run_max_instances
  cpu           = var.cloud_run_cpu
  memory        = var.cloud_run_memory

  environment_variables = {
    PROJECT_ID          = var.project_id
    ENVIRONMENT         = var.environment
    GEMINI_API_KEY      = var.gemini_api_key
    RATE_LIMIT_REQUESTS = "10"
    RATE_LIMIT_WINDOW   = "3600" # 1 hour in seconds
  }

  depends_on = [google_project_service.required_apis]
}

# Firestore Module
module "firestore" {
  source = "./modules/firestore"

  project_id    = var.project_id
  region        = var.region
  database_name = "(default)"

  depends_on = [google_project_service.required_apis]
}

# Firebase Module
module "firebase" {
  source = "./modules/firebase"

  project_id      = var.project_id
  hosting_site_id = var.firebase_hosting_site_id
  auth_domain     = var.auth_domain

  depends_on = [google_project_service.required_apis]
}

# Cloud Armor Module
module "cloud_armor" {
  source = "./modules/cloud-armor"

  project_id        = var.project_id
  policy_name       = "${var.project_id}-security-policy"
  cloud_run_service = module.cloud_run.service_name

  # Rate limiting rules
  rate_limit_threshold = 10
  rate_limit_interval  = 3600 # 1 hour

  depends_on = [module.cloud_run]
}