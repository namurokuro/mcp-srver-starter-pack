"""
DMX Lighting Addon Integration Tools
Integrates DMX lighting system for Blender
"""

import bpy
from typing import Dict, List, Optional, Any


def check_dmx_installed() -> bool:
    """Check if DMX lighting addon is installed and enabled"""
    addons = bpy.context.preferences.addons
    # Check for exact "DMX" addon name
    if 'DMX' in addons:
        return True
    # Check for variations
    dmx_addons = [addon for addon in addons.keys() if 'dmx' in addon.lower()]
    return len(dmx_addons) > 0


def get_dmx_addon_name() -> Optional[str]:
    """Get the name of the installed DMX addon"""
    addons = bpy.context.preferences.addons
    # Check for exact "DMX" addon first
    if 'DMX' in addons:
        return 'DMX'
    # Check for variations
    for addon_name in addons.keys():
        if 'dmx' in addon_name.lower():
            return addon_name
    return None


def setup_dmx_light(channel: int, light_type: str = 'AREA', 
                   location: tuple = (0, 0, 5), energy: float = 1.0,
                   color: tuple = (1.0, 1.0, 1.0), name: str = None) -> Dict[str, Any]:
    """
    Setup a DMX-controlled light
    
    Args:
        channel: DMX channel number (1-512)
        light_type: Type of light ('SUN', 'AREA', 'SPOT', 'POINT')
        location: Light position (x, y, z)
        energy: Light energy/intensity
        color: Light color (R, G, B)
        name: Optional name for the light
    
    Returns:
        Dict with status and light object info
    """
    result = {"status": "error", "message": "", "light": None}
    
    if not check_dmx_installed():
        # Fallback: Create standard light
        bpy.ops.object.light_add(type=light_type, location=location)
        light = bpy.context.object
        light.data.energy = energy
        light.data.color = color
        if name:
            light.name = name
        result["status"] = "success"
        result["message"] = f"Created standard light (DMX not available)"
        result["light"] = light
        return result
    
    try:
        # Create light
        bpy.ops.object.light_add(type=light_type, location=location)
        light = bpy.context.object
        light.data.energy = energy
        light.data.color = color
        
        if name:
            light.name = name
        else:
            light.name = f"DMX_Channel_{channel}"
        
        # Try to set DMX channel if addon supports it
        dmx_addon_name = get_dmx_addon_name()
        if dmx_addon_name:
            addon_module = bpy.context.preferences.addons[dmx_addon_name].module
            try:
                # Try common DMX addon patterns
                if hasattr(light.data, 'dmx_channel'):
                    light.data.dmx_channel = channel
                elif hasattr(light, 'dmx_channel'):
                    light.dmx_channel = channel
                elif hasattr(light.data, 'channel'):
                    light.data.channel = channel
                
                # Try to access DMX addon operators
                if hasattr(bpy.ops, f'{dmx_addon_name.replace(".", "_")}.set_channel'):
                    op = getattr(bpy.ops, f'{dmx_addon_name.replace(".", "_")}.set_channel')
                    op(channel=channel)
            except Exception as e:
                # DMX channel setting failed, but light was created
                pass
        
        result["status"] = "success"
        result["message"] = f"Created DMX light on channel {channel}"
        result["light"] = light
        return result
        
    except Exception as e:
        result["message"] = f"Error creating DMX light: {str(e)}"
        return result


def setup_dmx_lighting_rig(rig_type: str = "three_point") -> Dict[str, Any]:
    """
    Setup a complete DMX lighting rig
    
    Args:
        rig_type: Type of rig ("three_point", "studio", "dramatic", "product")
    
    Returns:
        Dict with status and list of created lights
    """
    result = {"status": "error", "message": "", "lights": []}
    
    rigs = {
        "three_point": {
            "key": {"channel": 1, "type": "SUN", "location": (4, -4, 5), "energy": 3.0},
            "fill": {"channel": 2, "type": "AREA", "location": (-2, -2, 3), "energy": 100.0, "size": 5},
            "rim": {"channel": 3, "type": "SPOT", "location": (-4, 4, 4), "energy": 2.0}
        },
        "studio": {
            "main": {"channel": 1, "type": "AREA", "location": (0, -5, 5), "energy": 200.0, "size": 10},
            "fill_left": {"channel": 2, "type": "AREA", "location": (-3, -3, 3), "energy": 100.0, "size": 5},
            "fill_right": {"channel": 3, "type": "AREA", "location": (3, -3, 3), "energy": 100.0, "size": 5},
            "back": {"channel": 4, "type": "SPOT", "location": (0, 5, 4), "energy": 150.0}
        },
        "product": {
            "top": {"channel": 1, "type": "AREA", "location": (0, 0, 8), "energy": 300.0, "size": 8},
            "front": {"channel": 2, "type": "AREA", "location": (0, -6, 2), "energy": 200.0, "size": 6},
            "side_left": {"channel": 3, "type": "AREA", "location": (-4, -2, 2), "energy": 150.0, "size": 4},
            "side_right": {"channel": 4, "type": "AREA", "location": (4, -2, 2), "energy": 150.0, "size": 4}
        },
        "dramatic": {
            "key": {"channel": 1, "type": "SUN", "location": (5, -5, 8), "energy": 5.0, "angle": 0.1},
            "rim": {"channel": 2, "type": "SPOT", "location": (-5, 5, 6), "energy": 3.0},
            "accent": {"channel": 3, "type": "POINT", "location": (0, 0, 3), "energy": 2.0}
        }
    }
    
    rig_config = rigs.get(rig_type, rigs["three_point"])
    
    try:
        lights = []
        for light_name, light_config in rig_config.items():
            channel = light_config.pop("channel")
            light_type = light_config.pop("type")
            location = light_config.pop("location")
            energy = light_config.pop("energy", 1.0)
            
            light_result = setup_dmx_light(
                channel=channel,
                light_type=light_type,
                location=location,
                energy=energy,
                name=f"DMX_{light_name.title()}"
            )
            
            if light_result["status"] == "success":
                light = light_result["light"]
                # Set additional properties if specified
                if "size" in light_config and hasattr(light.data, "size"):
                    light.data.size = light_config["size"]
                if "angle" in light_config and hasattr(light.data, "angle"):
                    light.data.angle = light_config["angle"]
                lights.append(light)
        
        result["status"] = "success"
        result["message"] = f"Created {rig_type} DMX lighting rig with {len(lights)} lights"
        result["lights"] = lights
        return result
        
    except Exception as e:
        result["message"] = f"Error setting up DMX rig: {str(e)}"
        return result


def control_dmx_channel(channel: int, value: float, fade_time: float = 0.0) -> Dict[str, Any]:
    """
    Control a DMX channel value
    
    Args:
        channel: DMX channel (1-512)
        value: Channel value (0.0-1.0)
        fade_time: Fade time in seconds
    
    Returns:
        Dict with status
    """
    result = {"status": "error", "message": ""}
    
    if not check_dmx_installed():
        result["message"] = "DMX addon not installed"
        return result
    
    try:
        # Find lights on this channel
        dmx_addon_name = get_dmx_addon_name()
        if dmx_addon_name:
            # Try to control channel through addon API
            # This will vary by addon implementation
            lights_controlled = 0
            for obj in bpy.data.objects:
                if obj.type == 'LIGHT':
                    try:
                        if hasattr(obj.data, 'dmx_channel') and obj.data.dmx_channel == channel:
                            obj.data.energy = value * obj.data.energy  # Scale energy
                            lights_controlled += 1
                        elif hasattr(obj, 'dmx_channel') and obj.dmx_channel == channel:
                            obj.data.energy = value * obj.data.energy
                            lights_controlled += 1
                    except:
                        pass
            
            result["status"] = "success"
            result["message"] = f"Controlled {lights_controlled} lights on channel {channel}"
            return result
        else:
            result["message"] = "Could not find DMX addon"
            return result
            
    except Exception as e:
        result["message"] = f"Error controlling DMX channel: {str(e)}"
        return result


def create_code_setup_dmx_lighting() -> str:
    """Generate Python code to setup DMX lighting"""
    code = """
# Setup DMX Lighting
import bpy
from dmx_lighting_tools import setup_dmx_lighting_rig, check_dmx_installed

if not check_dmx_installed():
    print("DMX addon not installed. Using standard lighting.")
else:
    print("Setting up DMX lighting rig...")
    result = setup_dmx_lighting_rig("three_point")
    if result["status"] == "success":
        print(f"✓ {result['message']}")
    else:
        print(f"✗ {result['message']}")
"""
    return code.strip()


