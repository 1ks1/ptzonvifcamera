from onvif import ONVIFCamera
import tkinter as tk
from tkinter import ttk
import sys
import ast

# Load config file
def load_config(filename):
    config = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                key, value = line.strip().split('=')
                config[key] = value
    except Exception as e:
        print(f"Configuration loading error: {e}")
    return config

# Load settings from config
config = load_config('config.inf')
ip = config.get('IP', '192.168.88.199')
port = int(config.get('PORT', 8899))
username = config.get('USERNAME', 'admin')
password = config.get('PASSWORD', 'admin')

# Init camera
try:
    camera = ONVIFCamera(ip, port, username, password)
    print("Cam is inited")
except Exception as e:
    print("Error initialise camera:", e)
    sys.exit()    

# Get PTZ-service
try:
    ptz_service = camera.create_ptz_service()
except Exception as e:
    print("Error getting PTZ-service:", e)
    sys.exit()

# Moving camera to preset if it exists 
def move_preset(presets,profiles,preset):
    if profiles and presets and len(presets) >= preset:
        p = int(preset)
        profile_token = profiles[0].token  
        token = int(presets[p-1].token)
        ptz_service.GotoPreset({'ProfileToken': profile_token,'PresetToken': token})
        print(f"Camera moed to {presets[p-1]['Name']}")
    else:
        print("Cant find presets")
 
    
# Getting profiles
try:
    media_service = camera.create_media_service()
    profiles = media_service.GetProfiles()
    print(profiles)
    print("==============profiles_count===============")
    profiles_count=len(profiles)
    print(profiles_count)
    token=profiles[1].token
    presets = ptz_service.GetPresets({'ProfileToken': token})
    print("Available presets:")
    # print(presets)
    for i, preset in enumerate(presets):
        print(f"{i + 1}. Name: {preset.Name}, Token: {preset.token}")
except Exception as e:
    print("Error getting profiles:", e)
    sys.exit()    


# Function for moving to position
def go_to_position():
    selected_name = combobox.get()
    for preset in presets:
        if preset['Name'] == selected_name:
            selected_preset = preset
    print(selected_preset)
    p_name = selected_preset['Name']
    p_token = int(selected_preset['token'])
    print(f"Mov to position : {p_name}")
    move_preset(presets,profiles,p_token)




# Function works with PTZ presets
def move_preset_one(event=None):
    move_preset(presets,profiles,1)

def move_preset_two(event=None):
    move_preset(presets,profiles,2)

def move_preset_3(event=None):
    move_preset(presets,profiles,3)

# Combobox presets
def combobox_preset(preset_number):
    move_preset(presets,profiles,preset_number)

    
# Functions for PTZ when invers move
def move_up(event=None):
    ptz_service.ContinuousMove({'ProfileToken': 'Profile_1', 'Velocity': {'PanTilt': {'x': 0, 'y': 0.5}}})

def move_down(event=None):
    ptz_service.ContinuousMove({'ProfileToken': 'Profile_1', 'Velocity': {'PanTilt': {'x': 0, 'y': -0.5}}})

def move_left(event=None):
    direction = -0.5 if not invert_var.get() else 0.5
    ptz_service.ContinuousMove({'ProfileToken': 'Profile_1', 'Velocity': {'PanTilt': {'x': direction, 'y': 0}}})

def move_right(event=None):
    direction = 0.5 if not invert_var.get() else -0.5
    ptz_service.ContinuousMove({'ProfileToken': 'Profile_1', 'Velocity': {'PanTilt': {'x': direction, 'y': 0}}})

def stop_move(event=None):
    ptz_service.Stop({'ProfileToken': 'Profile_1'})

# Function for indicate window size 
def update_window_size(event):
    size_label.config(text=f"{root.winfo_width()}x{root.winfo_height()}")

# GUI
root = tk.Tk()
root.title("PTZ Cam onvif")
root.geometry("300x380")

# Settings of weights
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_rowconfigure(5, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)


# Creating combobox of presets
combobox = ttk.Combobox(root, height=1, width=8, values=[(preset['Name']) for preset in presets], state='readonly')
combobox.grid(row=5, column=1, padx=1, pady=1)
if presets:
    combobox.current(0)

# Creating button for go to position
button = tk.Button(root, text="Go to", height=1, width=8, command=go_to_position)
button.grid(row=5, column=2, pady=1)

# Checkbox for inversion moving
invert_var = tk.BooleanVar()
invert_var.set(config.get('INVERT_DIRECTION', 'true').lower() == 'true')  # Setting the state from the configuration
invert_checkbox = tk.Checkbutton(root, text="R ↔ L", variable=invert_var)
invert_checkbox.grid(row=3, column=1, pady=5)

# Create buttons and assotiate it with functions
up_button = tk.Button(root, text="↑", height=2, width=5)
up_button.grid(row=0, column=1, sticky="nsew", pady=5)
up_button.bind("<ButtonPress>", move_up)
up_button.bind("<ButtonRelease>", stop_move)

down_button = tk.Button(root, text="↓", height=2, width=5)
down_button.grid(row=2, column=1, sticky="nsew", pady=5)
down_button.bind("<ButtonPress>", move_down)
down_button.bind("<ButtonRelease>", stop_move)

left_button = tk.Button(root, text="←", height=2, width=5)
left_button.grid(row=1, column=0, sticky="nsew", pady=5)
left_button.bind("<ButtonPress>", move_left)
left_button.bind("<ButtonRelease>", stop_move)

right_button = tk.Button(root, text="→", height=2, width=5)
right_button.grid(row=1, column=2, sticky="nsew", pady=5)
right_button.bind("<ButtonPress>", move_right)
right_button.bind("<ButtonRelease>", stop_move)

#==================================
# preset 1
right_button = tk.Button(root, text="1", height=1, width=1)
right_button.grid(row=4, column=0, sticky="nsew", pady=5)
right_button.bind("<ButtonPress>", move_preset_one)

# preset 2
right_button = tk.Button(root, text="2", height=1, width=1)
right_button.grid(row=4, column=1, sticky="nsew", pady=5)
right_button.bind("<ButtonPress>", move_preset_two)

# preset 3
right_button = tk.Button(root, text="3", height=1, width=1)
right_button.grid(row=4, column=2, sticky="nsew", pady=5)
right_button.bind("<ButtonPress>", move_preset_3)

# Indicator window size
size_label = tk.Label(root, text=f"{root.winfo_width()}x{root.winfo_height()}")
size_label.grid(row=3, column=2, pady=5)

# Bind update window size to event of window change size
root.bind("<Configure>", update_window_size)

# Start main
try:
    root.mainloop()
except Exception as e:
    print(f"Error main cicle: {e}")
