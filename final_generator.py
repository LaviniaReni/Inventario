#!/usr/bin/env python3
"""
Generador de Sistema de Inventario para Godot 4.5
Versión: 2.0 - COMPLETO

Uso: python generate_inventory.py
"""

import os
import sys
import time
from pathlib import Path

class InventoryGenerator:
    def __init__(self):
        self.base_path = Path("addons/inventory_system")
        self.files_created = 0
        self.dirs_created = 0
        self.start_time = time.time()
    
    def create_directory(self, path):
        try:
            full_path = self.base_path / path if path else self.base_path
            full_path.mkdir(parents=True, exist_ok=True)
            self.dirs_created += 1
            return True
        except Exception as e:
            print(f"❌ Error creando {path}: {e}")
            return False
    
    def create_file(self, path, content):
        try:
            full_path = self.base_path / path
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.files_created += 1
            return True
        except Exception as e:
            print(f"❌ Error creando {path}: {e}")
            return False
    
    def generate(self):
        print("=" * 60)
        print("🎮 GENERADOR DE INVENTARIO PARA GODOT 4.5")
        print("=" * 60)
        print()
        
        if not Path("project.godot").exists():
            print("⚠️  No se encontró 'project.godot'")
            response = input("¿Continuar de todos modos? (s/n): ")
            if response.lower() != 's':
                return False
        
        print("📁 Creando estructura...")
        
        self.create_directory("")
        self.create_directory("scripts")
        self.create_directory("scenes")
        self.create_directory("demo")
        self.create_directory("demo/demo_items")
        Path("items").mkdir(exist_ok=True)
        
        print("📝 Generando archivos...")
        
        self.create_file("plugin.cfg", PLUGIN_CFG)
        self.create_file("plugin.gd", PLUGIN_GD)
        self.create_file("scripts/item.gd", ITEM_GD)
        self.create_file("scripts/inventory_slot.gd", INVENTORY_SLOT_GD)
        self.create_file("scripts/inventory.gd", INVENTORY_GD)
        self.create_file("scripts/inventory_ui.gd", INVENTORY_UI_GD)
        self.create_file("scripts/inventory_slot_ui.gd", INVENTORY_SLOT_UI_GD)
        self.create_file("scripts/item_database.gd", ITEM_DATABASE_GD)
        self.create_file("scenes/inventory_slot_ui.tscn", INVENTORY_SLOT_UI_TSCN)
        self.create_file("scenes/inventory_ui.tscn", INVENTORY_UI_TSCN)
        self.create_file("demo/demo.gd", DEMO_GD)
        self.create_file("demo/demo.tscn", DEMO_TSCN)
        self.create_file("demo/demo_items/potion_health.tres", POTION_TRES)
        self.create_file("demo/demo_items/sword_iron.tres", SWORD_TRES)
        self.create_file("demo/demo_items/bread.tres", BREAD_TRES)
        self.create_file("demo/demo_items/gold_coin.tres", GOLD_TRES)
        self.create_file("README.md", README_MD)
        self.create_file("QUICK_START.md", QUICK_START_MD)
        self.create_file("AUTOLOAD_SETUP.md", AUTOLOAD_SETUP_MD)
        
        elapsed = time.time() - self.start_time
        print()
        print("=" * 60)
        print("✅ GENERACIÓN COMPLETADA")
        print("=" * 60)
        print()
        print(f"📊 Archivos creados: {self.files_created}")
        print(f"📊 Directorios: {self.dirs_created}")
        print(f"⏱️  Tiempo: {elapsed:.2f}s")
        print()
        print("🔧 PRÓXIMOS PASOS:")
        print()
        print("1. Abre Godot 4.5")
        print("2. Proyecto > Plugins > Activar 'Inventory System'")
        print("3. Proyecto > Autoload > Agregar:")
        print("   Path: addons/inventory_system/scripts/item_database.gd")
        print("   Name: ItemDatabase")
        print("4. Ejecuta: addons/inventory_system/demo/demo.tscn")
        print()
        return True

PLUGIN_CFG = """[plugin]

name="Inventory System"
description="Sistema de inventario completo con base de datos"
author="Inventory System"
version="2.0"
script="plugin.gd"
"""

PLUGIN_GD = """@tool
extends EditorPlugin

func _enter_tree():
\tadd_custom_type("InventoryManager", "Node", preload("res://addons/inventory_system/scripts/inventory.gd"), preload("res://icon.svg"))
\tadd_custom_type("InventoryUI", "Control", preload("res://addons/inventory_system/scripts/inventory_ui.gd"), preload("res://icon.svg"))
\tprint("✓ Inventory System activado")

func _exit_tree():
\tremove_custom_type("InventoryManager")
\tremove_custom_type("InventoryUI")
"""

ITEM_GD = """class_name InventoryItem
extends Resource

enum ItemType { CONSUMABLE, EQUIPMENT, QUEST, MATERIAL, MISC }

@export_group("Info Básica")
@export var id: String = ""
@export var name: String = ""
@export_multiline var description: String = ""
@export var icon: Texture2D
@export var item_type: ItemType = ItemType.MISC

@export_group("Stack")
@export var is_stackable: bool = true
@export var max_stack: int = 99

@export_group("Uso")
@export var is_usable: bool = false
@export var is_consumable: bool = false

@export_group("Custom")
@export var custom_data: Dictionary = {}
"""

INVENTORY_SLOT_GD = """class_name InventorySlot
extends Resource

signal quantity_changed(new_quantity: int)

@export var item: InventoryItem = null
@export var quantity: int = 0

func add_item(new_item: InventoryItem, amount: int = 1) -> int:
\tif item == null:
\t\titem = new_item
\t\tquantity = amount
\t\tquantity_changed.emit(quantity)
\t\treturn 0
\tif item.id == new_item.id and item.is_stackable:
\t\tvar space_left = item.max_stack - quantity
\t\tvar amount_to_add = min(amount, space_left)
\t\tquantity += amount_to_add
\t\tquantity_changed.emit(quantity)
\t\treturn amount - amount_to_add
\treturn amount

func remove_item(amount: int = 1) -> int:
\tvar removed = min(amount, quantity)
\tquantity -= removed
\tif quantity <= 0:
\t\tclear()
\telse:
\t\tquantity_changed.emit(quantity)
\treturn removed

func clear() -> void:
\titem = null
\tquantity = 0
\tquantity_changed.emit(0)

func is_empty() -> bool:
\treturn item == null

func get_data() -> Dictionary:
\tif is_empty():
\t\treturn {}
\treturn {"item_id": item.id, "quantity": quantity}
"""

INVENTORY_GD = """class_name InventoryManager
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
\tinitialize_slots()
\tif auto_save:
\t\tload_inventory()

func initialize_slots() -> void:
\tslots.clear()
\tfor i in range(size):
\t\tslots.append(InventorySlot.new())

func add_item(item: InventoryItem, amount: int = 1) -> bool:
\tif item == null:
\t\treturn false
\tvar remaining = amount
\tif item.is_stackable:
\t\tfor slot in slots:
\t\t\tif not slot.is_empty() and slot.item.id == item.id:
\t\t\t\tremaining = slot.add_item(item, remaining)
\t\t\t\tif remaining == 0:
\t\t\t\t\tinventory_changed.emit()
\t\t\t\t\titem_added.emit(item, amount)
\t\t\t\t\treturn true
\tfor slot in slots:
\t\tif slot.is_empty():
\t\t\tremaining = slot.add_item(item, remaining)
\t\t\tif remaining == 0:
\t\t\t\tinventory_changed.emit()
\t\t\t\titem_added.emit(item, amount)
\t\t\t\treturn true
\tif remaining < amount:
\t\tinventory_changed.emit()
\t\titem_added.emit(item, amount - remaining)
\telse:
\t\tinventory_full.emit()
\treturn remaining == 0

func add_item_by_id(item_id: String, amount: int = 1) -> bool:
\tif not ItemDatabase:
\t\treturn false
\tvar item = ItemDatabase.get_item(item_id)
\treturn add_item(item, amount) if item else false

func remove_item(item: InventoryItem, amount: int = 1) -> bool:
\tvar to_remove = amount
\tfor slot in slots:
\t\tif not slot.is_empty() and slot.item.id == item.id:
\t\t\tvar removed = slot.remove_item(to_remove)
\t\t\tto_remove -= removed
\t\t\tif to_remove == 0:
\t\t\t\tinventory_changed.emit()
\t\t\t\titem_removed.emit(item, amount)
\t\t\t\treturn true
\treturn to_remove == 0

func remove_item_by_id(item_id: String, amount: int = 1) -> bool:
\tif not ItemDatabase:
\t\treturn false
\tvar item = ItemDatabase.get_item(item_id)
\treturn remove_item(item, amount) if item else false

func has_item(item: InventoryItem, amount: int = 1) -> bool:
\treturn get_item_count(item) >= amount

func get_item_count(item: InventoryItem) -> int:
\tvar count = 0
\tfor slot in slots:
\t\tif not slot.is_empty() and slot.item.id == item.id:
\t\t\tcount += slot.quantity
\treturn count

func use_item(item: InventoryItem) -> bool:
\tif not has_item(item):
\t\treturn false
\titem_used.emit(item)
\tif item.is_consumable:
\t\tremove_item(item, 1)
\treturn true

func swap_slots(index_a: int, index_b: int) -> void:
\tif index_a < 0 or index_a >= slots.size() or index_b < 0 or index_b >= slots.size():
\t\treturn
\tvar temp_item = slots[index_a].item
\tvar temp_quantity = slots[index_a].quantity
\tslots[index_a].item = slots[index_b].item
\tslots[index_a].quantity = slots[index_b].quantity
\tslots[index_b].item = temp_item
\tslots[index_b].quantity = temp_quantity
\tinventory_changed.emit()

func clear_inventory() -> void:
\tfor slot in slots:
\t\tslot.clear()
\tinventory_changed.emit()

func save_inventory() -> void:
\tvar save_data = []
\tfor slot in slots:
\t\tsave_data.append(slot.get_data() if not slot.is_empty() else {})
\tvar file = FileAccess.open(save_path, FileAccess.WRITE)
\tif file:
\t\tfile.store_var(save_data)
\t\tfile.close()

func load_inventory() -> void:
\tif not FileAccess.file_exists(save_path) or not ItemDatabase:
\t\treturn
\tvar file = FileAccess.open(save_path, FileAccess.READ)
\tif file:
\t\tvar save_data = file.get_var()
\t\tfile.close()
\t\tclear_inventory()
\t\tfor i in range(min(save_data.size(), slots.size())):
\t\t\tvar slot_data = save_data[i]
\t\t\tif slot_data is Dictionary and slot_data.has("item_id"):
\t\t\t\tvar item = ItemDatabase.get_item(slot_data.item_id)
\t\t\t\tif item:
\t\t\t\t\tslots[i].add_item(item, slot_data.get("quantity", 1))
\t\tinventory_changed.emit()
"""

INVENTORY_UI_GD = """@tool
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
\tif Engine.is_editor_hint():
\t\treturn
\tif inventory == null:
\t\tinventory = InventoryManager.new()
\t\tadd_child(inventory)
\tsetup_grid()
\tinventory.inventory_changed.connect(_on_inventory_changed)
\tupdate_ui()

func setup_grid():
\tif grid == null:
\t\treturn
\tgrid.columns = columns
\tfor child in grid.get_children():
\t\tchild.queue_free()
\tslot_uis.clear()
\tfor i in range(inventory.size):
\t\tvar slot_ui = create_slot()
\t\tif slot_ui:
\t\t\tgrid.add_child(slot_ui)
\t\t\tslot_ui.index = i
\t\t\tslot_ui.inventory = inventory
\t\t\tslot_ui.custom_minimum_size = slot_size
\t\t\tslot_ui.slot_clicked.connect(_on_slot_clicked)
\t\t\tslot_ui.slot_right_clicked.connect(_on_slot_right_clicked)
\t\t\tslot_uis.append(slot_ui)

func create_slot() -> Control:
\treturn slot_scene.instantiate() if slot_scene else null

func _on_inventory_changed():
\tupdate_ui()

func update_ui():
\tfor i in range(min(slot_uis.size(), inventory.slots.size())):
\t\tslot_uis[i].update_slot(inventory.slots[i])

func _on_slot_clicked(slot_index: int, item: InventoryItem):
\titem_clicked.emit(item, slot_index)

func _on_slot_right_clicked(slot_index: int, item: InventoryItem):
\titem_right_clicked.emit(item, slot_index)
"""

INVENTORY_SLOT_UI_GD = """extends Panel

signal slot_clicked(slot_index: int, item: InventoryItem)
signal slot_right_clicked(slot_index: int, item: InventoryItem)

var index: int = -1
var inventory: InventoryManager

@onready var icon: TextureRect = $Icon
@onready var quantity_label: Label = $Quantity

static var dragged_slot: Panel = null
static var dragged_index: int = -1

func update_slot(slot: InventorySlot):
\tif not icon or not quantity_label:
\t\treturn
\tif slot.is_empty():
\t\ticon.texture = null
\t\tquantity_label.text = ""
\t\tmodulate = Color(1, 1, 1, 0.3)
\t\ttooltip_text = ""
\telse:
\t\ticon.texture = slot.item.icon
\t\tquantity_label.text = str(slot.quantity) if slot.quantity > 1 else ""
\t\tmodulate = Color.WHITE
\t\ttooltip_text = "%s\\n%s" % [slot.item.name, slot.item.description]

func _gui_input(event):
\tif event is InputEventMouseButton and event.pressed:
\t\tif event.button_index == MOUSE_BUTTON_LEFT:
\t\t\tif not inventory.slots[index].is_empty():
\t\t\t\tslot_clicked.emit(index, inventory.slots[index].item)
\t\telif event.button_index == MOUSE_BUTTON_RIGHT:
\t\t\tif not inventory.slots[index].is_empty():
\t\t\t\tslot_right_clicked.emit(index, inventory.slots[index].item)

func _get_drag_data(at_position):
\tif inventory.slots[index].is_empty():
\t\treturn null
\tdragged_slot = self
\tdragged_index = index
\tvar preview = Panel.new()
\tpreview.custom_minimum_size = size
\tvar preview_icon = TextureRect.new()
\tpreview_icon.texture = icon.texture
\tpreview_icon.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
\tpreview_icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
\tpreview.add_child(preview_icon)
\tpreview_icon.size = size
\tset_drag_preview(preview)
\treturn {"index": index}

func _can_drop_data(at_position, data):
\treturn data is Dictionary and data.has("index")

func _drop_data(at_position, data):
\tif data.has("index"):
\t\tinventory.swap_slots(data.index, index)
"""

ITEM_DATABASE_GD = """extends Node

signal database_loaded

var items: Dictionary = {}

@export var items_folder: String = "res://addons/inventory_system/demo/demo_items/"
@export var auto_load_on_ready: bool = true

func _ready():
\tif auto_load_on_ready:
\t\tawait get_tree().process_frame
\t\tload_all_items()

func load_all_items() -> void:
\tprint("🗄️ ItemDatabase: Cargando items desde: ", items_folder)
\titems.clear()
\tif not DirAccess.dir_exists_absolute(items_folder):
\t\tDirAccess.make_dir_recursive_absolute(items_folder)
\t\treturn
\tvar loaded_count = 0
\tvar dir = DirAccess.open(items_folder)
\tif dir:
\t\tdir.list_dir_begin()
\t\tvar file_name = dir.get_next()
\t\twhile file_name != "":
\t\t\tif not file_name.begins_with(".") and file_name.ends_with(".tres"):
\t\t\t\tvar item = load(items_folder + file_name)
\t\t\t\tif item is InventoryItem and not item.id.is_empty():
\t\t\t\t\titems[item.id] = item
\t\t\t\t\tloaded_count += 1
\t\t\tfile_name = dir.get_next()
\t\tdir.list_dir_end()
\t\tprint("✓ ItemDatabase: %d items cargados" % loaded_count)
\t\tdatabase_loaded.emit()

func get_item(item_id: String) -> InventoryItem:
\treturn items.get(item_id, null)

func has_item(item_id: String) -> bool:
\treturn items.has(item_id)

func get_all_items() -> Array[InventoryItem]:
\tvar result: Array[InventoryItem] = []
\tfor item in items.values():
\t\tresult.append(item)
\treturn result

func get_item_count() -> int:
\treturn items.size()

func get_items_by_type(type: InventoryItem.ItemType) -> Array[InventoryItem]:
\tvar result: Array[InventoryItem] = []
\tfor item in items.values():
\t\tif item.item_type == type:
\t\t\tresult.append(item)
\treturn result

func search_items(query: String) -> Array[InventoryItem]:
\tvar result: Array[InventoryItem] = []
\tvar query_lower = query.to_lower()
\tfor item in items.values():
\t\tif query_lower in item.name.to_lower():
\t\t\tresult.append(item)
\treturn result

func print_database_info() -> void:
\tprint("\\n" + "=" * 50)
\tprint("📊 ItemDatabase Info")
\tprint("=" * 50)
\tprint("Total items: ", items.size())
\tfor type in InventoryItem.ItemType.values():
\t\tvar type_name = InventoryItem.ItemType.keys()[type]
\t\tvar count = get_items_by_type(type).size()
\t\tprint("  %s: %d" % [type_name, count])
\tprint("=" * 50 + "\\n")
"""

INVENTORY_SLOT_UI_TSCN = """[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://addons/inventory_system/scripts/inventory_slot_ui.gd" id="1"]

[node name="InventorySlotUI" type="Panel"]
custom_minimum_size = Vector2(64, 64)
script = ExtResource("1")

[node name="Icon" type="TextureRect" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
expand_mode = 1
stretch_mode = 5

[node name="Quantity" type="Label" parent="."]
layout_mode = 1
anchors_preset = 3
anchor_left = 1.0
anchor_top = 1.0
anchor_right = 1.0
anchor_bottom = 1.0
offset_left = -40.0
offset_top = -23.0
grow_horizontal = 0
grow_vertical = 0
theme_override_colors/font_outline_color = Color(0, 0, 0, 1)
theme_override_constants/outline_size = 4
text = "99"
horizontal_alignment = 2
vertical_alignment = 2
"""

INVENTORY_UI_TSCN = """[gd_scene load_steps=3 format=3]

[ext_resource type="Script" path="res://addons/inventory_system/scripts/inventory_ui.gd" id="1"]
[ext_resource type="PackedScene" path="res://addons/inventory_system/scenes/inventory_slot_ui.tscn" id="2"]

[node name="InventoryUI" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
script = ExtResource("1")
slot_scene = ExtResource("2")

[node name="Panel" type="Panel" parent="."]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -180.0
offset_top = -140.0
offset_right = 180.0
offset_bottom = 140.0
grow_horizontal = 2
grow_vertical = 2

[node name="MarginContainer" type="MarginContainer" parent="Panel"]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
theme_override_constants/margin_left = 10
theme_override_constants/margin_top = 10
theme_override_constants/margin_right = 10
theme_override_constants/margin_bottom = 10

[node name="GridContainer" type="GridContainer" parent="Panel/MarginContainer"]
layout_mode = 2
theme_override_constants/h_separation = 4
theme_override_constants/v_separation = 4
columns = 5
"""

DEMO_GD = """extends Node2D

@onready var inventory_ui: InventoryUI = $InventoryUI
@onready var inventory: InventoryManager = $InventoryUI.inventory
@onready var info_label: Label = $InfoLabel

func _ready():
\tif ItemDatabase.get_item_count() == 0:
\t\tItemDatabase.database_loaded.connect(_on_database_loaded)
\telse:
\t\t_on_database_loaded()
\tinventory.item_added.connect(_on_item_added)
\tinventory.item_removed.connect(_on_item_removed)
\tinventory.item_used.connect(_on_item_used)
\tinventory_ui.item_clicked.connect(_on_item_clicked)
\tinventory_ui.item_right_clicked.connect(_on_item_right_clicked)
\tinventory_ui.visible = false
\tprint("🎮 DEMO DE INVENTARIO")
\tprint("Presiona ESC para abrir/cerrar")

func _on_database_loaded():
\tprint("✓ Base de datos cargada")
\tif ItemDatabase.has_item("potion_health"):
\t\tinventory.add_item_by_id("potion_health", 5)
\tif ItemDatabase.has_item("sword_iron"):
\t\tinventory.add_item_by_id("sword_iron", 1)
\tif ItemDatabase.has_item("bread"):
\t\tinventory.add_item_by_id("bread", 10)
\tif ItemDatabase.has_item("gold_coin"):
\t\tinventory.add_item_by_id("gold_coin", 50)

func _input(event):
\tif event.is_action_pressed("ui_cancel"):
\t\tinventory_ui.visible = !inventory_ui.visible
\t\tget_viewport().set_input_as_handled()

func _on_item_added(item: InventoryItem, amount: int):
\tshow_info("✓ Agregado: %d x %s" % [amount, item.name])

func _on_item_removed(item: InventoryItem, amount: int):
\tshow_info("✗ Removido: %d x %s" % [amount, item.name])

func _on_item_used(item: InventoryItem):
\tshow_info("⚡ Usando: %s" % item.name)

func _on_item_clicked(item: InventoryItem, slot_index: int):
\tif item.is_usable:
\t\tinventory.use_item(item)

func _on_item_right_clicked(item: InventoryItem, slot_index: int):
\tinventory.remove_item(item, 1)

func show_info(text: String):
\tinfo_label.text = text
\tprint(text)
"""

DEMO_TSCN = """[gd_scene load_steps=3 format=3]

[ext_resource type="Script" path="res://addons/inventory_system/demo/demo.gd" id="1"]
[ext_resource type="PackedScene" path="res://addons/inventory_system/scenes/inventory_ui.tscn" id="2"]

[node name="Demo" type="Node2D"]
script = ExtResource("1")

[node name="InventoryUI" parent="." instance=ExtResource("2")]

[node name="InfoLabel" type="Label" parent="."]
offset_left = 20.0
offset_top = 20.0
offset_right = 500.0
offset_bottom = 60.0
theme_override_colors/font_color = Color(0.2, 1, 0.3, 1)
theme_override_colors/font_outline_color = Color(0, 0, 0, 1)
theme_override_constants/outline_size = 4
theme_override_font_sizes/font_size = 20
text = "Presiona ESC para abrir inventario"

[node name="Instructions" type="Label" parent="."]
offset_left = 20.0
offset_top = 70.0
offset_right = 500.0
offset_bottom = 200.0
theme_override_colors/font_outline_color = Color(0, 0, 0, 1)
theme_override_constants/outline_size = 2
text = "CONTROLES:
ESC: Abrir/Cerrar
Click Izquierdo: Usar
Click Derecho: Soltar 1
Arrastra: Reorganizar"
"""

POTION_TRES = """[gd_resource type="Resource" script_class="InventoryItem" load_steps=2 format=3]

[ext_resource type="Script" path="res://addons/inventory_system/scripts/item.gd" id="1"]

[resource]
script = ExtResource("1")
id = "potion_health"
name = "Poción de Vida"
description = "Restaura 50 HP"
item_type = 0
is_stackable = true
max_stack = 99
is_usable = true
is_consumable = true
custom_data = {"heal_amount": 50}
"""

SWORD_TRES = """[gd_resource type="Resource" script_class="InventoryItem" load_steps=2 format=3]

[ext_resource type="Script" path="res://addons/inventory_system/scripts/item.gd" id="1"]

[resource]
script = ExtResource("1")
id = "sword_iron"
name = "Espada de Hierro"
description = "Una espada común"
item_type = 1
is_stackable = false
max_stack = 1
is_usable = true
is_consumable = false
custom_data = {"damage": 15}
"""

BREAD_TRES = """[gd_resource type="Resource" script_class="InventoryItem" load_steps=2 format=3]

[ext_resource type="Script" path="res://addons/inventory_system/scripts/item.gd" id="1"]

[resource]
script = ExtResource("1")
id = "bread"
name = "Pan"
description = "Pan fresco"
item_type = 0
is_stackable = true
max_stack = 50
is_usable = true
is_consumable = true
custom_data = {"hunger_restore": 30}
"""

GOLD_TRES = """[gd_resource type="Resource" script_class="InventoryItem" load_steps=2 format=3]

[ext_resource type="Script" path="res://addons/inventory_system/scripts/item.gd" id="1"]

[resource]
script = ExtResource("1")
id = "gold_coin"
name = "Moneda de Oro"
description = "Una moneda brillante"
item_type = 4
is_stackable = true
max_stack = 999
is_usable = false
is_consumable = false
custom_data = {"value": 1}
"""

README_MD = """# 📦 Sistema de Inventario para Godot 4.5

## 🚀 Inicio Rápido

### 1. Activar Plugin
- **Proyecto > Configuración del Proyecto > Plugins**
- Activar **"Inventory System"** ✓

### 2. Configurar ItemDatabase (IMPORTANTE)
- **Proyecto > Configuración del Proyecto > Autoload**
- Path: `res://addons/inventory_system/scripts/item_database.gd`
- Name: `ItemDatabase`
- Click "Agregar"

### 3. Usar en tu juego

```gdscript
extends Node2D

@onready var inventory = $InventoryUI.inventory

func _ready():
    inventory.add_item_by_id("potion_health", 5)
    inventory.item_used.connect(func(item):
        print("Usaste: ", item.name)
    )

func _input(event):
    if event.is_action_pressed("ui_cancel"):
        $InventoryUI.visible = !$InventoryUI.visible
```

## 📚 API Principal

### Inventario
```gdscript
inventory.add_item_by_id("item_id", cantidad)
inventory.remove_item_by_id("item_id", cantidad)
inventory.use_item_by_id("item_id")
if inventory.has_item(item, 3):
    print("Tienes al menos 3")
```

### ItemDatabase
```gdscript
var item = ItemDatabase.get_item("item_id")
var consumables = ItemDatabase.get_items_by_type(InventoryItem.ItemType.CONSUMABLE)
var results = ItemDatabase.search_items("poción")
ItemDatabase.print_database_info()
```

## 🎮 Controles

- **ESC**: Abrir/Cerrar
- **Click Izquierdo**: Usar item
- **Click Derecho**: Soltar 1
- **Arrastrar**: Reorganizar

## 📦 Crear Items

1. Click derecho > **Nuevo Recurso**
2. Buscar **"InventoryItem"**
3. Configurar ID, nombre, icono
4. Guardar en `items/mi_item.tres`

## 🎯 Demo

Ejecuta: `addons/inventory_system/demo/demo.tscn`
"""

QUICK_START_MD = """# 🚀 Guía Rápida

## Paso 1: Activar Plugin
Proyecto > Plugins > Activar "Inventory System"

## Paso 2: Configurar Autoload (CRÍTICO)
Proyecto > Autoload > Agregar:
- Path: `addons/inventory_system/scripts/item_database.gd`
- Name: `ItemDatabase`

## Paso 3: Agregar a tu escena
Agrega nodo **InventoryUI**

## Paso 4: Script básico
```gdscript
extends Node2D

@onready var inventory = $InventoryUI.inventory

func _ready():
    inventory.add_item_by_id("potion_health", 5)
    $InventoryUI.visible = false

func _input(event):
    if event.is_action_pressed("ui_cancel"):
        $InventoryUI.visible = !$InventoryUI.visible
```

## Paso 5: Crear tus items
1. Nuevo Recurso > InventoryItem
2. Configurar ID, nombre, icono
3. Guardar en `items/`

¡Listo! 🎉
"""

AUTOLOAD_SETUP_MD = """# 🔧 Configurar ItemDatabase

## Paso Crítico

Para que el sistema funcione, DEBES configurar ItemDatabase como Autoload.

## Pasos:

1. **Proyecto > Configuración del Proyecto > Autoload**

2. Click en **+**

3. Configurar:
   - **Path**: `res://addons/inventory_system/scripts/item_database.gd`
   - **Name**: `ItemDatabase`
   - **Activado**: ✓

4. Click **"Agregar"**

## Verificar

En cualquier script:
```gdscript
func _ready():
    print(ItemDatabase.get_item_count())
```

Si ves el número de items, funciona correctamente.

## Carpeta de Items

Por defecto: `res://addons/inventory_system/demo/demo_items/`

Para cambiar:
1. Selecciona ItemDatabase en Autoload
2. En Inspector: `Items Folder` = `"res://items/"`

## Problemas

**"ItemDatabase no encontrado"**
→ No está en Autoload

**"0 items cargados"**
→ Verifica la carpeta de items
→ Items deben tener ID configurado
"""

if __name__ == "__main__":
    generator = InventoryGenerator()
    success = generator.generate()
    sys.exit(0 if success else 1)