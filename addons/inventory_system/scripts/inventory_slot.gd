class_name InventorySlot
extends Resource

signal quantity_changed(new_quantity: int)

@export var item: InventoryItem = null
@export var quantity: int = 0

func add_item(new_item: InventoryItem, amount: int = 1) -> int:
	if item == null:
		item = new_item
		quantity = amount
		quantity_changed.emit(quantity)
		return 0
	if item.id == new_item.id and item.is_stackable:
		var space_left = item.max_stack - quantity
		var amount_to_add = min(amount, space_left)
		quantity += amount_to_add
		quantity_changed.emit(quantity)
		return amount - amount_to_add
	return amount

func remove_item(amount: int = 1) -> int:
	var removed = min(amount, quantity)
	quantity -= removed
	if quantity <= 0:
		clear()
	else:
		quantity_changed.emit(quantity)
	return removed

func clear() -> void:
	item = null
	quantity = 0
	quantity_changed.emit(0)

func is_empty() -> bool:
	return item == null

func get_data() -> Dictionary:
	if is_empty():
		return {}
	return {"item_id": item.id, "quantity": quantity}
