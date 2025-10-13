class_name CraftingTableUI
extends Control

signal closed

@export var inventory_ui: Control

@onready var crafting_grid = $Panel/MarginContainer/VBox/CraftingArea/CraftingGrid
@onready var result_slot = $Panel/MarginContainer/VBox/CraftingArea/ResultArea/ResultSlot

var crafting_manager: CraftingManager
var crafting_slots: Array[InventorySlot] = []
var result_item: InventoryItem = null
var result_quantity: int = 0
var current_recipe: CraftingRecipe = null

var held_item: InventoryItem = null
var held_quantity: int = 0
var cursor_preview: Control = null

func _ready():
	crafting_manager = CraftingManager.new()
	add_child(crafting_manager)
	
	initialize_crafting_grid()
	setup_cursor_preview()
	
	crafting_manager.recipe_found.connect(_on_recipe_found)

func initialize_crafting_grid():
	for i in range(9):
		var slot = InventorySlot.new()
		crafting_slots.append(slot)
		
		var slot_ui = create_slot_ui(i)
		crafting_grid.add_child(slot_ui)

func create_slot_ui(index: int) -> Control:
	var slot_ui = preload("res://addons/inventory_system/scenes/inventory_slot_ui.tscn").instantiate()
	slot_ui.index = index
	slot_ui.custom_minimum_size = Vector2(64, 64)
	return slot_ui

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
	if result_item:
		result_slot.get_node("Icon").texture = result_item.icon
		result_slot.get_node("Quantity").text = str(result_quantity) if result_quantity > 1 else ""
		result_slot.modulate = Color.WHITE

func clear_result_slot():
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
