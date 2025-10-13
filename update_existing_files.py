#!/usr/bin/env python3
"""
Actualizador de Archivos Existentes
Modifica inventory.gd e inventory_slot_ui.gd con las nuevas funciones Minecraft
"""

import os
from pathlib import Path

# Colores para consola
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def find_project_root() -> Path:
    """Busca el directorio raíz del proyecto"""
    current = Path.cwd()
    for _ in range(5):
        if (current / "project.godot").exists():
            return current
        current = current.parent
    return Path.cwd()

PROJECT_ROOT = find_project_root()

def update_inventory_gd():
    """Actualiza inventory.gd con sistema de armadura"""
    print(f"\n{Colors.CYAN}Actualizando inventory.gd...{Colors.RESET}")
    
    inventory_path = PROJECT_ROOT / "addons" / "inventory_system" / "scripts" / "inventory.gd"
    
    if not inventory_path.exists():
        print(f"{Colors.RED}✗ No se encontró inventory.gd{Colors.RESET}")
        return False
    
    content = inventory_path.read_text(encoding='utf-8')
    
    # Verificar si ya tiene el sistema de armadura
    if "armor_slots" in content:
        print(f"{Colors.YELLOW}⚠ inventory.gd ya tiene sistema de armadura{Colors.RESET}")
        return True
    
    # Código para agregar al final
    armor_system = """

# ============================================
# SISTEMA DE ARMADURA (Agregado automáticamente)
# ============================================

enum ArmorSlot { HELMET = 0, CHESTPLATE = 1, LEGGINGS = 2, BOOTS = 3 }

var armor_slots: Array[InventorySlot] = []
var offhand_slot: InventorySlot = null

func initialize_armor_slots():
\tarmor_slots.clear()
\tfor i in range(4):
\t\tarmor_slots.append(InventorySlot.new())
\toffhand_slot = InventorySlot.new()

func equip_armor(item: InventoryItem, slot_type: ArmorSlot) -> bool:
\tif item == null or item.item_type != InventoryItem.ItemType.EQUIPMENT:
\t\treturn false
\t
\tvar armor_type = item.custom_data.get("armor_type", "")
\tvar expected_type = ["helmet", "chestplate", "leggings", "boots"][slot_type]
\t
\tif armor_type != expected_type:
\t\treturn false
\t
\tif not armor_slots[slot_type].is_empty():
\t\tvar old_armor = armor_slots[slot_type].item
\t\tarmor_slots[slot_type].clear()
\t\tadd_item(old_armor, 1)
\t
\tarmor_slots[slot_type].add_item(item, 1)
\tremove_item(item, 1)
\tinventory_changed.emit()
\treturn true

func unequip_armor(slot_type: ArmorSlot) -> bool:
\tif armor_slots[slot_type].is_empty():
\t\treturn false
\t
\tvar armor = armor_slots[slot_type].item
\tarmor_slots[slot_type].clear()
\tadd_item(armor, 1)
\tinventory_changed.emit()
\treturn true

func get_equipped_armor(slot_type: ArmorSlot) -> InventoryItem:
\treturn armor_slots[slot_type].item if not armor_slots[slot_type].is_empty() else null

func get_total_armor_value() -> int:
\tvar total = 0
\tfor armor_slot in armor_slots:
\t\tif not armor_slot.is_empty():
\t\t\ttotal += armor_slot.item.custom_data.get("armor_value", 0)
\treturn total

func equip_offhand(item: InventoryItem) -> bool:
\tif item == null:
\t\treturn false
\t
\tif not offhand_slot.is_empty():
\t\tvar old_item = offhand_slot.item
\t\toffhand_slot.clear()
\t\tadd_item(old_item, 1)
\t
\toffhand_slot.add_item(item, 1)
\tremove_item(item, 1)
\tinventory_changed.emit()
\treturn true

func unequip_offhand() -> bool:
\tif offhand_slot.is_empty():
\t\treturn false
\t
\tvar item = offhand_slot.item
\toffhand_slot.clear()
\tadd_item(item, 1)
\tinventory_changed.emit()
\treturn true
"""
    
    # Agregar al final del archivo
    content += armor_system
    
    # Guardar
    inventory_path.write_text(content, encoding='utf-8')
    print(f"{Colors.GREEN}✓ inventory.gd actualizado con sistema de armadura{Colors.RESET}")
    return True


def update_inventory_slot_ui_gd():
    """Actualiza inventory_slot_ui.gd con controles Minecraft"""
    print(f"\n{Colors.CYAN}Actualizando inventory_slot_ui.gd...{Colors.RESET}")
    
    slot_ui_path = PROJECT_ROOT / "addons" / "inventory_system" / "scripts" / "inventory_slot_ui.gd"
    
    if not slot_ui_path.exists():
        print(f"{Colors.RED}✗ No se encontró inventory_slot_ui.gd{Colors.RESET}")
        return False
    
    content = slot_ui_path.read_text(encoding='utf-8')
    
    # Verificar si ya tiene las funciones
    if "_quick_move_item" in content:
        print(f"{Colors.YELLOW}⚠ inventory_slot_ui.gd ya tiene controles Minecraft{Colors.RESET}")
        return True
    
    # Encontrar la función _gui_input existente
    if "func _gui_input(event):" not in content:
        print(f"{Colors.RED}✗ No se encontró función _gui_input en inventory_slot_ui.gd{Colors.RESET}")
        return False
    
    # Reemplazar _gui_input con la versión mejorada
    new_gui_input = """func _gui_input(event):
\tif not inventory or index < 0 or index >= inventory.slots.size():
\t\treturn
\t
\tif event is InputEventMouseButton and event.pressed:
\t\tif event.button_index == MOUSE_BUTTON_LEFT:
\t\t\tif event.shift_pressed:
\t\t\t\t# SHIFT + CLICK: Quick move
\t\t\t\t_quick_move_item()
\t\t\telse:
\t\t\t\tif not inventory.slots[index].is_empty():
\t\t\t\t\tslot_clicked.emit(index, inventory.slots[index].item)
\t\t
\t\telif event.button_index == MOUSE_BUTTON_RIGHT:
\t\t\tif not inventory.slots[index].is_empty():
\t\t\t\tslot_right_clicked.emit(index, inventory.slots[index].item)
\t\t
\t\telif event.button_index == MOUSE_BUTTON_MIDDLE:
\t\t\t# MIDDLE CLICK: Pick block (creative)
\t\t\tif not inventory.slots[index].is_empty():
\t\t\t\t_pick_block()"""
    
    # Buscar y reemplazar la función _gui_input
    import re
    pattern = r'func _gui_input\(event\):.*?(?=\nfunc|\n\nfunc|\Z)'
    content = re.sub(pattern, new_gui_input, content, flags=re.DOTALL)
    
    # Agregar las funciones helper al final
    minecraft_functions = """

# ============================================
# CONTROLES MINECRAFT (Agregado automáticamente)
# ============================================

func _quick_move_item():
\t\"\"\"Mueve items rápidamente entre hotbar e inventario principal\"\"\"
\tvar slot = inventory.slots[index]
\tif slot.is_empty():
\t\treturn
\t
\t# Si está en hotbar (0-8), mover a inventario principal (9-35)
\t# Si está en inventario, mover a hotbar
\tvar target_start = 9 if index < 9 else 0
\tvar target_end = 36 if index < 9 else 9
\t
\tfor i in range(target_start, target_end):
\t\tif i >= inventory.slots.size():
\t\t\tbreak
\t\t
\t\tif inventory.slots[i].is_empty():
\t\t\t# Slot vacío: mover todo
\t\t\tinventory.slots[i].add_item(slot.item, slot.quantity)
\t\t\tslot.clear()
\t\t\tbreak
\t\telif inventory.slots[i].item.id == slot.item.id and inventory.slots[i].item.is_stackable:
\t\t\t# Mismo item: stackear
\t\t\tvar remaining = inventory.slots[i].add_item(slot.item, slot.quantity)
\t\t\tif remaining == 0:
\t\t\t\tslot.clear()
\t\t\t\tbreak
\t\t\telse:
\t\t\t\tslot.quantity = remaining
\t
\tinventory.inventory_changed.emit()

func _pick_block():
\t\"\"\"Copia el item al hotbar (modo creativo)\"\"\"
\tvar slot = inventory.slots[index]
\tif slot.is_empty():
\t\treturn
\t
\t# Buscar slot vacío o el mismo item en el hotbar
\tfor i in range(9):
\t\tif inventory.slots[i].is_empty():
\t\t\tinventory.slots[i].add_item(slot.item, slot.item.max_stack)
\t\t\tinventory.inventory_changed.emit()
\t\t\tbreak
\t\telif inventory.slots[i].item.id == slot.item.id:
\t\t\t# Ya tiene el item
\t\t\tbreak
"""
    
    content += minecraft_functions
    
    # Guardar
    slot_ui_path.write_text(content, encoding='utf-8')
    print(f"{Colors.GREEN}✓ inventory_slot_ui.gd actualizado con controles Minecraft{Colors.RESET}")
    return True


def update_plugin_gd():
    """Actualiza plugin.gd para registrar nuevos tipos"""
    print(f"\n{Colors.CYAN}Actualizando plugin.gd...{Colors.RESET}")
    
    plugin_path = PROJECT_ROOT / "addons" / "inventory_system" / "plugin.gd"
    
    if not plugin_path.exists():
        print(f"{Colors.YELLOW}⚠ No se encontró plugin.gd{Colors.RESET}")
        return True  # No es crítico
    
    content = plugin_path.read_text(encoding='utf-8')
    
    # Verificar si ya tiene CraftingManager
    if "CraftingManager" in content:
        print(f"{Colors.YELLOW}⚠ plugin.gd ya registra CraftingManager{Colors.RESET}")
        return True
    
    # Buscar la función _enter_tree
    if "func _enter_tree():" in content:
        # Agregar registros después de las líneas existentes
        new_registrations = """\tadd_custom_type("CraftingManager", "Node", preload("res://addons/inventory_system/scripts/crafting_manager.gd"), preload("res://icon.svg"))
\tadd_custom_type("CraftingTableUI", "Control", preload("res://addons/inventory_system/scripts/crafting_table_ui.gd"), preload("res://icon.svg"))
"""
        
        # Encontrar el final de _enter_tree
        tree_start = content.find("func _enter_tree():")
        if tree_start != -1:
            # Buscar la siguiente función o el final
            next_func = content.find("\nfunc ", tree_start + 1)
            if next_func == -1:
                next_func = len(content)
            
            # Insertar antes de la siguiente función
            content = content[:next_func] + new_registrations + content[next_func:]
            
            plugin_path.write_text(content, encoding='utf-8')
            print(f"{Colors.GREEN}✓ plugin.gd actualizado{Colors.RESET}")
    
    return True


def create_demo_scene():
    """Crea la escena de demo completa"""
    print(f"\n{Colors.CYAN}Creando escena de demo...{Colors.RESET}")
    
    demo_scene = """[gd_scene load_steps=4 format=3 uid="uid://demo_minecraft"]

[ext_resource type="Script" path="res://demos/minecraft_demo.gd" id="1"]
[ext_resource type="PackedScene" uid="uid://dylkpea7x0fj6" path="res://addons/inventory_system/scenes/inventory_ui.tscn" id="2"]
[ext_resource type="PackedScene" uid="uid://dxeyi01lth3tr" path="res://addons/inventory_system/scenes/hotbar_ui.tscn" id="3"]

[node name="MinecraftDemo" type="Node2D"]
script = ExtResource("1")

[node name="InventoryUI" parent="." instance=ExtResource("2")]
visible = false
offset_left = 200.0
offset_top = 150.0
offset_right = 200.0
offset_bottom = 150.0

[node name="HotbarUI" parent="." instance=ExtResource("3")]
anchors_preset = 0
anchor_left = 0.0
anchor_top = 0.0
anchor_right = 0.0
anchor_bottom = 0.0
offset_left = 200.0
offset_top = 520.0
offset_right = 600.0
offset_bottom = 600.0
grow_horizontal = 1
grow_vertical = 1

[node name="InfoLabel" type="Label" parent="."]
offset_left = 20.0
offset_top = 20.0
offset_right = 600.0
offset_bottom = 60.0
theme_override_colors/font_color = Color(0.2, 1, 0.3, 1)
theme_override_colors/font_outline_color = Color(0, 0, 0, 1)
theme_override_constants/outline_size = 4
theme_override_font_sizes/font_size = 20
text = "Presiona E para inventario | Enter para mesa de trabajo"

[node name="ControlsLabel" type="Label" parent="."]
offset_left = 20.0
offset_top = 70.0
offset_right = 400.0
offset_bottom = 300.0
theme_override_colors/font_outline_color = Color(0, 0, 0, 1)
theme_override_constants/outline_size = 2
theme_override_font_sizes/font_size = 14
text = "🎮 CONTROLES MINECRAFT

INVENTARIO:
• E: Abrir/Cerrar
• Click Izq: Tomar/Colocar
• Click Der: Dividir stack
• Shift+Click: Mover rápido
• Q: Soltar 1 item

HOTBAR:
• 1-9: Seleccionar slot
• Scroll: Cambiar slot

CRAFTING:
• Enter: Mesa de trabajo
• Arrastra items a grilla"
"""
    
    demo_path = PROJECT_ROOT / "demos" / "minecraft_demo.tscn"
    demo_path.parent.mkdir(parents=True, exist_ok=True)
    demo_path.write_text(demo_scene, encoding='utf-8')
    print(f"{Colors.GREEN}✓ Escena minecraft_demo.tscn creada{Colors.RESET}")
    return True


def main():
    """Función principal del actualizador"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'ACTUALIZADOR DE ARCHIVOS EXISTENTES':^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")
    
    print(f"{Colors.BLUE}ℹ Proyecto: {PROJECT_ROOT}{Colors.RESET}\n")
    
    success = True
    
    # Actualizar archivos
    success &= update_inventory_gd()
    success &= update_inventory_slot_ui_gd()
    success &= update_plugin_gd()
    success &= create_demo_scene()
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    if success:
        print(f"{Colors.GREEN}✓ Actualización completada exitosamente{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Próximos pasos:{Colors.RESET}")
        print("1. Ejecuta el instalador principal: python install_minecraft_system.py")
        print("2. Abre Godot y ejecuta create_recipes.gd")
        print("3. Prueba la demo: demos/minecraft_demo.tscn")
    else:
        print(f"{Colors.RED}✗ Algunos archivos no se pudieron actualizar{Colors.RESET}")
        print(f"{Colors.YELLOW}Revisa los mensajes anteriores{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())