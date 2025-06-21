resource "google_compute_security_policy" "policy" {
  name        = var.policy_name
  description = "Security policy for re-frame application"
  
  # Default rule - allow traffic
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default rule - allow all traffic"
  }
  
  # Rate limiting rule
  rule {
    action   = "rate_based_ban"
    priority = "1000"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      
      rate_limit_threshold {
        count        = var.rate_limit_threshold
        interval_sec = var.rate_limit_interval
      }
      
      ban_duration_sec = 600  # Ban for 10 minutes
    }
    description = "Rate limiting - ${var.rate_limit_threshold} requests per ${var.rate_limit_interval} seconds"
  }
  
  # Block common attack patterns
  rule {
    action   = "deny(403)"
    priority = "900"
    match {
      expr {
        expression = <<-EOT
          // SQL Injection patterns
          request.headers['user-agent'].contains('sqlmap') ||
          request.path.contains('union') && request.path.contains('select') ||
          request.path.contains('exec(') ||
          request.path.contains('EXEC(') ||
          
          // XSS patterns
          request.path.contains('<script') ||
          request.path.contains('javascript:') ||
          request.body.size > 0 && request.body.contains('<script') ||
          
          // Path traversal
          request.path.contains('../') ||
          request.path.contains('..\\') ||
          
          // Common scanner patterns
          request.headers['user-agent'].contains('nikto') ||
          request.headers['user-agent'].contains('nmap') ||
          request.headers['user-agent'].contains('masscan')
        EOT
      }
    }
    description = "Block common attack patterns"
  }
  
  # Geo-blocking rule (optional - uncomment if needed)
  # rule {
  #   action   = "deny(403)"
  #   priority = "800"
  #   match {
  #     expr {
  #       expression = "origin.region_code in ['CN', 'RU', 'KP']"
  #     }
  #   }
  #   description = "Geo-blocking for high-risk countries"
  # }
  
  # Adaptive protection (DDoS mitigation)
  adaptive_protection_config {
    layer_7_ddos_defense_config {
      enable = true
      rule_visibility = "STANDARD"
    }
  }
  
  # Recaptcha options for future use
  recaptcha_options_config {
    redirect_site_key = ""  # To be configured when reCAPTCHA is set up
  }
}