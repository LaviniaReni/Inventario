#!/usr/bin/env python3
"""
Instalador Automático del Sistema de Inventario Minecraft para Godot 4.5
Autor: Sistema de Inventario
Versión: 1.0

Uso: python install_minecraft_system.py
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

# Colores para la consola
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

# Detectar la raíz del proyecto Godot
def find_project_root() -> Path:
    """Busca el directorio raíz del proyecto Godot (contiene project.godot)"""
    current = Path.cwd()
    
    # Buscar hacia arriba hasta encontrar project.godot
    for _ in range(5):  # Máximo 5 niveles arriba
        if (current / "project.godot").exists():
            return current
        current = current.parent
    
    # Si no encuentra, usar directorio actual
    return Path.cwd()

PROJECT_ROOT = find_project_root()

# Estructura de archivos a crear
FILE_STRUCTURE = {
    "scripts": {
        "crafting_recipe.gd": """class_name CraftingRecipe
extends Resource

@export var id: String = ""
@export var result_item_id: String = ""
@export var result_quantity: int = 1
@export var shapeless: bool = false
@export var pattern: Array[String] = ["", "", "", "", "", "", "", "", ""]

func matches(grid: Array[String]) -> bool:
\tif shapeless:
\t\treturn matches_shapeless(grid)
\telse:
\t\treturn matches_shaped(grid)

func matches_shapeless(grid: Array[String]) -> bool:
\tvar pattern_items = {}
\tvar grid_items = {}
\t
\tfor item_id in pattern:
\t\tif item_id != "":
\t\t\tpattern_items[item_id] = pattern_items.get(item_id, 0) + 1
\t
\tfor item_id in grid:
\t\tif item_id != "":
\t\t\tgrid_items[item_id] = grid_items.get(item_id, 0) + 1
\t
\treturn pattern_items == grid_items

func matches_shaped(grid: Array[String]) -> bool:
\treturn grid == pattern
""",
        "crafting_manager.gd": """class_name CraftingManager
extends Node

signal recipe_found(recipe: CraftingRecipe)
signal crafted(item: InventoryItem, quantity: int)

var recipes: Array[CraftingRecipe] = []

func _ready():
\tload_recipes()

func load_recipes():
\tvar recipes_path = "res://recipes/"
\tif not DirAccess.dir_exists_absolute(recipes_path):
\t\tDirAccess.make_dir_recursive_absolute(recipes_path)
\t\tprint("⚠️ Carpeta recipes/ vacía. Usa create_recipes.gd")
\t\treturn
\t
\tvar dir = DirAccess.open(recipes_path)
\tif dir:
\t\tdir.list_dir_begin()
\t\tvar file_name = dir.get_next()
\t\t
\t\twhile file_name != "":
\t\t\tif file_name.ends_with(".tres"):
\t\t\t\tvar recipe = load(recipes_path + file_name)
\t\t\t\tif recipe is CraftingRecipe:
\t\t\t\t\trecipes.append(recipe)
\t\t\tfile_name = dir.get_next()
\t\t
\t\tdir.list_dir_end()
\t
\tprint("✓ CraftingManager: %d recetas cargadas" % recipes.size())

func find_recipe(grid_slots: Array[InventorySlot]) -> CraftingRecipe:
\tvar grid_ids: Array[String] = []
\t
\tfor slot in grid_slots:
\t\tif slot.is_empty():
\t\t\tgrid_ids.append("")
\t\telse:
\t\t\tgrid_ids.append(slot.item.id)
\t
\tfor recipe in recipes:
\t\tif recipe.matches(grid_ids):
\t\t\trecipe_found.emit(recipe)
\t\t\treturn recipe
\t
\treturn null

func can_craft(recipe: CraftingRecipe, grid_slots: Array[InventorySlot]) -> bool:
\tif recipe == null:
\t\treturn false
\t
\tfor i in range(grid_slots.size()):
\t\tvar required_id = recipe.pattern[i]
\t\tvar slot = grid_slots[i]
\t\t
\t\tif required_id == "" and not slot.is_empty():
\t\t\tif not recipe.shapeless:
\t\t\t\treturn false
\t\telif required_id != "" and (slot.is_empty() or slot.item.id != required_id):
\t\t\treturn false
\t
\treturn true

func craft(recipe: CraftingRecipe, grid_slots: Array[InventorySlot], inventory: InventoryManager) -> bool:
\tif not can_craft(recipe, grid_slots):
\t\treturn false
\t
\tfor i in range(grid_slots.size()):
\t\tif recipe.pattern[i] != "":
\t\t\tgrid_slots[i].remove_item(1)
\t
\tvar result_item = ItemDatabase.get_item(recipe.result_item_id)
\tif result_item:
\t\tinventory.add_item(result_item, recipe.result_quantity)
\t\tcrafted.emit(result_item, recipe.result_quantity)
\t\treturn true
\t
\treturn false
""",
        "crafting_table_ui.gd": """class_name CraftingTableUI
extends Control

signal closed

@export var inventory_ui: Control

@onready var crafting_grid = $Panel/MarginContainer/VBox/CraftingArea/CraftingGrid
@onready var result_slot = $Panel/MarginContainer/VBox/CraftingArea/ResultArea/ResultSlot

var crafting_manager: CraftingManager
var crafting_slots: Array[InventorySlot] = []
var result_item: InventoryItem = null
var result_quantity: int = 0
var current_recipe: CraftingRecipe = null

var held_item: InventoryItem = null
var held_quantity: int = 0
var cursor_preview: Control = null

func _ready():
\tcrafting_manager = CraftingManager.new()
\tadd_child(crafting_manager)
\t
\tinitialize_crafting_grid()
\tsetup_cursor_preview()
\t
\tcrafting_manager.recipe_found.connect(_on_recipe_found)

func initialize_crafting_grid():
\tfor i in range(9):
\t\tvar slot = InventorySlot.new()
\t\tcrafting_slots.append(slot)
\t\t
\t\tvar slot_ui = create_slot_ui(i)
\t\tcrafting_grid.add_child(slot_ui)

func create_slot_ui(index: int) -> Control:
\tvar slot_ui = preload("res://addons/inventory_system/scenes/inventory_slot_ui.tscn").instantiate()
\tslot_ui.index = index
\tslot_ui.custom_minimum_size = Vector2(64, 64)
\treturn slot_ui

func setup_cursor_preview():
\tcursor_preview = Panel.new()
\tcursor_preview.custom_minimum_size = Vector2(64, 64)
\tcursor_preview.mouse_filter = Control.MOUSE_FILTER_IGNORE
\tcursor_preview.z_index = 100
\t
\tvar icon = TextureRect.new()
\ticon.name = "Icon"
\ticon.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
\ticon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
\ticon.mouse_filter = Control.MOUSE_FILTER_IGNORE
\tcursor_preview.add_child(icon)
\ticon.set_anchors_preset(Control.PRESET_FULL_RECT)
\t
\tvar qty = Label.new()
\tqty.name = "Quantity"
\tqty.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
\tqty.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
\tcursor_preview.add_child(qty)
\tqty.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
\t
\tadd_child(cursor_preview)
\tcursor_preview.visible = false

func _process(_delta):
\tif held_item:
\t\tcursor_preview.global_position = get_global_mouse_position() - cursor_preview.size / 2
\t\tcursor_preview.visible = true
\t\tcursor_preview.get_node("Icon").texture = held_item.icon
\t\tcursor_preview.get_node("Quantity").text = str(held_quantity) if held_quantity > 1 else ""
\telse:
\t\tcursor_preview.visible = false

func check_recipe():
\tcurrent_recipe = crafting_manager.find_recipe(crafting_slots)
\t
\tif current_recipe:
\t\tresult_item = ItemDatabase.get_item(current_recipe.result_item_id)
\t\tresult_quantity = current_recipe.result_quantity
\t\tupdate_result_slot()
\telse:
\t\tresult_item = null
\t\tresult_quantity = 0
\t\tclear_result_slot()

func update_result_slot():
\tif result_item:
\t\tresult_slot.get_node("Icon").texture = result_item.icon
\t\tresult_slot.get_node("Quantity").text = str(result_quantity) if result_quantity > 1 else ""
\t\tresult_slot.modulate = Color.WHITE

func clear_result_slot():
\tresult_slot.get_node("Icon").texture = null
\tresult_slot.get_node("Quantity").text = ""
\tresult_slot.modulate = Color(1, 1, 1, 0.3)

func _on_recipe_found(recipe: CraftingRecipe):
\tprint("✓ Receta: %s" % recipe.result_item_id)

func _input(event):
\tif event.is_action_pressed("ui_cancel"):
\t\tclose_crafting_table()
\t\tget_viewport().set_input_as_handled()

func close_crafting_table():
\tfor slot in crafting_slots:
\t\tif not slot.is_empty() and inventory_ui and inventory_ui.inventory:
\t\t\tinventory_ui.inventory.add_item(slot.item, slot.quantity)
\t\t\tslot.clear()
\t
\tif held_item and inventory_ui and inventory_ui.inventory:
\t\tinventory_ui.inventory.add_item(held_item, held_quantity)
\t\theld_item = null
\t\theld_quantity = 0
\t
\tclosed.emit()
\tqueue_free()
""",
    },
    "autoloads": {
        "input_manager.gd": """extends Node

func _ready():
\tsetup_minecraft_controls()

func setup_minecraft_controls():
\tadd_input_action("open_inventory", KEY_E)
\t
\tfor i in range(1, 10):
\t\tadd_input_action("hotbar_slot_%d" % i, KEY_0 + i)
\t
\tadd_input_action("drop_item", KEY_Q)
\tadd_input_action("drop_stack", KEY_Q, true, true)
\tadd_input_action("swap_hands", KEY_F)
\tadd_input_action("pick_block", MOUSE_BUTTON_MIDDLE)
\t
\tprint("✓ Controles Minecraft configurados")

func add_input_action(action_name: String, key_or_button, ctrl: bool = false, shift: bool = false):
\tif InputMap.has_action(action_name):
\t\treturn
\t
\tInputMap.add_action(action_name)
\t
\tif key_or_button is int and key_or_button >= KEY_0 and key_or_button <= KEY_Z:
\t\tvar event = InputEventKey.new()
\t\tevent.keycode = key_or_button
\t\tevent.ctrl_pressed = ctrl
\t\tevent.shift_pressed = shift
\t\tInputMap.action_add_event(action_name, event)
\telif key_or_button is int:
\t\tvar event = InputEventMouseButton.new()
\t\tevent.button_index = key_or_button
\t\tInputMap.action_add_event(action_name, event)
""",
    },
    "demos": {
        "minecraft_demo.gd": """extends Node2D

@onready var inventory_ui = $InventoryUI
@onready var inventory = $InventoryUI.inventory
@onready var hotbar_ui = $HotbarUI
@onready var info_label = $InfoLabel

var crafting_table_ui = null

func _ready():
\tif ItemDatabase.get_item_count() == 0:
\t\tawait ItemDatabase.database_loaded
\t
\tadd_starting_items()
\t
\tinventory.item_added.connect(_on_item_added)
\tinventory.item_used.connect(_on_item_used)
\t
\tinventory_ui.visible = false
\t
\tprint_controls()

func print_controls():
\tprint("\\n" + "="*50)
\tprint("🎮 CONTROLES MINECRAFT")
\tprint("="*50)
\tprint("E: Inventario")
\tprint("1-9: Hotbar")
\tprint("Q: Soltar item")
\tprint("Enter: Mesa de trabajo")
\tprint("="*50 + "\\n")

func add_starting_items():
\tif ItemDatabase.has_item("wood"):
\t\tinventory.add_item_by_id("wood", 64)
\tif ItemDatabase.has_item("stone"):
\t\tinventory.add_item_by_id("stone", 64)
\tif ItemDatabase.has_item("stick"):
\t\tinventory.add_item_by_id("stick", 32)

func _input(event):
\tif event.is_action_pressed("open_inventory"):
\t\tinventory_ui.visible = !inventory_ui.visible
\t\tget_viewport().set_input_as_handled()
\t
\tif event.is_action_pressed("ui_accept"):
\t\tif not crafting_table_ui:
\t\t\topen_crafting_table()
\t\tget_viewport().set_input_as_handled()

func open_crafting_table():
\tvar scene = load("res://addons/inventory_system/scenes/crafting_table_ui.tscn")
\tif scene:
\t\tcrafting_table_ui = scene.instantiate()
\t\tadd_child(crafting_table_ui)
\t\tcrafting_table_ui.inventory_ui = inventory_ui
\t\tcrafting_table_ui.closed.connect(_on_crafting_closed)
\t\tshow_info("Mesa de trabajo abierta")

func _on_crafting_closed():
\tcrafting_table_ui = null

func _on_item_added(item: InventoryItem, amount: int):
\tshow_info("+ %d x %s" % [amount, item.name])

func _on_item_used(item: InventoryItem):
\tshow_info("⚡ %s" % item.name)

func show_info(text: String):
\tinfo_label.text = text
\tprint(text)
""",
    },
    "recipes_creator": {
        "create_recipes.gd": """@tool
extends EditorScript

func _run():
\tprint("\\n" + "="*50)
\tprint("Creando recetas...")
\tprint("="*50 + "\\n")
\t
\tcreate_recipes_folder()
\tcreate_example_recipes()
\t
\tprint("\\n✓ Recetas creadas exitosamente!")
\tprint("Ubicación: res://recipes/\\n")

func create_recipes_folder():
\tvar dir = DirAccess.open("res://")
\tif not dir.dir_exists("recipes"):
\t\tdir.make_dir("recipes")
\t\tprint("✓ Carpeta recipes/ creada")

func create_example_recipes():
\tvar recipes = [
\t\t{
\t\t\t"id": "sticks",
\t\t\t"result": "stick",
\t\t\t"quantity": 4,
\t\t\t"pattern": ["wood", "", "", "wood", "", "", "", "", ""]
\t\t},
\t\t{
\t\t\t"id": "wooden_sword",
\t\t\t"result": "sword_iron",
\t\t\t"quantity": 1,
\t\t\t"pattern": ["wood", "", "", "wood", "", "", "stick", "", ""]
\t\t},
\t\t{
\t\t\t"id": "torches",
\t\t\t"result": "torch",
\t\t\t"quantity": 4,
\t\t\t"pattern": ["coal", "", "", "stick", "", "", "", "", ""]
\t\t},
\t]
\t
\tfor recipe_data in recipes:
\t\tvar recipe = CraftingRecipe.new()
\t\trecipe.id = recipe_data.id
\t\trecipe.result_item_id = recipe_data.result
\t\trecipe.result_quantity = recipe_data.quantity
\t\trecipe.shapeless = false
\t\trecipe.pattern = recipe_data.pattern
\t\t
\t\tvar path = "res://recipes/%s.tres" % recipe_data.id
\t\tResourceSaver.save(recipe, path)
\t\tprint("✓ Creada: %s" % recipe_data.id)
""",
    },
}

# Items adicionales necesarios
ADDITIONAL_ITEMS = {
    "wood.tres": """[gd_resource type="Resource" script_class="InventoryItem" load_steps=2 format=3]

[ext_resource type="Script" path="res://addons/inventory_system/scripts/item.gd" id="1"]
[ext_resource type="Texture2D" path="res://icon.svg" id="2"]

[resource]
script = ExtResource("1")
id = "wood"
name = "Madera"
description = "Madera procesada"
icon = ExtResource("2")
item_type = 3
max_stack = 64
""",
    "stick.tres": """[gd_resource type="Resource" script_class="InventoryItem" load_steps=2 format=3]

[ext_resource type="Script" path="res://addons/inventory_system/scripts/item.gd" id="1"]
[ext_resource type="Texture2D" path="res://icon.svg" id="2"]

[resource]
script = ExtResource("1")
id = "stick"
name = "Palo"
description = "Útil para herramientas"
icon = ExtResource("2")
item_type = 3
max_stack = 64
""",
    "stone.tres": """[gd_resource type="Resource" script_class="InventoryItem" load_steps=2 format=3]

[ext_resource type="Script" path="res://addons/inventory_system/scripts/item.gd" id="1"]
[ext_resource type="Texture2D" path="res://icon.svg" id="2"]

[resource]
script = ExtResource("1")
id = "stone"
name = "Piedra"
description = "Piedra común"
icon = ExtResource("2")
item_type = 3
max_stack = 64
""",
    "coal.tres": """[gd_resource type="Resource" script_class="InventoryItem" load_steps=2 format=3]

[ext_resource type="Script" path="res://addons/inventory_system/scripts/item.gd" id="1"]
[ext_resource type="Texture2D" path="res://icon.svg" id="2"]

[resource]
script = ExtResource("1")
id = "coal"
name = "Carbón"
description = "Combustible"
icon = ExtResource("2")
item_type = 3
max_stack = 64
""",
    "torch.tres": """[gd_resource type="Resource" script_class="InventoryItem" load_steps=2 format=3]

[ext_resource type="Script" path="res://addons/inventory_system/scripts/item.gd" id="1"]
[ext_resource type="Texture2D" path="res://icon.svg" id="2"]

[resource]
script = ExtResource("1")
id = "torch"
name = "Antorcha"
description = "Ilumina el camino"
icon = ExtResource("2")
item_type = 4
max_stack = 64
""",
}


def create_directory_structure():
    """Crea la estructura de directorios necesaria"""
    print_header("CREANDO ESTRUCTURA DE DIRECTORIOS")
    
    dirs_to_create = [
        PROJECT_ROOT / "addons" / "inventory_system" / "scripts",
        PROJECT_ROOT / "addons" / "inventory_system" / "scenes",
        PROJECT_ROOT / "autoloads",
        PROJECT_ROOT / "recipes",
        PROJECT_ROOT / "demos",
    ]
    
    for directory in dirs_to_create:
        directory.mkdir(parents=True, exist_ok=True)
        print_success(f"Directorio: {directory.relative_to(PROJECT_ROOT)}")


def create_files():
    """Crea todos los archivos de scripts"""
    print_header("CREANDO ARCHIVOS DE SCRIPTS")
    
    base_path = PROJECT_ROOT / "addons" / "inventory_system" / "scripts"
    for filename, content in FILE_STRUCTURE["scripts"].items():
        filepath = base_path / filename
        filepath.write_text(content, encoding='utf-8')
        print_success(f"Script: {filename}")
    
    # Autoloads
    autoload_path = PROJECT_ROOT / "autoloads"
    for filename, content in FILE_STRUCTURE["autoloads"].items():
        filepath = autoload_path / filename
        filepath.write_text(content, encoding='utf-8')
        print_success(f"Autoload: {filename}")
    
    # Demos
    demo_path = PROJECT_ROOT / "demos"
    for filename, content in FILE_STRUCTURE["demos"].items():
        filepath = demo_path / filename
        filepath.write_text(content, encoding='utf-8')
        print_success(f"Demo: {filename}")
    
    # Recipe creator
    for filename, content in FILE_STRUCTURE["recipes_creator"].items():
        filepath = PROJECT_ROOT / filename
        filepath.write_text(content, encoding='utf-8')
        print_success(f"Herramienta: {filename}")


def create_items():
    """Crea los items adicionales necesarios"""
    print_header("CREANDO ITEMS ADICIONALES")
    
    items_path = PROJECT_ROOT / "addons" / "inventory_system" / "demo" / "demo_items"
    items_path.mkdir(parents=True, exist_ok=True)
    
    for filename, content in ADDITIONAL_ITEMS.items():
        filepath = items_path / filename
        if not filepath.exists():  # No sobreescribir si ya existe
            filepath.write_text(content, encoding='utf-8')
            print_success(f"Item: {filename}")
        else:
            print_warning(f"Item ya existe: {filename}")


def update_project_settings():
    """Actualiza project.godot para agregar el autoload"""
    print_header("ACTUALIZANDO CONFIGURACIÓN DEL PROYECTO")
    
    project_file = PROJECT_ROOT / "project.godot"
    
    if not project_file.exists():
        print_error("No se encontró project.godot")
        return False
    
    content = project_file.read_text(encoding='utf-8')
    
    # Verificar si ya existe la sección autoload
    if '[autoload]' not in content:
        content += '\n[autoload]\n\n'
    
    # Agregar InputManager si no existe
    input_manager_line = 'InputManager="*res://autoloads/input_manager.gd"'
    if 'InputManager=' not in content:
        # Encontrar la sección [autoload] y agregar después
        autoload_index = content.find('[autoload]')
        if autoload_index != -1:
            # Buscar el final de la línea [autoload]
            end_of_line = content.find('\n', autoload_index)
            # Insertar la nueva línea
            content = content[:end_of_line+1] + input_manager_line + '\n' + content[end_of_line+1:]
            
            project_file.write_text(content, encoding='utf-8')
            print_success("InputManager agregado a Autoload")
        else:
            print_error("No se pudo actualizar project.godot")
            return False
    else:
        print_warning("InputManager ya existe en Autoload")
    
    return True


def update_inventory_slot_ui():
    """Actualiza inventory_slot_ui.gd con funciones Minecraft"""
    print_header("ACTUALIZANDO INVENTORY_SLOT_UI.GD")
    
    slot_ui_path = PROJECT_ROOT / "addons" / "inventory_system" / "scripts" / "inventory_slot_ui.gd"
    
    if not slot_ui_path.exists():
        print_error(f"No se encontró: {slot_ui_path}")
        return False
    
    content = slot_ui_path.read_text(encoding='utf-8')
    
    # Agregar funciones al final si no existen
    if "_quick_move_item" not in content:
        additional_code = """

# Minecraft-style controls
func _quick_move_item():
\tvar slot = inventory.slots[index]
\tif slot.is_empty():
\t\treturn
\t
\tvar target_start = 9 if index < 9 else 0
\tvar target_end = 36 if index < 9 else 9
\t
\tfor i in range(target_start, target_end):
\t\tif inventory.slots[i].is_empty() or (inventory.slots[i].item.id == slot.item.id and inventory.slots[i].item.is_stackable):
\t\t\tvar remaining = inventory.slots[i].add_item(slot.item, slot.quantity)
\t\t\tslot.quantity = remaining
\t\t\tif remaining == 0:
\t\t\t\tslot.clear()
\t\t\t\tbreak
\t
\tinventory.inventory_changed.emit()
"""
        content += additional_code
        slot_ui_path.write_text(content, encoding='utf-8')
        print_success("Funciones Minecraft agregadas a inventory_slot_ui.gd")
    else:
        print_warning("inventory_slot_ui.gd ya tiene las funciones Minecraft")
    
    return True


def create_crafting_table_scene():
    """Crea la escena de crafting table"""
    print_header("CREANDO ESCENA DE CRAFTING TABLE")
    
    scene_content = """[gd_scene load_steps=2 format=3 uid="uid://crafting_table_scene"]

[ext_resource type="Script" path="res://addons/inventory_system/scripts/crafting_table_ui.gd" id="1"]

[node name="CraftingTableUI" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
script = ExtResource("1")

[node name="Background" type="ColorRect" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
color = Color(0, 0, 0, 0.7)

[node name="Panel" type="Panel" parent="."]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -300.0
offset_top = -250.0
offset_right = 300.0
offset_bottom = 250.0
grow_horizontal = 2
grow_vertical = 2

[node name="MarginContainer" type="MarginContainer" parent="Panel"]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
theme_override_constants/margin_left = 20
theme_override_constants/margin_top = 20
theme_override_constants/margin_right = 20
theme_override_constants/margin_bottom = 20

[node name="VBox" type="VBoxContainer" parent="Panel/MarginContainer"]
layout_mode = 2
theme_override_constants/separation = 15

[node name="Title" type="Label" parent="Panel/MarginContainer/VBox"]
layout_mode = 2
text = "Mesa de Trabajo"
horizontal_alignment = 1
theme_override_font_sizes/font_size = 24

[node name="CraftingArea" type="HBoxContainer" parent="Panel/MarginContainer/VBox"]
layout_mode = 2
theme_override_constants/separation = 30
alignment = 1

[node name="CraftingGrid" type="GridContainer" parent="Panel/MarginContainer/VBox/CraftingArea"]
layout_mode = 2
theme_override_constants/h_separation = 4
theme_override_constants/v_separation = 4
columns = 3

[node name="Arrow" type="Label" parent="Panel/MarginContainer/VBox/CraftingArea"]
layout_mode = 2
text = "→"
theme_override_font_sizes/font_size = 48

[node name="ResultArea" type="VBoxContainer" parent="Panel/MarginContainer/VBox/CraftingArea"]
layout_mode = 2

[node name="ResultLabel" type="Label" parent="Panel/MarginContainer/VBox/CraftingArea/ResultArea"]
layout_mode = 2
text = "Resultado"
horizontal_alignment = 1

[node name="ResultSlot" type="Panel" parent="Panel/MarginContainer/VBox/CraftingArea/ResultArea"]
custom_minimum_size = Vector2(64, 64)
layout_mode = 2

[node name="Icon" type="TextureRect" parent="Panel/MarginContainer/VBox/CraftingArea/ResultArea/ResultSlot"]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
expand_mode = 1
stretch_mode = 5

[node name="Quantity" type="Label" parent="Panel/MarginContainer/VBox/CraftingArea/ResultArea/ResultSlot"]
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
horizontal_alignment = 2
vertical_alignment = 2
"""
    
    scene_path = PROJECT_ROOT / "addons" / "inventory_system" / "scenes" / "crafting_table_ui.tscn"
    scene_path.write_text(scene_content, encoding='utf-8')
    print_success("Escena crafting_table_ui.tscn creada")
    return True


def create_backup():
    """Crea un backup de los archivos existentes"""
    print_header("CREANDO BACKUP")
    
    backup_dir = PROJECT_ROOT / "backup_minecraft_system"
    
    if backup_dir.exists():
        print_warning("Ya existe un backup. Se omitirá.")
        return
    
    backup_dir.mkdir(exist_ok=True)
    
    # Backup de archivos importantes
    files_to_backup = [
        "project.godot",
        "addons/inventory_system/scripts/inventory.gd",
        "addons/inventory_system/scripts/inventory_slot_ui.gd",
    ]
    
    for file_rel in files_to_backup:
        src = PROJECT_ROOT / file_rel
        if src.exists():
            dst = backup_dir / file_rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print_success(f"Backup: {file_rel}")
    
    print_info(f"Backup guardado en: {backup_dir.relative_to(PROJECT_ROOT)}")


def print_summary():
    """Imprime un resumen de la instalación"""
    print_header("INSTALACIÓN COMPLETADA")
    
    print(f"{Colors.GREEN}✓ Sistema de Crafting Minecraft instalado correctamente!{Colors.RESET}\n")
    
    print(f"{Colors.BOLD}Archivos creados:{Colors.RESET}")
    print("  📁 addons/inventory_system/scripts/")
    print("     - crafting_recipe.gd")
    print("     - crafting_manager.gd")
    print("     - crafting_table_ui.gd")
    print("  📁 autoloads/")
    print("     - input_manager.gd")
    print("  📁 demos/")
    print("     - minecraft_demo.gd")
    print("  📄 create_recipes.gd")
    
    print(f"\n{Colors.BOLD}Próximos pasos:{Colors.RESET}")
    print(f"{Colors.CYAN}1.{Colors.RESET} Abre el proyecto en Godot 4.5")
    print(f"{Colors.CYAN}2.{Colors.RESET} File > Run > Selecciona 'create_recipes.gd' para generar recetas")
    print(f"{Colors.CYAN}3.{Colors.RESET} Abre la escena demos/minecraft_demo.tscn")
    print(f"{Colors.CYAN}4.{Colors.RESET} Presiona F5 para jugar")
    
    print(f"\n{Colors.BOLD}Controles:{Colors.RESET}")
    print(f"  {Colors.GREEN}E{Colors.RESET}         - Abrir/Cerrar inventario")
    print(f"  {Colors.GREEN}1-9{Colors.RESET}       - Seleccionar slot hotbar")
    print(f"  {Colors.GREEN}Enter{Colors.RESET}     - Abrir mesa de trabajo")
    print(f"  {Colors.GREEN}Q{Colors.RESET}         - Soltar 1 item")
    print(f"  {Colors.GREEN}Ctrl+Q{Colors.RESET}    - Soltar stack")
    print(f"  {Colors.GREEN}Shift+Click{Colors.RESET} - Mover rápido")
    
    print(f"\n{Colors.BOLD}Documentación:{Colors.RESET}")
    print(f"  📖 Revisa los comentarios en cada script")
    print(f"  📖 Consulta HOTBAR_GUIDE.md para más info")
    
    print(f"\n{Colors.YELLOW}⚠️  IMPORTANTE:{Colors.RESET}")
    print(f"  • Verifica que ItemDatabase esté en Autoload")
    print(f"  • Ejecuta create_recipes.gd antes de probar")
    print(f"  • Backup guardado en: backup_minecraft_system/")
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}¡Disfruta tu sistema tipo Minecraft!{Colors.RESET} 🎮\n")


def verify_installation():
    """Verifica que todo se haya instalado correctamente"""
    print_header("VERIFICANDO INSTALACIÓN")
    
    checks = [
        ("project.godot", PROJECT_ROOT / "project.godot"),
        ("input_manager.gd", PROJECT_ROOT / "autoloads" / "input_manager.gd"),
        ("crafting_recipe.gd", PROJECT_ROOT / "addons" / "inventory_system" / "scripts" / "crafting_recipe.gd"),
        ("crafting_manager.gd", PROJECT_ROOT / "addons" / "inventory_system" / "scripts" / "crafting_manager.gd"),
        ("crafting_table_ui.gd", PROJECT_ROOT / "addons" / "inventory_system" / "scripts" / "crafting_table_ui.gd"),
        ("minecraft_demo.gd", PROJECT_ROOT / "demos" / "minecraft_demo.gd"),
        ("create_recipes.gd", PROJECT_ROOT / "create_recipes.gd"),
    ]
    
    all_ok = True
    for name, path in checks:
        if path.exists():
            print_success(f"{name}")
        else:
            print_error(f"{name} - NO ENCONTRADO")
            all_ok = False
    
    if all_ok:
        print(f"\n{Colors.GREEN}✓ Todos los archivos verificados correctamente{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}✗ Algunos archivos faltan. Revisa la instalación.{Colors.RESET}")
    
    return all_ok


def main():
    """Función principal de instalación"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("="*60)
    print("   INSTALADOR AUTOMÁTICO - SISTEMA MINECRAFT")
    print("   Inventario + Crafting + Controles")
    print("="*60)
    print(f"{Colors.RESET}\n")
    
    print_info(f"Directorio del proyecto: {PROJECT_ROOT}")
    print_info("Iniciando instalación...\n")
    
    try:
        # 1. Crear backup
        create_backup()
        
        # 2. Crear estructura de directorios
        create_directory_structure()
        
        # 3. Crear archivos de scripts
        create_files()
        
        # 4. Crear items adicionales
        create_items()
        
        # 5. Crear escena de crafting table
        create_crafting_table_scene()
        
        # 6. Actualizar inventory_slot_ui.gd
        update_inventory_slot_ui()
        
        # 7. Actualizar project.godot
        update_project_settings()
        
        # 8. Verificar instalación
        if verify_installation():
            print_summary()
            return 0
        else:
            print_error("La verificación falló. Revisa los errores anteriores.")
            return 1
            
    except Exception as e:
        print_error(f"Error durante la instalación: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())