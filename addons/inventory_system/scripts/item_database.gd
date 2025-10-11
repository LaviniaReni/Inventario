extends Node

signal database_loaded

var items: Dictionary = {}

@export var items_folder: String = "res://addons/inventory_system/demo/demo_items/"
@export var auto_load_on_ready: bool = true

func _ready():
	if auto_load_on_ready:
		await get_tree().process_frame
		load_all_items()

func load_all_items() -> void:
	print("🗄️ ItemDatabase: Cargando items desde: ", items_folder)
	items.clear()
	if not DirAccess.dir_exists_absolute(items_folder):
		DirAccess.make_dir_recursive_absolute(items_folder)
		return
	var loaded_count = 0
	var dir = DirAccess.open(items_folder)
	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		while file_name != "":
			if not file_name.begins_with(".") and file_name.ends_with(".tres"):
				var item = load(items_folder + file_name)
				if item is InventoryItem and not item.id.is_empty():
					items[item.id] = item
					loaded_count += 1
			file_name = dir.get_next()
		dir.list_dir_end()
		print("✓ ItemDatabase: %d items cargados" % loaded_count)
		database_loaded.emit()

func get_item(item_id: String) -> InventoryItem:
	return items.get(item_id, null)

func has_item(item_id: String) -> bool:
	return items.has(item_id)

func get_all_items() -> Array[InventoryItem]:
	var result: Array[InventoryItem] = []
	for item in items.values():
		result.append(item)
	return result

func get_item_count() -> int:
	return items.size()

func get_items_by_type(type: InventoryItem.ItemType) -> Array[InventoryItem]:
	var result: Array[InventoryItem] = []
	for item in items.values():
		if item.item_type == type:
			result.append(item)
	return result

func search_items(query: String) -> Array[InventoryItem]:
	var result: Array[InventoryItem] = []
	var query_lower = query.to_lower()
	for item in items.values():
		if query_lower in item.name.to_lower():
			result.append(item)
	return result

func print_database_info() -> void:
	print("\n" + "=".repeat(50))
	print("📊 ItemDatabase Info")
	print("=".repeat(50))
	print("Total items: ", items.size())
	for type in InventoryItem.ItemType.values():
		var type_name = InventoryItem.ItemType.keys()[type]
		var count = get_items_by_type(type).size()
		print("  %s: %d" % [type_name, count])
	print("=".repeat(50) + "\n")
