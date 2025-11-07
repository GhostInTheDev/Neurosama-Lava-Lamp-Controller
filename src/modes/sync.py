import time
import struct
# Placeholder: assumes LavaLampController is available via the structure

# --- Helper function used for building the scene string ---
def _build_music_scene_string(colors, duration=60):
    """
    Builds the minimal scene string for 'music' mode activation.
    [ID=00][Count][Mode=01][Pad=00][Color Data (6 bytes each)]
    """
    scene = bytearray()
    
    # --- MINIMAL HEADER ---
    scene.append(0x00)  # ID/Version
    scene.append(len(colors))  # Color count (e.g., 0x01 for 1 color)
    scene.append(0x01)  # Mode: 0x01 is the magic byte for JUMP/MUSIC cycling!
    scene.append(0x00)  # Padding/Flags
    
    # --- Color Data (HSV, 2 bytes each, Big Endian) ---
    for h, s, v in colors:
        scene.extend(struct.pack('>H', h))
        scene.extend(struct.pack('>H', s))
        scene.extend(struct.pack('>H', v))
    
    return scene.hex()


# THE SYNC FUNCTION
def stream_sync(lamp):
    """
    Activates the single-command 'Stream Sync' mode (ON) or deactivates it (OFF).
    If duration is provided, it runs for that duration, then cleans up.
    """
    print("\n🎧 Activating Stream Sync Mode...")
    
    # Use a single, stable color (Red) for the minimal DPS 25 packet
    colors = [(0, 1000, 1000)]
    
    scene_hex = _build_music_scene_string(colors)
    
    try:
        # 1. Set mode to 'music' (DPS 21)
        lamp.set_mode('music') 
        time.sleep(0.5)
        
        # 2. Send the minimal structured command (DPS 25)
        lamp.set_scene_raw(scene_hex)
        time.sleep(0.5)
        
        # 3. TOGGLE THE MUSIC STATE FLAG (DPS 27) - The 'GO' button
        lamp.set_music_toggle(True)
        print(f"✅ Stream Sync mode activated.")
        
        # Cleanup logic for scheduled runs
        # if duration is not None:
        #      time.sleep(duration)
        #      lamp.set_music_toggle(False)
        #      # CRITICAL FIX: Switch back to a standard mode after disabling toggle
        #      lamp.set_mode('colour')
        #      print("⏯️  Stream Sync mode toggle deactivated and set back to 'colour' mode.")

    except Exception as e:
        print(f"❌ Failed to activate sync mode: {e}")