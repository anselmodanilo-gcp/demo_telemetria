output "instance_name" {
  description = "Name of the Compute Engine VM instance"
  value       = google_compute_instance.telemetry_vm.name
}

output "instance_zone" {
  description = "Compute Engine VM Zone"
  value       = google_compute_instance.telemetry_vm.zone
}

output "instance_internal_ip" {
  description = "Private IP address of the VM"
  value       = google_compute_instance.telemetry_vm.network_interface[0].network_ip
}

output "instance_external_ip" {
  description = "Public IP address of the VM"
  value       = length(google_compute_instance.telemetry_vm.network_interface[0].access_config) > 0 ? google_compute_instance.telemetry_vm.network_interface[0].access_config[0].nat_ip : "No Public IP (Using Cloud NAT)"
}

output "dashboard_url" {
  description = "Web URL to access the live Fleet Telemetry Interactive Dashboard"
  value       = length(google_compute_instance.telemetry_vm.network_interface[0].access_config) > 0 ? "http://${google_compute_instance.telemetry_vm.network_interface[0].access_config[0].nat_ip}:8000" : "http://<VM_INTERNAL_IP>:8000"
}

output "api_telemetry_url" {
  description = "REST Ingestion endpoint for vehicle telemetry payloads"
  value       = length(google_compute_instance.telemetry_vm.network_interface[0].access_config) > 0 ? "http://${google_compute_instance.telemetry_vm.network_interface[0].access_config[0].nat_ip}:8000/api/v1/telemetry" : "http://<VM_INTERNAL_IP>:8000/api/v1/telemetry"
}

output "ssh_command" {
  description = "Google Cloud CLI command to SSH into the VM"
  value       = "gcloud compute ssh ${google_compute_instance.telemetry_vm.name} --zone=${google_compute_instance.telemetry_vm.zone} --project=${var.project_id}"
}

output "startup_logs_command" {
  description = "Command to follow startup and initialization logs on the VM"
  value       = "gcloud compute ssh ${google_compute_instance.telemetry_vm.name} --zone=${google_compute_instance.telemetry_vm.zone} --project=${var.project_id} --command='sudo journalctl -u telemetry_service -f'"
}

output "vpc_network_name" {
  description = "Name of the created VPC Network"
  value       = google_compute_network.telemetry_vpc.name
}

output "subnet_name" {
  description = "Name of the created Subnetwork in us-central1"
  value       = google_compute_subnetwork.telemetry_subnet.name
}

output "cloud_nat_name" {
  description = "Name of the Cloud NAT gateway"
  value       = google_compute_router_nat.telemetry_nat.name
}
