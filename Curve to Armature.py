bl_info = {
    "name": "Curve to Armature",
    "author": "ChatGPT",
    "version": (1, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Object > Convert Curve to Armature",
    "description": "Generate bones along the curve control points (Bezier, NURBS, Poly)",
    "category": "Object",
}

import bpy
import mathutils

class OBJECT_OT_curve_to_armature(bpy.types.Operator):
    bl_idname = "object.curve_to_armature"
    bl_label = "Convert Curve to Armature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'CURVE':
            self.report({'ERROR'}, "アクティブオブジェクトがカーブではありません")
            return {'CANCELLED'}

        curve_obj = obj
        armature_data = bpy.data.armatures.new(curve_obj.name + "_Armature")
        armature_obj = bpy.data.objects.new(curve_obj.name + "_Armature", armature_data)
        context.collection.objects.link(armature_obj)

        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = armature_obj.data.edit_bones

        bone_index = 0  # ボーンの通し番号

        for spline in curve_obj.data.splines:
            prev_bone = None
            is_bezier = spline.type == 'BEZIER'

            # BEZIER: bezier_points, それ以外: points
            points = spline.bezier_points if is_bezier else spline.points

            for i in range(len(points)):
                point = points[i]
                co = point.co.xyz if not is_bezier else point.co  # NURBS/POLYは4Dベクトル（w含む）
                world_co = curve_obj.matrix_world @ co

                bone = edit_bones.new(f"Bone_{bone_index}")
                bone.head = world_co

                # tailの設定
                if i < len(points) - 1:
                    next_point = points[i + 1]
                    next_co = next_point.co.xyz if not is_bezier else next_point.co
                    bone.tail = curve_obj.matrix_world @ next_co
                else:
                    bone.tail = world_co + mathutils.Vector((0, 0.1, 0))

                # 親子関係
                if prev_bone:
                    bone.parent = prev_bone
                    bone.use_connect = True

                prev_bone = bone
                bone_index += 1

        bpy.ops.object.mode_set(mode='OBJECT')
        self.report({'INFO'}, "アーマチュアを生成しました")
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(OBJECT_OT_curve_to_armature.bl_idname)


def register():
    bpy.utils.register_class(OBJECT_OT_curve_to_armature)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_curve_to_armature)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
