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
		push_warning("ItemDatabase ya está cargado")
		return
	
	print("🗄️ ItemDatabase: Cargando items desde: ", items_folder)
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
		print("✓ ItemDatabase: %d items cargados correctamente" % loaded_count)
		database_loaded.emit()
	else:
		push_error("No se pudo abrir carpeta: %s" % items_folder)
		is_loaded = true
		database_loaded.emit()

func get_item(item_id: String) -> InventoryItem:
	"""Obtiene un item por su ID"""
	if not is_loaded:
		push_warning("ItemDatabase aún no está cargado")
	return items.get(item_id, null)

func has_item(item_id: String) -> bool:
	"""Verifica si existe un item con el ID dado"""
	return items.has(item_id)

func get_all_items() -> Array[InventoryItem]:
	"""Retorna todos los items cargados"""
	var result: Array[InventoryItem] = []
	for item in items.values():
		result.append(item)
	return result

func get_item_count() -> int:
	"""Retorna la cantidad total de items cargados"""
	return items.size()

func get_items_by_type(type: InventoryItem.ItemType) -> Array[InventoryItem]:
	"""Retorna todos los items de un tipo específico"""
	var result: Array[InventoryItem] = []
	for item in items.values():
		if item.item_type == type:
			result.append(item)
	return result

func search_items(query: String) -> Array[InventoryItem]:
	"""Busca items por nombre o descripción"""
	var result: Array[InventoryItem] = []
	var query_lower = query.to_lower()
	
	for item in items.values():
		if query_lower in item.name.to_lower() or query_lower in item.description.to_lower():
			result.append(item)
	
	return result

func reload_items() -> void:
	"""Recarga todos los items desde disco"""
	is_loaded = false
	load_all_items()

func print_database_info() -> void:
	"""Imprime información detallada de la base de datos"""
	print("\n" + "=".repeat(50))
	print("📊 ItemDatabase Info")
	print("=".repeat(50))
	print("Total items: ", items.size())
	print("Estado: ", "Cargado" if is_loaded else "No cargado")
	
	for type in InventoryItem.ItemType.values():
		var type_name = InventoryItem.ItemType.keys()[type]
		var count = get_items_by_type(type).size()
		if count > 0:
			print("  %s: %d" % [type_name, count])
	
	print("=".repeat(50) + "\n")
