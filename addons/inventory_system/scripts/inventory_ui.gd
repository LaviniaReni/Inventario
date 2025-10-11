@tool
class_name InventoryUI
extends Control

signal item_clicked(item: InventoryItem, slot_index: int)
signal item_right_clicked(item: InventoryItem, slot_index: int)

@export var inventory: InventoryManager
@export var slot_scene: PackedScene
@export var columns: int = 5
@export var slot_size: Vector2 = Vector2(64, 64)

@onready var grid = $Panel/MarginContainer/GridContainer

var slot_uis: Array = []

func _ready():
	if Engine.is_editor_hint():
		return
	if inventory == null:
		inventory = InventoryManager.new()
		add_child(inventory)
	setup_grid()
	inventory.inventory_changed.connect(_on_inventory_changed)
	update_ui()

func setup_grid():
	if grid == null:
		return
	grid.columns = columns
	for child in grid.get_children():
		child.queue_free()
	slot_uis.clear()
	for i in range(inventory.size):
		var slot_ui = create_slot()
		if slot_ui:
			grid.add_child(slot_ui)
			slot_ui.index = i
			slot_ui.inventory = inventory
			slot_ui.custom_minimum_size = slot_size
			slot_ui.slot_clicked.connect(_on_slot_clicked)
			slot_ui.slot_right_clicked.connect(_on_slot_right_clicked)
			slot_uis.append(slot_ui)

func create_slot() -> Control:
	return slot_scene.instantiate() if slot_scene else null

func _on_inventory_changed():
	update_ui()

func update_ui():
	for i in range(min(slot_uis.size(), inventory.slots.size())):
		slot_uis[i].update_slot(inventory.slots[i])

func _on_slot_clicked(slot_index: int, item: InventoryItem):
	item_clicked.emit(item, slot_index)

func _on_slot_right_clicked(slot_index: int, item: InventoryItem):
	item_right_clicked.emit(item, slot_index)
