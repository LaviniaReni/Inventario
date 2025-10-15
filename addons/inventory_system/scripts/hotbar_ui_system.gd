@tool
class_name HotbarUI
extends Control

## Clase interna: HotbarSlotUI
class HotbarSlotUI extends Panel:
	var slot_index: int = -1
	var is_selected: bool = false
	var hotbar: Hotbar
	var inventory: InventoryManager
	var icon: TextureRect
	var quantity_label: Label
	var key_label: Label
	var selection_indicator: Panel
	
	func _ready():
		_create_ui()
		update_key_label()
	
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
		
		key_label = Label.new()
		key_label.name = "KeyLabel"
		key_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
		key_label.vertical_alignment = VERTICAL_ALIGNMENT_TOP
		add_child(key_label)
		key_label.set_anchors_preset(Control.PRESET_TOP_LEFT)
		
		selection_indicator = Panel.new()
		selection_indicator.name = "SelectionIndicator"
		selection_indicator.visible = false
		selection_indicator.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(selection_indicator)
		selection_indicator.set_anchors_preset(Control.PRESET_FULL_RECT)
	
	func setup(index: int, hotbar_ref: Hotbar):
		slot_index = index
		hotbar = hotbar_ref
		inventory = hotbar.inventory
		update_key_label()
	
	func update_slot():
		if not inventory or not hotbar:
			return
		
		var item = hotbar.get_item_at_slot(slot_index)
		var quantity = hotbar.get_quantity_at_slot(slot_index)
		
		if item == null:
			icon.texture = null
			quantity_label.text = ""
			modulate = Color(1, 1, 1, 0.5)
			tooltip_text = ""
		else:
			icon.texture = item.icon
			quantity_label.text = str(quantity) if quantity > 1 else ""
			modulate = Color.WHITE
			tooltip_text = "%s\n%s\n%s" % [
				item.name,
				item.description,
				"[%s] para usar" % (slot_index + 1) if slot_index < 9 else ""
			]
		
		update_selection()
	
	func update_selection():
		if selection_indicator:
			selection_indicator.visible = is_selected
	
	func set_selected(selected: bool):
		is_selected = selected
		update_selection()
	
	func update_key_label():
		if key_label and slot_index >= 0:
			if slot_index < 9:
				key_label.text = str(slot_index + 1)
			else:
				key_label.text = ""
	
	func _gui_input(event):
		if event is InputEventMouseButton and event.pressed:
			if event.button_index == MOUSE_BUTTON_LEFT:
				if hotbar:
					hotbar.select_slot(slot_index)
					if hotbar.auto_use_on_select:
						return
					if is_selected:
						hotbar.use_selected_item()
			elif event.button_index == MOUSE_BUTTON_RIGHT:
				if hotbar:
					hotbar.use_item_at_slot(slot_index)

## Clase principal: HotbarUI
@export var hotbar: Hotbar
@export var inventory: InventoryManager
@export var slot_size: Vector2 = Vector2(64, 64)
@export var spacing: int = 4

var container: HBoxContainer
var slot_uis: Array = []

func _ready():
	if Engine.is_editor_hint():
		return
	
	if not has_node("Container"):
		_create_structure()
	
	container = $Container
	
	if hotbar == null:
		hotbar = Hotbar.new()
		add_child(hotbar)
	
	if inventory:
		hotbar.inventory = inventory
	elif get_parent().has_node("InventoryUI"):
		var inv_ui = get_parent().get_node("InventoryUI")
		if inv_ui.inventory:
			hotbar.inventory = inv_ui.inventory
			inventory = inv_ui.inventory
	
	setup_hotbar()
	
	if hotbar:
		hotbar.slot_selected.connect(_on_slot_selected)
		hotbar.item_used_from_hotbar.connect(_on_item_used)
	
	if inventory:
		inventory.inventory_changed.connect(_on_inventory_changed)
	
	update_ui()

func _create_structure():
	var hbox = HBoxContainer.new()
	hbox.name = "Container"
	add_child(hbox)
	hbox.set_anchors_preset(Control.PRESET_CENTER)

func setup_hotbar():
	if not container:
		return
	
	for child in container.get_children():
		child.queue_free()
	slot_uis.clear()
	
	for i in range(hotbar.hotbar_size):
		var slot_ui = HotbarSlotUI.new()
		container.add_child(slot_ui)
		slot_ui.setup(i, hotbar)
		slot_ui.custom_minimum_size = slot_size
		slot_uis.append(slot_ui)
	
	if container:
		container.add_theme_constant_override("separation", spacing)

func _on_inventory_changed():
	update_ui()

func _on_slot_selected(index: int, item: InventoryItem):
	update_selection(index)

func _on_item_used(item: InventoryItem):
	pass

func update_ui():
	for i in range(slot_uis.size()):
		slot_uis[i].update_slot()

func update_selection(selected_index: int):
	for i in range(slot_uis.size()):
		slot_uis[i].set_selected(i == selected_index)

func get_selected_slot_index() -> int:
	return hotbar.selected_slot if hotbar else 0

func get_selected_item() -> InventoryItem:
	return hotbar.get_selected_item() if hotbar else null
