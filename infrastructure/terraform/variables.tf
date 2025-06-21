variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (e.g., alpha, beta, prod)"
  type        = string
  default     = "alpha"
}

# Cloud Run Variables
variable "cloud_run_service_name" {
  description = "Name of the Cloud Run service"
  type        = string
  default     = "re-frame-backend"
}

variable "backend_image_url" {
  description = "Docker image URL for the backend service"
  type        = string
  default     = "gcr.io/PROJECT_ID/re-frame-backend:latest"
}

variable "cloud_run_max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 2  # Keep low for cost savings
}

variable "cloud_run_cpu" {
  description = "CPU allocation for Cloud Run instances"
  type        = string
  default     = "1"  # Minimum CPU
}

variable "cloud_run_memory" {
  description = "Memory allocation for Cloud Run instances"
  type        = string
  default     = "512Mi"  # Minimum memory for cost savings
}

# Firebase Variables
variable "firebase_hosting_site_id" {
  description = "Firebase Hosting site ID"
  type        = string
  default     = "re-frame-social"
}

variable "auth_domain" {
  description = "Firebase Auth domain"
  type        = string
  default     = "re-frame-social.firebaseapp.com"
}

# API Keys (sensitive)
variable "gemini_api_key" {
  description = "Google AI Studio API key for Gemini"
  type        = string
  sensitive   = true
}