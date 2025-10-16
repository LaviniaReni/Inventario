@tool
extends EditorScript

## Script de utilidades para testing del sistema de inventario
## Uso: Script > Ejecutar > test_utilities.gd

func _run():
	var separator = ""
	for i in range(60):
		separator += "="
	
	print("\n" + separator)
	print("🧪 UTILIDADES DE TESTING - INVENTORY SYSTEM")
	print(separator + "\n")
	
	show_statistics()

func show_statistics():
	"""Muestra estadísticas del proyecto"""
	print("📊 ESTADÍSTICAS DEL PROYECTO\n")
	
	var separator = ""
	for i in range(60):
		separator += "="
	print(separator)
	
	# Contar items
	var items_count = count_files("res://addons/inventory_system/demo/demo_items/", ".tres")
	print("📦 Items totales: %d" % items_count)
	
	# Contar recetas
	var recipes_count = count_files("res://recipes/", ".tres")
	print("🔨 Recetas totales: %d" % recipes_count)
	
	# Contar escenas demo
	var demos_count = count_files("res://addons/inventory_system/demo/", ".tscn")
	print("🎮 Demos disponibles: %d" % demos_count)
	
	print(separator + "\n")
	
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
