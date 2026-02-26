variable "admin_username" {
  type        = string
  description = "The username for the VMs"
  default     = "hawkadmin"
}

variable "admin_password" {
  type        = string
  description = "The password for the VMs"
  default     = "ComplexPassword123!" # Must meet Azure complexity requirements
}

variable "prefix" {
  type        = string
  description = "A prefix used for all resources in this project"
  default     = "HawkGrid"
}

variable "resource_group_location" {
  type        = string
  description = "The Azure region where resources will be created"
  default     = "centralindia"
}