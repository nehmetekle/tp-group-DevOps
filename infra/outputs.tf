output "container_name" {
  value = var.container_name
}

output "image" {
  value = local.full_image
}

output "app_url" {
  value = "http://localhost:${var.external_port}"
}

output "health_url" {
  value = "http://localhost:${var.external_port}/health"
}

output "metrics_url" {
  value = "http://localhost:${var.external_port}/metrics"
}