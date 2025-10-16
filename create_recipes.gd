@tool
extends EditorScript

func _run():
	var separator = ""
	for i in range(50):
		separator += "="
	
	print("\n" + separator)
	print("Creando recetas...")
	print(separator + "\n")
	
	create_recipes_folder()
	create_example_recipes()
	
	print("\n✓ Recetas creadas exitosamente!")
	print("Ubicación: res://recipes/\n")

func create_recipes_folder():
	var dir = DirAccess.open("res://")
	if not dir.dir_exists("recipes"):
		dir.make_dir("recipes")
		print("✓ Carpeta recipes/ creada")

func create_example_recipes():
	var recipes = [
		{
			"id": "sticks",
			"result": "stick",
			"quantity": 4,
			"pattern": ["wood", "", "", "wood", "", "", "", "", ""]
		},
		{
			"id": "wooden_sword",
			"result": "sword_iron",
			"quantity": 1,
			"pattern": ["wood", "", "", "wood", "", "", "stick", "", ""]
		},
		{
			"id": "torches",
			"result": "torch",
			"quantity": 4,
			"pattern": ["coal", "", "", "stick", "", "", "", "", ""]
		},
	]
	
	for recipe_data in recipes:
		var recipe = CraftingRecipe.new()
		recipe.id = recipe_data.id
		recipe.result_item_id = recipe_data.result
		recipe.result_quantity = recipe_data.quantity
		recipe.shapeless = false
		recipe.pattern = recipe_data.pattern
		
		var path = "res://recipes/%s.tres" % recipe_data.id
		ResourceSaver.save(recipe, path)
		print("✓ Creada: %s" % recipe_data.id)
