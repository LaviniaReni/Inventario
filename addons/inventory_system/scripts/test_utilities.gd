@tool
extends EditorScript

## Script de utilidades para testing del sistema de inventario
## Uso: Script > Ejecutar > test_utilities.gd

func _run():
	print("\n" + "=" * 60)
	print("🧪 UTILIDADES DE TESTING - INVENTORY SYSTEM")
	print("=" * 60 + "\n")
	
	var option = show_menu()
	
	match option:
		1:
			validate_items()
		2:
			validate_recipes()
		3:
			create_example_items()
		4:
			create_example_recipes()
		5:
			clean_project()
		6:
			show_statistics()
		_:
			print("❌ Opción inválida")

func show_menu() -> int:
	print("Selecciona una opción:")
	print("1. Validar items existentes")
	print("2. Validar recetas")
	print("3. Crear items de ejemplo")
	print("4. Crear recetas de ejemplo")
	print("5. Limpiar proyecto")
	print("6. Mostrar estadísticas")
	print()
	
	# Por defecto ejecutar opción 6 (estadísticas)
	return 6

func validate_items():
	"""Valida todos los items del proyecto"""
	print("🔍 Validando items...\n")
	
	var items_path = "res://addons/inventory_system/demo/demo_items/"
	var dir = DirAccess.open(items_path)
	
	if not dir:
		print("❌ No se pudo abrir carpeta de items")
		return
	
	var valid_count = 0
	var error_count = 0
	var warnings: Array = []
	
	dir.list_dir_begin()
	var file_name = dir.get_next()
	
	while file_name != "":
		if file_name.ends_with(".tres"):
			var item = load(items_path + file_name)
			
			if item is InventoryItem:
				var errors = validate_item(item, file_name)
				if errors.is_empty():
					valid_count += 1
					print("✓ %s" % file_name)
				else:
					error_count += 1
					print("❌ %s:" % file_name)
					for error in errors:
						print("   - %s" % error)
						warnings.append("[%s] %s" % [file_name, error])
			else:
				error_count += 1
				print("❌ %s: No es un InventoryItem" % file_name)
		
		file_name = dir.get_next()
	
	dir.list_dir_end()
	
	print("\n" + "=" * 60)
	print("📊 RESUMEN DE VALIDACIÓN")
	print("=" * 60)
	print("✓ Items válidos: %d" % valid_count)
	print("❌ Items con errores: %d" % error_count)
	
	if warnings.size() > 0:
		print("\n⚠️ ADVERTENCIAS:")
		for warning in warnings:
			print("  %s" % warning)
	
	print()

func validate_item(item: InventoryItem, filename: String) -> Array:
	"""Valida un item individual y retorna array de errores"""
	var errors: Array = []
	
	if item.id.is_empty():
		errors.append("ID vacío")
	
	if item.name.is_empty():
		errors.append("Nombre vacío")
	
	if item.icon == null:
		errors.append("Sin icono")
	
	if item.is_stackable and item.max_stack <= 0:
		errors.append("max_stack debe ser > 0 para items stackeables")
	
	if item.is_consumable and not item.is_usable:
		errors.append("Item consumible debe ser usable")
	
	return errors

func validate_recipes():
	"""Valida todas las recetas"""
	print("🔍 Validando recetas...\n")
	
	var recipes_path = "res://recipes/"
	
	if not DirAccess.dir_exists_absolute(recipes_path):
		print("⚠️ Carpeta recipes/ no existe")
		return
	
	var dir = DirAccess.open(recipes_path)
	if not dir:
		print("❌ No se pudo abrir carpeta de recetas")
		return
	
	var valid_count = 0
	var error_count = 0
	
	dir.list_dir_begin()
	var file_name = dir.get_next()
	
	while file_name != "":
		if file_name.ends_with(".tres"):
			var recipe = load(recipes_path + file_name)
			
			if recipe is CraftingRecipe:
				var errors = validate_recipe(recipe, file_name)
				if errors.is_empty():
					valid_count += 1
					print("✓ %s" % file_name)
				else:
					error_count += 1
					print("❌ %s:" % file_name)
					for error in errors:
						print("   - %s" % error)
			else:
				error_count += 1
				print("❌ %s: No es una CraftingRecipe" % file_name)
		
		file_name = dir.get_next()
	
	dir.list_dir_end()
	
	print("\n✓ Recetas válidas: %d" % valid_count)
	print("❌ Recetas con errores: %d\n" % error_count)

func validate_recipe(recipe: CraftingRecipe, filename: String) -> Array:
	"""Valida una receta individual"""
	var errors: Array = []
	
	if recipe.id.is_empty():
		errors.append("ID vacío")
	
	if recipe.result_item_id.is_empty():
		errors.append("result_item_id vacío")
	
	if recipe.result_quantity <= 0:
		errors.append("result_quantity debe ser > 0")
	
	if recipe.pattern.size() != 9:
		errors.append("pattern debe tener exactamente 9 elementos")
	
	# Verificar que al menos un ingrediente existe
	var has_ingredient = false
	for item_id in recipe.pattern:
		if item_id != "":
			has_ingredient = true
			break
	
	if not has_ingredient:
		errors.append("Receta sin ingredientes")
	
	return errors

func create_example_items():
	"""Crea items de ejemplo adicionales"""
	print("📦 Creando items de ejemplo...\n")
	
	var items_data = [
		{
			"id": "diamond",
			"name": "Diamante",
			"description": "Mineral precioso",
			"type": InventoryItem.ItemType.MATERIAL,
			"stack": 64
		},
		{
			"id": "iron_ingot",
			"name": "Lingote de Hierro",
			"description": "Hierro refinado",
			"type": InventoryItem.ItemType.MATERIAL,
			"stack": 64
		},
		{
			"id": "apple",
			"name": "Manzana",
			"description": "Recupera 2 HP",
			"type": InventoryItem.ItemType.CONSUMABLE,
			"stack": 16,
			"usable": true,
			"consumable": true,
			"custom": {"heal_amount": 2}
		}
	]
	
	for data in items_data:
		var item = InventoryItem.new()
		item.id = data.id
		item.name = data.name
		item.description = data.description
		item.item_type = data.type
		item.max_stack = data.get("stack", 99)
		item.is_usable = data.get("usable", false)
		item.is_consumable = data.get("consumable", false)
		item.custom_data = data.get("custom", {})
		item.icon = load("res://icon.svg")  # Placeholder
		
		var path = "res://addons/inventory_system/demo/demo_items/%s.tres" % data.id
		ResourceSaver.save(item, path)
		print("✓ Creado: %s" % data.id)
	
	print("\n✅ Items de ejemplo creados\n")

func create_example_recipes():
	"""Crea recetas de ejemplo"""
	print("🔨 Creando recetas de ejemplo...\n")
	
	ensure_recipes_folder()
	
	var recipes_data = [
		{
			"id": "sticks",
			"result": "stick",
			"quantity": 4,
			"pattern": ["wood", "", "", "wood", "", "", "", "", ""]
		},
		{
			"id": "torches",
			"result": "torch",
			"quantity": 4,
			"pattern": ["coal", "", "", "stick", "", "", "", "", ""]
		},
		{
			"id": "wooden_planks",
			"result": "wood",
			"quantity": 4,
			"pattern": ["wood", "", "", "", "", "", "", "", ""],
			"shapeless": true
		}
	]
	
	for data in recipes_data:
		var recipe = CraftingRecipe.new()
		recipe.id = data.id
		recipe.result_item_id = data.result
		recipe.result_quantity = data.quantity
		recipe.shapeless = data.get("shapeless", false)
		recipe.pattern = data.pattern
		
		var path = "res://recipes/%s.tres" % data.id
		ResourceSaver.save(recipe, path)
		print("✓ Creada: %s" % data.id)
	
	print("\n✅ Recetas de ejemplo creadas\n")

func ensure_recipes_folder():
	"""Asegura que existe la carpeta de recetas"""
	var dir = DirAccess.open("res://")
	if not dir.dir_exists("recipes"):
		dir.make_dir("recipes")
		print("✓ Carpeta recipes/ creada")

func clean_project():
	"""Limpia archivos temporales y guardados"""
	print("🧹 Limpiando proyecto...\n")
	
	# Eliminar archivos de guardado
	var save_path = "user://inventory.save"
	if FileAccess.file_exists(save_path):
		DirAccess.remove_absolute(save_path)
		print("✓ Eliminado: inventory.save")
	
	print("\n✅ Proyecto limpiado\n")

func show_statistics():
	"""Muestra estadísticas del proyecto"""
	print("📊 ESTADÍSTICAS DEL PROYECTO\n")
	print("=" * 60)
	
	# Contar items
	var items_count = count_files("res://addons/inventory_system/demo/demo_items/", ".tres")
	print("📦 Items totales: %d" % items_count)
	
	# Contar recetas
	var recipes_count = count_files("res://recipes/", ".tres")
	print("🔨 Recetas totales: %d" % recipes_count)
	
	# Contar escenas demo
	var demos_count = count_files("res://addons/inventory_system/demo/", ".tscn")
	print("🎮 Demos disponibles: %d" % demos_count)
	
	# Tamaño del proyecto
	var total_size = calculate_addon_size()
	print("💾 Tamaño del addon: %.2f MB" % (total_size / 1024.0 / 1024.0))
	
	print("=" * 60 + "\n")
	
	# Listar demos
	print("🎮 DEMOS DISPONIBLES:")
	list_demos()
	
	print("\n✅ Análisis completado\n")

func count_files(path: String, extension: String) -> int:
	"""Cuenta archivos con una extensión específica"""
	if not DirAccess.dir_exists_absolute(path):
		return 0
	
	var count = 0
	var dir = DirAccess.open(path)
	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		while file_name != "":
			if file_name.ends_with(extension):
				count += 1
			file_name = dir.get_next()
		dir.list_dir_end()
	
	return count

func calculate_addon_size() -> int:
	"""Calcula el tamaño total del addon"""
	return calculate_folder_size("res://addons/inventory_system/")

func calculate_folder_size(path: String) -> int:
	"""Calcula el tamaño de una carpeta recursivamente"""
	var size = 0
	var dir = DirAccess.open(path)
	
	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		
		while file_name != "":
			var full_path = path + file_name
			
			if dir.current_is_dir():
				if file_name != "." and file_name != "..":
					size += calculate_folder_size(full_path + "/")
			else:
				var file = FileAccess.open(full_path, FileAccess.READ)
				if file:
					size += file.get_length()
					file.close()
			
			file_name = dir.get_next()
		
		dir.list_dir_end()
	
	return size

func list_demos():
	"""Lista todas las demos disponibles"""
	var demos = [
		{
			"path": "res://addons/inventory_system/demo/demo.tscn",
			"name": "Demo Básico",
			"desc": "Inventario simple con controles básicos"
		},
		{
			"path": "res://addons/inventory_system/demo/demo_hotbar.tscn",
			"name": "Demo con Hotbar",
			"desc": "Inventario + Hotbar con selección de slots"
		},
		{
			"path": "res://demos/minecraft_demo.tscn",
			"name": "Demo Minecraft",
			"desc": "Sistema completo con crafting estilo Minecraft"
		}
	]
	
	for demo in demos:
		if FileAccess.file_exists(demo.path):
			print("  ✓ %s" % demo.name)
			print("    %s" % demo.desc)
			print("    Ruta: %s\n" % demo.path)
		else:
			print("  ❌ %s (archivo no encontrado)" % demo.name)
			print("    Ruta esperada: %s\n" % demo.path)
