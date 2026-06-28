output "container_name" {
  value = docker_container.app.name
}

output "image" {
  value = local.full_image
}

output "app_url" {
  value = "http://localhost:${var.external_port}"
}