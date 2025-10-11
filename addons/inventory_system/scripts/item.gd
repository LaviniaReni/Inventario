class_name InventoryItem
extends Resource

enum ItemType { CONSUMABLE, EQUIPMENT, QUEST, MATERIAL, MISC }

@export_group("Info Básica")
@export var id: String = ""
@export var name: String = ""
@export_multiline var description: String = ""
@export var icon: Texture2D
@export var item_type: ItemType = ItemType.MISC

@export_group("Stack")
@export var is_stackable: bool = true
@export var max_stack: int = 99

@export_group("Uso")
@export var is_usable: bool = false
@export var is_consumable: bool = false

@export_group("Custom")
@export var custom_data: Dictionary = {}
