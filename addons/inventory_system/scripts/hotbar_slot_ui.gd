extends Panel

var slot_index: int = -1
var is_selected: bool = false
var hotbar: Hotbar
var inventory: InventoryManager

@onready var icon: TextureRect = $Icon
@onready var quantity_label: Label = $Quantity
@onready var key_label: Label = $KeyLabel
@onready var selection_indicator: Panel = $SelectionIndicator

func _ready():
	update_key_label()

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
		# Slot vacío
		icon.texture = null
		quantity_label.text = ""
		modulate = Color(1, 1, 1, 0.5)
		tooltip_text = ""
	else:
		# Slot con item
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
				# Usar item si ya estaba seleccionado
				if is_selected:
					hotbar.use_selected_item()
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			# Click derecho: usar directamente
			if hotbar:
				hotbar.use_item_at_slot(slot_index)
