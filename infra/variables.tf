variable "docker_host" {
  description = "Docker host used by Terraform"
  type        = string
  default     = "unix:///var/run/docker.sock"
}

variable "registry" {
  description = "Docker registry"
  type        = string
}

variable "image_name" {
  description = "Docker image name"
  type        = string
  default     = "devops-task-api"
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
}

variable "container_name" {
  description = "Staging container name"
  type        = string
  default     = "devops-task-api-staging"
}

variable "network_name" {
  description = "Docker network name"
  type        = string
  default     = "cicd-network"
}

variable "app_port" {
  description = "Internal app port"
  type        = number
  default     = 8000
}

variable "external_port" {
  description = "External app port"
  type        = number
  default     = 8002
}