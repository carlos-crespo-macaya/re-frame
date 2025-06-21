variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "database_name" {
  description = "Firestore database name"
  type        = string
  default     = "(default)"
}