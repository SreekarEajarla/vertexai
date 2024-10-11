variable "project_id" {
  description = "Project ID"
  type        = string
  default     = "NLD-DATA-PLTF-ACQUIRING-DEV"
}

locals {
  trimmed_project_id = substr(var.project_id, 4, length(var.project_id) - 4)
  parts = split("-", local.trimmed_project_id)
  middle_parts = slice(local.parts, 0, length(local.parts) - 1)
  formatted_middle = join("-", local.middle_parts)

  environment_mapping = {
    "dev" = "development"
  }
}

output "formatted_project_name" {
  description = "Formatted project name"
  value       = "${local.formatted_middle}-${lookup(local.environment_mapping, local.parts[length(local.parts) - 1], local.parts[length(local.parts) - 1])}"
}
