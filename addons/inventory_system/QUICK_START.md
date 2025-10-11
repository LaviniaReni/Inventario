# 🚀 Guía Rápida

## Paso 1: Activar Plugin
Proyecto > Plugins > Activar "Inventory System"

## Paso 2: Configurar Autoload (CRÍTICO)
Proyecto > Autoload > Agregar:
- Path: `addons/inventory_system/scripts/item_database.gd`
- Name: `ItemDatabase`

## Paso 3: Agregar a tu escena
Agrega nodo **InventoryUI**

## Paso 4: Script básico
```gdscript
extends Node2D

@onready var inventory = $InventoryUI.inventory

func _ready():
    inventory.add_item_by_id("potion_health", 5)
    $InventoryUI.visible = false

func _input(event):
    if event.is_action_pressed("ui_cancel"):
        $InventoryUI.visible = !$InventoryUI.visible
```

## Paso 5: Crear tus items
1. Nuevo Recurso > InventoryItem
2. Configurar ID, nombre, icono
3. Guardar en `items/`

¡Listo! 🎉
