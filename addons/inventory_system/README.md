# 📦 Sistema de Inventario para Godot 4.5

Un sistema de inventario completo estilo Minecraft para Godot 4.5, con hotbar, crafting, armadura y controles avanzados.

![Godot](https://img.shields.io/badge/Godot-4.5-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Características

- 🎒 **Inventario completo** con drag & drop
- 🔥 **Hotbar** con 9 slots de acceso rápido
- 🔨 **Sistema de crafteo** con grilla 3x3
- 💾 **Auto-guardado** opcional
- 🛡️ **Sistema de armadura** (4 slots + offhand)
- 🎮 **Controles estilo Minecraft**
- 📊 **Base de datos** de items
- 🔍 **Búsqueda y filtrado** de items
- 🎨 **UI personalizable**
- 📝 **Recetas shaped y shapeless**

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/inventory-system.git
cd inventory-system
```

### 2. Activar el plugin

1. Abrir el proyecto en Godot 4.5
2. Ir a **Proyecto > Configuración del Proyecto > Plugins**
3. Activar **"Inventory System"** ✓

### 3. Configurar ItemDatabase (IMPORTANTE)

1. Ir a **Proyecto > Configuración del Proyecto > Autoload**
2. Agregar el siguiente autoload:
   - **Path:** `res://addons/inventory_system/scripts/item_database.gd`
   - **Name:** `ItemDatabase`
3. Click en **"Agregar"**

---

## 📖 Guía de Uso

### Configuración Básica

```gdscript
extends Node2D

@onready var inventory_ui = $InventoryUI
@onready var inventory = $InventoryUI.inventory

func _ready():
	# Esperar a que se cargue la base de datos
	if ItemDatabase.get_item_count() == 0:
		await ItemDatabase.database_loaded
	
	# Agregar items iniciales
	inventory.add_item_by_id("potion_health", 5)
	inventory.add_item_by_id("sword_iron", 1)
	
	# Conectar señales
	inventory.item_added.connect(_on_item_added)
	inventory.item_used.connect(_on_item_used)
	
	# Ocultar inventario inicialmente
	inventory_ui.visible = false

func _input(event):
	if event.is_action_pressed("ui_cancel"):
		inventory_ui.visible = !inventory_ui.visible

func _on_item_added(item: InventoryItem, amount: int):
	print("✓ Agregado: %d x %s" % [amount, item.name])

func _on_item_used(item: InventoryItem):
	print("⚡ Usando: %s" % item.name)
```

### Agregar Hotbar

```gdscript
@onready var hotbar_ui = $HotbarUI
@onready var hotbar = $HotbarUI.hotbar

func _ready():
	# Configurar acciones de input
	Hotbar.setup_input_actions()
	
	# Conectar señales del hotbar
	hotbar.slot_selected.connect(_on_hotbar_slot_selected)
	hotbar.item_used_from_hotbar.connect(_on_hotbar_item_used)

func _on_hotbar_slot_selected(index: int, item: InventoryItem):
	if item:
		print("Seleccionado: Slot %d - %s" % [index + 1, item.name])
	else:
		print("Seleccionado: Slot %d (vacío)" % (index + 1))

func _on_hotbar_item_used(item: InventoryItem):
	print("⚡ Usado desde hotbar: %s" % item.name)
```

### Sistema de Crafteo

```gdscript
@onready var crafting_table_ui

func _input(event):
	if event.is_action_pressed("ui_accept"):
		open_crafting_table()

func open_crafting_table():
	var scene = load("res://addons/inventory_system/scenes/crafting_table_ui.tscn")
	if scene:
		crafting_table_ui = scene.instantiate()
		add_child(crafting_table_ui)
		crafting_table_ui.inventory_ui = inventory_ui
		crafting_table_ui.closed.connect(_on_crafting_closed)

func _on_crafting_closed():
	crafting_table_ui = null
```

---

## 🎮 Controles

### Inventario
- **ESC**: Abrir/Cerrar inventario
- **Click Izq**: Usar item
- **Click Der**: Soltar 1 item
- **Shift + Click**: Mover rápido entre hotbar/inventario
- **Click Medio**: Pick block (modo creativo)
- **Arrastrar**: Reorganizar items

### Hotbar
- **1-9**: Seleccionar slot
- **Scroll Arriba/Abajo**: Cambiar slot
- **Enter/Espacio**: Usar item seleccionado

### Crafteo
- **Enter**: Abrir mesa de trabajo
- **ESC**: Cerrar mesa de trabajo
- **Arrastrar items**: Colocar en grilla

---

## 📦 Crear Items

### Método 1: Desde el Editor

1. Click derecho en carpeta `demo_items/` > **Nuevo Recurso**
2. Buscar **"InventoryItem"**
3. Configurar propiedades:
   - **id**: Identificador único (ej: "iron_sword")
   - **name**: Nombre visible (ej: "Espada de Hierro")
   - **description**: Descripción del item
   - **icon**: Textura del icono
   - **item_type**: Tipo (CONSUMABLE, EQUIPMENT, etc.)
   - **is_stackable**: ¿Se puede apilar?
   - **max_stack**: Cantidad máxima por stack
   - **is_usable**: ¿Se puede usar?
   - **is_consumable**: ¿Se consume al usar?
   - **custom_data**: Datos personalizados (Dictionary)
4. Guardar como `.tres`

### Método 2: Por Código

```gdscript
var new_item = InventoryItem.new()
new_item.id = "diamond_sword"
new_item.name = "Espada de Diamante"
new_item.description = "Una espada poderosa"
new_item.icon = load("res://icons/diamond_sword.png")
new_item.item_type = InventoryItem.ItemType.EQUIPMENT
new_item.is_stackable = false
new_item.max_stack = 1
new_item.is_usable = true
new_item.custom_data = {
	"damage": 25,
	"durability": 1000
}

ResourceSaver.save(new_item, "res://addons/inventory_system/demo/demo_items/diamond_sword.tres")
```

---

## 🔨 Crear Recetas de Crafteo

### Receta Shaped (forma específica)

```gdscript
var recipe = CraftingRecipe.new()
recipe.id = "wooden_sword"
recipe.result_item_id = "sword_iron"
recipe.result_quantity = 1
recipe.shapeless = false
recipe.pattern = [
	"wood", "", "",
	"wood", "", "",
	"stick", "", ""
]

ResourceSaver.save(recipe, "res://recipes/wooden_sword.tres")
```

### Receta Shapeless (orden no importa)

```gdscript
var recipe = CraftingRecipe.new()
recipe.id = "bread"
recipe.result_item_id = "bread"
recipe.result_quantity = 1
recipe.shapeless = true
recipe.pattern = [
	"wheat", "wheat", "wheat",
	"", "", "",
	"", "", ""
]

ResourceSaver.save(recipe, "res://recipes/bread.tres")
```

### Script de Generación Rápida

Usa `create_recipes.gd` para generar múltiples recetas:

```gdscript
# En el editor: Script > Ejecutar > create_recipes.gd
```

---

## 📊 API Reference

### InventoryManager

```gdscript
# Agregar items
add_item(item: InventoryItem, amount: int) -> bool
add_item_by_id(item_id: String, amount: int) -> bool

# Remover items
remove_item(item: InventoryItem, amount: int) -> bool
remove_item_by_id(item_id: String, amount: int) -> bool

# Verificar items
has_item(item: InventoryItem, amount: int) -> bool
get_item_count(item: InventoryItem) -> int

# Usar items
use_item(item: InventoryItem) -> bool
use_item_by_id(item_id: String) -> bool

# Gestión de slots
swap_slots(index_a: int, index_b: int) -> void
clear_inventory() -> void

# Armadura
equip_armor(item: InventoryItem, slot_type: ArmorSlot) -> bool
unequip_armor(slot_type: ArmorSlot) -> bool
get_total_armor_value() -> int

# Offhand
equip_offhand(item: InventoryItem) -> bool
unequip_offhand() -> bool
```

### ItemDatabase

```gdscript
# Obtener items
get_item(item_id: String) -> InventoryItem
has_item(item_id: String) -> bool
get_all_items() -> Array[InventoryItem]
get_item_count() -> int

# Filtrado
get_items_by_type(type: ItemType) -> Array[InventoryItem]
search_items(query: String) -> Array[InventoryItem]

# Utilidades
reload_items() -> void
print_database_info() -> void
```

### Hotbar

```gdscript
# Selección
select_slot(index: int) -> void
select_next_slot() -> void
select_previous_slot() -> void

# Obtener items
get_selected_item() -> InventoryItem
get_item_at_slot(slot_index: int) -> InventoryItem
get_quantity_at_slot(slot_index: int) -> int

# Usar items
use_selected_item() -> bool
use_item_at_slot(slot_index: int) -> bool

# Configuración
static setup_input_actions() -> void
```

### CraftingManager

```gdscript
# Recetas
find_recipe(grid_slots: Array[InventorySlot]) -> CraftingRecipe
can_craft(recipe: CraftingRecipe, grid_slots: Array[InventorySlot]) -> bool
craft(recipe: CraftingRecipe, grid_slots: Array[InventorySlot], inventory: InventoryManager) -> bool

# Carga
load_recipes() -> void
```

---

## 📡 Señales

### InventoryManager
```gdscript
signal inventory_changed()
signal item_added(item: InventoryItem, amount: int)
signal item_removed(item: InventoryItem, amount: int)
signal item_used(item: InventoryItem)
signal inventory_full()
```

### Hotbar
```gdscript
signal slot_selected(index: int, item: InventoryItem)
signal item_used_from_hotbar(item: InventoryItem)
```

### CraftingManager
```gdscript
signal recipe_found(recipe: CraftingRecipe)
signal crafted(item: InventoryItem, quantity: int)
```

---

## 🎯 Demos Incluidos

### 1. Demo Básico (`demo.tscn`)
- Inventario simple
- Controles básicos
- Items de prueba

### 2. Demo con Hotbar (`demo_hotbar.tscn`)
- Inventario + Hotbar
- Selección de slots
- Uso rápido de items

### 3. Demo Minecraft (`minecraft_demo.tscn`)
- Sistema completo
- Mesa de crafteo
- Controles avanzados

**Para probar:**
```
Proyecto > Ejecutar Escena Actual
```

---

## 🛠️ Personalización

### Cambiar tamaño del inventario

```gdscript
# En InventoryUI o por código
inventory.size = 36
```

### Cambiar slots del hotbar

```gdscript
# En HotbarUI o por código
hotbar.hotbar_size = 9
```

### Personalizar UI

Modifica las escenas `.tscn` en `addons/inventory_system/scenes/`:
- `inventory_ui.tscn` - UI principal
- `inventory_slot_ui.tscn` - Slots individuales
- `hotbar_ui.tscn` - Barra de acceso rápido
- `crafting_table_ui.tscn` - Mesa de trabajo

### Configurar auto-guardado

```gdscript
inventory.auto_save = true
inventory.save_path = "user://my_inventory.save"
```

---

## 📝 Ejemplos Avanzados

### Sistema de Pociones

```gdscript
func _on_item_used(item: InventoryItem):
	if item.custom_data.has("heal_amount"):
		player.health += item.custom_data.heal_amount
		print("❤️ +%d HP" % item.custom_data.heal_amount)
	
	if item.custom_data.has("effect"):
		player.apply_effect(item.custom_data.effect)
```

### Sistema de Durabilidad

```gdscript
func use_tool(item: InventoryItem):
	if item.custom_data.has("durability"):
		item.custom_data.durability -= 1
		
		if item.custom_data.durability <= 0:
			inventory.remove_item(item, 1)
			print("🔨 %s se rompió!" % item.name)
```

### Drop de Items

```gdscript
func drop_item(item: InventoryItem, position: Vector2):
	inventory.remove_item(item, 1)
	
	var dropped_item = ItemPickup.new()
	dropped_item.item = item
	dropped_item.global_position = position
	get_parent().add_child(dropped_item)
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

---

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/tu-usuario/inventory-system/issues)
- **Documentación**: Este README
- **Discord**: [Tu servidor de Discord]

---

## 🙏 Créditos

Desarrollado por [Drovacs]

**Agradecimientos especiales:**
- Comunidad de Godot
- Iconos de [Fuente de iconos]

---

## 📚 Recursos Adicionales

- [Documentación de Godot 4](https://docs.godotengine.org/en/stable/)
- [Tutorial de Inventory Systems](https://youtube.com/...)
- [Asset Pack de Items](https://itch.io/...)

---

**¿Te gustó el proyecto? ¡Dale una ⭐ en GitHub!**
