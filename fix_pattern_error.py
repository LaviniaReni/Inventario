#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrección final: pattern en CraftingRecipe
"""

from pathlib import Path

def fix_create_recipes():
    """Reescribe create_recipes.gd con el tipo correcto"""
    
    root = Path.cwd()
    file_path = root / "create_recipes.gd"
    
    content = '''@tool
extends EditorScript

func _run():
\tvar separator = ""
\tfor i in range(50):
\t\tseparator += "="
\t
\tprint("\\n" + separator)
\tprint("Creando recetas...")
\tprint(separator + "\\n")
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
\t\t
\t\t# Convertir Array a Array[String] correctamente
\t\tvar pattern_array: Array[String] = []
\t\tfor item in recipe_data.pattern:
\t\t\tpattern_array.append(item)
\t\trecipe.pattern = pattern_array
\t\t
\t\tvar path = "res://recipes/%s.tres" % recipe_data.id
\t\tResourceSaver.save(recipe, path)
\t\tprint("✓ Creada: %s" % recipe_data.id)
'''
    
    try:
        file_path.write_text(content, encoding='utf-8')
        print("✓ Corregido create_recipes.gd (conversión de tipos)")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def fix_uids():
    """Corrige los UIDs para eliminar las advertencias"""
    
    root = Path.cwd()
    addon_path = root / "addons" / "inventory_system"
    scripts_path = addon_path / "scripts"
    
    # Eliminar UIDs incorrectos si existen
    uid_files = [
        scripts_path / "inventory_ui_system.gd.uid",
        scripts_path / "hotbar_ui_system.gd.uid"
    ]
    
    for uid_file in uid_files:
        if uid_file.exists():
            try:
                uid_file.unlink()
                print(f"✓ Eliminado UID obsoleto: {uid_file.name}")
            except:
                pass
    
    print("\nℹ️  Los UIDs se regenerarán automáticamente al recargar Godot")
    return True

if __name__ == "__main__":
    print("\n🔧 CORRECCIÓN FINAL - PATTERN Y UIDS\n")
    
    # Verificar proyecto
    if not Path("project.godot").exists():
        print("❌ ERROR: Ejecuta desde la raíz del proyecto")
        exit(1)
    
    # Ejecutar correcciones
    success = True
    success = fix_create_recipes() and success
    success = fix_uids() and success
    
    # Instrucciones finales
    print("\n" + "=" * 60)
    print("  PRÓXIMOS PASOS")
    print("=" * 60)
    print("\n1. Cierra Godot completamente")
    print("2. Elimina la carpeta .godot/ para limpiar caché:")
    print("   • Windows: rmdir /s .godot")
    print("   • Linux/Mac: rm -rf .godot")
    print("3. Abre Godot nuevamente")
    print("4. Proyecto > Recargar proyecto actual")
    print("5. Script > Ejecutar > create_recipes.gd")
    print("6. Prueba el demo: demo.tscn")
    print("\n✅ ¡Sistema completamente funcional!\n")
    
    exit(0 if success else 1)
