variable "project_id" {
  description = "Project ID"
  type        = string
}

locals {
  parts = split("-", var.project_id)
  middle_parts = slice(local.parts, 1, 3)
  formatted_middle = join("-", local.middle_parts)
  environment_mapping = {
    "dev" = "development"
  }
}

output "formatted_project_name" {
  description = "Formatted project name"
  value       = "${local.formatted_middle}-${lookup(local.environment_mapping, local.parts[3], local.parts[3])}"
}
