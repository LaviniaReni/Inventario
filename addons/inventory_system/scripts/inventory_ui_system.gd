@tool
class_name InventoryUI
extends Control

## Clase interna: InventorySlotUI
class InventorySlotUI extends Panel:
	signal slot_clicked(slot_index: int, item: InventoryItem)
	signal slot_right_clicked(slot_index: int, item: InventoryItem)
	
	var index: int = -1
	var inventory: InventoryManager
	var icon: TextureRect
	var quantity_label: Label
	var _last_item_id: String = ""
	var _last_quantity: int = 0
	
	func _ready():
		_create_ui()
	
	func _create_ui():
		icon = TextureRect.new()
		icon.name = "Icon"
		icon.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		add_child(icon)
		icon.set_anchors_preset(Control.PRESET_FULL_RECT)
		
		quantity_label = Label.new()
		quantity_label.name = "Quantity"
		quantity_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		quantity_label.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
		add_child(quantity_label)
		quantity_label.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	
	func update_slot(slot: InventorySlot):
		if not icon or not quantity_label:
			return
		
		if slot.is_empty():
			icon.texture = null
			quantity_label.text = ""
			modulate = Color(1, 1, 1, 0.3)
			tooltip_text = ""
			_last_item_id = ""
			_last_quantity = 0
		else:
			icon.texture = slot.item.icon
			quantity_label.text = str(slot.quantity) if slot.quantity > 1 else ""
			modulate = Color.WHITE
			
			if _last_item_id != slot.item.id or _last_quantity != slot.quantity:
				tooltip_text = _generate_tooltip(slot)
				_last_item_id = slot.item.id
				_last_quantity = slot.quantity
	
	func _generate_tooltip(slot: InventorySlot) -> String:
		var tooltip = "%s\n%s" % [slot.item.name, slot.item.description]
		
		if slot.item.is_usable:
			tooltip += "\n[Click Izq] Usar"
		if slot.quantity > 1:
			tooltip += "\n[Click Der] Soltar 1"
		tooltip += "\n[Shift+Click] Mover rápido"
		
		return tooltip
	
	func _gui_input(event):
		if not inventory or index < 0 or index >= inventory.slots.size():
			return
		
		if event is InputEventMouseButton and event.pressed:
			match event.button_index:
				MOUSE_BUTTON_LEFT:
					if event.shift_pressed:
						_quick_move_item()
					else:
						if not inventory.slots[index].is_empty():
							slot_clicked.emit(index, inventory.slots[index].item)
				MOUSE_BUTTON_RIGHT:
					if not inventory.slots[index].is_empty():
						slot_right_clicked.emit(index, inventory.slots[index].item)
	
	func _quick_move_item():
		var slot = inventory.slots[index]
		if slot.is_empty():
			return
		
		var target_start = 9 if index < 9 else 0
		var target_end = 36 if index < 9 else 9
		
		for i in range(target_start, target_end):
			if i >= inventory.slots.size():
				break
			
			if inventory.slots[i].is_empty():
				inventory.slots[i].add_item(slot.item, slot.quantity)
				slot.clear()
				break
			elif inventory.slots[i].item.id == slot.item.id and inventory.slots[i].item.is_stackable:
				var remaining = inventory.slots[i].add_item(slot.item, slot.quantity)
				if remaining == 0:
					slot.clear()
					break
				else:
					slot.quantity = remaining
		
		inventory.inventory_changed.emit()
	
	func _get_drag_data(at_position):
		if not inventory or index < 0 or index >= inventory.slots.size():
			return null
		
		if inventory.slots[index].is_empty():
			return null
		
		var preview = Panel.new()
		preview.custom_minimum_size = size
		
		var preview_icon = TextureRect.new()
		preview_icon.texture = icon.texture
		preview_icon.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
		preview_icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		preview.add_child(preview_icon)
		preview_icon.size = size
		
		set_drag_preview(preview)
		
		return {"index": index, "source": self}
	
	func _can_drop_data(at_position, data):
		if not data is Dictionary or not data.has("index"):
			return false
		if data.get("source") == self:
			return false
		return true
	
	func _drop_data(at_position, data):
		if not inventory:
			return
		if data.has("index"):
			inventory.swap_slots(data.index, index)

## Clase principal: InventoryUI
signal item_clicked(item: InventoryItem, slot_index: int)
signal item_right_clicked(item: InventoryItem, slot_index: int)

@export var inventory: InventoryManager
@export var columns: int = 5
@export var slot_size: Vector2 = Vector2(64, 64)

var grid: GridContainer
var slot_uis: Array = []

func _ready():
	if Engine.is_editor_hint():
		return
	
	if not has_node("Panel"):
		_create_structure()
	
	grid = $Panel/MarginContainer/GridContainer
	
	if inventory == null:
		inventory = InventoryManager.new()
		add_child(inventory)
	
	setup_grid()
	inventory.inventory_changed.connect(_on_inventory_changed)
	update_ui()

func _create_structure():
	var panel = Panel.new()
	panel.name = "Panel"
	add_child(panel)
	panel.set_anchors_preset(Control.PRESET_FULL_RECT)
	
	var margin = MarginContainer.new()
	margin.name = "MarginContainer"
	panel.add_child(margin)
	margin.set_anchors_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 10)
	margin.add_theme_constant_override("margin_right", 10)
	margin.add_theme_constant_override("margin_top", 10)
	margin.add_theme_constant_override("margin_bottom", 10)
	
	var grid_container = GridContainer.new()
	grid_container.name = "GridContainer"
	margin.add_child(grid_container)

func setup_grid():
	if grid == null:
		return
	
	grid.columns = columns
	for child in grid.get_children():
		child.queue_free()
	slot_uis.clear()
	
	for i in range(inventory.size):
		var slot_ui = InventorySlotUI.new()
		grid.add_child(slot_ui)
		slot_ui.index = i
		slot_ui.inventory = inventory
		slot_ui.custom_minimum_size = slot_size
		slot_ui.slot_clicked.connect(_on_slot_clicked)
		slot_ui.slot_right_clicked.connect(_on_slot_right_clicked)
		slot_uis.append(slot_ui)

func _on_inventory_changed():
	update_ui()

func update_ui():
	for i in range(min(slot_uis.size(), inventory.slots.size())):
		slot_uis[i].update_slot(inventory.slots[i])

func _on_slot_clicked(slot_index: int, item: InventoryItem):
	item_clicked.emit(item, slot_index)

func _on_slot_right_clicked(slot_index: int, item: InventoryItem):
	item_right_clicked.emit(item, slot_index)
