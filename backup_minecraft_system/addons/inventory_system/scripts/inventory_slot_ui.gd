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
			if event.shift_pressed:
				# SHIFT + CLICK: Quick move
				_quick_move_item()
			else:
				if not inventory.slots[index].is_empty():
					slot_clicked.emit(index, inventory.slots[index].item)
		
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			if not inventory.slots[index].is_empty():
				slot_right_clicked.emit(index, inventory.slots[index].item)
		
		elif event.button_index == MOUSE_BUTTON_MIDDLE:
			# MIDDLE CLICK: Pick block (creative)
			if not inventory.slots[index].is_empty():
				_pick_block()

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


# ============================================
# CONTROLES MINECRAFT (Agregado automáticamente)
# ============================================

func _quick_move_item():
	"""Mueve items rápidamente entre hotbar e inventario principal"""
	var slot = inventory.slots[index]
	if slot.is_empty():
		return
	
	# Si está en hotbar (0-8), mover a inventario principal (9-35)
	# Si está en inventario, mover a hotbar
	var target_start = 9 if index < 9 else 0
	var target_end = 36 if index < 9 else 9
	
	for i in range(target_start, target_end):
		if i >= inventory.slots.size():
			break
		
		if inventory.slots[i].is_empty():
			# Slot vacío: mover todo
			inventory.slots[i].add_item(slot.item, slot.quantity)
			slot.clear()
			break
		elif inventory.slots[i].item.id == slot.item.id and inventory.slots[i].item.is_stackable:
			# Mismo item: stackear
			var remaining = inventory.slots[i].add_item(slot.item, slot.quantity)
			if remaining == 0:
				slot.clear()
				break
			else:
				slot.quantity = remaining
	
	inventory.inventory_changed.emit()

func _pick_block():
	"""Copia el item al hotbar (modo creativo)"""
	var slot = inventory.slots[index]
	if slot.is_empty():
		return
	
	# Buscar slot vacío o el mismo item en el hotbar
	for i in range(9):
		if inventory.slots[i].is_empty():
			inventory.slots[i].add_item(slot.item, slot.item.max_stack)
			inventory.inventory_changed.emit()
			break
		elif inventory.slots[i].item.id == slot.item.id:
			# Ya tiene el item
			break
