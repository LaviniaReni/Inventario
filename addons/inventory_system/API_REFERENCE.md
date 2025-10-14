# 📚 API Reference - Sistema de Inventario

Documentación completa de todas las clases, métodos y señales del sistema.

---

## 📦 InventoryManager

### Propiedades

```gdscript
@export var size: int = 20                    # Tamaño del inventario
@export var auto_save: bool = false           # Auto-guardado habilitado
@export var save_path: String = "user://..."  # Ruta del archivo de guardado

var slots: Array[InventorySlot]               # Array de slots del inventario
var armor_slots: Array[InventorySlot]         # Slots de armadura
var offhand_slot: InventorySlot               # Slot de mano secundaria
```

### Métodos - Gestión de Items

#### `add_item(item: InventoryItem, amount: int = 1) -> bool`
Agrega un item al inventario.

**Parámetros:**
- `item`: El item a agregar
- `amount`: Cantidad a agregar (default: 1)

**Retorna:** `true` si se agregó completamente, `false` si el inventario está lleno

**Ejemplo:**
```gdscript
var potion = ItemDatabase.get_item("potion_health")
if inventory.add_item(potion, 5):
    print("5 pociones agregadas!")
else:
    print("Inventario lleno")
```

---

#### `add_item_by_id(item_id: String, amount: int = 1) -> bool`
Agrega un item por su ID desde ItemDatabase.

**Ejemplo:**
```gdscript
inventory.add_item_by_id("sword_iron", 1)
```

---

#### `remove_item(item: InventoryItem, amount: int = 1) -> bool`
Remueve un item del inventario.

**Retorna:** `true` si se removió completamente

**Ejemplo:**
```gdscript
inventory.remove_item(sword, 1)
```

---

#### `remove_item_by_id(item_id: String, amount: int = 1) -> bool`
Remueve un item por su ID.

---

#### `has_item(item: InventoryItem, amount: int = 1) -> bool`
Verifica si el inventario tiene suficiente cantidad de un item.

**Ejemplo:**
```gdscript
if inventory.has_item(wood, 10):
    print("Tienes suficiente madera")
```

---

#### `get_item_count(item: InventoryItem) -> int`
Retorna la cantidad total de un item en el inventario.

**Ejemplo:**
```gdscript
var gold_count = inventory.get_item_count(gold_coin)
print("Tienes %d monedas" % gold_count)
```

---

### Métodos - Uso de Items

#### `use_item(item: InventoryItem) -> bool`
Usa un item. Si es consumible, lo consume automáticamente.

**Retorna:** `true` si el item fue usado

**Ejemplo:**
```gdscript
if inventory.use_item(health_potion):
    player.health += 50
```

---

#### `use_item_by_id(item_id: String) -> bool`
Usa un item por su ID.

---

### Métodos - Gestión de Slots

#### `swap_slots(index_a: int, index_b: int) -> void`
Intercambia el contenido de dos slots. Si ambos tienen el mismo item stackeable, intenta combinarlos.

**Ejemplo:**
```gdscript
inventory.swap_slots(0, 5)  # Intercambia slot 0 y 5
```

---

#### `clear_inventory() -> void`
Limpia completamente el inventario (elimina todos los items).

---

### Métodos - Guardado/Carga

#### `save_inventory() -> void`
Guarda el inventario en disco (usa `save_path`).

---

#### `load_inventory() -> void`
Carga el inventario desde disco.

**Ejemplo:**
```gdscript
func _ready():
    inventory.auto_save = true
    inventory.load_inventory()
```

---

### Métodos - Sistema de Armadura

#### `equip_armor(item: InventoryItem, slot_type: ArmorSlot) -> bool`
Equipa una pieza de armadura.

**Enums disponibles:**
```gdscript
ArmorSlot.HELMET      # Casco
ArmorSlot.CHESTPLATE  # Peto
ArmorSlot.LEGGINGS    # Pantalones
ArmorSlot.BOOTS       # Botas
```

**Ejemplo:**
```gdscript
var helmet = ItemDatabase.get_item("iron_helmet")
inventory.equip_armor(helmet, InventoryManager.ArmorSlot.HELMET)
```

---

#### `unequip_armor(slot_type: ArmorSlot) -> bool`
Desequipa una pieza de armadura.

---

#### `get_equipped_armor(slot_type: ArmorSlot) -> InventoryItem`
Retorna la armadura equipada en un slot específico (o `null` si está vacío).

---

#### `get_total_armor_value() -> int`
Calcula el valor total de armadura equipada.

**Ejemplo:**
```gdscript
var defense = inventory.get_total_armor_value()
var damage_taken = max(1, attack_damage - defense)
```

---

### Métodos - Offhand

#### `equip_offhand(item: InventoryItem) -> bool`
Equipa un item en la mano secundaria.

---

#### `unequip_offhand() -> bool`
Desequipa el item de la mano secundaria.

---

### Señales

```gdscript
signal inventory_changed()                                    # El inventario cambió
signal item_added(item: InventoryItem, amount: int)          # Item agregado
signal item_removed(item: InventoryItem, amount: int)        # Item removido
signal item_used(item: InventoryItem)                        # Item usado
signal inventory_full()                                       # Inventario lleno
```

**Ejemplo de uso:**
```gdscript
func _ready():
    inventory.item_added.connect(_on_item_added)
    inventory.item_used.connect(_on_item_used)
    inventory.inventory_full.connect(_on_inventory_full)

func _on_item_added(item: InventoryItem, amount: int):
    show_notification("✓ +%d %s" % [amount, item.name])

func _on_item_used(item: InventoryItem):
    if item.custom_data.has("heal_amount"):
        player.heal(item.custom_data.heal_amount)

func _on_inventory_full():
    show_notification("⚠️ Inventario lleno!")
```

---

## 🗄️ ItemDatabase (Autoload)

### Propiedades

```gdscript
var items: Dictionary                             # Dictionary de items {id: InventoryItem}
var is_loaded: bool                               # Estado de carga
@export var items_folder: String                  # Carpeta de items
@export var auto_load_on_ready: bool = true       # Cargar automáticamente
```

### Métodos

#### `get_item(item_id: String) -> InventoryItem`
Obtiene un item por su ID.

**Retorna:** El item o `null` si no existe

**Ejemplo:**
```gdscript
var sword = ItemDatabase.get_item("iron_sword")
if sword:
    inventory.add_item(sword, 1)
```

---

#### `has_item(item_id: String) -> bool`
Verifica si existe un item con el ID dado.

---

#### `get_all_items() -> Array[InventoryItem]`
Retorna todos los items cargados.

**Ejemplo:**
```gdscript
var all_items = ItemDatabase.get_all_items()
for item in all_items:
    print(item.name)
```

---

#### `get_items_by_type(type: InventoryItem.ItemType) -> Array[InventoryItem]`
Retorna todos los items de un tipo específico.

**Tipos disponibles:**
```gdscript
InventoryItem.ItemType.CONSUMABLE   # Consumibles (pociones, comida)
InventoryItem.ItemType.EQUIPMENT    # Equipamiento (armas, armaduras)
InventoryItem.ItemType.QUEST        # Items de quest
InventoryItem.ItemType.MATERIAL     # Materiales (madera, piedra)
InventoryItem.ItemType.MISC         # Misceláneos
```

**Ejemplo:**
```gdscript
var weapons = ItemDatabase.get_items_by_type(InventoryItem.ItemType.EQUIPMENT)
```

---

#### `search_items(query: String) -> Array[InventoryItem]`
Busca items por nombre o descripción.

**Ejemplo:**
```gdscript
var healing_items = ItemDatabase.search_items("heal")
```

---

#### `reload_items() -> void`
Recarga todos los items desde disco.

---

#### `print_database_info() -> void`
Imprime información detallada de la base de datos en consola.

---

### Señales

```gdscript
signal database_loaded()  # La base de datos terminó de cargar
```

**Uso:**
```gdscript
func _ready():
    if ItemDatabase.get_item_count() == 0:
        await ItemDatabase.database_loaded
    
    # Ahora los items están cargados
    inventory.add_item_by_id("sword_iron", 1)
```

---

## 🔥 Hotbar

### Propiedades

```gdscript
@export var hotbar_size: int = 9                  # Cantidad de slots
@export var inventory: InventoryManager           # Referencia al inventario
@export var selected_slot: int = 0                # Slot seleccionado actual
@export var enable_scroll: bool = true            # Habilitar scroll
@export var enable_number_keys: bool = true       # Habilitar teclas 1-9
@export var auto_use_on_select: bool = false      # Usar al seleccionar
```

### Métodos

#### `select_slot(index: int) -> void`
Selecciona un slot específico del hotbar.

**Ejemplo:**
```gdscript
hotbar.select_slot(0)  # Selecciona el primer slot
```

---

#### `select_next_slot() -> void`
Selecciona el siguiente slot (con wrap-around).

---

#### `select_previous_slot() -> void`
Selecciona el slot anterior (con wrap-around).

---

#### `get_selected_item() -> InventoryItem`
Retorna el item del slot seleccionado actual.

**Ejemplo:**
```gdscript
var current_item = hotbar.get_selected_item()
if current_item:
    print("Item actual: %s" % current_item.name)
```

---

#### `get_item_at_slot(slot_index: int) -> InventoryItem`
Retorna el item en un slot específico.

---

#### `get_quantity_at_slot(slot_index: int) -> int`
Retorna la cantidad de items en un slot específico.

---

#### `use_selected_item() -> bool`
Usa el item del slot seleccionado.

**Retorna:** `true` si el item fue usado

---

#### `use_item_at_slot(slot_index: int) -> bool`
Usa el item de un slot específico.

---

#### `static setup_input_actions() -> void`
Configura las acciones de input para el hotbar (teclas 1-9).

**Debe llamarse antes de usar el hotbar:**
```gdscript
func _ready():
    Hotbar.setup_input_actions()
```

---

### Señales

```gdscript
signal slot_selected(index: int, item: InventoryItem)    # Slot seleccionado
signal item_used_from_hotbar(item: InventoryItem)        # Item usado desde hotbar
```

**Ejemplo:**
```gdscript
func _ready():
    hotbar.slot_selected.connect(_on_slot_selected)
    hotbar.item_used_from_hotbar.connect(_on_item_used)

func _on_slot_selected(index: int, item: InventoryItem):
    if item:
        print("Seleccionado: [%d] %s" % [index + 1, item.name])

func _on_item_used(item: InventoryItem):
    print("⚡ Usado: %s" % item.name)
```

---

## 🔨 CraftingManager

### Propiedades

```gdscript
var recipes: Array[CraftingRecipe]  # Array de recetas cargadas
```

### Métodos

#### `load_recipes() -> void`
Carga todas las recetas desde `res://recipes/`.

Se llama automáticamente en `_ready()`.

---

#### `find_recipe(grid_slots: Array[InventorySlot]) -> CraftingRecipe`
Busca una receta que coincida con la grilla actual.

**Parámetros:**
- `grid_slots`: Array de 9 slots representando la grilla 3x3

**Retorna:** La receta encontrada o `null`

**Ejemplo:**
```gdscript
var recipe = crafting_manager.find_recipe(crafting_slots)
if recipe:
    print("Receta encontrada: %s" % recipe.result_item_id)
```

---

#### `can_craft(recipe: CraftingRecipe, grid_slots: Array[InventorySlot]) -> bool`
Verifica si se puede craftear una receta con los items actuales.

---

#### `craft(recipe: CraftingRecipe, grid_slots: Array[InventorySlot], inventory: InventoryManager) -> bool`
Ejecuta el crafteo: consume los ingredientes y agrega el resultado al inventario.

**Retorna:** `true` si el crafteo fue exitoso

**Ejemplo:**
```gdscript
if crafting_manager.craft(recipe, grid_slots, inventory):
    print("✓ Crafteado: %s" % recipe.result_item_id)
```

---

### Señales

```gdscript
signal recipe_found(recipe: CraftingRecipe)           # Receta encontrada
signal crafted(item: InventoryItem, quantity: int)    # Item crafteado
```

---

## 📄 InventoryItem (Resource)

### Propiedades

```gdscript
# Info Básica
@export var id: String = ""                    # ID único del item
@export var name: String = ""                  # Nombre visible
@export_multiline var description: String = "" # Descripción
@export var icon: Texture2D                    # Icono del item
@export var item_type: ItemType = ItemType.MISC # Tipo de item

# Stack
@export var is_stackable: bool = true          # ¿Se puede apilar?
@export var max_stack: int = 99                # Máximo por stack

# Uso
@export var is_usable: bool = false            # ¿Se puede usar?
@export var is_consumable: bool = false        # ¿Se consume al usar?

# Custom
@export var custom_data: Dictionary = {}       # Datos personalizados
```

### Enums

```gdscript
enum ItemType {
    CONSUMABLE,  # Consumibles (pociones, comida)
    EQUIPMENT,   # Equipamiento (armas, armaduras)
    QUEST,       # Items de quest
    MATERIAL,    # Materiales (madera, piedra)
    MISC         # Misceláneos
}
```

### Ejemplo de Creación

```gdscript
var health_potion = InventoryItem.new()
health_potion.id = "potion_health"
health_potion.name = "Poción de Vida"
health_potion.description = "Restaura 50 HP"
health_potion.icon = load("res://icons/potion_red.png")
health_potion.item_type = InventoryItem.ItemType.CONSUMABLE
health_potion.is_stackable = true
health_potion.max_stack = 10
health_potion.is_usable = true
health_potion.is_consumable = true
health_potion.custom_data = {
    "heal_amount": 50,
    "cooldown": 3.0
}

ResourceSaver.save(health_potion, "res://items/potion_health.tres")
```

---

## 🧩 CraftingRecipe (Resource)

### Propiedades

```gdscript
@export var id: String = ""                        # ID único de la receta
@export var result_item_id: String = ""            # ID del item resultante
@export var result_quantity: int = 1               # Cantidad a craftear
@export var shapeless: bool = false                # ¿Orden no importa?
@export var pattern: Array[String] = ["", "", "", "", "", "", "", "", ""]  # Patrón 3x3
```

### Métodos

#### `matches(grid: Array[String]) -> bool`
Verifica si la grilla coincide con esta receta.

**Parámetros:**
- `grid`: Array de 9 strings con IDs de items (o "" para vacío)

---

#### `matches_shapeless(grid: Array[String]) -> bool`
Verifica coincidencia sin importar el orden.

---

#### `matches_shaped(grid: Array[String]) -> bool`
Verifica coincidencia exacta de posiciones.

---

### Ejemplo de Receta Shaped

```gdscript
var sword_recipe = CraftingRecipe.new()
sword_recipe.id = "iron_sword"
sword_recipe.result_item_id = "sword_iron"
sword_recipe.result_quantity = 1
sword_recipe.shapeless = false
sword_recipe.pattern = [
    "iron_ingot", "", "",
    "iron_ingot", "", "",
    "stick",      "", ""
]

ResourceSaver.save(sword_recipe, "res://recipes/iron_sword.tres")
```

### Ejemplo de Receta Shapeless

```gdscript
var bread_recipe = CraftingRecipe.new()
bread_recipe.id = "bread"
bread_recipe.result_item_id = "bread"
bread_recipe.result_quantity = 1
bread_recipe.shapeless = true  # Orden no importa
bread_recipe.pattern = [
    "wheat", "wheat", "wheat",
    "", "", "",
    "", "", ""
]
```

---

## 🎯 InventorySlot (Resource)

### Propiedades

```gdscript
@export var item: InventoryItem = null  # Item en el slot
@export var quantity: int = 0           # Cantidad actual
```

### Métodos

#### `add_item(new_item: InventoryItem, amount: int = 1) -> int`
Agrega items al slot.

**Retorna:** Cantidad que no pudo agregarse (0 si todo se agregó)

---

#### `remove_item(amount: int = 1) -> int`
Remueve items del slot.

**Retorna:** Cantidad removida

---

#### `clear() -> void`
Limpia el slot completamente.

---

#### `is_empty() -> bool`
Verifica si el slot está vacío.

---

#### `get_data() -> Dictionary`
Retorna los datos del slot para guardado.

**Retorna:**
```gdscript
{
    "item_id": String,
    "quantity": int
}
```

---

### Señales

```gdscript
signal quantity_changed(new_quantity: int)  # La cantidad cambió
```

---

## 🎨 InventoryUI

### Propiedades

```gdscript
@export var inventory: InventoryManager      # Referencia al inventario
@export var slot_scene: PackedScene          # Escena del slot UI
@export var columns: int = 5                 # Columnas de la grilla
@export var slot_size: Vector2 = Vector2(64, 64)  # Tamaño de cada slot
```

### Señales

```gdscript
signal item_clicked(item: InventoryItem, slot_index: int)
signal item_right_clicked(item: InventoryItem, slot_index: int)
```

**Ejemplo:**
```gdscript
func _ready():
    inventory_ui.item_clicked.connect(_on_item_clicked)
    inventory_ui.item_right_clicked.connect(_on_item_right_clicked)

func _on_item_clicked(item: InventoryItem, slot_index: int):
    if item.is_usable:
        inventory.use_item(item)

func _on_item_right_clicked(item: InventoryItem, slot_index: int):
    inventory.remove_item(item, 1)  # Soltar 1
```

---

## 🔥 HotbarUI

### Propiedades

```gdscript
@export var hotbar: Hotbar                   # Referencia al hotbar
@export var inventory: InventoryManager      # Referencia al inventario
@export var slot_scene: PackedScene          # Escena del slot UI
@export var slot_size: Vector2 = Vector2(64, 64)  # Tamaño de slots
@export var spacing: int = 4                 # Espaciado entre slots
```

---

## 📝 Ejemplos Completos

### Sistema de Pociones con Cooldown

```gdscript
extends Node2D

@onready var inventory = $InventoryUI.inventory

var potion_cooldowns: Dictionary = {}

func _ready():
    inventory.item_used.connect(_on_item_used)

func _process(delta):
    # Reducir cooldowns
    for item_id in potion_cooldowns.keys():
        potion_cooldowns[item_id] -= delta
        if potion_cooldowns[item_id] <= 0:
            potion_cooldowns.erase(item_id)

func _on_item_used(item: InventoryItem):
    if item.item_type == InventoryItem.ItemType.CONSUMABLE:
        # Verificar cooldown
        if potion_cooldowns.has(item.id):
            print("⏱️ Cooldown activo!")
            return
        
        # Aplicar efecto
        if item.custom_data.has("heal_amount"):
            player.health += item.custom_data.heal_amount
            print("❤️ +%d HP" % item.custom_data.heal_amount)
        
        # Activar cooldown
        var cooldown = item.custom_data.get("cooldown", 0.0)
        if cooldown > 0:
            potion_cooldowns[item.id] = cooldown
```

### Sistema de Crafteo Automático

```gdscript
extends Node2D

@onready var crafting_manager = CraftingManager.new()

func _ready():
    add_child(crafting_manager)
    crafting_manager.crafted.connect(_on_item_crafted)

func auto_craft(recipe_id: String) -> bool:
    """Intenta craftear automáticamente una receta"""
    var recipe = find_recipe_by_id(recipe_id)
    if not recipe:
        return false
    
    # Verificar ingredientes
    if not has_ingredients(recipe):
        print("⚠️ Faltan ingredientes")
        return false
    
    # Crear grilla temporal
    var grid_slots = create_crafting_grid(recipe)
    
    # Craftear
    return crafting_manager.craft(recipe, grid_slots, inventory)

func has_ingredients(recipe: CraftingRecipe) -> bool:
    """Verifica si tenemos todos los ingredientes"""
    var required = {}
    for item_id in recipe.pattern:
        if item_id != "":
            required[item_id] = required.get(item_id, 0) + 1
    
    for item_id in required.keys():
        var item = ItemDatabase.get_item(item_id)
        if not inventory.has_item(item, required[item_id]):
            return false
    
    return true

func _on_item_crafted(item: InventoryItem, quantity: int):
    print("✓ Crafteado: %d x %s" % [quantity, item.name])
```

### Sistema de Drop con Física

```gdscript
class_name ItemPickup
extends RigidBody2D

var item: InventoryItem
var quantity: int = 1

@onready var sprite = $Sprite2D
@onready var label = $Label

func _ready():
    if item:
        sprite.texture = item.icon
        label.text = str(quantity) if quantity > 1 else ""
    
    # Aplicar impulso aleatorio
    apply_central_impulse(Vector2(randf_range(-50, 50), -100))

func _on_area_entered(area):
    if area.is_in_group("player"):
        var player = area.get_parent()
        if player.inventory.add_item(item, quantity):
            queue_free()
```

---

## 🎓 Tips y Mejores Prácticas

### 1. Siempre esperar a que cargue ItemDatabase

```gdscript
func _ready():
    if ItemDatabase.get_item_count() == 0:
        await ItemDatabase.database_loaded
    # Ahora es seguro usar items
```

### 2. Usar custom_data para propiedades específicas

```gdscript
# En la definición del item
item.custom_data = {
    "damage": 25,
    "durability": 100,
    "critical_chance": 0.15,
    "effects": ["poison", "fire"]
}

# En el código
if item.custom_data.has("damage"):
    var damage = item.custom_data.damage
```

### 3. Validar antes de usar items

```gdscript
func use_item_safe(item: InventoryItem) -> bool:
    if not item:
        return false
    if not item.is_usable:
        print("❌ Este item no se puede usar")
        return false
    if not inventory.has_item(item):
        print("❌ No tienes este item")
        return false
    
    return inventory.use_item(item)
```

### 4. Cachear referencias a items frecuentes

```gdscript
var health_potion: InventoryItem
var mana_potion: InventoryItem

func _ready():
    await ItemDatabase.database_loaded
    health_potion = ItemDatabase.get_item("potion_health")
    mana_potion = ItemDatabase.get_item("potion_mana")
```

---

## ⚠️ Errores Comunes

### Error 1: ItemDatabase no cargado

```gdscript
# ❌ MAL
func _ready():
    inventory.add_item_by_id("sword_iron", 1)  # Puede fallar

# ✅ BIEN
func _ready():
    await ItemDatabase.database_loaded
    inventory.add_item_by_id("sword_iron", 1)
```

### Error 2: No verificar si el item existe

```gdscript
# ❌ MAL
var item = ItemDatabase.get_item("invalid_id")
inventory.add_item(item, 1)  # Crash si item es null

# ✅ BIEN
var item = ItemDatabase.get_item("invalid_id")
if item:
    inventory.add_item(item, 1)
```

### Error 3: Modificar items compartidos

```gdscript
# ❌ MAL - Modifica el recurso original
var item = ItemDatabase.get_item("sword")
item.custom_data["durability"] = 50  # Afecta TODOS los items

# ✅ BIEN - Duplicar el recurso si necesitas modificarlo
var item = ItemDatabase.get_item("sword").duplicate()
item.custom_data["durability"] = 50
```

---

¿Necesitas más información sobre alguna clase o método específico?
