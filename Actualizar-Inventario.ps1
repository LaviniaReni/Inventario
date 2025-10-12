# Script de actualización para Windows
# Ejecutar desde la raíz del proyecto Godot 4.5

Write-Host "🔧 Actualizando Sistema de Inventario para Godot 4.5..." -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en la carpeta correcta
if (-not (Test-Path "project.godot")) {
    Write-Host "❌ Error: No se encontró project.godot" -ForegroundColor Red
    Write-Host "   Asegúrate de ejecutar este script desde la raíz de tu proyecto Godot" -ForegroundColor Yellow
    pause
    exit
}

# Crear carpeta de backup
$backupFolder = ".backups\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Write-Host "📦 Creando backup en: $backupFolder" -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $backupFolder | Out-Null
Copy-Item -Path "addons\inventory_system\scripts" -Destination "$backupFolder\scripts" -Recurse -Force
Write-Host "✅ Backup creado" -ForegroundColor Green
Write-Host ""

# Función para actualizar archivo
function Update-File {
    param($FilePath, $Content)
    Write-Host "✏️  Actualizando: $FilePath" -ForegroundColor Cyan
    Set-Content -Path $FilePath -Value $Content -Encoding UTF8
    Write-Host "✅ Actualizado" -ForegroundColor Green
}

# 1. Actualizar inventory.gd
$inventoryContent = @'
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

func _ready():
	initialize_slots()
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
'@

Update-File "addons\inventory_system\scripts\inventory.gd" $inventoryContent

# 2. Actualizar item_database.gd
$databaseContent = @'
extends Node

signal database_loaded

var items: Dictionary = {}
var is_loaded: bool = false

@export var items_folder: String = "res://addons/inventory_system/demo/demo_items/"
@export var auto_load_on_ready: bool = true

func _ready():
	if auto_load_on_ready:
		call_deferred("load_all_items")

func load_all_items() -> void:
	if is_loaded:
		push_warning("ItemDatabase ya está cargado")
		return
	
	print("🗄️ ItemDatabase: Cargando items desde: ", items_folder)
	items.clear()
	
	if not DirAccess.dir_exists_absolute(items_folder):
		push_warning("Carpeta de items no existe: %s" % items_folder)
		DirAccess.make_dir_recursive_absolute(items_folder)
		is_loaded = true
		database_loaded.emit()
		return
	
	var loaded_count = 0
	var dir = DirAccess.open(items_folder)
	
	if dir:
		dir.list_dir_begin()
		var file_name = dir.get_next()
		
		while file_name != "":
			if not file_name.begins_with(".") and file_name.ends_with(".tres"):
				var full_path = items_folder + file_name
				var item = load(full_path)
				
				if item is InventoryItem:
					if item.id.is_empty():
						push_warning("Item sin ID: %s" % full_path)
					elif items.has(item.id):
						push_warning("ID duplicado: %s en %s" % [item.id, full_path])
					else:
						items[item.id] = item
						loaded_count += 1
				else:
					push_warning("Archivo no es InventoryItem: %s" % full_path)
			
			file_name = dir.get_next()
		
		dir.list_dir_end()
		
		is_loaded = true
		print("✓ ItemDatabase: %d items cargados correctamente" % loaded_count)
		database_loaded.emit()
	else:
		push_error("No se pudo abrir carpeta: %s" % items_folder)
		is_loaded = true
		database_loaded.emit()

func get_item(item_id: String) -> InventoryItem:
	if not is_loaded:
		push_warning("ItemDatabase aún no está cargado")
	return items.get(item_id, null)

func has_item(item_id: String) -> bool:
	return items.has(item_id)

func get_all_items() -> Array[InventoryItem]:
	var result: Array[InventoryItem] = []
	for item in items.values():
		result.append(item)
	return result

func get_item_count() -> int:
	return items.size()

func get_items_by_type(type: InventoryItem.ItemType) -> Array[InventoryItem]:
	var result: Array[InventoryItem] = []
	for item in items.values():
		if item.item_type == type:
			result.append(item)
	return result

func search_items(query: String) -> Array[InventoryItem]:
	var result: Array[InventoryItem] = []
	var query_lower = query.to_lower()
	
	for item in items.values():
		if query_lower in item.name.to_lower() or query_lower in item.description.to_lower():
			result.append(item)
	
	return result

func reload_items() -> void:
	is_loaded = false
	load_all_items()

func print_database_info() -> void:
	print("\n" + "=".repeat(50))
	print("📊 ItemDatabase Info")
	print("=".repeat(50))
	print("Total items: ", items.size())
	print("Estado: ", "Cargado" if is_loaded else "No cargado")
	
	for type in InventoryItem.ItemType.values():
		var type_name = InventoryItem.ItemType.keys()[type]
		var count = get_items_by_type(type).size()
		if count > 0:
			print("  %s: %d" % [type_name, count])
	
	print("=".repeat(50) + "\n")
'@

Update-File "addons\inventory_system\scripts\item_database.gd" $databaseContent

# 3. Actualizar hotbar.gd
$hotbarContent = @'
class_name Hotbar
extends Node

signal slot_selected(index: int, item: InventoryItem)
signal item_used_from_hotbar(item: InventoryItem)

@export var hotbar_size: int = 9
@export var inventory: InventoryManager
@export var selected_slot: int = 0
@export var enable_scroll: bool = true
@export var enable_number_keys: bool = true
@export var auto_use_on_select: bool = false

var hotbar_slots: Array[int] = []

func _ready():
	initialize_hotbar()
	if inventory:
		inventory.inventory_changed.connect(_on_inventory_changed)
		validate_hotbar_size()

func initialize_hotbar():
	hotbar_slots.clear()
	for i in range(hotbar_size):
		hotbar_slots.append(i)

func validate_hotbar_size():
	if not inventory:
		return
	if hotbar_size > inventory.size:
		push_warning("Hotbar size (%d) mayor que inventory size (%d), ajustando..." % [hotbar_size, inventory.size])
		hotbar_size = inventory.size
		initialize_hotbar()

func _input(event):
	if not inventory:
		return
	
	if enable_number_keys:
		for i in range(1, min(hotbar_size + 1, 10)):
			var action_name = "hotbar_slot_%d" % i
			if InputMap.has_action(action_name) and event.is_action_pressed(action_name):
				select_slot(i - 1)
				if selected_slot == i - 1:
					get_viewport().set_input_as_handled()
				return
	
	if enable_scroll and event is InputEventMouseButton:
		if event.pressed:
			if event.button_index == MOUSE_BUTTON_WHEEL_UP:
				select_previous_slot()
				get_viewport().set_input_as_handled()
			elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
				select_next_slot()
				get_viewport().set_input_as_handled()

func select_slot(index: int):
	if index < 0 or index >= hotbar_size:
		return
	
	selected_slot = index
	var item = get_selected_item()
	slot_selected.emit(selected_slot, item)
	
	if auto_use_on_select and item and item.is_usable:
		use_selected_item()

func select_next_slot():
	select_slot((selected_slot + 1) % hotbar_size)

func select_previous_slot():
	select_slot((selected_slot - 1 + hotbar_size) % hotbar_size)

func get_selected_item() -> InventoryItem:
	return get_item_at_slot(selected_slot)

func get_item_at_slot(slot_index: int) -> InventoryItem:
	if not inventory:
		return null
	
	var inv_index = get_inventory_index(slot_index)
	if inv_index < 0 or inv_index >= inventory.slots.size():
		return null
	
	var slot = inventory.slots[inv_index]
	return slot.item if slot else null

func get_quantity_at_slot(slot_index: int) -> int:
	if not inventory:
		return 0
	
	var inv_index = get_inventory_index(slot_index)
	if inv_index < 0 or inv_index >= inventory.slots.size():
		return 0
	
	var slot = inventory.slots[inv_index]
	return slot.quantity if slot else 0

func use_selected_item() -> bool:
	return use_item_at_slot(selected_slot)

func use_item_at_slot(slot_index: int) -> bool:
	if slot_index < 0 or slot_index >= hotbar_size:
		return false
	
	var item = get_item_at_slot(slot_index)
	if not item or not item.is_usable:
		return false
	
	if inventory.use_item(item):
		item_used_from_hotbar.emit(item)
		return true
	return false

func get_inventory_index(hotbar_index: int) -> int:
	if hotbar_index < 0 or hotbar_index >= hotbar_slots.size():
		return -1
	
	var inv_idx = hotbar_slots[hotbar_index]
	if not inventory or inv_idx >= inventory.slots.size():
		return -1
	
	return inv_idx

func _on_inventory_changed():
	if inventory and inventory.size < hotbar_size:
		validate_hotbar_size()

static func setup_input_actions():
	for i in range(1, 10):
		var action_name = "hotbar_slot_%d" % i
		if not InputMap.has_action(action_name):
			InputMap.add_action(action_name)
			var event = InputEventKey.new()
			event.keycode = KEY_0 + i
			InputMap.action_add_event(action_name, event)
'@

Update-File "addons\inventory_system\scripts\hotbar.gd" $hotbarContent

# 4. Actualizar inventory_slot_ui.gd
$slotUIContent = @'
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
'@

Update-File "addons\inventory_system\scripts\inventory_slot_ui.gd" $slotUIContent

# 5. Corregir typo en project.godot
Write-Host ""
Write-Host "✏️  Corrigiendo typo en project.godot..." -ForegroundColor Cyan
$projectContent = Get-Content "project.godot" -Raw
$projectContent = $projectContent -replace 'Prueva de inventario', 'Prueba de inventario'
Set-Content -Path "project.godot" -Value $projectContent -Encoding UTF8
Write-Host "✅ project.godot corregido" -ForegroundColor Green

Write-Host ""
Write-Host "Actualizacion completada exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "Backup guardado en: $backupFolder" -ForegroundColor Yellow
Write-Host ""
Write-Host "Proximos pasos:" -ForegroundColor Cyan
Write-Host "   1. Abre tu proyecto en Godot 4.5" -ForegroundColor White
Write-Host "   2. Espera a que se reimporten los archivos" -ForegroundColor White
Write-Host "   3. Prueba la demo: addons/inventory_system/demo/demo.tscn" -ForegroundColor White
Write-Host "   4. Verifica que todo funcione correctamente" -ForegroundColor White
Write-Host ""
pause