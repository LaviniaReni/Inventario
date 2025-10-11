# 🔧 Configurar ItemDatabase

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
