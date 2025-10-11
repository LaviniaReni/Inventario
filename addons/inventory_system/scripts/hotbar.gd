class_name Hotbar
extends Node

signal slot_selected(index: int, item: InventoryItem)
signal item_used_from_hotbar(item: InventoryItem)

@export var hotbar_size: int = 9
@export var inventory: InventoryManager
@export var selected_slot: int = 0
@export var enable_scroll: bool = true
@export var enable_number_keys: bool = true
@export var auto_use_on_select: bool = false

var hotbar_slots: Array[int] = [] # Índices del inventario

func _ready():
	initialize_hotbar()
	if inventory:
		inventory.inventory_changed.connect(_on_inventory_changed)

func initialize_hotbar():
	hotbar_slots.clear()
	# Los primeros N slots del inventario son el hotbar
	for i in range(hotbar_size):
		hotbar_slots.append(i)

func _input(event):
	if not inventory:
		return
	
	# Teclas numéricas 1-9
	if enable_number_keys:
		for i in range(1, min(hotbar_size + 1, 10)):
			var action_name = "hotbar_slot_%d" % i
			if InputMap.has_action(action_name) and event.is_action_pressed(action_name):
				select_slot(i - 1)
				get_viewport().set_input_as_handled()
				return
	
	# Scroll del mouse
	if enable_scroll and event is InputEventMouseButton:
		if event.pressed:
			if event.button_index == MOUSE_BUTTON_WHEEL_UP:
				select_previous_slot()
				get_viewport().set_input_as_handled()
			elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
				select_next_slot()
				get_viewport().set_input_as_handled()

func select_slot(index: int):
	if index < 0 or index >= hotbar_size:
		return
	
	selected_slot = index
	var item = get_selected_item()
	slot_selected.emit(selected_slot, item)
	
	if auto_use_on_select and item and item.is_usable:
		use_selected_item()

func select_next_slot():
	select_slot((selected_slot + 1) % hotbar_size)

func select_previous_slot():
	select_slot((selected_slot - 1 + hotbar_size) % hotbar_size)

func get_selected_item() -> InventoryItem:
	if not inventory:
		return null
	
	var inv_index = get_inventory_index(selected_slot)
	if inv_index < 0 or inv_index >= inventory.slots.size():
		return null
	
	return inventory.slots[inv_index].item

func get_item_at_slot(slot_index: int) -> InventoryItem:
	if not inventory:
		return null
	
	var inv_index = get_inventory_index(slot_index)
	if inv_index < 0 or inv_index >= inventory.slots.size():
		return null
	
	return inventory.slots[inv_index].item

func get_quantity_at_slot(slot_index: int) -> int:
	if not inventory:
		return 0
	
	var inv_index = get_inventory_index(slot_index)
	if inv_index < 0 or inv_index >= inventory.slots.size():
		return 0
	
	return inventory.slots[inv_index].quantity

func use_selected_item() -> bool:
	var item = get_selected_item()
	if not item or not item.is_usable:
		return false
	
	if inventory.use_item(item):
		item_used_from_hotbar.emit(item)
		return true
	return false

func use_item_at_slot(slot_index: int) -> bool:
	if slot_index < 0 or slot_index >= hotbar_size:
		return false
	
	var item = get_item_at_slot(slot_index)
	if not item or not item.is_usable:
		return false
	
	if inventory.use_item(item):
		item_used_from_hotbar.emit(item)
		return true
	return false

func get_inventory_index(hotbar_index: int) -> int:
	if hotbar_index < 0 or hotbar_index >= hotbar_slots.size():
		return -1
	return hotbar_slots[hotbar_index]

func _on_inventory_changed():
	# El hotbar se actualiza automáticamente al cambiar el inventario
	pass

# Configurar acciones de input si no existen
static func setup_input_actions():
	for i in range(1, 10):
		var action_name = "hotbar_slot_%d" % i
		if not InputMap.has_action(action_name):
			InputMap.add_action(action_name)
			var event = InputEventKey.new()
			event.keycode = KEY_0 + i
			InputMap.action_add_event(action_name, event)
