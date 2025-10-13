extends Node2D

@onready var inventory_ui = $InventoryUI
@onready var inventory = $InventoryUI.inventory
@onready var hotbar_ui = $HotbarUI
@onready var info_label = $InfoLabel

var crafting_table_ui = null

func _ready():
	if ItemDatabase.get_item_count() == 0:
		await ItemDatabase.database_loaded
	
	add_starting_items()
	
	inventory.item_added.connect(_on_item_added)
	inventory.item_used.connect(_on_item_used)
	
	inventory_ui.visible = false
	
	print_controls()

func print_controls():
	print("\n" + "="*50)
	print("🎮 CONTROLES MINECRAFT")
	print("="*50)
	print("E: Inventario")
	print("1-9: Hotbar")
	print("Q: Soltar item")
	print("Enter: Mesa de trabajo")
	print("="*50 + "\n")

func add_starting_items():
	if ItemDatabase.has_item("wood"):
		inventory.add_item_by_id("wood", 64)
	if ItemDatabase.has_item("stone"):
		inventory.add_item_by_id("stone", 64)
	if ItemDatabase.has_item("stick"):
		inventory.add_item_by_id("stick", 32)

func _input(event):
	if event.is_action_pressed("open_inventory"):
		inventory_ui.visible = !inventory_ui.visible
		get_viewport().set_input_as_handled()
	
	if event.is_action_pressed("ui_accept"):
		if not crafting_table_ui:
			open_crafting_table()
		get_viewport().set_input_as_handled()

func open_crafting_table():
	var scene = load("res://addons/inventory_system/scenes/crafting_table_ui.tscn")
	if scene:
		crafting_table_ui = scene.instantiate()
		add_child(crafting_table_ui)
		crafting_table_ui.inventory_ui = inventory_ui
		crafting_table_ui.closed.connect(_on_crafting_closed)
		show_info("Mesa de trabajo abierta")

func _on_crafting_closed():
	crafting_table_ui = null

func _on_item_added(item: InventoryItem, amount: int):
	show_info("+ %d x %s" % [amount, item.name])

func _on_item_used(item: InventoryItem):
	show_info("⚡ %s" % item.name)

func show_info(text: String):
	info_label.text = text
	print(text)
