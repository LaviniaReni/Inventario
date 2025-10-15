#!/usr/bin/env python3
"""
Corrección rápida de todos los errores de sintaxis
"""

import re
from pathlib import Path

def fix_string_multiplication(file_path):
    """Corrige el error de multiplicación de strings"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Patrón 1: print("\n" + "="*60)
        content = re.sub(r'print\("\\n" \+ "="\*(\d+)\)', r'print("\\n" + "=" * \1)', content)
        
        # Patrón 2: print("="*60 + "\n")
        content = re.sub(r'print\("="\*(\d+) \+ "\\n"\)', r'print("=" * \1 + "\\n")', content)
        
        # Patrón 3: "="*60 (general)
        content = re.sub(r'"="\*(\d+)', r'"=" * \1', content)
        
        # Patrón 4: solo para estar seguros
        content = content.replace('"="*', '"=" *')
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"❌ Error en {file_path}: {e}")
        return False

def main():
    """Función principal"""
    print("\n🔧 CORRECCIÓN RÁPIDA DE ERRORES DE SINTAXIS\n")
    
    # Archivos a corregir
    files = [
        "autoloads/input_manager.gd",
        "addons/inventory_system/scripts/test_utilities.gd",
        "create_recipes.gd"
    ]
    
    base_path = Path.cwd()
    
    if not (base_path / "project.godot").exists():
        print("❌ No se encontró project.godot")
        print("   Ejecuta desde la raíz del proyecto\n")
        return
    
    fixed_count = 0
    
    for file_rel in files:
        file_path = base_path / file_rel
        
        if not file_path.exists():
            print(f"⚠️  No encontrado: {file_rel}")
            continue
        
        print(f"🔍 Verificando: {file_rel}")
        
        if fix_string_multiplication(file_path):
            print(f"✅ Corregido: {file_rel}")
            fixed_count += 1
        else:
            print(f"ℹ️  Sin cambios: {file_rel}")
    
    print(f"\n{'='*60}")
    print(f"✅ Archivos corregidos: {fixed_count}")
    print(f"{'='*60}\n")
    
    if fixed_count > 0:
        print("📋 Próximos pasos:")
        print("  1. Guarda todos los archivos en Godot")
        print("  2. Ve a Proyecto > Recargar proyecto actual")
        print("  3. O simplemente cierra y reabre Godot")
    
    print()

if __name__ == "__main__":
    main()
