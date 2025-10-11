@tool
class_name HotbarUI
extends Control

@export var hotbar: Hotbar
@export var inventory: InventoryManager
@export var slot_scene: PackedScene
@export var slot_size: Vector2 = Vector2(64, 64)
@export var spacing: int = 4

@onready var container: HBoxContainer = $Container

var slot_uis: Array = []

func _ready():
	if Engine.is_editor_hint():
		return
	
	# Crear hotbar si no existe
	if hotbar == null:
		hotbar = Hotbar.new()
		add_child(hotbar)
	
	# Vincular inventario
	if inventory:
		hotbar.inventory = inventory
	elif get_parent().has_node("InventoryUI"):
		var inv_ui = get_parent().get_node("InventoryUI")
		if inv_ui.inventory:
			hotbar.inventory = inv_ui.inventory
			inventory = inv_ui.inventory
	
	setup_hotbar()
	
	# Conectar señales
	if hotbar:
		hotbar.slot_selected.connect(_on_slot_selected)
		hotbar.item_used_from_hotbar.connect(_on_item_used)
	
	if inventory:
		inventory.inventory_changed.connect(_on_inventory_changed)
	
	update_ui()

func setup_hotbar():
	if not container:
		return
	
	# Limpiar slots existentes
	for child in container.get_children():
		child.queue_free()
	slot_uis.clear()
	
	# Crear slots
	for i in range(hotbar.hotbar_size):
		var slot_ui = create_slot()
		if slot_ui:
			container.add_child(slot_ui)
			slot_ui.setup(i, hotbar)
			slot_ui.custom_minimum_size = slot_size
			slot_uis.append(slot_ui)
	
	# Configurar espaciado
	if container:
		container.add_theme_constant_override("separation", spacing)

func create_slot() -> Control:
	if slot_scene:
		return slot_scene.instantiate()
	return null

func _on_inventory_changed():
	update_ui()

func _on_slot_selected(index: int, item: InventoryItem):
	update_selection(index)

func _on_item_used(item: InventoryItem):
	# Feedback visual opcional
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
