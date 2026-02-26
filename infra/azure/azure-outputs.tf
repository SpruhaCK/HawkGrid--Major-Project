output "attacker_public_ip" {
  value = azurerm_public_ip.attacker_ip.ip_address
}

output "target_public_ip" {
  value = azurerm_public_ip.target_ip.ip_address
}

output "attacker_private_ip" {
  value = azurerm_network_interface.attacker_nic.private_ip_address
}

output "target_private_ip" {
  value = azurerm_network_interface.target_nic.private_ip_address
}