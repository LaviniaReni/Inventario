class_name CraftingManager
extends Node

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
	
	# Consumir ingredientes
	for i in range(grid_slots.size()):
		if recipe.pattern[i] != "":
			grid_slots[i].remove_item(1)
	
	# Agregar resultado
	var result_item = ItemDatabase.get_item(recipe.result_item_id)
	if result_item:
		inventory.add_item(result_item, recipe.result_quantity)
		crafted.emit(result_item, recipe.result_quantity)
		return true
	
	return false
