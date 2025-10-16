def print_summary(self):
        """Imprime resumen de cambios"""
        self.print_header("RESUMEN DE EJECUCIÓN")
        
        if self.changes_made:
            print(f"✅ CAMBIOS REALIZADOS ({len(self.changes_made)}):")
            for change in self.changes_made:
                print(f"  • {change}")
        else:
            print("  No se realizaron cambios")
        
        if self.warnings:
            print(f"\n⚠️  ADVERTENCIAS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para reparar y organizar el Sistema de Inventario de Godot 4.5
Ejecutar desde la raíz del proyecto: python fix_inventory.py

Requisitos: Python 3.6+
Autor: Sistema de Inventario v2.0
"""

import os
import sys
import shutil
from pathlib import Path

class InventoryFixer:
    def __init__(self):
        self.root = Path.cwd()
        self.addon_path = self.root / "addons" / "inventory_system"
        self.scripts_path = self.addon_path / "scripts"
        self.changes_made = []
        self.errors = []
        self.warnings = []
        
    def print_header(self, text):
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")
    
    def log_change(self, change):
        self.changes_made.append(change)
        print(f"✓ {change}")
    
    def log_error(self, error):
        self.errors.append(error)
        print(f"✗ ERROR: {error}")
    
    def log_warning(self, warning):
        self.warnings.append(warning)
        print(f"⚠️  ADVERTENCIA: {warning}")
    
    def verify_project_structure(self):
        """Verifica que la estructura del proyecto sea válida"""
        self.print_header("VERIFICANDO ESTRUCTURA DEL PROYECTO")
        
        # Verificar project.godot
        if not (self.root / "project.godot").exists():
            self.log_error("project.godot no encontrado")
            print("   Este script debe ejecutarse desde la raíz del proyecto Godot")
            return False
        
        # Verificar carpeta addons
        if not self.addon_path.exists():
            self.log_error(f"Carpeta addon no encontrada: {self.addon_path}")
            return False
        
        # Verificar carpeta scripts
        if not self.scripts_path.exists():
            self.log_error(f"Carpeta scripts no encontrada: {self.scripts_path}")
            return False
        
        # Verificar archivos críticos
        critical_files = [
            self.scripts_path / "item.gd",
            self.scripts_path / "inventory.gd",
            self.scripts_path / "inventory_slot.gd",
            self.scripts_path / "item_database.gd"
        ]
        
        missing_files = []
        for file_path in critical_files:
            if not file_path.exists():
                missing_files.append(file_path.name)
        
        if missing_files:
            self.log_error(f"Archivos críticos faltantes: {', '.join(missing_files)}")
            return False
        
        print("✓ Estructura del proyecto válida")
        return True
    
    def delete_files(self):
        """Elimina archivos innecesarios"""
        self.print_header("ELIMINANDO ARCHIVOS INNECESARIOS")
        
        files_to_delete = []
        
        # Carpeta .vs/
        vs_folder = self.root / ".vs"
        if vs_folder.exists() and vs_folder.is_dir():
            files_to_delete.append(("folder", vs_folder, ".vs/"))
        
        # Backup
        backup_file = self.root / "autoloads" / "input_manager.gd.backup"
        if backup_file.exists() and backup_file.is_file():
            files_to_delete.append(("file", backup_file, "input_manager.gd.backup"))
        
        # crafting_system.gd (será reemplazado)
        crafting_system = self.scripts_path / "crafting_system.gd"
        if crafting_system.exists() and crafting_system.is_file():
            files_to_delete.append(("file", crafting_system, "crafting_system.gd"))
        
        # crafting_system.gd.uid
        crafting_system_uid = self.scripts_path / "crafting_system.gd.uid"
        if crafting_system_uid.exists() and crafting_system_uid.is_file():
            files_to_delete.append(("file", crafting_system_uid, "crafting_system.gd.uid"))
        
        if not files_to_delete:
            print("  No hay archivos para eliminar")
            return
        
        # Confirmar eliminación
        print(f"\nSe eliminarán {len(files_to_delete)} elemento(s):")
        for item_type, path, name in files_to_delete:
            print(f"  - {name}")
        
        # Eliminar archivos
        for item_type, path, name in files_to_delete:
            try:
                if item_type == "folder":
                    shutil.rmtree(path)
                else:
                    path.unlink()
                self.log_change(f"Eliminado: {name}")
            except PermissionError:
                self.log_error(f"Sin permisos para eliminar: {name}")
            except Exception as e:
                self.log_error(f"Error eliminando {name}: {e}")
    
    def create_crafting_manager(self):
        """Crea el archivo crafting_manager.gd"""
        self.print_header("CREANDO CRAFTING_MANAGER.GD")
        
        file_path = self.scripts_path / "crafting_manager.gd"
        
        # Verificar si ya existe
        if file_path.exists():
            self.log_warning(f"{file_path.name} ya existe, será sobrescrito")
        
        content = '''class_name CraftingManager
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
\t\tprint("⚠️ Carpeta recipes/ vacía")
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
\t# Consumir ingredientes
\tfor i in range(grid_slots.size()):
\t\tif recipe.pattern[i] != "":
\t\t\tgrid_slots[i].remove_item(1)
\t
\t# Agregar resultado
\tvar result_item = ItemDatabase.get_item(recipe.result_item_id)
\tif result_item:
\t\tinventory.add_item(result_item, recipe.result_quantity)
\t\tcrafted.emit(result_item, recipe.result_quantity)
\t\treturn true
\t
\treturn false
'''
        
        try:
            file_path.write_text(content, encoding='utf-8')
            self.log_change(f"Creado: {file_path.name}")
        except Exception as e:
            self.log_error(f"Error creando crafting_manager.gd: {e}")
            return
        
        # Crear UID
        uid_path = self.scripts_path / "crafting_manager.gd.uid"
        try:
            uid_path.write_text("uid://crafting_mgr_script\n", encoding='utf-8')
            self.log_change(f"Creado: {uid_path.name}")
        except Exception as e:
            self.log_error(f"Error creando UID: {e}")
    
    def create_crafting_table_ui(self):
        """Crea el archivo crafting_table_ui.gd"""
        self.print_header("CREANDO CRAFTING_TABLE_UI.GD")
        
        file_path = self.scripts_path / "crafting_table_ui.gd"
        
        # Verificar si ya existe
        if file_path.exists():
            self.log_warning(f"{file_path.name} ya existe, será sobrescrito")
        
        content = '''class_name CraftingTableUI
extends Control

signal closed

@export var inventory_ui: Control

var crafting_grid: GridContainer
var result_slot: Panel
var crafting_manager: CraftingManager
var crafting_slots: Array[InventorySlot] = []
var result_item: InventoryItem = null
var result_quantity: int = 0
var current_recipe: CraftingRecipe = null

# Variables para arrastrar items
var held_item: InventoryItem = null
var held_quantity: int = 0
var cursor_preview: Control = null

func _ready():
\t# Inicializar CraftingManager
\tcrafting_manager = CraftingManager.new()
\tadd_child(crafting_manager)
\t
\t# Obtener referencias
\tcrafting_grid = $Panel/MarginContainer/VBox/CraftingArea/CraftingGrid
\tresult_slot = $Panel/MarginContainer/VBox/CraftingArea/ResultArea/ResultSlot
\t
\t# Inicializar slots de crafteo
\tinitialize_crafting_grid()
\t
\t# Setup cursor preview
\tsetup_cursor_preview()
\t
\t# Conectar señales
\tcrafting_manager.recipe_found.connect(_on_recipe_found)

func initialize_crafting_grid():
\t# Crear 9 slots de crafteo (3x3)
\tfor i in range(9):
\t\tvar slot = InventorySlot.new()
\t\tcrafting_slots.append(slot)
\t\t
\t\tvar slot_ui = Panel.new()
\t\tslot_ui.custom_minimum_size = Vector2(64, 64)
\t\tslot_ui.set_meta("slot_index", i)
\t\t
\t\tvar icon = TextureRect.new()
\t\ticon.name = "Icon"
\t\ticon.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
\t\ticon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
\t\tslot_ui.add_child(icon)
\t\ticon.set_anchors_preset(Control.PRESET_FULL_RECT)
\t\t
\t\tvar quantity = Label.new()
\t\tquantity.name = "Quantity"
\t\tquantity.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
\t\tquantity.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
\t\tslot_ui.add_child(quantity)
\t\tquantity.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
\t\t
\t\tslot_ui.gui_input.connect(_on_crafting_slot_input.bind(i))
\t\tcrafting_grid.add_child(slot_ui)

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

func _on_crafting_slot_input(event: InputEvent, slot_index: int):
\tif event is InputEventMouseButton and event.pressed:
\t\tif event.button_index == MOUSE_BUTTON_LEFT:
\t\t\thandle_slot_click(slot_index)
\t\telif event.button_index == MOUSE_BUTTON_RIGHT:
\t\t\thandle_slot_right_click(slot_index)

func handle_slot_click(slot_index: int):
\tvar slot = crafting_slots[slot_index]
\t
\tif held_item == null:
\t\tif not slot.is_empty():
\t\t\theld_item = slot.item
\t\t\theld_quantity = slot.quantity
\t\t\tslot.clear()
\t\t\tupdate_crafting_slot(slot_index)
\t\t\tcheck_recipe()
\telse:
\t\tif slot.is_empty():
\t\t\tslot.add_item(held_item, held_quantity)
\t\t\theld_item = null
\t\t\theld_quantity = 0
\t\telif slot.item.id == held_item.id and held_item.is_stackable:
\t\t\tvar remaining = slot.add_item(held_item, held_quantity)
\t\t\tif remaining == 0:
\t\t\t\theld_item = null
\t\t\t\theld_quantity = 0
\t\t\telse:
\t\t\t\theld_quantity = remaining
\t\telse:
\t\t\tvar temp_item = slot.item
\t\t\tvar temp_qty = slot.quantity
\t\t\tslot.clear()
\t\t\tslot.add_item(held_item, held_quantity)
\t\t\theld_item = temp_item
\t\t\theld_quantity = temp_qty
\t\t
\t\tupdate_crafting_slot(slot_index)
\t\tcheck_recipe()

func handle_slot_right_click(slot_index: int):
\tvar slot = crafting_slots[slot_index]
\t
\tif held_item == null and not slot.is_empty():
\t\tvar half = ceili(slot.quantity / 2.0)
\t\theld_item = slot.item
\t\theld_quantity = half
\t\tslot.remove_item(half)
\t\tupdate_crafting_slot(slot_index)
\t\tcheck_recipe()

func update_crafting_slot(slot_index: int):
\tvar slot = crafting_slots[slot_index]
\tvar slot_ui = crafting_grid.get_child(slot_index)
\t
\tif slot.is_empty():
\t\tslot_ui.get_node("Icon").texture = null
\t\tslot_ui.get_node("Quantity").text = ""
\t\tslot_ui.modulate = Color(1, 1, 1, 0.3)
\telse:
\t\tslot_ui.get_node("Icon").texture = slot.item.icon
\t\tslot_ui.get_node("Quantity").text = str(slot.quantity) if slot.quantity > 1 else ""
\t\tslot_ui.modulate = Color.WHITE

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
\tprint("✓ Receta encontrada: %s" % recipe.result_item_id)

func _input(event):
\tif event.is_action_pressed("ui_cancel"):
\t\tclose_crafting_table()
\t\tget_viewport().set_input_as_handled()

func close_crafting_table():
\t# Devolver items de la grilla al inventario
\tfor slot in crafting_slots:
\t\tif not slot.is_empty() and inventory_ui and inventory_ui.inventory:
\t\t\tinventory_ui.inventory.add_item(slot.item, slot.quantity)
\t\t\tslot.clear()
\t
\t# Devolver item sostenido
\tif held_item and inventory_ui and inventory_ui.inventory:
\t\tinventory_ui.inventory.add_item(held_item, held_quantity)
\t\theld_item = null
\t\theld_quantity = 0
\t
\tclosed.emit()
\tqueue_free()
'''
        
        try:
            file_path.write_text(content, encoding='utf-8')
            self.log_change(f"Creado: {file_path.name}")
        except Exception as e:
            self.log_error(f"Error creando crafting_table_ui.gd: {e}")
            return
        
        # Crear UID
        uid_path = self.scripts_path / "crafting_table_ui.gd.uid"
        try:
            uid_path.write_text("uid://crafting_table_ui_script\n", encoding='utf-8')
            self.log_change(f"Creado: {uid_path.name}")
        except Exception as e:
            self.log_error(f"Error creando UID: {e}")
    
    def update_plugin(self):
        """Actualiza plugin.gd para registrar CraftingManager"""
        self.print_header("ACTUALIZANDO PLUGIN.GD")
        
        plugin_path = self.addon_path / "plugin.gd"
        
        if not plugin_path.exists():
            self.log_error("plugin.gd no encontrado")
            return
        
        # Crear backup del plugin original
        backup_path = plugin_path.with_suffix('.gd.backup_temp')
        try:
            shutil.copy2(plugin_path, backup_path)
            self.log_change("Backup creado: plugin.gd.backup_temp")
        except Exception as e:
            self.log_warning(f"No se pudo crear backup del plugin: {e}")
        
        new_content = '''@tool
extends EditorPlugin

func _enter_tree():
\tadd_custom_type("InventoryManager", "Node", preload("res://addons/inventory_system/scripts/inventory.gd"), preload("res://icon.svg"))
\tadd_custom_type("InventoryUI", "Control", preload("res://addons/inventory_system/scripts/inventory_ui_system.gd"), preload("res://icon.svg"))
\tadd_custom_type("Hotbar", "Node", preload("res://addons/inventory_system/scripts/hotbar.gd"), preload("res://icon.svg"))
\tadd_custom_type("HotbarUI", "Control", preload("res://addons/inventory_system/scripts/hotbar_ui_system.gd"), preload("res://icon.svg"))
\tadd_custom_type("CraftingManager", "Node", preload("res://addons/inventory_system/scripts/crafting_manager.gd"), preload("res://icon.svg"))
\tprint("✓ Inventory System activado (v2.0 completo)")

func _exit_tree():
\tremove_custom_type("InventoryManager")
\tremove_custom_type("InventoryUI")
\tremove_custom_type("Hotbar")
\tremove_custom_type("HotbarUI")
\tremove_custom_type("CraftingManager")
'''
        
        try:
            plugin_path.write_text(new_content, encoding='utf-8')
            self.log_change("Actualizado: plugin.gd (con CraftingManager)")
            
            # Eliminar backup temporal si todo salió bien
            if backup_path.exists():
                backup_path.unlink()
        except Exception as e:
            self.log_error(f"Error actualizando plugin.gd: {e}")
            # Restaurar backup si algo salió mal
            if backup_path.exists():
                try:
                    shutil.copy2(backup_path, plugin_path)
                    self.log_change("Restaurado backup de plugin.gd")
                    backup_path.unlink()
                except Exception as restore_error:
                    self.log_error(f"Error restaurando backup: {restore_error}")
    
    def create_recipes_folder(self):
        """Crea carpeta de recetas si no existe"""
        self.print_header("VERIFICANDO CARPETA RECIPES")
        
        recipes_path = self.root / "recipes"
        if not recipes_path.exists():
            try:
                recipes_path.mkdir(parents=True, exist_ok=True)
                self.log_change("Creada carpeta: recipes/")
            except Exception as e:
                self.log_error(f"Error creando carpeta recipes/: {e}")
        else:
            print("  ✓ Carpeta recipes/ ya existe")
    
    def update_gitignore(self):
        """Actualiza .gitignore para excluir archivos innecesarios"""
        self.print_header("ACTUALIZANDO .GITIGNORE")
        
        gitignore_path = self.root / ".gitignore"
        additions = [
            "\n# Visual Studio",
            ".vs/",
            "*.sln",
            "*.csproj",
            "\n# Backups",
            "*.backup",
            "*.backup_temp",
            "*~",
            "\n# OS",
            ".DS_Store",
            "Thumbs.db"
        ]
        
        try:
            if gitignore_path.exists():
                content = gitignore_path.read_text(encoding='utf-8')
            else:
                content = "# Godot 4+ specific ignores\n.godot/\n/android/\n"
            
            # Evitar duplicados
            lines_to_add = []
            for line in additions:
                if line.strip() and line not in content:
                    lines_to_add.append(line)
            
            if lines_to_add:
                content += "\n" + "\n".join(lines_to_add) + "\n"
                gitignore_path.write_text(content, encoding='utf-8')
                self.log_change(f"Actualizado: .gitignore ({len(lines_to_add)} líneas agregadas)")
            else:
                print("  ✓ .gitignore ya está actualizado")
        except Exception as e:
            self.log_error(f"Error actualizando .gitignore: {e}")
    
    def print_summary(self):
        """Imprime resumen de cambios"""
        self.print_header("RESUMEN DE CAMBIOS")
        
        print(f"✓ Cambios realizados: {len(self.changes_made)}")
        for change in self.changes_made:
            print(f"  • {change}")
        
        if self.errors:
            print(f"\n❌ ERRORES ENCONTRADOS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
            print("\n⚠️  Algunos errores pueden requerir intervención manual")
        
        print(f"\n{'='*60}")
        print("  PRÓXIMOS PASOS")
        print(f"{'='*60}\n")
        
        if not self.errors:
            print("1. Abre el proyecto en Godot 4.5")
            print("2. Ve a: Proyecto > Recargar proyecto actual")
            print("3. Verifica la consola para mensajes de ItemDatabase")
            print("4. Ejecuta: Script > Ejecutar > create_recipes.gd")
            print("5. Prueba las demos en addons/inventory_system/demo/")
            print("\n✅ ¡Sistema de inventario reparado exitosamente!\n")
        else:
            print("1. Revisa los errores mostrados arriba")
            print("2. Corrige los problemas manualmente")
            print("3. Vuelve a ejecutar este script")
            print("\n⚠️  El script se completó con errores\n")
    
    def create_backup(self):
        """Crea un backup completo antes de modificar"""
        self.print_header("CREANDO BACKUP DEL PROYECTO")
        
        backup_dir = self.root / "backup_inventory_fix"
        
        if backup_dir.exists():
            self.log_warning("Ya existe un backup anterior")
            return
        
        try:
            # Crear carpeta de backup
            backup_dir.mkdir(exist_ok=True)
            
            # Copiar archivos críticos
            files_to_backup = [
                self.addon_path / "plugin.gd",
                self.scripts_path / "crafting_system.gd",
                self.root / ".gitignore"
            ]
            
            for file_path in files_to_backup:
                if file_path.exists():
                    backup_file = backup_dir / file_path.name
                    shutil.copy2(file_path, backup_file)
            
            self.log_change(f"Backup creado en: {backup_dir}")
        except Exception as e:
            self.log_warning(f"No se pudo crear backup: {e}")
    
    def verify_python_version(self):
        """Verifica que la versión de Python sea compatible"""
        if sys.version_info < (3, 6):
            print("❌ ERROR: Se requiere Python 3.6 o superior")
            print(f"   Versión actual: {sys.version}")
            return False
        return True
    
    def run(self):
        """Ejecuta todas las correcciones"""
        print("\n" + "🔧" * 30)
        print("  REPARADOR DEL SISTEMA DE INVENTARIO")
        print("  Godot 4.5 - Versión 2.0")
        print("🔧" * 30)
        
        # Verificar versión de Python
        if not self.verify_python_version():
            return False
        
        # Verificar estructura del proyecto
        if not self.verify_project_structure():
            return False
        
        # Preguntar confirmación
        print("\n⚠️  ADVERTENCIA: Este script modificará archivos en tu proyecto")
        response = input("¿Deseas continuar? (s/n): ").lower().strip()
        
        if response not in ['s', 'si', 'y', 'yes']:
            print("\n❌ Operación cancelada por el usuario\n")
            return False
        
        # Crear backup
        self.create_backup()
        
        # Ejecutar correcciones
        try:
            self.delete_files()
            self.create_crafting_manager()
            self.create_crafting_table_ui()
            self.update_plugin()
            self.create_recipes_folder()
            self.update_gitignore()
        except KeyboardInterrupt:
            print("\n\n❌ Operación interrumpida por el usuario")
            print("⚠️  Algunos cambios pueden haberse aplicado parcialmente\n")
            return False
        except Exception as e:
            self.log_error(f"Error inesperado: {e}")
            return False
        
        # Resumen
        self.print_summary()
        
        return len(self.errors) == 0

def main():
    """Función principal"""
    try:
        fixer = InventoryFixer()
        success = fixer.run()
        
        # Código de salida
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()