import bpy
import math

def clear_scene():
    """Clear all objects and materials to start fresh."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)

def create_material(name, color, emission=False, emission_strength=1.0):
    """Create a basic principled BSDF material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        
        # Adjust for Blender Principled BSDF emission changes
        if emission:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = color
            elif 'Emission' in bsdf.inputs:
                bsdf.inputs['Emission'].default_value = color
            if 'Emission Strength' in bsdf.inputs:
                bsdf.inputs['Emission Strength'].default_value = emission_strength
    return mat

def add_text(text, location, scale=1.0, color=(1,1,1,1)):
    """Add 3D text to the scene."""
    bpy.ops.object.text_add(location=location)
    txt_obj = bpy.context.active_object
    txt_obj.data.body = text
    txt_obj.scale = (scale, scale, scale)
    txt_obj.rotation_euler = (math.radians(75), 0, 0)
    txt_obj.data.extrude = 0.1
    
    mat = create_material(f"Mat_Text_{text}", color, emission=True, emission_strength=2.0)
    txt_obj.data.materials.append(mat)
    return txt_obj

def build_architecture_visualization():
    clear_scene()
    
    mat_sim = create_material("MatSim", (0.2, 0.8, 0.2, 1))
    mat_back = create_material("MatBack", (0.8, 0.2, 0.2, 1))
    mat_ml = create_material("MatML", (0.2, 0.2, 0.8, 1))
    mat_front = create_material("MatFront", (0.8, 0.8, 0.2, 1))
    mat_data = create_material("MatData", (1, 1, 1, 1), emission=True, emission_strength=5.0)
    mat_line = create_material("MatLine", (0.1, 0.1, 0.1, 1))

    # 1. Simulator Node
    bpy.ops.mesh.primitive_cube_add(size=2, location=(-8, 0, 0))
    sim = bpy.context.active_object
    sim.data.materials.append(mat_sim)
    add_text("Telemetry Simulator", (-9.5, -1, 1.5), scale=0.5)

    # 2. FastAPI Backend
    bpy.ops.mesh.primitive_cube_add(size=3, location=(0, 0, 0))
    back = bpy.context.active_object
    back.data.materials.append(mat_back)
    add_text("FastAPI Backend", (-1.5, -1, 2), scale=0.5)

    # 3. ML Models
    bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=1.5, location=(0, 6, 0))
    ml = bpy.context.active_object
    ml.data.materials.append(mat_ml)
    add_text("AI Models (SciKit)", (-1.5, 5, 1.5), scale=0.5)

    # 4. React Dashboard
    bpy.ops.mesh.primitive_cube_add(size=2, location=(8, 0, 0))
    front = bpy.context.active_object
    front.scale = (1, 2, 0.1)
    front.data.materials.append(mat_front)
    add_text("React Dashboard UI", (6.5, -1, 1.5), scale=0.5)

    # Lines / Paths
    # Sim to Back
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(-4, 0, 0))
    l1 = bpy.context.active_object
    l1.scale = (30, 1, 1)
    l1.data.materials.append(mat_line)

    # Back to ML
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(0, 3, 0))
    l2 = bpy.context.active_object
    l2.scale = (1, 30, 1)
    l2.data.materials.append(mat_line)

    # Back to Front
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(4, 0, 0))
    l3 = bpy.context.active_object
    l3.scale = (30, 1, 1)
    l3.data.materials.append(mat_line)

    # Animation Setup
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 220

    # Data Packet 1 (Sim -> Back) - Raw Telemetry
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(-7, 0, 0.5))
    pkt1 = bpy.context.active_object
    pkt1.data.materials.append(mat_data)
    pkt1.keyframe_insert(data_path="location", frame=1)
    pkt1.location = (-1.5, 0, 0.5)
    pkt1.keyframe_insert(data_path="location", frame=50)
    pkt1.hide_viewport = False
    pkt1.keyframe_insert(data_path="hide_viewport", frame=50)
    pkt1.hide_viewport = True
    pkt1.keyframe_insert(data_path="hide_viewport", frame=51)

    # Data Packet 2 (Back -> ML) - Data for Inference
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(0, 1.5, 0.5))
    pkt2 = bpy.context.active_object
    pkt2.data.materials.append(mat_data)
    pkt2.hide_viewport = True
    pkt2.keyframe_insert(data_path="hide_viewport", frame=49)
    pkt2.hide_viewport = False
    pkt2.keyframe_insert(data_path="hide_viewport", frame=50)
    pkt2.keyframe_insert(data_path="location", frame=50)
    pkt2.location = (0, 4.5, 0.5)
    pkt2.keyframe_insert(data_path="location", frame=80)
    pkt2.hide_viewport = False
    pkt2.keyframe_insert(data_path="hide_viewport", frame=80)
    pkt2.hide_viewport = True
    pkt2.keyframe_insert(data_path="hide_viewport", frame=81)

    # Data Packet 3 (ML -> Back) - AI Prediction Return (Glowing Green)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0, 4.5, 0.5))
    pkt3 = bpy.context.active_object
    mat_pred = create_material("MatPred", (0, 1, 0, 1), emission=True, emission_strength=10)
    pkt3.data.materials.append(mat_pred)
    pkt3.hide_viewport = True
    pkt3.keyframe_insert(data_path="hide_viewport", frame=89)
    pkt3.hide_viewport = False
    pkt3.keyframe_insert(data_path="hide_viewport", frame=90)
    pkt3.keyframe_insert(data_path="location", frame=90)
    pkt3.location = (0, 1.5, 0.5)
    pkt3.keyframe_insert(data_path="location", frame=120)
    pkt3.hide_viewport = False
    pkt3.keyframe_insert(data_path="hide_viewport", frame=120)
    pkt3.hide_viewport = True
    pkt3.keyframe_insert(data_path="hide_viewport", frame=121)

    # Data Packet 4 (Back -> Front) - WebSocket Broadcast
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(1.5, 0, 0.5))
    pkt4 = bpy.context.active_object
    pkt4.data.materials.append(mat_pred)
    pkt4.hide_viewport = True
    pkt4.keyframe_insert(data_path="hide_viewport", frame=129)
    pkt4.hide_viewport = False
    pkt4.keyframe_insert(data_path="hide_viewport", frame=130)
    pkt4.keyframe_insert(data_path="location", frame=130)
    pkt4.location = (7, 0, 0.5)
    pkt4.keyframe_insert(data_path="location", frame=180)

    # Dashboard UI updates text
    ui_text = add_text("Updating Live Charts...", (6.5, -2.5, 1.5), scale=0.4, color=(1, 0.5, 0, 1))
    ui_text.hide_viewport = True
    ui_text.keyframe_insert(data_path="hide_viewport", frame=1)
    ui_text.hide_viewport = True
    ui_text.keyframe_insert(data_path="hide_viewport", frame=179)
    ui_text.hide_viewport = False
    ui_text.keyframe_insert(data_path="hide_viewport", frame=180)

    # Camera Setup
    bpy.ops.object.camera_add(location=(0, -15, 12), rotation=(math.radians(50), 0, 0))
    cam = bpy.context.active_object
    bpy.context.scene.camera = cam

    # Lighting
    bpy.ops.object.light_add(type='SUN', location=(10, -10, 20))
    light = bpy.context.active_object
    light.data.energy = 5
    light.data.angle = math.radians(15)
    
    try:
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    except TypeError:
        try:
            bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
        except Exception:
            pass

    print("Working Architecture Visualization Generated!")

if __name__ == "__main__":
    build_architecture_visualization()
