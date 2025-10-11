extends Panel

signal slot_clicked(slot_index: int, item: InventoryItem)
signal slot_right_clicked(slot_index: int, item: InventoryItem)

var index: int = -1
var inventory: InventoryManager

@onready var icon: TextureRect = $Icon
@onready var quantity_label: Label = $Quantity

static var dragged_slot: Panel = null
static var dragged_index: int = -1

func update_slot(slot: InventorySlot):
	if not icon or not quantity_label:
		return
	if slot.is_empty():
		icon.texture = null
		quantity_label.text = ""
		modulate = Color(1, 1, 1, 0.3)
		tooltip_text = ""
	else:
		icon.texture = slot.item.icon
		quantity_label.text = str(slot.quantity) if slot.quantity > 1 else ""
		modulate = Color.WHITE
		tooltip_text = "%s\n%s" % [slot.item.name, slot.item.description]

func _gui_input(event):
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT:
			if not inventory.slots[index].is_empty():
				slot_clicked.emit(index, inventory.slots[index].item)
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			if not inventory.slots[index].is_empty():
				slot_right_clicked.emit(index, inventory.slots[index].item)

func _get_drag_data(at_position):
	if inventory.slots[index].is_empty():
		return null
	dragged_slot = self
	dragged_index = index
	var preview = Panel.new()
	preview.custom_minimum_size = size
	var preview_icon = TextureRect.new()
	preview_icon.texture = icon.texture
	preview_icon.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
	preview_icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	preview.add_child(preview_icon)
	preview_icon.size = size
	set_drag_preview(preview)
	return {"index": index}

func _can_drop_data(at_position, data):
	return data is Dictionary and data.has("index")

func _drop_data(at_position, data):
	if data.has("index"):
		inventory.swap_slots(data.index, index)
