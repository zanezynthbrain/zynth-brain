# TD.3. Blender Automation & Python Logic

This document provides the Python logic and code snippets for the ZYNTH AI agent to autonomously generate high-fidelity 3D scenes in Blender.

## 1. Core Scene Setup Logic

### 1.1. Unit & Scale Configuration
Always ensure the scene uses Metric units and a scale of 1.0.
```python
import bpy
bpy.context.scene.unit_settings.system = 'METRIC'
bpy.context.scene.unit_settings.scale_length = 1.0
```

### 1.2. PBR Material Creation
To create professional materials (Metal, Glass, Plastic), use the Principled BSDF shader.
```python
def create_pbr_material(name, color=(1,1,1,1), metallic=0.0, roughness=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    return mat
```

## 2. Spatial Layout Automation

### 2.1. Truss Generation Logic
Trusses are the backbone of event design.
```python
def create_truss_section(length, location=(0,0,0)):
    # Logic to create a box-truss section
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    truss = bpy.context.active_object
    truss.scale = (length, 0.3, 0.3)
    return truss
```

### 2.2. Lighting Rig Setup
```python
def setup_stage_wash(location=(0, -5, 5), energy=1000):
    bpy.ops.object.light_add(type='AREA', location=location)
    light = bpy.context.active_object
    light.data.energy = energy
    light.data.size = 5.0
    light.rotation_euler = (0.785, 0, 0) # 45 degrees down
```

## 3. Advanced Tactical Logic: "The Detail Layer"

To move beyond "sketches," the AI must apply these details:
- **Beveling**: Never leave edges perfectly sharp. Apply a small Bevel modifier to all structural elements.
- **Emission**: Use emissive materials for LED screens and accent lighting.
- **HDRI Environment**: Always load an HDRI (High Dynamic Range Image) for realistic reflections and ambient lighting.

## 4. SOP: Executing 3D Tasks via MCP
1.  **Initialize**: Clear the default cube and setup units.
2.  **Generate Materials**: Create a library of materials based on the theme (from TD.4).
3.  **Build Geometry**: Run Python loops to place walls, trusses, and furniture.
4.  **Lighting & Camera**: Setup the "Master Shot" camera and professional lighting.
5.  **Render/Export**: Send the final command to render a preview or export the .blend file.
