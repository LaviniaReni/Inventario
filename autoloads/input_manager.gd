extends Node

func _ready():
	setup_minecraft_controls()

func setup_minecraft_controls():
	add_input_action("open_inventory", KEY_E)
	
	for i in range(1, 10):
		add_input_action("hotbar_slot_%d" % i, KEY_0 + i)
	
	add_input_action("drop_item", KEY_Q)
	add_input_action("drop_stack", KEY_Q, true, true)
	add_input_action("swap_hands", KEY_F)
	add_input_action("pick_block", MOUSE_BUTTON_MIDDLE)
	
	print("✓ Controles Minecraft configurados")

func add_input_action(action_name: String, key_or_button, ctrl: bool = false, shift: bool = false):
	if InputMap.has_action(action_name):
		return
	
	InputMap.add_action(action_name)
	
	if key_or_button is int and key_or_button >= KEY_0 and key_or_button <= KEY_Z:
		var event = InputEventKey.new()
		event.keycode = key_or_button
		event.ctrl_pressed = ctrl
		event.shift_pressed = shift
		InputMap.action_add_event(action_name, event)
	elif key_or_button is int:
		var event = InputEventMouseButton.new()
		event.button_index = key_or_button
		InputMap.action_add_event(action_name, event)
