# Terraform backend configuration for remote state storage
terraform {
  backend "gcs" {
    bucket = "gen-lang-client-0135194996-terraform-state"
    prefix = "terraform/state"
  }
}