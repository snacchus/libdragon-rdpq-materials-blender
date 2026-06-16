import bpy
import addon_utils

from . import export_to_mkmaterial
from . import util

glTF2_addon_ver = None

for mod in addon_utils.modules():  # type: ignore
    if mod.__name__ == "io_scene_gltf2":
        glTF2_addon_ver = mod.bl_info["version"]
        break


# from io_scene_gltf2 import exporter_extension_layout_draw
# https://github.com/KhronosGroup/glTF-Blender-IO/commits/49b56804049c4724c89f6be49ea8382c0b63f9da/
gltf_export_props_use_exporter_extension_layout_draw = (
    glTF2_addon_ver is not None and glTF2_addon_ver >= (4, 4, 36)
)
# def draw()
# https://github.com/KhronosGroup/glTF-Blender-IO/commits/fae512b1981493794ccafb4b187f9ada3c5d3b1f/
gltf_export_props_use_draw = (
    glTF2_addon_ver is not None
    and glTF2_addon_ver < (4, 4, 36)
    and glTF2_addon_ver >= (4, 2, 40)
)
# def register_panel()
gltf_export_props_use_register_panel = (
    glTF2_addon_ver is not None and glTF2_addon_ver < (4, 2, 40)
)

if gltf_export_props_use_draw:

    def draw(context, layout):
        draw_gltf_extension_props(context, layout)


if gltf_export_props_use_register_panel:
    # https://github.com/KhronosGroup/glTF-Blender-IO/blob/3ade756cba3d9631b77cf002462b4315562e1869/example-addons/example_gltf_exporter_extension/__init__.py#L43
    def register_panel():
        try:
            bpy.utils.register_class(GLTF_PT_RDPQPanel)
        except Exception:
            pass
        return unregister_panel

    def unregister_panel():
        try:
            bpy.utils.unregister_class(GLTF_PT_RDPQPanel)
        except Exception:
            pass

    class GLTF_PT_RDPQPanel(bpy.types.Panel):

        bl_space_type = "FILE_BROWSER"
        bl_region_type = "TOOL_PROPS"
        bl_label = "libdragon RDPQ materials"
        bl_parent_id = "GLTF_PT_export_user_extensions"
        bl_options = {"DEFAULT_CLOSED"}

        @classmethod
        def poll(cls, context):
            sfile = context.space_data
            operator = sfile.active_operator
            return operator.bl_idname == "EXPORT_SCENE_OT_gltf"

        def draw(self, context):
            assert self.layout is not None
            draw_gltf_extension_props(context, self.layout)


# https://github.com/KhronosGroup/glTF-Blender-IO/blob/main/example-addons/example_gltf_exporter_extension

glTF_extension_name = "EXT_libdragon_rdpq_materials_jmat"


def export_standalone_image(
    blender_material: bpy.types.Material,
    blender_image: bpy.types.Image,
    export_settings,
):
    """Export a blender Image to a glTF TextureInfo.

    This is done by creating a temporary image texture node in the material's node
    tree, and passing that node to internal glTF code.

    Note the returned TextureInfo needs to be referenced in the glTF data
    (e.g. in the material extensions dict) for it to be present in the output glTF
    """
    assert glTF2_addon_ver is not None

    if glTF2_addon_ver >= (4, 3, 12):
        # https://github.com/KhronosGroup/glTF-Blender-IO/commits/8db37273b5d9819d8e0d964874d77ff3268537fa/
        from io_scene_gltf2.blender.exp.material import (  # type: ignore
            texture_info as gltf2_blender_gather_texture_info,
        )
    elif glTF2_addon_ver >= (3, 5, 8):
        # https://github.com/KhronosGroup/glTF-Blender-IO/commits/5c52c313bcadb4703eb34ec6d5b51d1e47c60089/
        from io_scene_gltf2.blender.exp.material import (  # type: ignore
            gltf2_blender_gather_texture_info,
        )
    else:
        from io_scene_gltf2.blender.exp import (  # type: ignore
            gltf2_blender_gather_texture_info,
        )

    saved_use_nodes = blender_material.use_nodes
    nodes = None
    temp_node = None
    temp_shader_node = None
    try:
        blender_material.use_nodes = True

        node_tree = blender_material.node_tree

        # It seems that the node_tree can never be None (Blender 4.2.11)
        assert node_tree is not None

        nodes = node_tree.nodes

        temp_node = nodes.new("ShaderNodeTexImage")
        temp_shader_node = nodes.new("ShaderNodeBsdfDiffuse")
        assert isinstance(temp_node, bpy.types.ShaderNodeTexImage)
        assert isinstance(temp_shader_node, bpy.types.ShaderNodeBsdfDiffuse)
        node_tree.links.new(temp_shader_node.inputs[0], temp_node.outputs[0])
        temp_node.image = blender_image

        # Older versions of the gltf addon require passing in an input socket
        gltf_socket = temp_shader_node.inputs[0]

        if glTF2_addon_ver >= (3, 3, 27):
            # https://github.com/KhronosGroup/glTF-Blender-IO/commits/c7e0b79bd73597da0783b36f2417e74db219716b/

            if glTF2_addon_ver >= (4, 3, 12):
                # https://github.com/KhronosGroup/glTF-Blender-IO/commits/8db37273b5d9819d8e0d964874d77ff3268537fa/
                from io_scene_gltf2.blender.exp.material import (  # type: ignore
                    search_node_tree as gltf2_blender_search_node_tree,
                )
            else:
                from io_scene_gltf2.blender.exp.material import (  # type: ignore
                    gltf2_blender_search_node_tree,
                )

            gltf_socket = gltf2_blender_search_node_tree.NodeSocket(
                gltf_socket,
                [node_tree],
            )

        res = gltf2_blender_gather_texture_info.gather_texture_info(
            gltf_socket,
            (gltf_socket,),
            export_settings,
        )
        texture_info = res[0]
    finally:
        if nodes is not None and temp_node is not None:
            nodes.remove(temp_node)
        if nodes is not None and temp_shader_node is not None:
            nodes.remove(temp_shader_node)
        blender_material.use_nodes = saved_use_nodes

    return texture_info


class glTF2ExportUserExtension:

    def __init__(self):
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension  # type: ignore

        self.Extension = Extension
        scene = bpy.context.scene
        assert scene is not None
        self.properties = util.LIBDRAGON_RDPQ(scene).gltf_extension

    def gather_material_hook(
        self,
        gltf2_material: "io_scene_gltf2.io.com.gltf2_io.Material",  # type: ignore
        blender_material: bpy.types.Material,
        export_settings,
    ):
        jmat, mat_textures = export_to_mkmaterial.rdpq_material_properties_to_dict(
            util.LIBDRAGON_RDPQ(blender_material)
        )
        for i in (0, 1):
            if i in mat_textures:
                gathered_texture_info = export_standalone_image(
                    blender_material,
                    mat_textures[i],
                    export_settings,
                )

                # gathered_texture_info.index.source is a gltf2_io.Image
                # Later on in the gltf export process, it will be picked up by the gltf
                # exporter as "child of root" data and appended to the list of images
                # in the gltf output.  Additionally texN.source will be set to the
                # corresponding index in the images array.
                jmat[f"tex{i}.source"] = gathered_texture_info.index.source
        gltf2_material.extensions[glTF_extension_name] = jmat


class glTFExtensionProperties(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="libdragon RDPQ materials",
        description="Include this extension in the exported glTF file.",
        default=True,
    )


def draw_gltf_extension_props(context: bpy.types.Context, layout: bpy.types.UILayout):
    layout.use_property_split = False
    scene = context.scene
    assert scene is not None
    layout.prop(util.LIBDRAGON_RDPQ(scene).gltf_extension, "enabled")
