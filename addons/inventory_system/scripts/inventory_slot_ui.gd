extends Panel

signal slot_clicked(slot_index: int, item: InventoryItem)
signal slot_right_clicked(slot_index: int, item: InventoryItem)

var index: int = -1
var inventory: InventoryManager

var _last_item_id: String = ""
var _last_quantity: int = 0

@onready var icon: TextureRect = $Icon
@onready var quantity_label: Label = $Quantity

var _is_dragging: bool = false
var _drag_data: Dictionary = {}

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
			tooltip_text = "%s\n%s" % [slot.item.name, slot.item.description]
			if slot.item.is_usable:
				tooltip_text += "\n[Click Izq] Usar"
			if slot.quantity > 1:
				tooltip_text += "\n[Click Der] Soltar 1"
			_last_item_id = slot.item.id
			_last_quantity = slot.quantity

func _gui_input(event):
	if not inventory or index < 0 or index >= inventory.slots.size():
		return
	
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT:
			if not inventory.slots[index].is_empty():
				slot_clicked.emit(index, inventory.slots[index].item)
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			if not inventory.slots[index].is_empty():
				slot_right_clicked.emit(index, inventory.slots[index].item)

func _get_drag_data(at_position):
	if not inventory or index < 0 or index >= inventory.slots.size():
		return null
	
	if inventory.slots[index].is_empty():
		return null
	
	_is_dragging = true
	
	var preview = Panel.new()
	preview.custom_minimum_size = size
	var preview_icon = TextureRect.new()
	preview_icon.texture = icon.texture
	preview_icon.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
	preview_icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	preview.add_child(preview_icon)
	preview_icon.size = size
	
	set_drag_preview(preview)
	
	_drag_data = {"index": index, "source": self}
	return _drag_data

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
	
	_is_dragging = false

func _notification(what):
	if what == NOTIFICATION_DRAG_END:
		_is_dragging = false
		_drag_data.clear()
