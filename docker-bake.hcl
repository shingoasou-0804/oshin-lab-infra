variable "DOCKER_ORG" {
  default = "oshin-lab-infra"
}

group "default" {
  targets = ["app"]
}

target "app" {
  context = "."
  dockerfile = "Dockerfile"
  tags = ["${DOCKER_ORG}/app:latest"]
  platforms = ["linux/amd64"]
  cache-from = ["type=local,src=/tmp/.buildx-cache/oshin-lab-infra"]
  cache-to = ["type=local,dest=/tmp/.buildx-cache/oshin-lab-infra,mode=max"]
  output = ["type=docker"]
} 
