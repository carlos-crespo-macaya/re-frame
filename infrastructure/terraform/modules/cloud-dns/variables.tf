variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "domain" {
  description = "Domain name (e.g., re-frame.social)"
  type        = string
}

variable "ttl" {
  description = "Default TTL for DNS records"
  type        = number
  default     = 300
}

variable "enable_firebase" {
  description = "Enable Firebase Hosting DNS records"
  type        = bool
  default     = true
}

variable "firebase_hosting_ips" {
  description = "Firebase Hosting IP addresses"
  type        = list(string)
  default = [
    "151.101.1.195",
    "151.101.65.195"
  ]
}

variable "firebase_site_id" {
  description = "Firebase Hosting site ID"
  type        = string
  default     = ""
}

variable "cloud_run_url" {
  description = "Cloud Run service URL (without https://)"
  type        = string
  default     = ""
}

variable "enable_email" {
  description = "Enable email forwarding records"
  type        = bool
  default     = false
}

variable "mx_records" {
  description = "MX records for email"
  type        = list(string)
  default = [
    "10 mx1.name.com.",
    "20 mx2.name.com."
  ]
}

variable "spf_record" {
  description = "SPF TXT record"
  type        = string
  default     = "\"v=spf1 include:spf.name.com ~all\""
}

variable "domain_verification_record" {
  description = "Domain verification TXT record (if needed)"
  type        = string
  default     = ""
}