provider "google" {
  project = "jagwirerobotic"
  region  = "us-central1"
}

resource "google_service_account" "svc_tf_ja_wire_robotics" {
  account_id   = "svc-tf-ja-wire-robotics"
  display_name = "Service Account for Terraform-managed resources"
}

resource "google_service_account_key" "svc_tf_ja_wire_robotics_key" {
  service_account_id = google_service_account.svc_tf_ja_wire_robotics.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

resource "google_project_iam_member" "svc_tf_ja_wire_robotics_roles" {
  for_each = toset([
    "roles/cloudbuild.builds.builder", # Build permissions for Cloud Build
    "roles/storage.admin",            # Full access to Cloud Storage
    "roles/run.admin",                # Correct role for Cloud Run management
    "roles/datastore.user",           # Access Firestore
    "roles/iam.serviceAccountUser",   # Impersonation rights
    "roles/logging.logWriter",         # Write logs to Cloud Logging
    "roles/artifactregistry.writer"

  ])

  project = "jagwirerobotic"
  role    = each.key
  member  = "serviceAccount:${google_service_account.svc_tf_ja_wire_robotics.email}"
}

resource "google_storage_bucket" "build_logs_bucket" {
  name          = "jagwirerobotic-build-logs"
  location      = "US"
  force_destroy = true
  uniform_bucket_level_access = true
}
