#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrección de tipos de clase en scripts de UI
"""

from pathlib import Path
import re

def fix_inventory_ui_system():
    """Corrige inventory_ui_system.gd para que la clase se reconozca correctamente"""
    
    root = Path.cwd()
    file_path = root / "addons" / "inventory_system" / "scripts" / "inventory_ui_system.gd"
    
    if not file_path.exists():
        print(f"❌ No se encontró: {file_path}")
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Verificar si ya tiene @tool al inicio
        if not content.strip().startswith('@tool'):
            content = '@tool\n' + content
        
        # Asegurar que class_name esté antes de extends
        if 'class_name InventoryUI' not in content:
            content = content.replace(
                'extends Control',
                'class_name InventoryUI\nextends Control'
            )
        
        # Remover @tool duplicado si existe
        lines = content.split('\n')
        tool_count = sum(1 for line in lines if line.strip() == '@tool')
        if tool_count > 1:
            # Mantener solo el primero
            new_lines = []
            tool_found = False
            for line in lines:
                if line.strip() == '@tool':
                    if not tool_found:
                        new_lines.append(line)
                        tool_found = True
                else:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
        
        file_path.write_text(content, encoding='utf-8')
        print("✓ Corregido inventory_ui_system.gd")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def fix_hotbar_ui_system():
    """Corrige hotbar_ui_system.gd"""
    
    root = Path.cwd()
    file_path = root / "addons" / "inventory_system" / "scripts" / "hotbar_ui_system.gd"
    
    if not file_path.exists():
        print(f"❌ No se encontró: {file_path}")
        return False
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Verificar si ya tiene @tool al inicio
        if not content.strip().startswith('@tool'):
            content = '@tool\n' + content
        
        # Asegurar que class_name esté antes de extends
        if 'class_name HotbarUI' not in content:
            content = content.replace(
                'extends Control',
                'class_name HotbarUI\nextends Control',
                1  # Solo la primera ocurrencia (la clase principal)
            )
        
        # Remover @tool duplicado
        lines = content.split('\n')
        tool_count = sum(1 for line in lines if line.strip() == '@tool')
        if tool_count > 1:
            new_lines = []
            tool_found = False
            for line in lines:
                if line.strip() == '@tool':
                    if not tool_found:
                        new_lines.append(line)
                        tool_found = True
                else:
                    new_lines.append(line)
            content = '\n'.join(new_lines)
        
        file_path.write_text(content, encoding='utf-8')
        print("✓ Corregido hotbar_ui_system.gd")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def fix_demo_scripts():
    """Corrige los scripts de demo que usan tipos incorrectos"""
    
    root = Path.cwd()
    addon_path = root / "addons" / "inventory_system"
    
    demo_files = [
        addon_path / "demo" / "demo.gd",
        addon_path / "demo" / "demo_with_hotbar.gd"
    ]
    
    for demo_file in demo_files:
        if not demo_file.exists():
            continue
        
        try:
            content = demo_file.read_text(encoding='utf-8')
            
            # Cambiar tipos específicos de script a nombres de clase
            replacements = [
                (r'@onready var inventory_ui:\s*inventory_ui_system\.gd', 
                 '@onready var inventory_ui: InventoryUI'),
                (r'@onready var hotbar_ui:\s*hotbar_ui_system\.gd',
                 '@onready var hotbar_ui: HotbarUI'),
                # Forma alternativa
                (r'var inventory_ui:\s*inventory_ui_system\.gd',
                 'var inventory_ui: InventoryUI'),
                (r'var hotbar_ui:\s*hotbar_ui_system\.gd',
                 'var hotbar_ui: HotbarUI'),
            ]
            
            modified = False
            for pattern, replacement in replacements:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    modified = True
            
            if modified:
                demo_file.write_text(content, encoding='utf-8')
                print(f"✓ Corregido {demo_file.name}")
        
        except Exception as e:
            print(f"⚠️  Error en {demo_file.name}: {e}")
    
    return True

def verify_class_names():
    """Verifica que todos los scripts tengan class_name correcto"""
    
    root = Path.cwd()
    scripts_path = root / "addons" / "inventory_system" / "scripts"
    
    expected_classes = {
        "inventory_ui_system.gd": "InventoryUI",
        "hotbar_ui_system.gd": "HotbarUI",
        "inventory.gd": "InventoryManager",
        "hotbar.gd": "Hotbar",
        "item.gd": "InventoryItem",
        "inventory_slot.gd": "InventorySlot",
        "crafting_recipe.gd": "CraftingRecipe",
        "crafting_manager.gd": "CraftingManager",
        "crafting_table_ui.gd": "CraftingTableUI",
    }
    
    print("\n📋 Verificando class_name en scripts...")
    
    all_ok = True
    for filename, expected_class in expected_classes.items():
        file_path = scripts_path / filename
        
        if not file_path.exists():
            print(f"  ⚠️  {filename} no existe")
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            if f"class_name {expected_class}" in content:
                print(f"  ✓ {filename} → {expected_class}")
            else:
                print(f"  ❌ {filename} → FALTA class_name {expected_class}")
                all_ok = False
        
        except Exception as e:
            print(f"  ❌ Error leyendo {filename}: {e}")
            all_ok = False
    
    return all_ok

def main():
    print("\n🔧 CORRECCIÓN DE TIPOS DE CLASE\n")
    
    # Verificar proyecto
    if not Path("project.godot").exists():
        print("❌ ERROR: Ejecuta desde la raíz del proyecto")
        return False
    
    print("🔨 Corrigiendo scripts de UI...")
    success = True
    success = fix_inventory_ui_system() and success
    success = fix_hotbar_ui_system() and success
    
    print("\n🔨 Corrigiendo scripts de demo...")
    success = fix_demo_scripts() and success
    
    print()
    success = verify_class_names() and success
    
    # Instrucciones finales
    print("\n" + "=" * 60)
    print("  PRÓXIMOS PASOS")
    print("=" * 60)
    print("\n1. En Godot: Proyecto > Recargar proyecto actual")
    print("2. Verifica que no haya errores en la consola")
    print("3. Abre: addons/inventory_system/demo/demo.tscn")
    print("4. Ejecuta la escena (F5 o botón Play)")
    print("5. Presiona ESC para abrir el inventario")
    
    if success:
        print("\n✅ ¡Todos los tipos corregidos!\n")
    else:
        print("\n⚠️  Algunos problemas detectados, revisa los mensajes arriba\n")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)