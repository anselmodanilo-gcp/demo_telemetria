variable "project_id" {
  description = "The Google Cloud Project ID where resources will be provisioned."
  type        = string
  default     = "advance-mantis-506814-g5"
}

variable "region" {
  description = "Google Cloud region for the VPC subnet, Cloud NAT, and Compute Engine VM."
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Google Cloud zone within the region."
  type        = string
  default     = "us-central1-a"
}

variable "network_name" {
  description = "Name of the custom VPC network."
  type        = string
  default     = "telemetry-vpc"
}

variable "subnet_cidr" {
  description = "Primary IP CIDR range for the telemetry subnet."
  type        = string
  default     = "10.10.0.0/24"
}

variable "machine_type" {
  description = "Compute Engine machine type (small e2 instance as requested)."
  type        = string
  default     = "e2-small"
}

variable "instance_name" {
  description = "Name of the Compute Engine Virtual Machine instance."
  type        = string
  default     = "telemetry-simulator-vm"
}

variable "boot_disk_size_gb" {
  description = "Boot disk capacity in GB."
  type        = number
  default     = 20
}

variable "boot_disk_type" {
  description = "Boot disk storage type (pd-balanced, pd-ssd, or pd-standard)."
  type        = string
  default     = "pd-balanced"
}

variable "assign_public_ip" {
  description = "Whether to attach an external public IP to the VM for direct web dashboard access."
  type        = bool
  default     = true
}

variable "git_repo_url" {
  description = "Git repository URL to clone on VM startup."
  type        = string
  default     = "https://github.com/anselmodanilo-gcp/demo_telemetria.git"
}

variable "git_branch" {
  description = "Git branch to checkout on VM startup."
  type        = string
  default     = "main"
}

variable "simulation_interval" {
  description = "Interval in seconds between telemetry frames."
  type        = number
  default     = 4.0
}
