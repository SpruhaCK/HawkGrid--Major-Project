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

resource "azurerm_log_analytics_workspace" "law" {
  name                = "hawkgrid-law"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
}