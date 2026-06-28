terraform {
  required_version = ">= 1.4.0"
}

locals {
  full_image = "${var.registry}/${var.image_name}:${var.image_tag}"
}

resource "terraform_data" "deploy_app" {
  triggers_replace = [
    local.full_image,
    var.container_name,
    var.external_port
  ]

  provisioner "local-exec" {
    command = <<EOT
docker network inspect ${var.network_name} >/dev/null 2>&1 || docker network create ${var.network_name}
docker rm -f ${var.container_name} >/dev/null 2>&1 || true
docker pull ${local.full_image}
docker run -d --name ${var.container_name} --restart unless-stopped --network ${var.network_name} -p ${var.external_port}:${var.app_port} ${local.full_image}
EOT
  }
}