# Phase 1: Billing and Budget Alerts Only
# Apply this FIRST before any other infrastructure

terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "gen-lang-client-0135194996-terraform-state"
    prefix = "terraform/phase1-billing"
  }
}

provider "google" {
  project         = var.project_id
  region          = var.region
  billing_project = var.project_id
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "gen-lang-client-0135194996"
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "billing_account_id" {
  description = "Billing account ID"
  type        = string
  default     = "01FB26-BC3BF1-C9A591"
}

variable "budget_alert_email" {
  description = "Email for budget alerts"
  type        = string
}

# Create budget with multiple alert thresholds
resource "google_billing_budget" "project_budget" {
  billing_account = var.billing_account_id
  display_name    = "${var.project_id}-budget"

  budget_filter {
    projects               = ["projects/${var.project_id}"]
    services               = []
    credit_types_treatment = "INCLUDE_ALL_CREDITS"
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = "300"
    }
  }

  # Alert thresholds
  threshold_rules {
    threshold_percent = 0.03 # $10 alert
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 0.17 # $50 alert
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 0.33 # $100 alert
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 0.50 # $150 alert
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 0.67 # $200 alert
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 0.83 # $250 alert - CRITICAL
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 0.90 # $270 alert - EMERGENCY
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 1.0 # $300 alert - BUDGET EXHAUSTED
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 1.2 # Alert if forecasted to exceed by 20%
    spend_basis       = "FORECASTED_SPEND"
  }

  all_updates_rule {
    monitoring_notification_channels = [google_monitoring_notification_channel.email.id]
    schema_version                   = "1.0"
  }
}

# Email notification channel
resource "google_monitoring_notification_channel" "email" {
  display_name = "Budget Alert Email"
  type         = "email"

  labels = {
    email_address = var.budget_alert_email
  }

  enabled = true
}

# Outputs
output "budget_name" {
  value = google_billing_budget.project_budget.display_name
}

output "notification_channel" {
  value = google_monitoring_notification_channel.email.display_name
}

output "alert_thresholds" {
  value = [
    for rule in google_billing_budget.project_budget.threshold_rules : {
      percent = format("%.0f", rule.threshold_percent * 100)
      amount  = format("%.0f", rule.threshold_percent * 300)
      basis   = rule.spend_basis
    }
  ]
}