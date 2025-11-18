# Australian Privacy Act ADM Compliance Framework - Azure Infrastructure
# Terraform Configuration for Azure Australia East/Southeast

terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }

  # Backend configuration for state storage
  backend "azurerm" {
    resource_group_name  = "adm-compliance-tfstate"
    storage_account_name = "admcompliancetfstate"
    container_name       = "tfstate"
    key                  = "terraform.tfstate"
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = false
      recover_soft_deleted_key_vaults = true
    }
  }
}

# Variables
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "location" {
  description = "Azure region (Australia East for data sovereignty)"
  type        = string
  default     = "australiaeast"
}

variable "location_secondary" {
  description = "Secondary Azure region (Australia Southeast for DR)"
  type        = string
  default     = "australiasoutheast"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "adm-compliance"
}

variable "db_admin_password" {
  description = "PostgreSQL admin password"
  type        = string
  sensitive   = true
}

# Local variables
locals {
  resource_prefix = "${var.app_name}-${var.environment}"
  tags = {
    Environment = var.environment
    Application = "ADM Compliance Framework"
    ManagedBy   = "Terraform"
    Compliance  = "Australian Privacy Act"
    DataSovereignty = "Australia"
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = "${local.resource_prefix}-rg"
  location = var.location
  tags     = local.tags
}

# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "${local.resource_prefix}-vnet"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = ["10.0.0.0/16"]
  tags                = local.tags
}

# Subnets
resource "azurerm_subnet" "aks" {
  name                 = "${local.resource_prefix}-aks-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_subnet" "database" {
  name                 = "${local.resource_prefix}-db-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]

  delegation {
    name = "database-delegation"
    service_delegation {
      name = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = ["Microsoft.Network/virtualNetworks/subnets/join/action"]
    }
  }
}

# PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "${local.resource_prefix}-psql"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "15"
  delegated_subnet_id    = azurerm_subnet.database.id
  administrator_login    = "psqladmin"
  administrator_password = var.db_admin_password

  storage_mb = 32768
  sku_name   = "GP_Standard_D2s_v3"

  backup_retention_days        = 35
  geo_redundant_backup_enabled = true

  high_availability {
    mode = "ZoneRedundant"
  }

  tags = local.tags
}

# PostgreSQL Database
resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "adm_compliance"
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_AU.utf8"
  charset   = "utf8"
}

# Key Vault
resource "azurerm_key_vault" "main" {
  name                        = "${local.resource_prefix}-kv"
  location                    = azurerm_resource_group.main.location
  resource_group_name         = azurerm_resource_group.main.name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 90
  purge_protection_enabled    = true
  sku_name                    = "premium"

  network_acls {
    default_action = "Deny"
    bypass         = "AzureServices"
  }

  tags = local.tags
}

data "azurerm_client_config" "current" {}

# Storage Account
resource "azurerm_storage_account" "main" {
  name                     = "${replace(local.resource_prefix, "-", "")}sa"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "GRS"  # Geo-redundant
  account_kind             = "StorageV2"

  min_tls_version                 = "TLS1_2"
  enable_https_traffic_only       = true
  allow_nested_items_to_be_public = false

  blob_properties {
    versioning_enabled = true

    delete_retention_policy {
      days = 30
    }
  }

  tags = local.tags
}

# Storage Containers
resource "azurerm_storage_container" "uploads" {
  name                  = "uploads"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "reports" {
  name                  = "reports"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "evidence" {
  name                  = "evidence"
  storage_account_name  = azurerm_storage_account.main.name
  container_access_type = "private"
}

# Log Analytics Workspace
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${local.resource_prefix}-logs"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 90

  tags = local.tags
}

# Azure Kubernetes Service (AKS)
resource "azurerm_kubernetes_cluster" "main" {
  name                = "${local.resource_prefix}-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "${local.resource_prefix}-k8s"
  kubernetes_version  = "1.27"

  default_node_pool {
    name       = "default"
    node_count = 3
    vm_size    = "Standard_D2s_v3"
    vnet_subnet_id = azurerm_subnet.aks.id

    enable_auto_scaling = true
    min_count          = 2
    max_count          = 5

    zones = ["1", "2", "3"]  # Availability zones
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin    = "azure"
    load_balancer_sku = "standard"
    network_policy    = "azure"
  }

  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }

  tags = local.tags
}

# Application Gateway (WAF)
resource "azurerm_public_ip" "appgw" {
  name                = "${local.resource_prefix}-appgw-pip"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
  zones               = ["1", "2", "3"]

  tags = local.tags
}

resource "azurerm_subnet" "appgw" {
  name                 = "${local.resource_prefix}-appgw-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.3.0/24"]
}

resource "azurerm_application_gateway" "main" {
  name                = "${local.resource_prefix}-appgw"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location

  sku {
    name     = "WAF_v2"
    tier     = "WAF_v2"
    capacity = 2
  }

  waf_configuration {
    enabled          = true
    firewall_mode    = "Prevention"
    rule_set_type    = "OWASP"
    rule_set_version = "3.2"
  }

  gateway_ip_configuration {
    name      = "appgw-ip-config"
    subnet_id = azurerm_subnet.appgw.id
  }

  frontend_port {
    name = "https-port"
    port = 443
  }

  frontend_port {
    name = "http-port"
    port = 80
  }

  frontend_ip_configuration {
    name                 = "appgw-frontend-ip"
    public_ip_address_id = azurerm_public_ip.appgw.id
  }

  backend_address_pool {
    name = "aks-backend-pool"
  }

  backend_http_settings {
    name                  = "backend-http-settings"
    cookie_based_affinity = "Disabled"
    port                  = 80
    protocol              = "Http"
    request_timeout       = 60
  }

  http_listener {
    name                           = "http-listener"
    frontend_ip_configuration_name = "appgw-frontend-ip"
    frontend_port_name             = "http-port"
    protocol                       = "Http"
  }

  request_routing_rule {
    name                       = "http-routing-rule"
    rule_type                  = "Basic"
    http_listener_name         = "http-listener"
    backend_address_pool_name  = "aks-backend-pool"
    backend_http_settings_name = "backend-http-settings"
    priority                   = 100
  }

  tags = local.tags
}

# Outputs
output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.main.name
}

output "postgresql_server_fqdn" {
  value = azurerm_postgresql_flexible_server.main.fqdn
}

output "key_vault_uri" {
  value = azurerm_key_vault.main.vault_uri
}

output "storage_account_name" {
  value = azurerm_storage_account.main.name
}

output "application_gateway_ip" {
  value = azurerm_public_ip.appgw.ip_address
}
