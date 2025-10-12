# 🎯 Guía del Sistema de Hotbar

## 🚀 Inicio Rápido

### 1. Agregar Hotbar a tu escena

```gdscript
# Opción A: Instanciar la escena
var hotbar_ui = preload("res://addons/inventory_system/scenes/hotbar_ui.tscn").instantiate()
add_child(hotbar_ui)

# Opción B: Crear nodo HotbarUI en el editor
# Agregar nodo > HotbarUI
```

### 2. Conectar con tu inventario

```gdscript
@onready var inventory = $InventoryUI.inventory
@onready var hotbar_ui = $HotbarUI
@onready var hotbar = $HotbarUI.hotbar

func _ready():
    # El hotbar se conecta automáticamente si está como hijo
    # O manualmente:
    hotbar_ui.inventory = inventory
    hotbar.inventory = inventory
```

### 3. Configurar Input Actions (Automático)

```gdscript
func _ready():
    Hotbar.setup_input_actions() # Crea las teclas 1-9 automáticamente
```

---

## 📚 API del Hotbar

### Seleccionar Slot

```gdscript
# Por índice (0-8)
hotbar.select_slot(3) # Selecciona slot 4

# Siguiente/Anterior
hotbar.select_next_slot()
hotbar.select_previous_slot()
```

### Obtener Items

```gdscript
# Item seleccionado actualmente
var item = hotbar.get_selected_item()

# Item en slot específico
var item = hotbar.get_item_at_slot(2) # Slot 3

# Cantidad en slot
var quantity = hotbar.get_quantity_at_slot(0)
```

### Usar Items

```gdscript
# Usar item seleccionado
hotbar.use_selected_item()

# Usar item en slot específico
hotbar.use_item_at_slot(4) # Slot 5
```

---

## 🎮 Controles por Defecto

| Acción | Control |
|--------|---------|
| **Seleccionar Slot 1-9** | Teclas `1` a `9` |
| **Siguiente Slot** | Scroll Up |
| **Anterior Slot** | Scroll Down |
| **Usar Item Seleccionado** | Enter / Espacio |
| **Usar Item (Click)** | Click Izquierdo en slot |
| **Usar Item (Click)** | Click Derecho en slot |

---

## ⚙️ Configuración

### En el Inspector

**Hotbar (Node)**
- `hotbar_size`: Cantidad de slots (default: 9)
- `enable_scroll`: Habilitar scroll (default: true)
- `enable_number_keys`: Habilitar teclas 1-9 (default: true)
- `auto_use_on_select`: Usar automáticamente al seleccionar (default: false)

**HotbarUI (Control)**
- `slot_size`: Tamaño de cada slot (default: 64x64)
- `spacing`: Espacio entre slots (default: 4)

### En Código

```gdscript
# Cambiar tamaño del hotbar
hotbar.hotbar_size = 6 # Solo 6 slots

# Deshabilitar scroll
hotbar.enable_scroll = false

# Uso automático al seleccionar
hotbar.auto_use_on_select = true
```

---

## 📡 Señales

### Hotbar

```gdscript
# Cuando se selecciona un slot
hotbar.slot_selected.connect(func(index, item):
    print("Slot %d seleccionado: %s" % [index, item.name if item else "vacío"])
)

# Cuando se usa un item desde el hotbar
hotbar.item_used_from_hotbar.connect(func(item):
    print("Usado desde hotbar: ", item.name)
)
```

### HotbarUI

El HotbarUI se actualiza automáticamente cuando cambia el inventario.

---

## 🎨 Personalización Visual

### Cambiar colores del slot seleccionado

Edita `hotbar_slot_ui.tscn`:

```gdscript
# En SelectionIndicator > StyleBoxFlat
border_color = Color(1, 0, 0, 1) # Rojo en vez de amarillo
border_width_left = 5 # Borde más grueso
```

### Cambiar tamaño y posición

```gdscript
# En tu escena
@onready var hotbar_ui = $HotbarUI

func _ready():
    hotbar_ui.position = Vector2(400, 500)
    hotbar_ui.slot_size = Vector2(80, 80) # Slots más grandes
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: FPS con armas

```gdscript
extends CharacterBody3D

@onready var hotbar = $HotbarUI/Hotbar
var current_weapon: Node3D

func _ready():
    hotbar.slot_selected.connect(_on_weapon_changed)
    _equip_weapon(hotbar.get_selected_item())

func _on_weapon_changed(index: int, item: InventoryItem):
    _equip_weapon(item)

func _equip_weapon(weapon_item: InventoryItem):
    # Desequipar arma actual
    if current_weapon:
        current_weapon.queue_free()
    
    # Equipar nueva arma
    if weapon_item and weapon_item.item_type == InventoryItem.ItemType.EQUIPMENT:
        var weapon_scene = load(weapon_item.custom_data.get("scene_path"))
        if weapon_scene:
            current_weapon = weapon_scene.instantiate()
            $Hand.add_child(current_weapon)

func _input(event):
    if event.is_action_pressed("fire"):
        if current_weapon and current_weapon.has_method("shoot"):
            current_weapon.shoot()
```

### Ejemplo 2: Survival con comida

```gdscript
extends CharacterBody2D

@onready var hotbar = $HotbarUI/Hotbar
@export var health: float = 100.0
@export var hunger: float = 100.0

func _ready():
    hotbar.item_used_from_hotbar.connect(_on_item_consumed)

func _on_item_consumed(item: InventoryItem):
    if item.is_consumable:
        match item.item_type:
            InventoryItem.ItemType.CONSUMABLE:
                # Comida restaura hambre
                if item.custom_data.has("hunger_restore"):
                    hunger = min(100, hunger + item.custom_data.hunger_restore)
                    print("Hambre: ", hunger)
                
                # Poción restaura vida
                if item.custom_data.has("heal_amount"):
                    health = min(100, health + item.custom_data.heal_amount)
                    print("Vida: ", health)

func _process(delta):
    # Hambre disminuye con el tiempo
    hunger = max(0, hunger - delta * 2)
```

### Ejemplo 3: Minecraft-like con bloques

```gdscript
extends Node2D

@onready var hotbar = $HotbarUI/Hotbar
@onready var tilemap = $TileMap

func _input(event):
    if event is InputEventMouseButton and event.pressed:
        var mouse_pos = get_global_mouse_position()
        var tile_pos = tilemap.local_to_map(mouse_pos)
        
        if event.button_index == MOUSE_BUTTON_LEFT:
            # Romper bloque
            tilemap.set_cell(0, tile_pos, -1)
        
        elif event.button_index == MOUSE_BUTTON_RIGHT:
            # Colocar bloque del hotbar
            var selected_item = hotbar.get_selected_item()
            if selected_item and selected_item.custom_data.has("tile_id"):
                var tile_id = selected_item.custom_data.tile_id
                tilemap.set_cell(0, tile_pos, 0, Vector2i(tile_id, 0))
                hotbar.inventory.remove_item(selected_item, 1)
```

---

## 🔧 Troubleshooting

### El hotbar no se muestra

```gdscript
# Verificar que esté visible
hotbar_ui.visible = true

# Verificar que tenga inventario
print(hotbar.inventory) # No debe ser null
```

### Las teclas 1-9 no funcionan

```gdscript
# Asegúrate de llamar a setup_input_actions
func _ready():
    Hotbar.setup_input_actions()
```

### Los slots están vacíos

```gdscript
# El hotbar muestra los primeros 9 slots del inventario
# Asegúrate de agregar items:
inventory.add_item_by_id("potion_health", 1)
```

### El scroll no funciona

```gdscript
# Verificar que esté habilitado
hotbar.enable_scroll = true

# Y que el mouse esté sobre el juego (no el editor)
```

---

## 🎯 Tips y Mejores Prácticas

### 1. Hotbar persistente entre escenas

```gdscript
# Usar un autoload (singleton)
# autoload/game_state.gd
extends Node

var player_inventory: InventoryManager

func _ready():
    player_inventory = InventoryManager.new()
    add_child(player_inventory)
```

### 2. Mostrar nombre del item seleccionado

```gdscript
@onready var item_name_label = $ItemNameLabel

func _ready():
    hotbar.slot_selected.connect(func(index, item):
        if item:
            item_name_label.text = item.name
        else:
            item_name_label.text = ""
    )
```

### 3. Cooldown visual

```gdscript
# En hotbar_slot_ui.gd
var cooldown_progress: float = 0.0

func _process(delta):
    if cooldown_progress > 0:
        cooldown_progress -= delta
        modulate = Color(0.5, 0.5, 0.5, 1.0)
    else:
        modulate = Color.WHITE

func start_cooldown(duration: float):
    cooldown_progress = duration
```

### 4. Hotbar dinámico (cambiar slots)

```gdscript
# Cambiar qué slots del inventario muestra el hotbar
func switch_hotbar_page(page: int):
    var start_index = page * 9
    for i in range(9):
        hotbar.hotbar_slots[i] = start_index + i
    hotbar_ui.update_ui()
```

---

## 📦 Estructura de Archivos

```
addons/inventory_system/
├── scripts/
│   ├── hotbar.gd              # Lógica del hotbar
│   ├── hotbar_ui.gd           # UI completa del hotbar
│   └── hotbar_slot_ui.gd      # UI de cada slot
├── scenes/
│   ├── hotbar_ui.tscn         # Escena del hotbar
│   └── hotbar_slot_ui.tscn    # Escena del slot
└── demo/
    ├── demo_with_hotbar.gd    # Demo de uso
    └── demo_hotbar.tscn       # Escena de demo
```

---

## ✅ Checklist de Implementación

- [x] Sistema de selección por teclas 1-9
- [x] Scroll del mouse para cambiar slot
- [x] Feedback visual del slot seleccionado
- [x] Usar items desde el hotbar
- [x] Sincronización automática con inventario
- [x] Tooltip con información del item
- [x] Cantidad visible en cada slot
- [x] Número de tecla visible en cada slot
- [x] API completa para scripts
- [x] Señales para eventos
- [x] Personalizable en el Inspector
- [x] Demo funcional incluida

---

## 🚀 ¡Listo para usar!

Ejecuta la demo: `addons/inventory_system/demo/demo_hotbar.tscn`
