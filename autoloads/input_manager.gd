extends Node

## InputManager - Configura todos los controles del sistema de inventario
## Este autoload debe estar configurado en Proyecto > Autoload

func _ready():
	print("⌨️ InputManager: Configurando controles...")
	setup_all_controls()
	print("✓ Controles configurados correctamente\n")

func setup_all_controls():
	"""Configura todos los controles del sistema"""
	setup_inventory_controls()
	setup_hotbar_controls()
	setup_minecraft_controls()
	setup_crafting_controls()

# ============================================
# CONTROLES DE INVENTARIO
# ============================================

func setup_inventory_controls():
	"""Configura controles básicos del inventario"""
	# Abrir/Cerrar inventario (ya existe ui_cancel, pero agregamos alternativa)
	add_key_action("open_inventory", KEY_E)
	add_key_action("toggle_inventory", KEY_TAB)

# ============================================
# CONTROLES DEL HOTBAR
# ============================================

func setup_hotbar_controls():
	"""Configura controles del hotbar (1-9)"""
	for i in range(1, 10):
		var action_name = "hotbar_slot_%d" % i
		add_key_action(action_name, KEY_0 + i)
	
	print("  ✓ Hotbar: Slots 1-9 configurados")

# ============================================
# CONTROLES ESTILO MINECRAFT
# ============================================

func setup_minecraft_controls():
	"""Configura controles adicionales estilo Minecraft"""
	# Soltar items
	add_key_action("drop_item", KEY_Q)
	add_key_action("drop_stack", KEY_Q, true, true)  # Ctrl+Q
	
	# Intercambiar manos
	add_key_action("swap_hands", KEY_F)
	
	# Pick block (modo creativo)
	add_mouse_action("pick_block", MOUSE_BUTTON_MIDDLE)
	
	# Uso rápido
	add_key_action("quick_use", KEY_E, false, true)  # Shift+E
	
	print("  ✓ Controles Minecraft configurados")

# ============================================
# CONTROLES DE CRAFTEO
# ============================================

func setup_crafting_controls():
	"""Configura controles de crafteo"""
	add_key_action("open_crafting", KEY_C)
	add_key_action("craft_all", KEY_SHIFT)  # Mantener shift para craftear múltiples
	
	print("  ✓ Controles de crafteo configurados")

# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

func add_key_action(action_name: String, keycode: int, ctrl: bool = false, shift: bool = false):
	"""Agrega una acción de teclado al InputMap"""
	if InputMap.has_action(action_name):
		return  # Ya existe, no sobrescribir
	
	InputMap.add_action(action_name)
	
	var event = InputEventKey.new()
	event.keycode = keycode
	event.ctrl_pressed = ctrl
	event.shift_pressed = shift
	InputMap.action_add_event(action_name, event)

func add_mouse_action(action_name: String, button: int):
	"""Agrega una acción de mouse al InputMap"""
	if InputMap.has_action(action_name):
		return
	
	InputMap.add_action(action_name)
	
	var event = InputEventMouseButton.new()
	event.button_index = button
	InputMap.action_add_event(action_name, event)

func add_gamepad_action(action_name: String, button: int):
	"""Agrega una acción de gamepad al InputMap"""
	if InputMap.has_action(action_name):
		return
	
	InputMap.add_action(action_name)
	
	var event = InputEventJoypadButton.new()
	event.button_index = button
	InputMap.action_add_event(action_name, event)

# ============================================
# SOPORTE PARA GAMEPAD (OPCIONAL)
# ============================================

func setup_gamepad_controls():
	"""Configura controles de gamepad (Xbox/PlayStation)"""
	# D-Pad para hotbar
	add_gamepad_action("hotbar_next", JOY_BUTTON_DPAD_RIGHT)
	add_gamepad_action("hotbar_prev", JOY_BUTTON_DPAD_LEFT)
	
	# Botones
	add_gamepad_action("open_inventory", JOY_BUTTON_Y)  # Y/Triangle
	add_gamepad_action("drop_item", JOY_BUTTON_B)       # B/Circle
	add_gamepad_action("use_item", JOY_BUTTON_A)        # A/Cross
	add_gamepad_action("open_crafting", JOY_BUTTON_X)   # X/Square
	
	# Bumpers para scroll de hotbar
	add_gamepad_action("hotbar_scroll_up", JOY_BUTTON_LEFT_SHOULDER)
	add_gamepad_action("hotbar_scroll_down", JOY_BUTTON_RIGHT_SHOULDER)
	
	print("  ✓ Controles de gamepad configurados")

# ============================================
# INFORMACIÓN Y DEBUG
# ============================================

func print_all_actions():
	"""Imprime todas las acciones configuradas"""
	print("\n" + "="*60)
	print("📋 ACCIONES DE INPUT CONFIGURADAS")
	print("="*60 + "\n")
	
	var actions = InputMap.get_actions()
	actions.sort()
	
	for action in actions:
		if action.begins_with("hotbar_") or action.begins_with("open_") or \
		   action.begins_with("drop_") or action.begins_with("swap_") or \
		   action.begins_with("pick_") or action.begins_with("craft_"):
			var events = InputMap.action_get_events(action)
			print("• %s:" % action)
			for event in events:
				print("  - %s" % event_to_string(event))
	
	print("\n" + "="*60 + "\n")

func event_to_string(event: InputEvent) -> String:
	"""Convierte un InputEvent a string legible"""
	if event is InputEventKey:
		var key_name = OS.get_keycode_string(event.keycode)
		var modifiers = ""
		if event.ctrl_pressed:
			modifiers += "Ctrl+"
		if event.shift_pressed:
			modifiers += "Shift+"
		if event.alt_pressed:
			modifiers += "Alt+"
		return modifiers + key_name
	
	elif event is InputEventMouseButton:
		match event.button_index:
			MOUSE_BUTTON_LEFT:
				return "Mouse Left"
			MOUSE_BUTTON_RIGHT:
				return "Mouse Right"
			MOUSE_BUTTON_MIDDLE:
				return "Mouse Middle"
			MOUSE_BUTTON_WHEEL_UP:
				return "Mouse Wheel Up"
			MOUSE_BUTTON_WHEEL_DOWN:
				return "Mouse Wheel Down"
			_:
				return "Mouse Button %d" % event.button_index
	
	elif event is InputEventJoypadButton:
		return "Gamepad Button %d" % event.button_index
	
	return str(event)

# ============================================
# CAMBIO DE CONTROLES EN RUNTIME
# ============================================

func change_key_binding(action_name: String, new_keycode: int):
	"""Cambia el binding de una acción existente"""
	if not InputMap.has_action(action_name):
		push_warning("Acción '%s' no existe" % action_name)
		return false
	
	# Eliminar eventos existentes
	InputMap.action_erase_events(action_name)
	
	# Agregar nuevo evento
	var event = InputEventKey.new()
	event.keycode = new_keycode
	InputMap.action_add_event(action_name, event)
	
	print("✓ Binding cambiado: %s → %s" % [action_name, OS.get_keycode_string(new_keycode)])
	return true

func reset_to_defaults():
	"""Resetea todos los controles a valores por defecto"""
	# Limpiar acciones existentes
	for action in InputMap.get_actions():
		if action.begins_with("hotbar_") or action.begins_with("open_") or \
		   action.begins_with("drop_") or action.begins_with("swap_") or \
		   action.begins_with("pick_") or action.begins_with("craft_"):
			InputMap.action_erase_events(action)
	
	# Reconfigurar
	setup_all_controls()
	print("✓ Controles reseteados a valores por defecto")

# ============================================
# GUARDADO/CARGA DE CONFIGURACIÓN
# ============================================

func save_input_config(path: String = "user://input_config.cfg"):
	"""Guarda la configuración de inputs"""
	var config = ConfigFile.new()
	
	for action in InputMap.get_actions():
		if action.begins_with("hotbar_") or action.begins_with("open_") or \
		   action.begins_with("drop_") or action.begins_with("swap_") or \
		   action.begins_with("pick_") or action.begins_with("craft_"):
			var events = InputMap.action_get_events(action)
			var events_data = []
			
			for event in events:
				if event is InputEventKey:
					events_data.append({
						"type": "key",
						"keycode": event.keycode,
						"ctrl": event.ctrl_pressed,
						"shift": event.shift_pressed,
						"alt": event.alt_pressed
					})
			
			config.set_value("input", action, events_data)
	
	config.save(path)
	print("✓ Configuración de input guardada en: %s" % path)

func load_input_config(path: String = "user://input_config.cfg"):
	"""Carga la configuración de inputs"""
	if not FileAccess.file_exists(path):
		print("⚠️ Archivo de configuración no encontrado: %s" % path)
		return false
	
	var config = ConfigFile.new()
	var err = config.load(path)
	
	if err != OK:
		print("❌ Error cargando configuración: %d" % err)
		return false
	
	for action in config.get_section_keys("input"):
		if InputMap.has_action(action):
			InputMap.action_erase_events(action)
		else:
			InputMap.add_action(action)
		
		var events_data = config.get_value("input", action)
		for event_data in events_data:
			if event_data.type == "key":
				var event = InputEventKey.new()
				event.keycode = event_data.keycode
				event.ctrl_pressed = event_data.get("ctrl", false)
				event.shift_pressed = event_data.get("shift", false)
				event.alt_pressed = event_data.get("alt", false)
				InputMap.action_add_event(action, event)
	
	print("✓ Configuración de input cargada desde: %s" % path)
	return true
