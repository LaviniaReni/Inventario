#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir TODOS los errores del Sistema de Inventario
Ejecutar: python fix_all_errors.py
"""

import sys
from pathlib import Path

class ErrorFixer:
    def __init__(self):
        self.root = Path.cwd()
        self.addon_path = self.root / "addons" / "inventory_system"
        self.scripts_path = self.addon_path / "scripts"
        self.changes = []
    
    def log(self, msg):
        print(f"✓ {msg}")
        self.changes.append(msg)
    
    def fix_test_utilities(self):
        """Corrige test_utilities.gd - problema con multiplicación de strings"""
        print("\n🔧 Corrigiendo test_utilities.gd...")
        
        file_path = self.scripts_path / "test_utilities.gd"
        if not file_path.exists():
            print("  ⚠️  Archivo no encontrado, omitiendo")
            return
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Reemplazar todas las multiplicaciones de string por repetición manual
            replacements = [
                ('print("\\n" + "=" * 60)', 'print("\\n" + "=".repeat(60))'),
                ('print("=" * 60 + "\\n")', 'print("=".repeat(60) + "\\n")'),
                ('separator = ""', 'var separator = ""'),
                ('for i in range(60):', 'for i in range(60):'),
                ('separator += "="', '\tseparator += "="'),
            ]
            
            # Buscar y reemplazar patrones problemáticos
            lines = content.split('\n')
            fixed_lines = []
            
            for line in lines:
                # Corregir multiplicación de strings
                if '"=" * ' in line or '"🔧" * ' in line:
                    # Extraer el operador y número
                    if '"=" * ' in line:
                        line = line.replace('"=" * ', '("=" * ')
                        line = line.replace(')', '.repeat())')
                        # Forma correcta en GDScript
                        import re
                        pattern = r'"(.)" \* (\d+)'
                        def replace_func(match):
                            char = match.group(1)
                            count = match.group(2)
                            return f'"{char}".repeat({count})'
                        line = re.sub(pattern, replace_func, line)
                
                fixed_lines.append(line)
            
            new_content = '\n'.join(fixed_lines)
            file_path.write_text(new_content, encoding='utf-8')
            self.log("Corregido test_utilities.gd (operadores de string)")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    def fix_create_recipes(self):
        """Corrige create_recipes.gd"""
        print("\n🔧 Corrigiendo create_recipes.gd...")
        
        file_path = self.root / "create_recipes.gd"
        if not file_path.exists():
            print("  ⚠️  Archivo no encontrado, omitiendo")
            return
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Reemplazar multiplicación de strings
            import re
            pattern = r'"(.)" \* (\d+)'
            def replace_func(match):
                char = match.group(1)
                count = match.group(2)
                return f'"{char}".repeat({count})'
            
            new_content = re.sub(pattern, replace_func, content)
            
            file_path.write_text(new_content, encoding='utf-8')
            self.log("Corregido create_recipes.gd")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    def create_missing_uids(self):
        """Crea los archivos UID faltantes"""
        print("\n🔧 Creando UIDs faltantes...")
        
        uid_files = [
            (self.scripts_path / "inventory_ui_system.gd.uid", "uid://btr0um11tppk1"),
            (self.scripts_path / "hotbar_ui_system.gd.uid", "uid://d3i2mymi0xfti"),
        ]
        
        for file_path, uid in uid_files:
            if file_path.exists():
                continue
            
            try:
                file_path.write_text(f"{uid}\n", encoding='utf-8')
                self.log(f"Creado {file_path.name}")
            except Exception as e:
                print(f"  ❌ Error creando {file_path.name}: {e}")
    
    def fix_test_utilities_complete(self):
        """Reescribe test_utilities.gd completamente sin errores"""
        print("\n🔧 Reescribiendo test_utilities.gd (método alternativo)...")
        
        file_path = self.scripts_path / "test_utilities.gd"
        
        content = '''@tool
extends EditorScript

## Script de utilidades para testing del sistema de inventario
## Uso: Script > Ejecutar > test_utilities.gd

func _run():
\tvar separator = ""
\tfor i in range(60):
\t\tseparator += "="
\t
\tprint("\\n" + separator)
\tprint("🧪 UTILIDADES DE TESTING - INVENTORY SYSTEM")
\tprint(separator + "\\n")
\t
\tshow_statistics()

func show_statistics():
\t"""Muestra estadísticas del proyecto"""
\tprint("📊 ESTADÍSTICAS DEL PROYECTO\\n")
\t
\tvar separator = ""
\tfor i in range(60):
\t\tseparator += "="
\tprint(separator)
\t
\t# Contar items
\tvar items_count = count_files("res://addons/inventory_system/demo/demo_items/", ".tres")
\tprint("📦 Items totales: %d" % items_count)
\t
\t# Contar recetas
\tvar recipes_count = count_files("res://recipes/", ".tres")
\tprint("🔨 Recetas totales: %d" % recipes_count)
\t
\t# Contar escenas demo
\tvar demos_count = count_files("res://addons/inventory_system/demo/", ".tscn")
\tprint("🎮 Demos disponibles: %d" % demos_count)
\t
\tprint(separator + "\\n")
\t
\t# Listar demos
\tprint("🎮 DEMOS DISPONIBLES:")
\tlist_demos()
\t
\tprint("\\n✅ Análisis completado\\n")

func count_files(path: String, extension: String) -> int:
\t"""Cuenta archivos con una extensión específica"""
\tif not DirAccess.dir_exists_absolute(path):
\t\treturn 0
\t
\tvar count = 0
\tvar dir = DirAccess.open(path)
\tif dir:
\t\tdir.list_dir_begin()
\t\tvar file_name = dir.get_next()
\t\twhile file_name != "":
\t\t\tif file_name.ends_with(extension):
\t\t\t\tcount += 1
\t\t\tfile_name = dir.get_next()
\t\tdir.list_dir_end()
\t
\treturn count

func list_demos():
\t"""Lista todas las demos disponibles"""
\tvar demos = [
\t\t{
\t\t\t"path": "res://addons/inventory_system/demo/demo.tscn",
\t\t\t"name": "Demo Básico",
\t\t\t"desc": "Inventario simple con controles básicos"
\t\t},
\t\t{
\t\t\t"path": "res://addons/inventory_system/demo/demo_hotbar.tscn",
\t\t\t"name": "Demo con Hotbar",
\t\t\t"desc": "Inventario + Hotbar con selección de slots"
\t\t}
\t]
\t
\tfor demo in demos:
\t\tif FileAccess.file_exists(demo.path):
\t\t\tprint("  ✓ %s" % demo.name)
\t\t\tprint("    %s" % demo.desc)
\t\t\tprint("    Ruta: %s\\n" % demo.path)
\t\telse:
\t\t\tprint("  ❌ %s (archivo no encontrado)" % demo.name)
\t\t\tprint("    Ruta esperada: %s\\n" % demo.path)
'''
        
        try:
            file_path.write_text(content, encoding='utf-8')
            self.log("Reescrito test_utilities.gd sin errores")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    def fix_create_recipes_complete(self):
        """Reescribe create_recipes.gd sin errores"""
        print("\n🔧 Reescribiendo create_recipes.gd...")
        
        file_path = self.root / "create_recipes.gd"
        
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
\t\trecipe.pattern = recipe_data.pattern
\t\t
\t\tvar path = "res://recipes/%s.tres" % recipe_data.id
\t\tResourceSaver.save(recipe, path)
\t\tprint("✓ Creada: %s" % recipe_data.id)
'''
        
        try:
            file_path.write_text(content, encoding='utf-8')
            self.log("Reescrito create_recipes.gd sin errores")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    def run(self):
        """Ejecuta todas las correcciones"""
        print("\n" + "🔧" * 30)
        print("  CORRECCIÓN DE ERRORES DE SINTAXIS")
        print("  Sistema de Inventario - Godot 4.5")
        print("🔧" * 30)
        
        # Verificar proyecto
        if not (self.root / "project.godot").exists():
            print("\n❌ ERROR: project.godot no encontrado")
            print("   Ejecuta desde la raíz del proyecto\n")
            return False
        
        # Ejecutar correcciones
        self.fix_test_utilities_complete()
        self.fix_create_recipes_complete()
        self.create_missing_uids()
        
        # Resumen
        print("\n" + "=" * 60)
        print("  RESUMEN")
        print("=" * 60)
        print(f"\n✅ Cambios realizados: {len(self.changes)}")
        for change in self.changes:
            print(f"  • {change}")
        
        print("\n" + "=" * 60)
        print("  PRÓXIMOS PASOS")
        print("=" * 60)
        print("\n1. Abre Godot 4.5")
        print("2. Proyecto > Recargar proyecto actual")
        print("3. Ejecuta: Script > Ejecutar > create_recipes.gd")
        print("4. Verifica que no hay errores en la consola")
        print("5. Prueba el demo: addons/inventory_system/demo/demo.tscn")
        print("\n✅ ¡Errores corregidos!\n")
        
        return True

if __name__ == "__main__":
    fixer = ErrorFixer()
    success = fixer.run()
    sys.exit(0 if success else 1)