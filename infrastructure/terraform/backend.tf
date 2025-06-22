# Terraform backend configuration for remote state storage
# Note: Backend configuration cannot use variables, so the bucket name must be hardcoded
# This should match: ${var.project_id}-terraform-state
terraform {
  backend "gcs" {
    bucket = "gen-lang-client-0135194996-terraform-state"
    prefix = "terraform/state"
  }
}