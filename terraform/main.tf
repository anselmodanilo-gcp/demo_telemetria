terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0.0, < 7.0.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# ------------------------------------------------------------------------------
# 1. Google Cloud APIs Activation
# ------------------------------------------------------------------------------
resource "google_project_service" "compute_api" {
  project            = var.project_id
  service            = "compute.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "logging_api" {
  project            = var.project_id
  service            = "logging.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "monitoring_api" {
  project            = var.project_id
  service            = "monitoring.googleapis.com"
  disable_on_destroy = false
}

# ------------------------------------------------------------------------------
# 2. VPC Network and Subnet (us-central1)
# ------------------------------------------------------------------------------
resource "google_compute_network" "telemetry_vpc" {
  name                    = var.network_name
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
  mtu                     = 1460
  depends_on              = [google_project_service.compute_api]
}

resource "google_compute_subnetwork" "telemetry_subnet" {
  name                     = "${var.network_name}-${var.region}-subnet"
  ip_cidr_range            = var.subnet_cidr
  region                   = var.region
  network                  = google_compute_network.telemetry_vpc.id
  private_ip_google_access = true
}

# ------------------------------------------------------------------------------
# 3. Cloud Router & Cloud NAT (Outbound connectivity)
# ------------------------------------------------------------------------------
resource "google_compute_router" "telemetry_router" {
  name    = "${var.network_name}-router"
  region  = var.region
  network = google_compute_network.telemetry_vpc.id
}

resource "google_compute_router_nat" "telemetry_nat" {
  name                               = "${var.network_name}-nat"
  router                             = google_compute_router.telemetry_router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# ------------------------------------------------------------------------------
# 4. Firewall Rules
# ------------------------------------------------------------------------------
# Allow SSH via Google Cloud IAP and standard SSH
resource "google_compute_firewall" "allow_ssh" {
  name        = "${var.network_name}-allow-ssh"
  network     = google_compute_network.telemetry_vpc.name
  description = "Allow SSH access to Compute Engine instances from Google IAP and internet"
  direction   = "INGRESS"
  priority    = 1000

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["35.235.240.0/20", "0.0.0.0/0"]
  target_tags   = ["telemetry-server"]
}

# Allow Port 8000 (FastAPI Telemetry Ingestion API & Live Web Dashboard) and Port 80
resource "google_compute_firewall" "allow_telemetry_web" {
  name        = "${var.network_name}-allow-telemetry-web"
  network     = google_compute_network.telemetry_vpc.name
  description = "Allow inbound traffic on port 8000 and 80 for Telemetry Web Dashboard and Ingestion API"
  direction   = "INGRESS"
  priority    = 1000

  allow {
    protocol = "tcp"
    ports    = ["8000", "80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["telemetry-server"]
}

# Allow Internal intra-VPC communication
resource "google_compute_firewall" "allow_internal" {
  name        = "${var.network_name}-allow-internal"
  network     = google_compute_network.telemetry_vpc.name
  description = "Allow internal traffic within the VPC"
  direction   = "INGRESS"
  priority    = 1000

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }
  allow {
    protocol = "icmp"
  }

  source_ranges = [var.subnet_cidr]
}

# Allow ICMP (Ping diagnostics)
resource "google_compute_firewall" "allow_icmp" {
  name      = "${var.network_name}-allow-icmp"
  network   = google_compute_network.telemetry_vpc.name
  direction = "INGRESS"
  priority  = 1000

  allow {
    protocol = "icmp"
  }

  source_ranges = ["0.0.0.0/0"]
}

# ------------------------------------------------------------------------------
# 5. Service Account & IAM Roles
# ------------------------------------------------------------------------------
resource "google_service_account" "telemetry_sa" {
  account_id   = "telemetry-simulator-sa"
  display_name = "Telemetry Simulator VM Service Account"
}

resource "google_project_iam_member" "sa_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.telemetry_sa.email}"
}

resource "google_project_iam_member" "sa_monitoring" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.telemetry_sa.email}"
}

# ------------------------------------------------------------------------------
# 6. Compute Engine Virtual Machine (e2-small in us-central1)
# ------------------------------------------------------------------------------
resource "google_compute_instance" "telemetry_vm" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone

  tags = ["telemetry-server", "http-server", "https-server"]

  boot_disk {
    auto_delete = true
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = var.boot_disk_size_gb
      type  = var.boot_disk_type
      labels = {
        environment = "demo"
        workload    = "telemetry-simulator"
      }
    }
  }

  network_interface {
    network    = google_compute_network.telemetry_vpc.self_link
    subnetwork = google_compute_subnetwork.telemetry_subnet.self_link

    dynamic "access_config" {
      for_each = var.assign_public_ip ? [1] : []
      content {
        network_tier = "STANDARD"
      }
    }
  }

  service_account {
    email  = google_service_account.telemetry_sa.email
    scopes = ["cloud-platform"]
  }

  metadata = {
    enable-oslogin = "TRUE"
  }

  metadata_startup_script = templatefile("${path.module}/scripts/startup.sh.tftpl", {
    git_repo_url        = var.git_repo_url
    git_branch          = var.git_branch
    simulation_interval = var.simulation_interval
  })

  labels = {
    app         = "fleet-telemetry"
    managed-by  = "terraform"
    environment = "demo"
  }

  depends_on = [
    google_compute_router_nat.telemetry_nat,
    google_compute_firewall.allow_telemetry_web,
    google_compute_firewall.allow_ssh,
    google_project_iam_member.sa_logging,
    google_project_iam_member.sa_monitoring
  ]
}
