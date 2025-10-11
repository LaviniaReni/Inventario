# 📦 Sistema de Inventario para Godot 4.5

## 🚀 Inicio Rápido

### 1. Activar Plugin
- **Proyecto > Configuración del Proyecto > Plugins**
- Activar **"Inventory System"** ✓

### 2. Configurar ItemDatabase (IMPORTANTE)
- **Proyecto > Configuración del Proyecto > Autoload**
- Path: `res://addons/inventory_system/scripts/item_database.gd`
- Name: `ItemDatabase`
- Click "Agregar"

### 3. Usar en tu juego

```gdscript
extends Node2D

@onready var inventory = $InventoryUI.inventory

func _ready():
	inventory.add_item_by_id("potion_health", 5)
	inventory.item_used.connect(func(item):
		print("Usaste: ", item.name)
	)

func _input(event):
	if event.is_action_pressed("ui_cancel"):
		$InventoryUI.visible = !$InventoryUI.visible
```

## 📚 API Principal

### Inventario
```gdscript
inventory.add_item_by_id("item_id", cantidad)
inventory.remove_item_by_id("item_id", cantidad)
inventory.use_item_by_id("item_id")
if inventory.has_item(item, 3):
	print("Tienes al menos 3")
```

### ItemDatabase
```gdscript
var item = ItemDatabase.get_item("item_id")
var consumables = ItemDatabase.get_items_by_type(InventoryItem.ItemType.CONSUMABLE)
var results = ItemDatabase.search_items("poción")
ItemDatabase.print_database_info()
```

## 🎮 Controles

- **ESC**: Abrir/Cerrar
- **Click Izquierdo**: Usar item
- **Click Derecho**: Soltar 1
- **Arrastrar**: Reorganizar

## 📦 Crear Items

1. Click derecho > **Nuevo Recurso**
2. Buscar **"InventoryItem"**
3. Configurar ID, nombre, icono
4. Guardar en `items/mi_item.tres`

## 🎯 Demo

Ejecuta: `addons/inventory_system/demo/demo.tscn`
