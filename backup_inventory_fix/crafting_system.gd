class_name CraftingSystem
extends Node

## Clase CraftingManager
class Manager extends Node:
	signal recipe_found(recipe: CraftingRecipe)
	signal crafted(item: InventoryItem, quantity: int)
	
	var recipes: Array[CraftingRecipe] = []
	
	func _ready():
		load_recipes()
	
	func load_recipes():
		var recipes_path = "res://recipes/"
		if not DirAccess.dir_exists_absolute(recipes_path):
			DirAccess.make_dir_recursive_absolute(recipes_path)
			print("⚠️ Carpeta recipes/ vacía")
			return
		
		var dir = DirAccess.open(recipes_path)
		if dir:
			dir.list_dir_begin()
			var file_name = dir.get_next()
			
			while file_name != "":
				if file_name.ends_with(".tres"):
					var recipe = load(recipes_path + file_name)
					if recipe is CraftingRecipe:
						recipes.append(recipe)
				file_name = dir.get_next()
			
			dir.list_dir_end()
		
		print("✓ CraftingManager: %d recetas cargadas" % recipes.size())
	
	func find_recipe(grid_slots: Array[InventorySlot]) -> CraftingRecipe:
		var grid_ids: Array[String] = []
		
		for slot in grid_slots:
			if slot.is_empty():
				grid_ids.append("")
			else:
				grid_ids.append(slot.item.id)
		
		for recipe in recipes:
			if recipe.matches(grid_ids):
				recipe_found.emit(recipe)
				return recipe
		
		return null
	
	func can_craft(recipe: CraftingRecipe, grid_slots: Array[InventorySlot]) -> bool:
		if recipe == null:
			return false
		
		for i in range(grid_slots.size()):
			var required_id = recipe.pattern[i]
			var slot = grid_slots[i]
			
			if required_id == "" and not slot.is_empty():
				if not recipe.shapeless:
					return false
			elif required_id != "" and (slot.is_empty() or slot.item.id != required_id):
				return false
		
		return true
	
	func craft(recipe: CraftingRecipe, grid_slots: Array[InventorySlot], inventory: InventoryManager) -> bool:
		if not can_craft(recipe, grid_slots):
			return false
		
		for i in range(grid_slots.size()):
			if recipe.pattern[i] != "":
				grid_slots[i].remove_item(1)
		
		var result_item = ItemDatabase.get_item(recipe.result_item_id)
		if result_item:
			inventory.add_item(result_item, recipe.result_quantity)
			crafted.emit(result_item, recipe.result_quantity)
			return true
		
		return false

## Clase CraftingTableUI
class TableUI extends Control:
	signal closed
	
	@export var inventory_ui: Control
	
	var crafting_grid: GridContainer
	var result_slot: Panel
	var crafting_manager: Manager
	var crafting_slots: Array[InventorySlot] = []
	var result_item: InventoryItem = null
	var result_quantity: int = 0
	var current_recipe: CraftingRecipe = null
	var held_item: InventoryItem = null
	var held_quantity: int = 0
	var cursor_preview: Control = null
	
	func _ready():
		crafting_manager = Manager.new()
		add_child(crafting_manager)
		
		initialize_crafting_grid()
		setup_cursor_preview()
		
		crafting_manager.recipe_found.connect(_on_recipe_found)
	
	func initialize_crafting_grid():
		for i in range(9):
			var slot = InventorySlot.new()
			crafting_slots.append(slot)
	
	func setup_cursor_preview():
		cursor_preview = Panel.new()
		cursor_preview.custom_minimum_size = Vector2(64, 64)
		cursor_preview.mouse_filter = Control.MOUSE_FILTER_IGNORE
		cursor_preview.z_index = 100
		
		var icon = TextureRect.new()
		icon.name = "Icon"
		icon.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
		cursor_preview.add_child(icon)
		icon.set_anchors_preset(Control.PRESET_FULL_RECT)
		
		var qty = Label.new()
		qty.name = "Quantity"
		qty.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		qty.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
		cursor_preview.add_child(qty)
		qty.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
		
		add_child(cursor_preview)
		cursor_preview.visible = false
	
	func _process(_delta):
		if held_item:
			cursor_preview.global_position = get_global_mouse_position() - cursor_preview.size / 2
			cursor_preview.visible = true
			cursor_preview.get_node("Icon").texture = held_item.icon
			cursor_preview.get_node("Quantity").text = str(held_quantity) if held_quantity > 1 else ""
		else:
			cursor_preview.visible = false
	
	func check_recipe():
		current_recipe = crafting_manager.find_recipe(crafting_slots)
		
		if current_recipe:
			result_item = ItemDatabase.get_item(current_recipe.result_item_id)
			result_quantity = current_recipe.result_quantity
			update_result_slot()
		else:
			result_item = null
			result_quantity = 0
			clear_result_slot()
	
	func update_result_slot():
		if result_item and result_slot:
			result_slot.get_node("Icon").texture = result_item.icon
			result_slot.get_node("Quantity").text = str(result_quantity) if result_quantity > 1 else ""
			result_slot.modulate = Color.WHITE
	
	func clear_result_slot():
		if result_slot:
			result_slot.get_node("Icon").texture = null
			result_slot.get_node("Quantity").text = ""
			result_slot.modulate = Color(1, 1, 1, 0.3)
	
	func _on_recipe_found(recipe: CraftingRecipe):
		print("✓ Receta: %s" % recipe.result_item_id)
	
	func _input(event):
		if event.is_action_pressed("ui_cancel"):
			close_crafting_table()
			get_viewport().set_input_as_handled()
	
	func close_crafting_table():
		for slot in crafting_slots:
			if not slot.is_empty() and inventory_ui and inventory_ui.inventory:
				inventory_ui.inventory.add_item(slot.item, slot.quantity)
				slot.clear()
		
		if held_item and inventory_ui and inventory_ui.inventory:
			inventory_ui.inventory.add_item(held_item, held_quantity)
			held_item = null
			held_quantity = 0
		
		closed.emit()
		queue_free()
