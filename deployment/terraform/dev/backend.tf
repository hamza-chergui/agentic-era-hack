terraform {
  backend "gcs" {
    bucket = "qwiklabs-gcp-03-9c0614a7634c-terraform-state"
    prefix = "dev"
  }
}
