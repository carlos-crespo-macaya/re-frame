resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = var.database_name
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
  
  # Cost-saving: Use smallest possible configuration
  concurrency_mode            = "OPTIMISTIC"
  app_engine_integration_mode = "DISABLED"
  
  # Point-in-time recovery (disabled for cost savings)
  point_in_time_recovery_enablement = "POINT_IN_TIME_RECOVERY_DISABLED"
  
  # Delete protection (disabled for alpha)
  delete_protection_state = "DELETE_PROTECTION_DISABLED"
}

# Firestore indexes for common queries
resource "google_firestore_index" "sessions_by_user" {
  project    = var.project_id
  database   = google_firestore_database.database.name
  collection = "sessions"
  
  fields {
    field_path = "userId"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "createdAt"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "reframes_by_session" {
  project    = var.project_id
  database   = google_firestore_database.database.name
  collection = "reframes"
  
  fields {
    field_path = "sessionId"
    order      = "ASCENDING"
  }
  
  fields {
    field_path = "createdAt"
    order      = "DESCENDING"
  }
}

# Firestore security rules
resource "google_firebaserules_ruleset" "firestore" {
  project = var.project_id
  source {
    files {
      name = "firestore.rules"
      content = <<-EOT
        rules_version = '2';
        service cloud.firestore {
          match /databases/{database}/documents {
            // Sessions collection
            match /sessions/{sessionId} {
              allow read: if request.auth != null && 
                (request.auth.uid == resource.data.userId || 
                 resource.data.isAnonymous == true);
              allow create: if request.auth != null;
              allow update: if false; // Sessions are immutable
              allow delete: if request.auth != null && 
                request.auth.uid == resource.data.userId;
            }
            
            // Reframes collection
            match /reframes/{reframeId} {
              allow read: if request.auth != null && 
                request.auth.uid == resource.data.userId;
              allow create: if request.auth != null;
              allow update: if false; // Reframes are immutable
              allow delete: if false; // No deletion for audit trail
            }
            
            // Rate limiting collection (server-side only)
            match /rateLimits/{document} {
              allow read: if false;
              allow write: if false;
            }
          }
        }
      EOT
    }
  }
}

resource "google_firebaserules_release" "firestore" {
  project      = var.project_id
  release_id   = "cloud.firestore"
  ruleset_name = google_firebaserules_ruleset.firestore.name
}