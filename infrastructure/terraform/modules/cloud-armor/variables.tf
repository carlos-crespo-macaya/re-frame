variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "policy_name" {
  description = "Name of the Cloud Armor security policy"
  type        = string
}

variable "cloud_run_service" {
  description = "Name of the Cloud Run service to protect"
  type        = string
}

variable "rate_limit_threshold" {
  description = "Number of requests allowed in the rate limit interval"
  type        = number
  default     = 10
}

variable "rate_limit_interval" {
  description = "Rate limit interval in seconds"
  type        = number
  default     = 3600  # 1 hour
}