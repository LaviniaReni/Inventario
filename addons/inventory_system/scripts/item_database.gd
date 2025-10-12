extends Node

signal database_loaded

var items: Dictionary = {}
var is_loaded: bool = false

@export var items_folder: String = "res://addons/inventory_system/demo/demo_items/"
@export var auto_load_on_ready: bool = true

func _ready():
	if auto_load_on_ready:
		call_deferred("load_all_items")

func load_all_items() -> void:
	if is_loaded:
		push_warning("ItemDatabase ya estÃ¡ cargado")
		return
	
	print("ðŸ—„ï¸ ItemDatabase: Cargando items desde: ", items_folder)
	items.clear()
	
	if not DirAccess.dir_exists_absolute(items_folder):
		push_warning("Carpeta de items no existe: %s" % items_folder)
		DirAccess.make_dir_recursive_absolute(items_folder)
		is_loaded = true
		database_loaded.emit()
		return
	
	var loaded_count = 0
	var dir = DirAccess.open(items_folder)
	
	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		
		while file_name != "":
			if not file_name.begins_with(".") and file_name.ends_with(".tres"):
				var full_path = items_folder + file_name
				var item = load(full_path)
				
				if item is InventoryItem:
					if item.id.is_empty():
						push_warning("Item sin ID: %s" % full_path)
					elif items.has(item.id):
						push_warning("ID duplicado: %s en %s" % [item.id, full_path])
					else:
						items[item.id] = item
						loaded_count += 1
				else:
					push_warning("Archivo no es InventoryItem: %s" % full_path)
			
			file_name = dir.get_next()
		
		dir.list_dir_end()
		
		is_loaded = true
		print("âœ“ ItemDatabase: %d items cargados correctamente" % loaded_count)
		database_loaded.emit()
	else:
		push_error("No se pudo abrir carpeta: %s" % items_folder)
		is_loaded = true
		database_loaded.emit()

func get_item(item_id: String) -> InventoryItem:
	if not is_loaded:
		push_warning("ItemDatabase aÃºn no estÃ¡ cargado")
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
		if query_lower in item.name.to_lower() or query_lower in item.description.to_lower():
			result.append(item)
	
	return result

func reload_items() -> void:
	is_loaded = false
	load_all_items()

func print_database_info() -> void:
	print("\n" + "=".repeat(50))
	print("ðŸ“Š ItemDatabase Info")
	print("=".repeat(50))
	print("Total items: ", items.size())
	print("Estado: ", "Cargado" if is_loaded else "No cargado")
	
	for type in InventoryItem.ItemType.values():
		var type_name = InventoryItem.ItemType.keys()[type]
		var count = get_items_by_type(type).size()
		if count > 0:
			print("  %s: %d" % [type_name, count])
	
	print("=".repeat(50) + "\n")
