class_name CraftingRecipe
extends Resource

@export var id: String = ""
@export var result_item_id: String = ""
@export var result_quantity: int = 1
@export var shapeless: bool = false
@export var pattern: Array[String] = ["", "", "", "", "", "", "", "", ""]

func matches(grid: Array[String]) -> bool:
	if shapeless:
		return matches_shapeless(grid)
	else:
		return matches_shaped(grid)

func matches_shapeless(grid: Array[String]) -> bool:
	var pattern_items = {}
	var grid_items = {}
	
	for item_id in pattern:
		if item_id != "":
			pattern_items[item_id] = pattern_items.get(item_id, 0) + 1
	
	for item_id in grid:
		if item_id != "":
			grid_items[item_id] = grid_items.get(item_id, 0) + 1
	
	return pattern_items == grid_items

func matches_shaped(grid: Array[String]) -> bool:
	return grid == pattern
