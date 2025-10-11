@tool
extends EditorPlugin

func _enter_tree():
	add_custom_type("InventoryManager", "Node", preload("res://addons/inventory_system/scripts/inventory.gd"), preload("res://icon.svg"))
	add_custom_type("InventoryUI", "Control", preload("res://addons/inventory_system/scripts/inventory_ui.gd"), preload("res://icon.svg"))
	add_custom_type("Hotbar", "Node", preload("res://addons/inventory_system/scripts/hotbar.gd"), preload("res://icon.svg"))
	add_custom_type("HotbarUI", "Control", preload("res://addons/inventory_system/scripts/hotbar_ui.gd"), preload("res://icon.svg"))
	print("✓ Inventory System activado (con Hotbar)")

func _exit_tree():
	remove_custom_type("InventoryManager")
	remove_custom_type("InventoryUI")
	remove_custom_type("Hotbar")
	remove_custom_type("HotbarUI")
