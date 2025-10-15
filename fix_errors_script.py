#!/usr/bin/env python3
"""
Script para corregir errores de consolidación
"""

import os
from pathlib import Path
import shutil

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

def fix_input_manager(base_path):
    """Corrige los errores de input_manager.gd"""
    print_header("CORRIGIENDO INPUT_MANAGER.GD")
    
    file_path = Path(base_path) / "autoloads" / "input_manager.gd"
    
    if not file_path.exists():
        print_error(f"No se encontró: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar las líneas problemáticas
        fixes = [
            ('print("\\n" + "="*60)', 'print("\\n" + "="*60)'),
            ('print("="*60 + "\\n")', 'print("="*60 + "\\n")'),
            ('"="*60', '("=" * 60)'),
            ('"=".repeat(50)', '("=" * 50)'),
        ]
        
        for old, new in fixes:
            content = content.replace(old, new)
        
        # Buscar y corregir pattern específico
        import re
        # Corregir: print("=" * 50) cuando está mal escrito
        content = re.sub(r'print\("="\*(\d+)\)', r'print("=" * \1)', content)
        content = re.sub(r'"="\*(\d+)', r'("=" * \1)', content)
        content = re.sub(r'"\+"="\*(\d+)', r'("=" * \1)', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print_success("input_manager.gd corregido")
        return True
        
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def delete_backup(base_path):
    """Elimina el backup que está causando UIDs duplicados"""
    print_header("ELIMINANDO BACKUP (UIDs duplicados)")
    
    backup_path = Path(base_path) / "inventory_system_backup"
    
    if backup_path.exists():
        try:
            shutil.rmtree(backup_path)
            print_success(f"Backup eliminado: {backup_path}")
            return True
        except Exception as e:
            print_error(f"Error eliminando backup: {e}")
            return False
    else:
        print_info("No hay backup para eliminar")
        return True

def fix_consolidated_files(base_path):
    """Corrige las anotaciones @tool en archivos consolidados"""
    print_header("CORRIGIENDO ARCHIVOS CONSOLIDADOS")
    
    scripts_path = Path(base_path) / "addons" / "inventory_system" / "scripts"
    
    files_to_fix = [
        "inventory_ui_system.gd",
        "hotbar_ui_system.gd"
    ]
    
    for filename in files_to_fix:
        file_path = scripts_path / filename
        
        if not file_path.exists():
            print_warning(f"No encontrado: {filename}")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Buscar @tool mal ubicado
            new_lines = []
            tool_found = False
            
            for i, line in enumerate(lines):
                # Si encontramos @tool después de class_name, moverlo al inicio
                if '@tool' in line and i > 0:
                    # Verificar si hay class_name antes
                    has_class_before = any('class_name' in prev_line for prev_line in lines[:i])
                    if has_class_before:
                        # Saltar esta línea @tool (la agregaremos al inicio)
                        tool_found = True
                        continue
                
                new_lines.append(line)
            
            # Si encontramos @tool mal ubicado, agregarlo al inicio
            if tool_found:
                new_lines.insert(0, '@tool\n')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print_success(f"Corregido: {filename}")
            
        except Exception as e:
            print_error(f"Error en {filename}: {e}")

def remove_global_class_declarations(base_path):
    """Remueve class_name de las clases internas para evitar conflictos"""
    print_header("REMOVIENDO DECLARACIONES DE CLASES GLOBALES DUPLICADAS")
    
    scripts_path = Path(base_path) / "addons" / "inventory_system" / "scripts"
    
    # Estos archivos NO deben tener class_name porque crean conflictos
    files_to_check = {
        "inventory_ui_system.gd": ["InventoryUI"],
        "hotbar_ui_system.gd": ["HotbarUI"],
    }
    
    for filename, classes in files_to_check.items():
        file_path = scripts_path / filename
        
        if not file_path.exists():
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar si hay conflicto
            lines = content.split('\n')
            modified = False
            
            # Buscar y comentar class_name de clases internas si existe
            new_lines = []
            in_inner_class = False
            
            for line in lines:
                # Detectar clase interna
                if 'class ' in line and 'class_name' not in line and ':' in line:
                    in_inner_class = True
                
                # Si encontramos class_name dentro de clase interna
                if in_inner_class and 'class_name' in line:
                    # Comentar esta línea
                    new_lines.append('# ' + line + '  # Comentado para evitar conflicto')
                    modified = True
                    in_inner_class = False
                else:
                    new_lines.append(line)
                
                # Salir de clase interna
                if in_inner_class and line.strip() and not line.startswith(('\t', ' ')):
                    in_inner_class = False
            
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                print_success(f"Corregido: {filename}")
            else:
                print_info(f"Sin cambios: {filename}")
                
        except Exception as e:
            print_error(f"Error en {filename}: {e}")

def check_project_settings(base_path):
    """Verifica y muestra información sobre los autoloads"""
    print_header("VERIFICANDO CONFIGURACIÓN DEL PROYECTO")
    
    project_file = Path(base_path) / "project.godot"
    
    if not project_file.exists():
        print_error("project.godot no encontrado")
        return
    
    with open(project_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar autoloads
    if 'ItemDatabase' in content:
        print_success("ItemDatabase está configurado como autoload")
    else:
        print_warning("ItemDatabase NO está configurado como autoload")
        print_info("Agrega en project.godot:")
        print('  [autoload]')
        print('  ItemDatabase="*res://addons/inventory_system/scripts/item_database.gd"')
    
    if 'InputManager' in content:
        print_success("InputManager está configurado como autoload")
    else:
        print_warning("InputManager NO está configurado como autoload")

def clean_old_scenes(base_path):
    """Limpia escenas antiguas que referencian scripts eliminados"""
    print_header("LIMPIANDO REFERENCIAS ANTIGUAS")
    
    scenes_path = Path(base_path) / "addons" / "inventory_system" / "scenes"
    
    if not scenes_path.exists():
        print_info("No hay carpeta scenes/ para limpiar")
        return
    
    # Archivos de escena que pueden tener referencias rotas
    scene_files = list(scenes_path.glob("*.tscn"))
    
    for scene_file in scene_files:
        print_info(f"Verificando: {scene_file.name}")
        
        try:
            with open(scene_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar referencias a scripts eliminados
            broken_refs = [
                'inventory_slot_ui.gd',
                'hotbar_slot_ui.gd',
                'crafting_manager.gd',
                'crafting_table_ui.gd'
            ]
            
            has_broken = any(ref in content for ref in broken_refs)
            
            if has_broken:
                print_warning(f"  {scene_file.name} tiene referencias rotas")
                print_info(f"  Recomendación: Recrear esta escena en Godot")
            else:
                print_success(f"  {scene_file.name} OK")
                
        except Exception as e:
            print_error(f"Error leyendo {scene_file.name}: {e}")

def main():
    """Función principal"""
    print_header("🔧 CORRECCIÓN DE ERRORES DE CONSOLIDACIÓN")
    
    current_dir = Path.cwd()
    
    if not (current_dir / "project.godot").exists():
        print_error("No se encontró project.godot")
        print_warning("Ejecuta este script desde la raíz del proyecto Godot")
        return
    
    print_success(f"Proyecto detectado: {current_dir}")
    
    # Aplicar correcciones
    print("\n📋 Aplicando correcciones...\n")
    
    # 1. Corregir input_manager
    fix_input_manager(current_dir)
    
    # 2. Eliminar backup (causa UIDs duplicados)
    delete_backup(current_dir)
    
    # 3. Corregir archivos consolidados
    fix_consolidated_files(current_dir)
    
    # 4. Remover declaraciones duplicadas
    remove_global_class_declarations(current_dir)
    
    # 5. Verificar configuración
    check_project_settings(current_dir)
    
    # 6. Limpiar escenas antiguas
    clean_old_scenes(current_dir)
    
    # Instrucciones finales
    print_header("✅ CORRECCIONES APLICADAS")
    print("\n📋 Próximos pasos:")
    print("  1. Cierra Godot completamente")
    print("  2. Elimina la carpeta .godot/ (caché)")
    print("  3. Vuelve a abrir el proyecto")
    print("  4. Ve a Proyecto > Recargar proyecto actual")
    print("  5. Revisa la consola de errores")
    
    print("\n💡 Si siguen los errores:")
    print("  - Desactiva el addon en Proyecto > Configuración del proyecto > Plugins")
    print("  - Cierra y reabre Godot")
    print("  - Vuelve a activar el addon")

if __name__ == "__main__":
    main()
