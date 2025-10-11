extends Node2D

@onready var inventory_ui: InventoryUI = $InventoryUI
@onready var inventory: InventoryManager = $InventoryUI.inventory
@onready var info_label: Label = $InfoLabel

func _ready():
	if ItemDatabase.get_item_count() == 0:
		ItemDatabase.database_loaded.connect(_on_database_loaded)
	else:
		_on_database_loaded()
	inventory.item_added.connect(_on_item_added)
	inventory.item_removed.connect(_on_item_removed)
	inventory.item_used.connect(_on_item_used)
	inventory_ui.item_clicked.connect(_on_item_clicked)
	inventory_ui.item_right_clicked.connect(_on_item_right_clicked)
	inventory_ui.visible = false
	print("🎮 DEMO DE INVENTARIO")
	print("Presiona ESC para abrir/cerrar")

func _on_database_loaded():
	print("✓ Base de datos cargada")
	if ItemDatabase.has_item("potion_health"):
		inventory.add_item_by_id("potion_health", 5)
	if ItemDatabase.has_item("sword_iron"):
		inventory.add_item_by_id("sword_iron", 1)
	if ItemDatabase.has_item("bread"):
		inventory.add_item_by_id("bread", 10)
	if ItemDatabase.has_item("gold_coin"):
		inventory.add_item_by_id("gold_coin", 50)

func _input(event):
	if event.is_action_pressed("ui_cancel"):
		inventory_ui.visible = !inventory_ui.visible
		get_viewport().set_input_as_handled()

func _on_item_added(item: InventoryItem, amount: int):
	show_info("✓ Agregado: %d x %s" % [amount, item.name])

func _on_item_removed(item: InventoryItem, amount: int):
	show_info("✗ Removido: %d x %s" % [amount, item.name])

func _on_item_used(item: InventoryItem):
	show_info("⚡ Usando: %s" % item.name)

func _on_item_clicked(item: InventoryItem, slot_index: int):
	if item.is_usable:
		inventory.use_item(item)

func _on_item_right_clicked(item: InventoryItem, slot_index: int):
	inventory.remove_item(item, 1)

func show_info(text: String):
	info_label.text = text
	print(text)
