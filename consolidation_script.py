#!/usr/bin/env python3
"""
Script de consolidación automática del sistema de inventario
Uso: python consolidate_inventory.py
"""

import os
import shutil
from pathlib import Path

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.RESET} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.RESET} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {text}")

# Archivos a eliminar
FILES_TO_DELETE = [
    "addons/inventory_system/scripts/inventory_slot_ui.gd",
    "addons/inventory_system/scripts/inventory_slot_ui.gd.uid",
    "addons/inventory_system/scripts/inventory_ui.gd",
    "addons/inventory_system/scripts/inventory_ui.gd.uid",
    "addons/inventory_system/scripts/hotbar_slot_ui.gd",
    "addons/inventory_system/scripts/hotbar_slot_ui.gd.uid",
    "addons/inventory_system/scripts/hotbar_ui.gd",
    "addons/inventory_system/scripts/hotbar_ui.gd.uid",
    "addons/inventory_system/scripts/crafting_manager.gd",
    "addons/inventory_system/scripts/crafting_manager.gd.uid",
    "addons/inventory_system/scripts/crafting_table_ui.gd",
    "addons/inventory_system/scripts/crafting_table_ui.gd.uid",
]

# Contenido de los archivos consolidados
INVENTORY_UI_SYSTEM = '''@tool
class_name InventoryUI
extends Control

## Clase interna: InventorySlotUI
class InventorySlotUI extends Panel:
\tsignal slot_clicked(slot_index: int, item: InventoryItem)
\tsignal slot_right_clicked(slot_index: int, item: InventoryItem)
\t
\tvar index: int = -1
\tvar inventory: InventoryManager
\tvar icon: TextureRect
\tvar quantity_label: Label
\tvar _last_item_id: String = ""
\tvar _last_quantity: int = 0
\t
\tfunc _ready():
\t\t_create_ui()
\t
\tfunc _create_ui():
\t\ticon = TextureRect.new()
\t\ticon.name = "Icon"
\t\ticon.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
\t\ticon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
\t\tadd_child(icon)
\t\ticon.set_anchors_preset(Control.PRESET_FULL_RECT)
\t\t
\t\tquantity_label = Label.new()
\t\tquantity_label.name = "Quantity"
\t\tquantity_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
\t\tquantity_label.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
\t\tadd_child(quantity_label)
\t\tquantity_label.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
\t
\tfunc update_slot(slot: InventorySlot):
\t\tif not icon or not quantity_label:
\t\t\treturn
\t\t
\t\tif slot.is_empty():
\t\t\ticon.texture = null
\t\t\tquantity_label.text = ""
\t\t\tmodulate = Color(1, 1, 1, 0.3)
\t\t\ttooltip_text = ""
\t\t\t_last_item_id = ""
\t\t\t_last_quantity = 0
\t\telse:
\t\t\ticon.texture = slot.item.icon
\t\t\tquantity_label.text = str(slot.quantity) if slot.quantity > 1 else ""
\t\t\tmodulate = Color.WHITE
\t\t\t
\t\t\tif _last_item_id != slot.item.id or _last_quantity != slot.quantity:
\t\t\t\ttooltip_text = _generate_tooltip(slot)
\t\t\t\t_last_item_id = slot.item.id
\t\t\t\t_last_quantity = slot.quantity
\t
\tfunc _generate_tooltip(slot: InventorySlot) -> String:
\t\tvar tooltip = "%s\\n%s" % [slot.item.name, slot.item.description]
\t\t
\t\tif slot.item.is_usable:
\t\t\ttooltip += "\\n[Click Izq] Usar"
\t\tif slot.quantity > 1:
\t\t\ttooltip += "\\n[Click Der] Soltar 1"
\t\ttooltip += "\\n[Shift+Click] Mover rápido"
\t\t
\t\treturn tooltip
\t
\tfunc _gui_input(event):
\t\tif not inventory or index < 0 or index >= inventory.slots.size():
\t\t\treturn
\t\t
\t\tif event is InputEventMouseButton and event.pressed:
\t\t\tmatch event.button_index:
\t\t\t\tMOUSE_BUTTON_LEFT:
\t\t\t\t\tif event.shift_pressed:
\t\t\t\t\t\t_quick_move_item()
\t\t\t\t\telse:
\t\t\t\t\t\tif not inventory.slots[index].is_empty():
\t\t\t\t\t\t\tslot_clicked.emit(index, inventory.slots[index].item)
\t\t\t\tMOUSE_BUTTON_RIGHT:
\t\t\t\t\tif not inventory.slots[index].is_empty():
\t\t\t\t\t\tslot_right_clicked.emit(index, inventory.slots[index].item)
\t
\tfunc _quick_move_item():
\t\tvar slot = inventory.slots[index]
\t\tif slot.is_empty():
\t\t\treturn
\t\t
\t\tvar target_start = 9 if index < 9 else 0
\t\tvar target_end = 36 if index < 9 else 9
\t\t
\t\tfor i in range(target_start, target_end):
\t\t\tif i >= inventory.slots.size():
\t\t\t\tbreak
\t\t\t
\t\t\tif inventory.slots[i].is_empty():
\t\t\t\tinventory.slots[i].add_item(slot.item, slot.quantity)
\t\t\t\tslot.clear()
\t\t\t\tbreak
\t\t\telif inventory.slots[i].item.id == slot.item.id and inventory.slots[i].item.is_stackable:
\t\t\t\tvar remaining = inventory.slots[i].add_item(slot.item, slot.quantity)
\t\t\t\tif remaining == 0:
\t\t\t\t\tslot.clear()
\t\t\t\t\tbreak
\t\t\t\telse:
\t\t\t\t\tslot.quantity = remaining
\t\t
\t\tinventory.inventory_changed.emit()
\t
\tfunc _get_drag_data(at_position):
\t\tif not inventory or index < 0 or index >= inventory.slots.size():
\t\t\treturn null
\t\t
\t\tif inventory.slots[index].is_empty():
\t\t\treturn null
\t\t
\t\tvar preview = Panel.new()
\t\tpreview.custom_minimum_size = size
\t\t
\t\tvar preview_icon = TextureRect.new()
\t\tpreview_icon.texture = icon.texture
\t\tpreview_icon.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
\t\tpreview_icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
\t\tpreview.add_child(preview_icon)
\t\tpreview_icon.size = size
\t\t
\t\tset_drag_preview(preview)
\t\t
\t\treturn {"index": index, "source": self}
\t
\tfunc _can_drop_data(at_position, data):
\t\tif not data is Dictionary or not data.has("index"):
\t\t\treturn false
\t\tif data.get("source") == self:
\t\t\treturn false
\t\treturn true
\t
\tfunc _drop_data(at_position, data):
\t\tif not inventory:
\t\t\treturn
\t\tif data.has("index"):
\t\t\tinventory.swap_slots(data.index, index)

## Clase principal: InventoryUI
signal item_clicked(item: InventoryItem, slot_index: int)
signal item_right_clicked(item: InventoryItem, slot_index: int)

@export var inventory: InventoryManager
@export var columns: int = 5
@export var slot_size: Vector2 = Vector2(64, 64)

var grid: GridContainer
var slot_uis: Array = []

func _ready():
\tif Engine.is_editor_hint():
\t\treturn
\t
\tif not has_node("Panel"):
\t\t_create_structure()
\t
\tgrid = $Panel/MarginContainer/GridContainer
\t
\tif inventory == null:
\t\tinventory = InventoryManager.new()
\t\tadd_child(inventory)
\t
\tsetup_grid()
\tinventory.inventory_changed.connect(_on_inventory_changed)
\tupdate_ui()

func _create_structure():
\tvar panel = Panel.new()
\tpanel.name = "Panel"
\tadd_child(panel)
\tpanel.set_anchors_preset(Control.PRESET_FULL_RECT)
\t
\tvar margin = MarginContainer.new()
\tmargin.name = "MarginContainer"
\tpanel.add_child(margin)
\tmargin.set_anchors_preset(Control.PRESET_FULL_RECT)
\tmargin.add_theme_constant_override("margin_left", 10)
\tmargin.add_theme_constant_override("margin_right", 10)
\tmargin.add_theme_constant_override("margin_top", 10)
\tmargin.add_theme_constant_override("margin_bottom", 10)
\t
\tvar grid_container = GridContainer.new()
\tgrid_container.name = "GridContainer"
\tmargin.add_child(grid_container)

func setup_grid():
\tif grid == null:
\t\treturn
\t
\tgrid.columns = columns
\tfor child in grid.get_children():
\t\tchild.queue_free()
\tslot_uis.clear()
\t
\tfor i in range(inventory.size):
\t\tvar slot_ui = InventorySlotUI.new()
\t\tgrid.add_child(slot_ui)
\t\tslot_ui.index = i
\t\tslot_ui.inventory = inventory
\t\tslot_ui.custom_minimum_size = slot_size
\t\tslot_ui.slot_clicked.connect(_on_slot_clicked)
\t\tslot_ui.slot_right_clicked.connect(_on_slot_right_clicked)
\t\tslot_uis.append(slot_ui)

func _on_inventory_changed():
\tupdate_ui()

func update_ui():
\tfor i in range(min(slot_uis.size(), inventory.slots.size())):
\t\tslot_uis[i].update_slot(inventory.slots[i])

func _on_slot_clicked(slot_index: int, item: InventoryItem):
\titem_clicked.emit(item, slot_index)

func _on_slot_right_clicked(slot_index: int, item: InventoryItem):
\titem_right_clicked.emit(item, slot_index)
'''

HOTBAR_UI_SYSTEM = '''@tool
class_name HotbarUI
extends Control

## Clase interna: HotbarSlotUI
class HotbarSlotUI extends Panel:
\tvar slot_index: int = -1
\tvar is_selected: bool = false
\tvar hotbar: Hotbar
\tvar inventory: InventoryManager
\tvar icon: TextureRect
\tvar quantity_label: Label
\tvar key_label: Label
\tvar selection_indicator: Panel
\t
\tfunc _ready():
\t\t_create_ui()
\t\tupdate_key_label()
\t
\tfunc _create_ui():
\t\ticon = TextureRect.new()
\t\ticon.name = "Icon"
\t\ticon.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
\t\ticon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
\t\tadd_child(icon)
\t\ticon.set_anchors_preset(Control.PRESET_FULL_RECT)
\t\t
\t\tquantity_label = Label.new()
\t\tquantity_label.name = "Quantity"
\t\tquantity_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
\t\tquantity_label.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
\t\tadd_child(quantity_label)
\t\tquantity_label.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
\t\t
\t\tkey_label = Label.new()
\t\tkey_label.name = "KeyLabel"
\t\tkey_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
\t\tkey_label.vertical_alignment = VERTICAL_ALIGNMENT_TOP
\t\tadd_child(key_label)
\t\tkey_label.set_anchors_preset(Control.PRESET_TOP_LEFT)
\t\t
\t\tselection_indicator = Panel.new()
\t\tselection_indicator.name = "SelectionIndicator"
\t\tselection_indicator.visible = false
\t\tselection_indicator.mouse_filter = Control.MOUSE_FILTER_IGNORE
\t\tadd_child(selection_indicator)
\t\tselection_indicator.set_anchors_preset(Control.PRESET_FULL_RECT)
\t
\tfunc setup(index: int, hotbar_ref: Hotbar):
\t\tslot_index = index
\t\thotbar = hotbar_ref
\t\tinventory = hotbar.inventory
\t\tupdate_key_label()
\t
\tfunc update_slot():
\t\tif not inventory or not hotbar:
\t\t\treturn
\t\t
\t\tvar item = hotbar.get_item_at_slot(slot_index)
\t\tvar quantity = hotbar.get_quantity_at_slot(slot_index)
\t\t
\t\tif item == null:
\t\t\ticon.texture = null
\t\t\tquantity_label.text = ""
\t\t\tmodulate = Color(1, 1, 1, 0.5)
\t\t\ttooltip_text = ""
\t\telse:
\t\t\ticon.texture = item.icon
\t\t\tquantity_label.text = str(quantity) if quantity > 1 else ""
\t\t\tmodulate = Color.WHITE
\t\t\ttooltip_text = "%s\\n%s\\n%s" % [
\t\t\t\titem.name,
\t\t\t\titem.description,
\t\t\t\t"[%s] para usar" % (slot_index + 1) if slot_index < 9 else ""
\t\t\t]
\t\t
\t\tupdate_selection()
\t
\tfunc update_selection():
\t\tif selection_indicator:
\t\t\tselection_indicator.visible = is_selected
\t
\tfunc set_selected(selected: bool):
\t\tis_selected = selected
\t\tupdate_selection()
\t
\tfunc update_key_label():
\t\tif key_label and slot_index >= 0:
\t\t\tif slot_index < 9:
\t\t\t\tkey_label.text = str(slot_index + 1)
\t\t\telse:
\t\t\t\tkey_label.text = ""
\t
\tfunc _gui_input(event):
\t\tif event is InputEventMouseButton and event.pressed:
\t\t\tif event.button_index == MOUSE_BUTTON_LEFT:
\t\t\t\tif hotbar:
\t\t\t\t\thotbar.select_slot(slot_index)
\t\t\t\t\tif hotbar.auto_use_on_select:
\t\t\t\t\t\treturn
\t\t\t\t\tif is_selected:
\t\t\t\t\t\thotbar.use_selected_item()
\t\t\telif event.button_index == MOUSE_BUTTON_RIGHT:
\t\t\t\tif hotbar:
\t\t\t\t\thotbar.use_item_at_slot(slot_index)

## Clase principal: HotbarUI
@export var hotbar: Hotbar
@export var inventory: InventoryManager
@export var slot_size: Vector2 = Vector2(64, 64)
@export var spacing: int = 4

var container: HBoxContainer
var slot_uis: Array = []

func _ready():
\tif Engine.is_editor_hint():
\t\treturn
\t
\tif not has_node("Container"):
\t\t_create_structure()
\t
\tcontainer = $Container
\t
\tif hotbar == null:
\t\thotbar = Hotbar.new()
\t\tadd_child(hotbar)
\t
\tif inventory:
\t\thotbar.inventory = inventory
\telif get_parent().has_node("InventoryUI"):
\t\tvar inv_ui = get_parent().get_node("InventoryUI")
\t\tif inv_ui.inventory:
\t\t\thotbar.inventory = inv_ui.inventory
\t\t\tinventory = inv_ui.inventory
\t
\tsetup_hotbar()
\t
\tif hotbar:
\t\thotbar.slot_selected.connect(_on_slot_selected)
\t\thotbar.item_used_from_hotbar.connect(_on_item_used)
\t
\tif inventory:
\t\tinventory.inventory_changed.connect(_on_inventory_changed)
\t
\tupdate_ui()

func _create_structure():
\tvar hbox = HBoxContainer.new()
\thbox.name = "Container"
\tadd_child(hbox)
\thbox.set_anchors_preset(Control.PRESET_CENTER)

func setup_hotbar():
\tif not container:
\t\treturn
\t
\tfor child in container.get_children():
\t\tchild.queue_free()
\tslot_uis.clear()
\t
\tfor i in range(hotbar.hotbar_size):
\t\tvar slot_ui = HotbarSlotUI.new()
\t\tcontainer.add_child(slot_ui)
\t\tslot_ui.setup(i, hotbar)
\t\tslot_ui.custom_minimum_size = slot_size
\t\tslot_uis.append(slot_ui)
\t
\tif container:
\t\tcontainer.add_theme_constant_override("separation", spacing)

func _on_inventory_changed():
\tupdate_ui()

func _on_slot_selected(index: int, item: InventoryItem):
\tupdate_selection(index)

func _on_item_used(item: InventoryItem):
\tpass

func update_ui():
\tfor i in range(slot_uis.size()):
\t\tslot_uis[i].update_slot()

func update_selection(selected_index: int):
\tfor i in range(slot_uis.size()):
\t\tslot_uis[i].set_selected(i == selected_index)

func get_selected_slot_index() -> int:
\treturn hotbar.selected_slot if hotbar else 0

func get_selected_item() -> InventoryItem:
\treturn hotbar.get_selected_item() if hotbar else null
'''

CRAFTING_SYSTEM = '''class_name CraftingSystem
extends Node

## Clase CraftingManager
class Manager extends Node:
\tsignal recipe_found(recipe: CraftingRecipe)
\tsignal crafted(item: InventoryItem, quantity: int)
\t
\tvar recipes: Array[CraftingRecipe] = []
\t
\tfunc _ready():
\t\tload_recipes()
\t
\tfunc load_recipes():
\t\tvar recipes_path = "res://recipes/"
\t\tif not DirAccess.dir_exists_absolute(recipes_path):
\t\t\tDirAccess.make_dir_recursive_absolute(recipes_path)
\t\t\tprint("⚠️ Carpeta recipes/ vacía")
\t\t\treturn
\t\t
\t\tvar dir = DirAccess.open(recipes_path)
\t\tif dir:
\t\t\tdir.list_dir_begin()
\t\t\tvar file_name = dir.get_next()
\t\t\t
\t\t\twhile file_name != "":
\t\t\t\tif file_name.ends_with(".tres"):
\t\t\t\t\tvar recipe = load(recipes_path + file_name)
\t\t\t\t\tif recipe is CraftingRecipe:
\t\t\t\t\t\trecipes.append(recipe)
\t\t\t\tfile_name = dir.get_next()
\t\t\t
\t\t\tdir.list_dir_end()
\t\t
\t\tprint("✓ CraftingManager: %d recetas cargadas" % recipes.size())
\t
\tfunc find_recipe(grid_slots: Array[InventorySlot]) -> CraftingRecipe:
\t\tvar grid_ids: Array[String] = []
\t\t
\t\tfor slot in grid_slots:
\t\t\tif slot.is_empty():
\t\t\t\tgrid_ids.append("")
\t\t\telse:
\t\t\t\tgrid_ids.append(slot.item.id)
\t\t
\t\tfor recipe in recipes:
\t\t\tif recipe.matches(grid_ids):
\t\t\t\trecipe_found.emit(recipe)
\t\t\t\treturn recipe
\t\t
\t\treturn null
\t
\tfunc can_craft(recipe: CraftingRecipe, grid_slots: Array[InventorySlot]) -> bool:
\t\tif recipe == null:
\t\t\treturn false
\t\t
\t\tfor i in range(grid_slots.size()):
\t\t\tvar required_id = recipe.pattern[i]
\t\t\tvar slot = grid_slots[i]
\t\t\t
\t\t\tif required_id == "" and not slot.is_empty():
\t\t\t\tif not recipe.shapeless:
\t\t\t\t\treturn false
\t\t\telif required_id != "" and (slot.is_empty() or slot.item.id != required_id):
\t\t\t\treturn false
\t\t
\t\treturn true
\t
\tfunc craft(recipe: CraftingRecipe, grid_slots: Array[InventorySlot], inventory: InventoryManager) -> bool:
\t\tif not can_craft(recipe, grid_slots):
\t\t\treturn false
\t\t
\t\tfor i in range(grid_slots.size()):
\t\t\tif recipe.pattern[i] != "":
\t\t\t\tgrid_slots[i].remove_item(1)
\t\t
\t\tvar result_item = ItemDatabase.get_item(recipe.result_item_id)
\t\tif result_item:
\t\t\tinventory.add_item(result_item, recipe.result_quantity)
\t\t\tcrafted.emit(result_item, recipe.result_quantity)
\t\t\treturn true
\t\t
\t\treturn false

## Clase CraftingTableUI
class TableUI extends Control:
\tsignal closed
\t
\t@export var inventory_ui: Control
\t
\tvar crafting_grid: GridContainer
\tvar result_slot: Panel
\tvar crafting_manager: Manager
\tvar crafting_slots: Array[InventorySlot] = []
\tvar result_item: InventoryItem = null
\tvar result_quantity: int = 0
\tvar current_recipe: CraftingRecipe = null
\tvar held_item: InventoryItem = null
\tvar held_quantity: int = 0
\tvar cursor_preview: Control = null
\t
\tfunc _ready():
\t\tcrafting_manager = Manager.new()
\t\tadd_child(crafting_manager)
\t\t
\t\tinitialize_crafting_grid()
\t\tsetup_cursor_preview()
\t\t
\t\tcrafting_manager.recipe_found.connect(_on_recipe_found)
\t
\tfunc initialize_crafting_grid():
\t\tfor i in range(9):
\t\t\tvar slot = InventorySlot.new()
\t\t\tcrafting_slots.append(slot)
\t
\tfunc setup_cursor_preview():
\t\tcursor_preview = Panel.new()
\t\tcursor_preview.custom_minimum_size = Vector2(64, 64)
\t\tcursor_preview.mouse_filter = Control.MOUSE_FILTER_IGNORE
\t\tcursor_preview.z_index = 100
\t\t
\t\tvar icon = TextureRect.new()
\t\ticon.name = "Icon"
\t\ticon.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
\t\ticon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
\t\ticon.mouse_filter = Control.MOUSE_FILTER_IGNORE
\t\tcursor_preview.add_child(icon)
\t\ticon.set_anchors_preset(Control.PRESET_FULL_RECT)
\t\t
\t\tvar qty = Label.new()
\t\tqty.name = "Quantity"
\t\tqty.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
\t\tqty.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
\t\tcursor_preview.add_child(qty)
\t\tqty.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
\t\t
\t\tadd_child(cursor_preview)
\t\tcursor_preview.visible = false
\t
\tfunc _process(_delta):
\t\tif held_item:
\t\t\tcursor_preview.global_position = get_global_mouse_position() - cursor_preview.size / 2
\t\t\tcursor_preview.visible = true
\t\t\tcursor_preview.get_node("Icon").texture = held_item.icon
\t\t\tcursor_preview.get_node("Quantity").text = str(held_quantity) if held_quantity > 1 else ""
\t\telse:
\t\t\tcursor_preview.visible = false
\t
\tfunc check_recipe():
\t\tcurrent_recipe = crafting_manager.find_recipe(crafting_slots)
\t\t
\t\tif current_recipe:
\t\t\tresult_item = ItemDatabase.get_item(current_recipe.result_item_id)
\t\t\tresult_quantity = current_recipe.result_quantity
\t\t\tupdate_result_slot()
\t\telse:
\t\t\tresult_item = null
\t\t\tresult_quantity = 0
\t\t\tclear_result_slot()
\t
\tfunc update_result_slot():
\t\tif result_item and result_slot:
\t\t\tresult_slot.get_node("Icon").texture = result_item.icon
\t\t\tresult_slot.get_node("Quantity").text = str(result_quantity) if result_quantity > 1 else ""
\t\t\tresult_slot.modulate = Color.WHITE
\t
\tfunc clear_result_slot():
\t\tif result_slot:
\t\t\tresult_slot.get_node("Icon").texture = null
\t\t\tresult_slot.get_node("Quantity").text = ""
\t\t\tresult_slot.modulate = Color(1, 1, 1, 0.3)
\t
\tfunc _on_recipe_found(recipe: CraftingRecipe):
\t\tprint("✓ Receta: %s" % recipe.result_item_id)
\t
\tfunc _input(event):
\t\tif event.is_action_pressed("ui_cancel"):
\t\t\tclose_crafting_table()
\t\t\tget_viewport().set_input_as_handled()
\t
\tfunc close_crafting_table():
\t\tfor slot in crafting_slots:
\t\t\tif not slot.is_empty() and inventory_ui and inventory_ui.inventory:
\t\t\t\tinventory_ui.inventory.add_item(slot.item, slot.quantity)
\t\t\t\tslot.clear()
\t\t
\t\tif held_item and inventory_ui and inventory_ui.inventory:
\t\t\tinventory_ui.inventory.add_item(held_item, held_quantity)
\t\t\theld_item = null
\t\t\theld_quantity = 0
\t\t
\t\tclosed.emit()
\t\tqueue_free()
'''

PLUGIN_GD = '''@tool
extends EditorPlugin

func _enter_tree():
\tadd_custom_type("InventoryManager", "Node", preload("res://addons/inventory_system/scripts/inventory.gd"), preload("res://icon.svg"))
\tadd_custom_type("InventoryUI", "Control", preload("res://addons/inventory_system/scripts/inventory_ui_system.gd"), preload("res://icon.svg"))
\tadd_custom_type("Hotbar", "Node", preload("res://addons/inventory_system/scripts/hotbar.gd"), preload("res://icon.svg"))
\tadd_custom_type("HotbarUI", "Control", preload("res://addons/inventory_system/scripts/hotbar_ui_system.gd"), preload("res://icon.svg"))
\tprint("✓ Inventory System activado (versión consolidada)")

func _exit_tree():
\tremove_custom_type("InventoryManager")
\tremove_custom_type("InventoryUI")
\tremove_custom_type("Hotbar")
\tremove_custom_type("HotbarUI")
'''

def create_backup(base_path):
    """Crea un backup del directorio"""
    print_header("CREANDO BACKUP")
    
    addon_path = Path(base_path) / "addons" / "inventory_system"
    if not addon_path.exists():
        print_error(f"No se encontró el addon en: {addon_path}")
        return False
    
    backup_path = Path(base_path) / "inventory_system_backup"
    
    try:
        if backup_path.exists():
            shutil.rmtree(backup_path)
        
        shutil.copytree(addon_path, backup_path)
        print_success(f"Backup creado en: {backup_path}")
        return True
    except Exception as e:
        print_error(f"Error creando backup: {e}")
        return False

def delete_old_files(base_path):
    """Elimina archivos antiguos"""
    print_header("ELIMINANDO ARCHIVOS ANTIGUOS")
    
    deleted_count = 0
    not_found_count = 0
    
    for file_path in FILES_TO_DELETE:
        full_path = Path(base_path) / file_path
        
        if full_path.exists():
            try:
                full_path.unlink()
                print_success(f"Eliminado: {file_path}")
                deleted_count += 1
            except Exception as e:
                print_error(f"Error eliminando {file_path}: {e}")
        else:
            print_warning(f"No encontrado: {file_path}")
            not_found_count += 1
    
    print()
    print_info(f"Archivos eliminados: {deleted_count}")
    if not_found_count > 0:
        print_info(f"Archivos no encontrados: {not_found_count}")
    
    return deleted_count > 0

def create_consolidated_files(base_path):
    """Crea los archivos consolidados"""
    print_header("CREANDO ARCHIVOS CONSOLIDADOS")
    
    scripts_path = Path(base_path) / "addons" / "inventory_system" / "scripts"
    scripts_path.mkdir(parents=True, exist_ok=True)
    
    files_to_create = {
        "inventory_ui_system.gd": INVENTORY_UI_SYSTEM,
        "hotbar_ui_system.gd": HOTBAR_UI_SYSTEM,
        "crafting_system.gd": CRAFTING_SYSTEM,
    }
    
    created_count = 0
    
    for filename, content in files_to_create.items():
        file_path = scripts_path / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print_success(f"Creado: {filename}")
            created_count += 1
        except Exception as e:
            print_error(f"Error creando {filename}: {e}")
    
    print()
    print_info(f"Archivos consolidados creados: {created_count}")
    
    return created_count == len(files_to_create)

def update_plugin_file(base_path):
    """Actualiza el archivo plugin.gd"""
    print_header("ACTUALIZANDO PLUGIN.GD")
    
    plugin_path = Path(base_path) / "addons" / "inventory_system" / "plugin.gd"
    
    try:
        with open(plugin_path, 'w', encoding='utf-8') as f:
            f.write(PLUGIN_GD)
        print_success("plugin.gd actualizado correctamente")
        return True
    except Exception as e:
        print_error(f"Error actualizando plugin.gd: {e}")
        return False

def generate_report(base_path):
    """Genera un reporte de la consolidación"""
    print_header("REPORTE FINAL")
    
    scripts_path = Path(base_path) / "addons" / "inventory_system" / "scripts"
    
    if not scripts_path.exists():
        print_error("No se encontró la carpeta de scripts")
        return
    
    gd_files = list(scripts_path.glob("*.gd"))
    uid_files = list(scripts_path.glob("*.uid"))
    
    print_info(f"Archivos .gd encontrados: {len(gd_files)}")
    print_info(f"Archivos .uid encontrados: {len(uid_files)}")
    
    print("\n📄 Estructura final:")
    for file in sorted(gd_files):
        print(f"  ✓ {file.name}")
    
    print("\n📦 Archivos consolidados principales:")
    consolidated = ["inventory_ui_system.gd", "hotbar_ui_system.gd", "crafting_system.gd"]
    for file in consolidated:
        file_path = scripts_path / file
        if file_path.exists():
            size = file_path.stat().st_size / 1024
            print(f"  ✓ {file} ({size:.1f} KB)")
        else:
            print(f"  ✗ {file} (no encontrado)")

def main():
    """Función principal"""
    print_header("🔧 CONSOLIDACIÓN AUTOMÁTICA DEL SISTEMA DE INVENTARIO")
    
    # Detectar directorio base del proyecto
    current_dir = Path.cwd()
    
    print_info(f"Directorio actual: {current_dir}")
    
    # Verificar si estamos en un proyecto Godot
    if not (current_dir / "project.godot").exists():
        print_error("No se encontró project.godot")
        print_warning("Asegúrate de ejecutar este script desde la raíz del proyecto Godot")
        return
    
    print_success("Proyecto Godot detectado")
    
    # Confirmar con el usuario
    print("\n⚠️  Este script va a:")
    print("  1. Crear un backup de tu addon")
    print("  2. Eliminar archivos antiguos")
    print("  3. Crear archivos consolidados")
    print("  4. Actualizar plugin.gd")
    
    response = input("\n¿Continuar? (s/n): ").lower().strip()
    
    if response != 's':
        print_warning("Operación cancelada por el usuario")
        return
    
    # Ejecutar consolidación
    success = True
    
    # 1. Crear backup
    if not create_backup(current_dir):
        print_error("Error creando backup. Abortando...")
        return
    
    # 2. Eliminar archivos antiguos
    if not delete_old_files(current_dir):
        print_warning("No se eliminaron archivos (puede que ya estén consolidados)")
    
    # 3. Crear archivos consolidados
    if not create_consolidated_files(current_dir):
        success = False
        print_error("Error creando archivos consolidados")
    
    # 4. Actualizar plugin.gd
    if not update_plugin_file(current_dir):
        success = False
        print_error("Error actualizando plugin.gd")
    
    # 5. Generar reporte
    generate_report(current_dir)
    
    # Resultado final
    if success:
        print_header("✅ CONSOLIDACIÓN COMPLETADA CON ÉXITO")
        print("📋 Próximos pasos:")
        print("  1. Abre Godot")
        print("  2. Ve a Proyecto > Recargar proyecto actual")
        print("  3. Verifica que el addon funcione correctamente")
        print(f"\n💾 Backup disponible en: inventory_system_backup/")
    else:
        print_header("❌ CONSOLIDACIÓN COMPLETADA CON ERRORES")
        print("⚠️  Revisa los errores anteriores")
        print(f"💾 Puedes restaurar desde: inventory_system_backup/")

if __name__ == "__main__":
    main()