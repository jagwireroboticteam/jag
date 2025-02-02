
# ✅ Create Service Account
resource "google_service_account" "svc_tf_ja_wire_robotics" {
  account_id   = "svc-tf-ja-wire-robotics"
  display_name = "Service Account for Terraform-managed resources"
}

# ✅ Generate Service Account Key
resource "google_service_account_key" "svc_tf_ja_wire_robotics_key" {
  service_account_id = google_service_account.svc_tf_ja_wire_robotics.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

# ✅ Assign IAM Roles (Including Firestore Admin)
resource "google_project_iam_member" "svc_tf_ja_wire_robotics_roles" {
  for_each = toset([
    "roles/cloudbuild.builds.builder",
    "roles/storage.admin",
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/logging.logWriter",
    "roles/artifactregistry.writer",
    "roles/resourcemanager.projectIamAdmin",
    "roles/datastore.owner",
    "roles/datastore.user",
    "roles/firebase.admin",
    "roles/iam.serviceAccountTokenCreator"
  ])

  project = "jagwirerobotic"
  role    = each.key
  member  = "serviceAccount:${google_service_account.svc_tf_ja_wire_robotics.email}"
}

# ✅ Store Service Account Key in Secret Manager
resource "google_secret_manager_secret" "robotics_secret" {
  project   = "jagwirerobotic"
  secret_id = "jagwire-crediential"

  replication {
    auto {}  # ✅ Fixed replication block
  }
}

# ✅ Store the JSON Key for Service Account in Secret Manager
resource "google_secret_manager_secret_version" "robotics_secret_version" {
  secret      = google_secret_manager_secret.robotics_secret.id
  secret_data = base64decode(google_service_account_key.svc_tf_ja_wire_robotics_key.private_key)
}

resource "google_project_iam_member" "secret_manager_access" {
  project = "jagwirerobotic"
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:svc-tf-ja-wire-robotics@jagwirerobotic.iam.gserviceaccount.com"
}
