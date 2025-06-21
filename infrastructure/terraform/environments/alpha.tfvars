# Alpha environment configuration
project_id  = "re-frame-alpha" # Replace with your actual project ID
region      = "us-central1"
environment = "alpha"

# Cloud Run configuration (minimal for cost savings)
cloud_run_service_name  = "re-frame-backend-alpha"
cloud_run_max_instances = 1 # Very limited for alpha
cloud_run_cpu           = "1"
cloud_run_memory        = "512Mi"

# Firebase configuration
firebase_hosting_site_id = "re-frame-alpha"
auth_domain              = "re-frame-alpha.firebaseapp.com"

# Note: Set GEMINI_API_KEY as an environment variable or use a secrets manager
# export TF_VAR_gemini_api_key="your-api-key-here"