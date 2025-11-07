# src/modes/__init__.py

# Import all specific mode functions from their respective files
from .basic import demo_basic_colors
from .rainbow import demo_rainbow, demo_random_rainbow 
from .party import demo_party_mode
from .nature import demo_fire_effect, demo_ocean_effect, demo_sunset_mode
from .utility import demo_police_lights, demo_strobe, demo_breathing
from .pastel import demo_pastel_mode
from .sync import stream_sync # Import the renamed sync function


# The mode registry dictionary, mapping command names to the function that runs them
all_modes = {
    # Demo from basic.py
    "basic_colors": demo_basic_colors, 
    
    # Modes from rainbow.py (UPDATED)
    "rainbow": demo_rainbow,             # Smooth cycle
    "random_rainbow": demo_random_rainbow, # New random mode

    # Modes from other files (assuming standard function names)
    "party": demo_party_mode,
    "fire": demo_fire_effect,
    "ocean": demo_ocean_effect,
    "sunset": demo_sunset_mode,
    "police": demo_police_lights,
    "strobe": demo_strobe,
    "breathing": demo_breathing,
    "pastel": demo_pastel_mode,
    
    # UPDATED: Sync mode registration
    "sync": stream_sync, 
}