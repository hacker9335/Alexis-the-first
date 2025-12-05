import time
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.modules.encoder import RotaryEncoder
from kmk.handlers.sequences import send_seq
from kmk.extensions.RGB import RGB
from kmk.modules.layers import Layers

keyboard = KMKKeyboard()

# ----- Layers -----
layers = Layers()
keyboard.modules.append(layers)

# ----- RGB -----
NUM_PIXELS = 4
IDLE_COLOR = (0, 0, 50)  # dim blue
FADE_DURATION = 0.5  # seconds

rgb = RGB(pin=keyboard.gpio6, num_pixels=NUM_PIXELS)
keyboard.extensions.append(rgb)
for i in range(NUM_PIXELS):
    rgb.pixels[i] = IDLE_COLOR

# Timing variables
last_button_time = 0
last_encoder_time = 0

# ----- Rotary Encoder -----
encoder = RotaryEncoder(
    pin_a=keyboard.gpio28,
    pin_b=keyboard.gpio27,
    clockwise=KC.VOLU,
    counter_clockwise=KC.VOLD,
)
keyboard.modules.append(encoder)

def encoder_callback(state):
    global last_encoder_time
    last_encoder_time = time.monotonic()
    print("Encoder turned!", state)
encoder.callback = encoder_callback

# Encoder switch → MUTE
ENCODER_SWITCH_PIN = keyboard.gpio26

# ----- Keymap / Macros -----
keyboard.keymap = [
    [
        send_seq("CTRL+Z"),   # GP7
        send_seq("CTRL+Y"),   # GP0
        send_seq("ALT+TAB"),  # GP1
        send_seq("WIN+L"),    # GP2
        send_seq("CTRL+C"),   # GP4
        send_seq("CTRL+V"),   # GP3
        KC.MUTE              # GP26
    ]
]

# ----- GPIO mapping -----
keyboard.gpio7 = keyboard.keymap[0][0]
keyboard.gpio0 = keyboard.keymap[0][1]
keyboard.gpio1 = keyboard.keymap[0][2]
keyboard.gpio2 = keyboard.keymap[0][3]
keyboard.gpio4 = keyboard.keymap[0][4]
keyboard.gpio3 = keyboard.keymap[0][5]
keyboard.gpio26 = keyboard.keymap[0][6]

# ----- Smooth Fade Helper -----
def ease_out_quad(t):
    return 1 - (1 - t)**2

# ----- RGB update function -----
def update_rgb():
    global last_button_time, last_encoder_time
    now = time.monotonic()

    event_time = max(last_button_time, last_encoder_time)
    elapsed = now - event_time
    t = min(1, elapsed / FADE_DURATION)
    fade_ratio = 1 - ease_out_quad(t)

    # Determine base color
    color = IDLE_COLOR
    if now - last_button_time < FADE_DURATION:
        color = (255, 0, 0)  # Red for button
    elif now - last_encoder_time < FADE_DURATION:
        color = (0, 255, 0)  # Green for encoder

    # Smooth fade
    r = int(color[0]*fade_ratio + IDLE_COLOR[0]*(1-fade_ratio))
    g = int(color[1]*fade_ratio + IDLE_COLOR[1]*(1-fade_ratio))
    b = int(color[2]*fade_ratio + IDLE_COLOR[2]*(1-fade_ratio))

    for i in range(NUM_PIXELS):
        rgb.pixels[i] = (r, g, b)

keyboard.on_after_scan = update_rgb

# ----- Key press callback with debug -----
def on_press(key):
    global last_button_time
    last_button_time = time.monotonic()
    print(f"Button pressed: {key}")
    return True

keyboard.key_pressed = on_press

# ----- Start KMK -----
if __name__ == "__main__":
    print("Starting keyboard with debug...")
    keyboard.go()
