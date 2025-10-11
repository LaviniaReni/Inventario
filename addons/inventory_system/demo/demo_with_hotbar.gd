extends Node2D

@onready var inventory_ui: InventoryUI = $InventoryUI
@onready var inventory: InventoryManager = $InventoryUI.inventory
@onready var hotbar_ui: HotbarUI = $HotbarUI
@onready var hotbar: Hotbar = $HotbarUI.hotbar
@onready var info_label: Label = $InfoLabel
@onready var selected_label: Label = $SelectedLabel

func _ready():
	# Configurar acciones de input
	Hotbar.setup_input_actions()
	
	# Esperar a que se cargue la base de datos
	if ItemDatabase.get_item_count() == 0:
		ItemDatabase.database_loaded.connect(_on_database_loaded)
	else:
		_on_database_loaded()
	
	# Conectar señales del inventario
	inventory.item_added.connect(_on_item_added)
	inventory.item_removed.connect(_on_item_removed)
	inventory.item_used.connect(_on_item_used)
	
	# Conectar señales del inventario UI
	inventory_ui.item_clicked.connect(_on_item_clicked)
	inventory_ui.item_right_clicked.connect(_on_item_right_clicked)
	
	# Conectar señales del hotbar
	hotbar.slot_selected.connect(_on_hotbar_slot_selected)
	hotbar.item_used_from_hotbar.connect(_on_hotbar_item_used)
	
	inventory_ui.visible = false
	
	print("🎮 DEMO DE INVENTARIO CON HOTBAR")
	print("Controles:")
	print("- ESC: Abrir/Cerrar inventario")
	print("- 1-9: Seleccionar slot del hotbar")
	print("- Scroll: Cambiar slot")
	print("- E: Usar item seleccionado")

func _on_database_loaded():
	print("✓ Base de datos cargada")
	
	# Agregar items al inventario
	if ItemDatabase.has_item("potion_health"):
		inventory.add_item_by_id("potion_health", 5)
	if ItemDatabase.has_item("sword_iron"):
		inventory.add_item_by_id("sword_iron", 1)
	if ItemDatabase.has_item("bread"):
		inventory.add_item_by_id("bread", 10)
	if ItemDatabase.has_item("gold_coin"):
		inventory.add_item_by_id("gold_coin", 50)
	
	update_selected_label()

func _input(event):
	# Abrir/Cerrar inventario
	if event.is_action_pressed("ui_cancel"):
		inventory_ui.visible = !inventory_ui.visible
		get_viewport().set_input_as_handled()
	
	# Usar item seleccionado
	if event.is_action_pressed("ui_accept"): # Enter o Espacio
		hotbar.use_selected_item()
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

func _on_hotbar_slot_selected(index: int, item: InventoryItem):
	update_selected_label()
	if item:
		show_info("Seleccionado: Slot %d - %s" % [index + 1, item.name])
	else:
		show_info("Seleccionado: Slot %d (vacío)" % (index + 1))

func _on_hotbar_item_used(item: InventoryItem):
	show_info("⚡ Usado desde hotbar: %s" % item.name)

func update_selected_label():
	var item = hotbar.get_selected_item()
	if item:
		selected_label.text = "Seleccionado [%d]: %s" % [hotbar.selected_slot + 1, item.name]
	else:
		selected_label.text = "Seleccionado [%d]: (vacío)" % (hotbar.selected_slot + 1)

func show_info(text: String):
	info_label.text = text
	print(text)
