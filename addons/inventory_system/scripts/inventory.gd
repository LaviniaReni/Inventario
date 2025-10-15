class_name InventoryManager
extends Node

signal inventory_changed
signal item_added(item: InventoryItem, amount: int)
signal item_removed(item: InventoryItem, amount: int)
signal item_used(item: InventoryItem)
signal inventory_full

@export var size: int = 20
@export var auto_save: bool = false
@export var save_path: String = "user://inventory.save"

var slots: Array[InventorySlot] = []

# Sistema de armadura
enum ArmorSlot { HELMET = 0, CHESTPLATE = 1, LEGGINGS = 2, BOOTS = 3 }
var armor_slots: Array[InventorySlot] = []
var offhand_slot: InventorySlot = null

func _ready():
	initialize_slots()
	initialize_armor_slots()
	if auto_save:
		load_inventory()

func _exit_tree():
	if auto_save:
		save_inventory()

func initialize_slots() -> void:
	slots.clear()
	for i in range(size):
		slots.append(InventorySlot.new())

func add_item(item: InventoryItem, amount: int = 1) -> bool:
	if item == null or amount <= 0:
		return false
	
	var remaining = amount
	
	if item.is_stackable:
		for slot in slots:
			if not slot.is_empty() and slot.item.id == item.id:
				remaining = slot.add_item(item, remaining)
				if remaining == 0:
					inventory_changed.emit()
					item_added.emit(item, amount)
					if auto_save:
						save_inventory()
					return true
	
	for slot in slots:
		if slot.is_empty():
			remaining = slot.add_item(item, remaining)
			if remaining == 0:
				inventory_changed.emit()
				item_added.emit(item, amount)
				if auto_save:
					save_inventory()
				return true
	
	if remaining < amount:
		inventory_changed.emit()
		item_added.emit(item, amount - remaining)
		if auto_save:
			save_inventory()
	else:
		inventory_full.emit()
	
	return remaining == 0

func add_item_by_id(item_id: String, amount: int = 1) -> bool:
	if not ItemDatabase or not ItemDatabase.has_item(item_id):
		push_warning("Item no encontrado: %s" % item_id)
		return false
	var item = ItemDatabase.get_item(item_id)
	return add_item(item, amount)

func remove_item(item: InventoryItem, amount: int = 1) -> bool:
	if item == null or amount <= 0:
		return false
	
	var to_remove = amount
	for slot in slots:
		if not slot.is_empty() and slot.item.id == item.id:
			var removed = slot.remove_item(to_remove)
			to_remove -= removed
			if to_remove == 0:
				inventory_changed.emit()
				item_removed.emit(item, amount)
				if auto_save:
					save_inventory()
				return true
	
	return false

func remove_item_by_id(item_id: String, amount: int = 1) -> bool:
	if not ItemDatabase or not ItemDatabase.has_item(item_id):
		return false
	var item = ItemDatabase.get_item(item_id)
	return remove_item(item, amount)

func has_item(item: InventoryItem, amount: int = 1) -> bool:
	return get_item_count(item) >= amount

func get_item_count(item: InventoryItem) -> int:
	if item == null:
		return 0
	var count = 0
	for slot in slots:
		if not slot.is_empty() and slot.item.id == item.id:
			count += slot.quantity
	return count

func use_item(item: InventoryItem) -> bool:
	if not has_item(item):
		return false
	item_used.emit(item)
	if item.is_consumable:
		remove_item(item, 1)
	return true

func use_item_by_id(item_id: String) -> bool:
	if not ItemDatabase or not ItemDatabase.has_item(item_id):
		return false
	var item = ItemDatabase.get_item(item_id)
	return use_item(item)

func swap_slots(index_a: int, index_b: int) -> void:
	if index_a < 0 or index_a >= slots.size() or index_b < 0 or index_b >= slots.size():
		return
	
	if not slots[index_a].is_empty() and not slots[index_b].is_empty():
		if slots[index_a].item.id == slots[index_b].item.id and slots[index_a].item.is_stackable:
			var remaining = slots[index_b].add_item(slots[index_a].item, slots[index_a].quantity)
			if remaining == 0:
				slots[index_a].clear()
			else:
				slots[index_a].quantity = remaining
			inventory_changed.emit()
			if auto_save:
				save_inventory()
			return
	
	var temp_item = slots[index_a].item
	var temp_quantity = slots[index_a].quantity
	slots[index_a].item = slots[index_b].item
	slots[index_a].quantity = slots[index_b].quantity
	slots[index_b].item = temp_item
	slots[index_b].quantity = temp_quantity
	inventory_changed.emit()
	if auto_save:
		save_inventory()

func clear_inventory() -> void:
	for slot in slots:
		slot.clear()
	inventory_changed.emit()
	if auto_save:
		save_inventory()

func save_inventory() -> void:
	var save_data = []
	for slot in slots:
		save_data.append(slot.get_data() if not slot.is_empty() else {})
	var file = FileAccess.open(save_path, FileAccess.WRITE)
	if file:
		file.store_var(save_data)
		file.close()

func load_inventory() -> void:
	if not FileAccess.file_exists(save_path):
		return
	
	if not ItemDatabase or ItemDatabase.get_item_count() == 0:
		push_warning("ItemDatabase no está listo, esperando...")
		await ItemDatabase.database_loaded
	
	var file = FileAccess.open(save_path, FileAccess.READ)
	if file:
		var save_data = file.get_var()
		file.close()
		
		clear_inventory()
		for i in range(min(save_data.size(), slots.size())):
			var slot_data = save_data[i]
			if slot_data is Dictionary and slot_data.has("item_id"):
				var item = ItemDatabase.get_item(slot_data.item_id)
				if item:
					slots[i].add_item(item, slot_data.get("quantity", 1))
		inventory_changed.emit()

func initialize_armor_slots():
	armor_slots.clear()
	for i in range(4):
		armor_slots.append(InventorySlot.new())
	offhand_slot = InventorySlot.new()

func equip_armor(item: InventoryItem, slot_type: ArmorSlot) -> bool:
	if item == null or item.item_type != InventoryItem.ItemType.EQUIPMENT:
		return false
	
	var armor_type = item.custom_data.get("armor_type", "")
	var expected_type = ["helmet", "chestplate", "leggings", "boots"][slot_type]
	
	if armor_type != expected_type:
		return false
	
	if not armor_slots[slot_type].is_empty():
		var old_armor = armor_slots[slot_type].item
		armor_slots[slot_type].clear()
		add_item(old_armor, 1)
	
	armor_slots[slot_type].add_item(item, 1)
	remove_item(item, 1)
	inventory_changed.emit()
	return true

func unequip_armor(slot_type: ArmorSlot) -> bool:
	if armor_slots[slot_type].is_empty():
		return false
	
	var armor = armor_slots[slot_type].item
	armor_slots[slot_type].clear()
	add_item(armor, 1)
	inventory_changed.emit()
	return true

func get_equipped_armor(slot_type: ArmorSlot) -> InventoryItem:
	return armor_slots[slot_type].item if not armor_slots[slot_type].is_empty() else null

func get_total_armor_value() -> int:
	var total = 0
	for armor_slot in armor_slots:
		if not armor_slot.is_empty():
			total += armor_slot.item.custom_data.get("armor_value", 0)
	return total

func equip_offhand(item: InventoryItem) -> bool:
	if item == null:
		return false
	
	if not offhand_slot.is_empty():
		var old_item = offhand_slot.item
		offhand_slot.clear()
		add_item(old_item, 1)
	
	offhand_slot.add_item(item, 1)
	remove_item(item, 1)
	inventory_changed.emit()
	return true

func unequip_offhand() -> bool:
	if offhand_slot.is_empty():
		return false
	
	var item = offhand_slot.item
	offhand_slot.clear()
	add_item(item, 1)
	inventory_changed.emit()
	return true
