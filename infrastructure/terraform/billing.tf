# Billing Budget and Alerts Configuration
# CRITICAL: This must be applied FIRST to prevent cost overruns

# Create budget with multiple alert thresholds
resource "google_billing_budget" "project_budget" {
  billing_account = var.billing_account_id
  display_name    = "${var.project_id}-budget"

  budget_filter {
    projects = ["projects/${var.project_id}"]

    # Monitor all services
    services = []

    # Include all charges
    credit_types_treatment = "INCLUDE_ALL_CREDITS"
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = var.budget_amount
    }
  }

  # Alert thresholds - aggressive for early warning
  threshold_rules {
    threshold_percent = 0.03 # $10 alert (3.33% of $300)
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

  # Forecasted spend alerts
  threshold_rules {
    threshold_percent = 1.2 # Alert if forecasted to exceed by 20%
    spend_basis       = "FORECASTED_SPEND"
  }

  # Email notifications
  all_updates_rule {
    monitoring_notification_channels = var.notification_channels
    schema_version                   = "1.0"
  }
}

# Create monitoring notification channel for email alerts
resource "google_monitoring_notification_channel" "email" {
  display_name = "Budget Alert Email"
  type         = "email"

  labels = {
    email_address = var.budget_alert_email
  }

  enabled = true
}

# Daily spend monitoring alert policy
resource "google_monitoring_alert_policy" "daily_spend_alert" {
  display_name = "${var.project_id}-daily-spend-alert"
  combiner     = "OR"

  conditions {
    display_name = "Daily spend exceeds $10"

    condition_threshold {
      filter          = "resource.type=\"billing_account\" AND metric.type=\"billing.googleapis.com/billing/v1/daily_cost\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 10

      aggregations {
        alignment_period   = "86400s" # 24 hours
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "86400s" # Auto close after 24 hours
  }

  documentation {
    content = "Daily spend has exceeded $10. Immediate action required to review and potentially scale down services."
  }
}

# Output important budget information
output "budget_name" {
  value       = google_billing_budget.project_budget.display_name
  description = "The name of the created budget"
}

output "budget_amount" {
  value       = google_billing_budget.project_budget.amount[0].specified_amount[0].units
  description = "The budget amount in USD"
}

# Output alert thresholds as a simple list to avoid Checkov parser issues
output "alert_threshold_percentages" {
  value = [
    for rule in google_billing_budget.project_budget.threshold_rules : 
    rule.threshold_percent
  ]
  description = "List of alert threshold percentages"
}

output "alert_threshold_amounts" {
  value = [
    for rule in google_billing_budget.project_budget.threshold_rules : 
    floor(rule.threshold_percent * tonumber(var.budget_amount))
  ]
  description = "List of alert threshold amounts in USD"
}