# Storage Account for Logs
resource "azurerm_storage_account" "logs" {
  name                     = "hawkgridlogs${random_id.id.hex}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "random_id" "id" {
  byte_length = 4
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "law" {
  name                = "hawkgrid-law"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
}

# Network Watcher (Required to enable flow logs in Azure)
resource "azurerm_network_watcher" "watcher" {
  name                = "hawkgrid-nww"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

# NSG Flow Logs (The Azure equivalent of AWS VPC Flow Logs)
resource "azurerm_network_watcher_flow_log" "nsg_flow_log" {
  network_watcher_name = azurerm_network_watcher.watcher.name
  resource_group_name  = azurerm_resource_group.rg.name
  name                 = "hawkgrid-nsg-flow-log"

  network_security_group_id = azurerm_network_security_group.nsg.id
  storage_account_id        = azurerm_storage_account.logs.id
  enabled                   = true

  retention_policy {
    enabled = true
    days    = 7
  }

  traffic_analytics {
    enabled               = true
    workspace_id          = azurerm_log_analytics_workspace.law.workspace_id
    workspace_region      = azurerm_log_analytics_workspace.law.location
    workspace_resource_id = azurerm_log_analytics_workspace.law.id
    interval_in_minutes   = 10 
  }
}