class_name CraftingTableUI
extends Control

signal closed

@export var inventory_ui: Control

var crafting_grid: GridContainer
var result_slot: Panel
var crafting_manager: CraftingManager
var crafting_slots: Array[InventorySlot] = []
var result_item: InventoryItem = null
var result_quantity: int = 0
var current_recipe: CraftingRecipe = null

# Variables para arrastrar items
var held_item: InventoryItem = null
var held_quantity: int = 0
var cursor_preview: Control = null

func _ready():
	# Inicializar CraftingManager
	crafting_manager = CraftingManager.new()
	add_child(crafting_manager)
	
	# Obtener referencias
	crafting_grid = $Panel/MarginContainer/VBox/CraftingArea/CraftingGrid
	result_slot = $Panel/MarginContainer/VBox/CraftingArea/ResultArea/ResultSlot
	
	# Inicializar slots de crafteo
	initialize_crafting_grid()
	
	# Setup cursor preview
	setup_cursor_preview()
	
	# Conectar señales
	crafting_manager.recipe_found.connect(_on_recipe_found)

func initialize_crafting_grid():
	# Crear 9 slots de crafteo (3x3)
	for i in range(9):
		var slot = InventorySlot.new()
		crafting_slots.append(slot)
		
		var slot_ui = Panel.new()
		slot_ui.custom_minimum_size = Vector2(64, 64)
		slot_ui.set_meta("slot_index", i)
		
		var icon = TextureRect.new()
		icon.name = "Icon"
		icon.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		slot_ui.add_child(icon)
		icon.set_anchors_preset(Control.PRESET_FULL_RECT)
		
		var quantity = Label.new()
		quantity.name = "Quantity"
		quantity.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		quantity.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
		slot_ui.add_child(quantity)
		quantity.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
		
		slot_ui.gui_input.connect(_on_crafting_slot_input.bind(i))
		crafting_grid.add_child(slot_ui)

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

func _on_crafting_slot_input(event: InputEvent, slot_index: int):
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT:
			handle_slot_click(slot_index)
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			handle_slot_right_click(slot_index)

func handle_slot_click(slot_index: int):
	var slot = crafting_slots[slot_index]
	
	if held_item == null:
		if not slot.is_empty():
			held_item = slot.item
			held_quantity = slot.quantity
			slot.clear()
			update_crafting_slot(slot_index)
			check_recipe()
	else:
		if slot.is_empty():
			slot.add_item(held_item, held_quantity)
			held_item = null
			held_quantity = 0
		elif slot.item.id == held_item.id and held_item.is_stackable:
			var remaining = slot.add_item(held_item, held_quantity)
			if remaining == 0:
				held_item = null
				held_quantity = 0
			else:
				held_quantity = remaining
		else:
			var temp_item = slot.item
			var temp_qty = slot.quantity
			slot.clear()
			slot.add_item(held_item, held_quantity)
			held_item = temp_item
			held_quantity = temp_qty
		
		update_crafting_slot(slot_index)
		check_recipe()

func handle_slot_right_click(slot_index: int):
	var slot = crafting_slots[slot_index]
	
	if held_item == null and not slot.is_empty():
		var half = ceili(slot.quantity / 2.0)
		held_item = slot.item
		held_quantity = half
		slot.remove_item(half)
		update_crafting_slot(slot_index)
		check_recipe()

func update_crafting_slot(slot_index: int):
	var slot = crafting_slots[slot_index]
	var slot_ui = crafting_grid.get_child(slot_index)
	
	if slot.is_empty():
		slot_ui.get_node("Icon").texture = null
		slot_ui.get_node("Quantity").text = ""
		slot_ui.modulate = Color(1, 1, 1, 0.3)
	else:
		slot_ui.get_node("Icon").texture = slot.item.icon
		slot_ui.get_node("Quantity").text = str(slot.quantity) if slot.quantity > 1 else ""
		slot_ui.modulate = Color.WHITE

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
	print("✓ Receta encontrada: %s" % recipe.result_item_id)

func _input(event):
	if event.is_action_pressed("ui_cancel"):
		close_crafting_table()
		get_viewport().set_input_as_handled()

func close_crafting_table():
	# Devolver items de la grilla al inventario
	for slot in crafting_slots:
		if not slot.is_empty() and inventory_ui and inventory_ui.inventory:
			inventory_ui.inventory.add_item(slot.item, slot.quantity)
			slot.clear()
	
	# Devolver item sostenido
	if held_item and inventory_ui and inventory_ui.inventory:
		inventory_ui.inventory.add_item(held_item, held_quantity)
		held_item = null
		held_quantity = 0
	
	closed.emit()
	queue_free()
