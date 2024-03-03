bl_info = {
    "name": "Trinity Skeleton Exporter (.json)",
    "author": "Tavi & Luma & ElChicoEevee",
    "version": (0, 0, 2),
    "blender": (3, 3, 0),
    "location": "File > Export",
    "description": "Blender addon for exporting armature as a Trinity Skeleton Json for later conversion with the proper schema. It uses code from source-tools and export-dae",
    "warning": "",
    "category": "Export",
}

import bpy
import json
import os
from bpy_extras.io_utils import ExportHelper
from mathutils import Matrix, Vector
from math import *
class TRSKLJsonExport(bpy.types.Operator, ExportHelper):
    bl_idname = "custom_export_scene.trskljsonexport"
    bl_label = "Export"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".json"  # Specify the default file extension

    def execute(self, context):
        directory = os.path.dirname(self.filepath)
        armature_obj = bpy.context.active_object

        if armature_obj and armature_obj.type == 'ARMATURE':
            data = export_armature_matrix(armature_obj)
            # Save the data to a JSON file
            with open(os.path.join(directory, self.filepath), "w") as file:
                json.dump(data, file, indent=4)
                
            print("Bone matrices exported successfully.")
        else:
            print("No armature selected.")
        return {'FINISHED'}

rx90 = Matrix.Rotation(radians(90),4,'X')
ry90 = Matrix.Rotation(radians(90),4,'Y')
rz90 = Matrix.Rotation(radians(90),4,'Z')
ryz90 = ry90 @ rz90

rx90n = Matrix.Rotation(radians(-90),4,'X')
ry90n = Matrix.Rotation(radians(-90),4,'Y')
rz90n = Matrix.Rotation(radians(-90),4,'Z')


def is_zero_scale(matrix):
    if (matrix[0][0] == 0.0) and (matrix[1][1] == 0) and (matrix[2][2] == 0):
        return True
    else:
        return False

def get_bone_local_transform(bone):
    visible = True
    armature = bone.id_data  # Assuming bone is part of an armature

    if not armature:
        return None  # If not part of an armature, return None or handle accordingly

    parent_bone = armature.data.bones[bone.parent.name] if bone.parent else None

    if parent_bone:
        pose_parent = armature.pose.bones[parent_bone.name]
        if is_zero_scale(pose_parent.matrix) or is_zero_scale(armature.matrix_world):
            visible = False
            matrix = Matrix()
        else:
            matrix = bone.matrix.copy()
    else:
        matrix = bone.matrix.copy()
    return {"matrix": matrix}, visible
def strflt(x):
    return '{0:.6f}'.format(x)


def strmtx(mtx):
    out = Matrix([mtx[0], mtx[2], mtx[1], mtx[3]])
    out.transpose()
    out = Matrix([out[0], out[2], out[1], out[3]])
    out.transpose()
    return " ".join([strflt(e) for v in out for e in v])

def is_bone_weighted(armature, bone_name):
    a = False
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for modifier in obj.modifiers:
                if modifier.type == 'ARMATURE' and modifier.object == armature:
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.mode_set(mode='OBJECT')

                    armature_data = modifier.object.data

                    try:

                        bpy.ops.object.mode_set(mode='OBJECT')  # Switch back to OBJECT mode

                        # Check if the bone is in the vertex groups
                        if bone_name in obj.vertex_groups:
                            a = True
                    except (KeyError, IndexError):
                        pass

    return a
    
def getEvaluatedPoseBones(armature_obj):
	depsgraph = bpy.context.evaluated_depsgraph_get()
	evaluated_armature = armature_obj.evaluated_get(depsgraph)

	return [evaluated_armature.pose.bones[bone.name] for bone in self.exportable_bones]


def getSmdFloat(fval):
	return "{:.6f}".format(float(fval))


def getSmdVec(iterable):
	return " ".join([getSmdFloat(val) for val in iterable])
    
    
def export_armature_matrix(armature_obj):
    transform_nodes = []
    bones = []
    data = {
        "res_0": 0,
        "transform_nodes": transform_nodes,
        "bones": bones,
                "iks": [
    
                ],
                "rig_offset": 0
            }


    # Assume the armature has only one pose for simplicity
    armature_obj.select_set(True)
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='POSE')
    mat_BlenderToSMD = ry90 @ rz90
    for posebone in armature_obj.pose.bones:
        inherit_position = 1  # Set tow 1 for example, you can modify this based on your requirements
        matrix = posebone.matrix
        result = is_bone_weighted(armature_obj, posebone.name)
        transform, visible = get_bone_local_transform(posebone)
      
        a = strmtx(transform["matrix"])
        if result == True:
            bones.append({
                    "inherit_position": inherit_position,
                    "unk_bool_2": 1,
                    "matrix": {
                        "x": {
                            "x": round(matrix[0][0], 6),
                            "y": round(matrix[0][1], 6),
                            "z": round(matrix[0][2], 6)
                        },
                        "y": {
                            "x": round(matrix[1][0], 6),
                            "y": round(matrix[1][1], 6),
                            "z": round(matrix[1][2], 6)
                        },
                        "z": {
                            "x": round(matrix[2][0], 6),
                            "y": round(matrix[2][1], 6),
                            "z": round(matrix[2][2], 6)
                        },
                        "w": {
                            "x": float(a.split(" ")[7]),
                            "y": float(a.split(" ")[3]),
                            "z": float(a.split(" ")[11])
                        },
                        # THIS IS THE F - n trouble child
                    }})

        parent = posebone.parent
        if result == True:
            bone_index = armature_obj.data.bones.find(posebone.name) - 2
        else:
            bone_index = -1
        # Get the parent index
        parent_index = -1  # Default value for bones without a parent
        if posebone.parent:
            parent_index = armature_obj.data.bones.find(posebone.parent.name)
        # Get the bone's Matrix from the current pose
        PoseMatrix = posebone.matrix
        if armature_obj.data.vs.legacy_rotation:
            PoseMatrix @= mat_BlenderToSMD 
        if parent:
            parentMat = parent.matrix
            if armature_obj.data.vs.legacy_rotation: parentMat @= mat_BlenderToSMD 
            PoseMatrix = parentMat.inverted() @ PoseMatrix
        else:
            PoseMatrix = armature_obj.matrix_world @ PoseMatrix

        transform_nodes.append({
                "name": posebone.name,
                "transform": {
                    "VecScale": {
                        "x": 1.0,
                        "y": 1.0,
                        "z": 1.0
                    },
                    "VecRot": {
                        "x": float(getSmdVec(PoseMatrix.to_euler()).split()[0]),
                        "y": float(getSmdVec(PoseMatrix.to_euler()).split()[1]),
                        "z": float(getSmdVec(PoseMatrix.to_euler()).split()[2])
                    },
                    "VecTranslate": {
                        "x": float(getSmdVec(PoseMatrix.to_translation()).split()[0]),
                        "y": float(getSmdVec(PoseMatrix.to_translation()).split()[1]),
                        "z": float(getSmdVec(PoseMatrix.to_translation()).split()[2])
                    }
                },
                "scalePivot": {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                },
                "rotatePivot": {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 0.0
                },
                "parent_idx": parent_index,
                "rig_idx": bone_index,
                "effect_node": "",
                "type": "Default"
                })
    return data

def menu_func_export(self, context):
    self.layout.operator(TRSKLJsonExport.bl_idname, text="Trinity Skeleton (.json)")

def register():
    bpy.utils.register_class(TRSKLJsonExport)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(TRSKLJsonExport)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
