terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.2"
    }
  }
}

provider "docker" {
  host = var.docker_host
}

locals {
  full_image = "${var.registry}/${var.image_name}:${var.image_tag}"
}

resource "docker_image" "app" {
  name         = local.full_image
  keep_locally = true
}

resource "docker_container" "app" {
  name    = var.container_name
  image   = docker_image.app.image_id
  restart = "unless-stopped"

  networks_advanced {
    name = var.network_name
  }

  ports {
    internal = var.app_port
    external = var.external_port
  }
}