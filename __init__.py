bl_info = {
    "name": "libdragon RDPQ materials",
    "version": (0, 0, 1),
    "author": "Dragorn421",
    "location": "Material Properties",
    "description": "RDPQ materials for the libdragon N64 homebrew SDK",
    "category": "Material",
    "blender": (3, 2, 0),
}

# bl_info docs:
# https://projects.blender.org/blender/blender-developer-docs/src/commit/69734d611d9c90fe51146e76b10b0f36bbcb7214/docs/handbook/addons/addon_meta_info.md

import bpy
import bpy.utils

from . import export_to_mkmaterial
from . import gltf_extension
from . import rdpq_material_props
from . import sync_to_fast64
from . import util

# import glTF2ExportUserExtension into __init__.py
# to make the extension visible to the glTF addon
from .gltf_extension import glTF2ExportUserExtension

# Used by old versions of the gltf addon
if gltf_extension.gltf_export_props_use_draw:
    from .gltf_extension import draw
if gltf_extension.gltf_export_props_use_register_panel:
    from .gltf_extension import register_panel


import importlib

loc = locals()
for n in (
    "export_to_mkmaterial",
    "gltf_extension",
    "rdpq_material_props",
    "rdpq_material_props_logic",
    "sync_to_fast64",
    "util",
):
    if n in loc:
        importlib.reload(loc[n])
    else:
        importlib.import_module(".%s" % n, __package__)


class RDPQWorldDefaultsPlaceholderProperties(bpy.types.PropertyGroup):
    slot_index: bpy.props.IntProperty(
        name="Slot",
        description="",
        default=1,
        min=1,
        max=15,
    )
    image: bpy.props.PointerProperty(
        type=bpy.types.Image,
        name="Image",
        description="",
    )


class RDPQWorldDefaultsProperties(bpy.types.PropertyGroup):
    antialias: bpy.props.EnumProperty(
        name="Antialias",
        description="",
        items=(
            ("NONE", "None", ""),
            ("STANDARD", "Standard", ""),
            ("REDUCED", "Reduced", ""),
        ),
        default="STANDARD",
    )
    fog: bpy.props.EnumProperty(
        name="Fog",
        description="",
        items=(
            ("NONE", "None", ""),
            ("STANDARD", "Standard", ""),
            ("CUSTOM", "Custom", ""),
        ),
        default="STANDARD",
    )
    dithering: bpy.props.EnumProperty(
        name="Dithering",
        description="",
        items=(
            ("RGB_SQUARE_A_SQUARE", "rgb=SQUARE alpha=SQUARE", ""),
            ("RGB_SQUARE_A_INVSQUARE", "rgb=SQUARE alpha=INVSQUARE", ""),
            ("RGB_SQUARE_A_NOISE", "rgb=SQUARE alpha=NOISE", ""),
            ("RGB_SQUARE_A_NONE", "rgb=SQUARE alpha=NONE", ""),
            ("RGB_BAYER_A_BAYER", "rgb=BAYER alpha=BAYER", ""),
            ("RGB_BAYER_A_INVBAYER", "rgb=BAYER alpha=INVBAYER", ""),
            ("RGB_BAYER_A_NOISE", "rgb=BAYER alpha=NOISE", ""),
            ("RGB_BAYER_A_NONE", "rgb=BAYER alpha=NONE", ""),
            ("RGB_NOISE_A_SQUARE", "rgb=NOISE alpha=SQUARE", ""),
            ("RGB_NOISE_A_INVSQUARE", "rgb=NOISE alpha=INVSQUARE", ""),
            ("RGB_NOISE_A_NOISE", "rgb=NOISE alpha=NOISE", ""),
            ("RGB_NOISE_A_NONE", "rgb=NOISE alpha=NONE", ""),
            ("RGB_NONE_A_BAYER", "rgb=NONE alpha=BAYER", ""),
            ("RGB_NONE_A_INVBAYER", "rgb=NONE alpha=INVBAYER", ""),
            ("RGB_NONE_A_NOISE", "rgb=NONE alpha=NOISE", ""),
            ("RGB_NONE_A_NONE", "rgb=NONE alpha=NONE", ""),
        ),
    )
    texture_filtering: bpy.props.EnumProperty(
        name="Texture Filtering",
        description="",
        items=(
            ("POINT", "Point", ""),
            ("BILINEAR", "Bilinear", ""),
            ("MEDIAN", "Median", ""),
        ),
        default="BILINEAR",
    )
    texture_perspective_correction: bpy.props.BoolProperty(
        name="Texture Perspective Correction",
        description="",
        default=True,
    )

    alpha_compare: bpy.props.BoolProperty(
        name="Alpha Compare",
        description="",
        default=False,
    )
    alpha_compare_threshold: bpy.props.IntProperty(
        name="Alpha Compare Threshold",
        description="",
        default=127,
        min=0,
        max=255,
    )

    z_compare: bpy.props.BoolProperty(
        name="Z Compare",
        description="",
        default=True,
    )
    z_update: bpy.props.BoolProperty(
        name="Z Update",
        description="",
        default=True,
    )

    fixed_z: bpy.props.BoolProperty(
        name="Fixed Z",
        description="",
    )
    fixed_z_value: bpy.props.IntProperty(
        name="Fixed Z",
        description="",
        min=0,
        max=0x7FFF,
    )
    fixed_z_deltaz: bpy.props.IntProperty(
        name="Fixed Z deltaz",
        description="",
        min=-32768,
        max=32767,
    )

    placeholders: bpy.props.CollectionProperty(
        type=RDPQWorldDefaultsPlaceholderProperties,
    )


class RDPQWorldProperties(bpy.types.PropertyGroup):
    defaults_: bpy.props.PointerProperty(type=RDPQWorldDefaultsProperties)

    @property
    def defaults(self) -> RDPQWorldDefaultsProperties:
        return self.defaults_


def prop_split(layout: bpy.types.UILayout, data, prop_name: str):
    layout.use_property_split = True
    layout.use_property_decorate = False
    layout.prop(data, prop_name)
    layout.use_property_split = False


class RDPQWorldDefaultsPlaceholderAddOperator(bpy.types.Operator):
    bl_idname = "libdragon_rdpq.rdpq_world_defaults_placeholder_add"
    bl_label = "Add placeholder to RDPQ world defaults"

    @classmethod
    def poll(cls, context):
        return hasattr(context, "world") and context.world is not None

    def execute(self, context):  # type: ignore
        world = context.world
        assert world is not None
        world_rdpq = util.LIBDRAGON_RDPQ(world)

        world_rdpq.defaults.placeholders.add()

        return {"FINISHED"}


class RDPQWorldDefaultsPlaceholderRemoveOperator(bpy.types.Operator):
    bl_idname = "libdragon_rdpq.rdpq_world_defaults_placeholder_remove"
    bl_label = "Remove placeholder from RDPQ world defaults"

    index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return hasattr(context, "world") and context.world is not None

    def execute(self, context):  # type: ignore
        world = context.world
        assert world is not None
        world_rdpq = util.LIBDRAGON_RDPQ(world)

        world_rdpq.defaults.placeholders.remove(self.index)

        return {"FINISHED"}


class RDPQWorldPanel(bpy.types.Panel):
    bl_label = "RDPQ Defaults"
    bl_idname = "WORLD_PT_libdragon_rdpq"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"

    @classmethod
    def poll(cls, context):
        return context.world is not None

    def draw(self, context):
        layout = self.layout
        assert layout is not None
        world = context.world
        assert world is not None
        world_rdpq = util.LIBDRAGON_RDPQ(world)

        layout.prop(world_rdpq.defaults, "antialias")
        layout.prop(world_rdpq.defaults, "fog")
        layout.prop(world_rdpq.defaults, "dithering")
        layout.prop(world_rdpq.defaults, "texture_filtering")
        layout.prop(world_rdpq.defaults, "texture_perspective_correction")

        row = layout.row()
        row.prop(world_rdpq.defaults, "alpha_compare", text="")
        col = row.column()
        col.prop(world_rdpq.defaults, "alpha_compare_threshold")
        col.enabled = world_rdpq.defaults.alpha_compare

        layout.prop(world_rdpq.defaults, "z_compare")
        layout.prop(world_rdpq.defaults, "z_update")

        row = layout.row()
        row.prop(world_rdpq.defaults, "fixed_z")
        col = row.column()
        col.prop(world_rdpq.defaults, "fixed_z_value")
        col.prop(world_rdpq.defaults, "fixed_z_deltaz")
        col.enabled = world_rdpq.defaults.fixed_z

        box = layout.box()
        box.label(text="Placeholders")
        set_placeholders: set[int] = set()
        for i, placeholder in enumerate(world_rdpq.defaults.placeholders):
            split = box.row().split(factor=0.3)
            split.prop(placeholder, "slot_index")
            row = split.row()
            if placeholder.slot_index in set_placeholders:
                row.label(text="Duplicate slot")
            else:
                set_placeholders.add(placeholder.slot_index)
                row.prop(placeholder, "image")
            row.operator(
                RDPQWorldDefaultsPlaceholderRemoveOperator.bl_idname,
                text="",
                icon="REMOVE",
            ).index = i
        box.operator(
            RDPQWorldDefaultsPlaceholderAddOperator.bl_idname,
            text="Add Placeholder",
            icon="ADD",
        )


class RDPQMaterialPanel(bpy.types.Panel):
    bl_idname = "MATERIAL_PT_libdragon_rdpq"
    bl_label = "RDPQ"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.material is not None

    def draw(self, context):
        layout = self.layout
        assert layout is not None
        mat = context.material
        assert mat is not None
        mat_rdpq = util.LIBDRAGON_RDPQ(mat)

        if sync_to_fast64.is_fast64_available():
            if sync_to_fast64.is_fast64_material(mat):
                if mat_rdpq.auto_sync_to_fast64:
                    layout.prop(mat_rdpq, "auto_sync_to_fast64")
                else:
                    row = layout.row()
                    if context.scene is None:
                        col = row.column()
                        col.prop(mat_rdpq, "auto_sync_to_fast64")
                        col.enabled = False
                    else:
                        row.prop(mat_rdpq, "auto_sync_to_fast64")
                    row.operator(
                        sync_to_fast64.RDPQMaterialPropsToFast64Operator.bl_idname,
                        text="Sync to Fast64 props",
                    )
            else:
                layout.operator(
                    sync_to_fast64.RDPQMaterialRecreateAsFast64Operator.bl_idname,
                    text="Recreate as Fast64 material",
                )

        def prop_texture(
            box: bpy.types.UILayout,
            texture_props: rdpq_material_props.RDPQMaterialTextureProperties,
        ):
            row = box.row()
            row.prop(texture_props, "use_placeholder", text="")
            col = row.column()
            col.prop(texture_props, "placeholder")
            col.enabled = texture_props.use_placeholder

            if not texture_props.use_placeholder:
                box.template_ID(
                    texture_props, "image", new="image.new", open="image.open"
                )
                prop_split(box, texture_props, "format")
                prop_split(box, texture_props, "mipmap")
                prop_split(box, texture_props, "dithering")

            # TODO do libdragon placeholders also contain ST information?
            # aka should ST props only be drawn if not a placeholder?

            box_s = box.box()
            box_s.label(text="S Properties")
            box_s.prop(texture_props.s, "translate")
            box_s.prop(texture_props.s, "scale")

            row = box_s.row()
            row.label(text="Repeats")
            col = row.column()
            col.prop(texture_props.s, "repeats", text="")
            col.enabled = not texture_props.s.repeats_inf
            row.prop(texture_props.s, "repeats_inf", text="Infinite")

            box_s.prop(texture_props.s, "mirror")

            box_t = box.box()
            box_t.label(text="T Properties")
            box_t.prop(texture_props.t, "translate")
            box_t.prop(texture_props.t, "scale")

            row = box_t.row()
            row.label(text="Repeats")
            col = row.column()
            col.prop(texture_props.t, "repeats", text="")
            col.enabled = not texture_props.t.repeats_inf
            row.prop(texture_props.t, "repeats_inf", text="Infinite")

            box_t.prop(texture_props.t, "mirror")

        box = layout.box()
        box.prop(mat_rdpq, "use_texture0")
        if mat_rdpq.use_texture0:
            prop_texture(box, mat_rdpq.texture0)
            box = layout.box()
            box.prop(mat_rdpq, "use_texture1")
            if mat_rdpq.use_texture1:
                prop_texture(box, mat_rdpq.texture1)

        box = layout.box()
        prop_split(box, mat_rdpq.combiner, "preset")
        if mat_rdpq.combiner.preset == "CUSTOM_1_PASS":
            box.prop(mat_rdpq.combiner, "rgb_A")
            box.prop(mat_rdpq.combiner, "rgb_B")
            box.prop(mat_rdpq.combiner, "rgb_C")
            box.prop(mat_rdpq.combiner, "rgb_D")
            box.prop(mat_rdpq.combiner, "alpha_A")
            box.prop(mat_rdpq.combiner, "alpha_B")
            box.prop(mat_rdpq.combiner, "alpha_C")
            box.prop(mat_rdpq.combiner, "alpha_D")
        if mat_rdpq.combiner.preset == "CUSTOM_2_PASSES":
            box.prop(mat_rdpq.combiner, "rgb_A_0")
            box.prop(mat_rdpq.combiner, "rgb_B_0")
            box.prop(mat_rdpq.combiner, "rgb_C_0")
            box.prop(mat_rdpq.combiner, "rgb_D_0")
            box.prop(mat_rdpq.combiner, "alpha_A_0")
            box.prop(mat_rdpq.combiner, "alpha_B_0")
            box.prop(mat_rdpq.combiner, "alpha_C_0")
            box.prop(mat_rdpq.combiner, "alpha_D_0")
            box.prop(mat_rdpq.combiner, "rgb_A_1")
            box.prop(mat_rdpq.combiner, "rgb_B_1")
            box.prop(mat_rdpq.combiner, "rgb_C_1")
            box.prop(mat_rdpq.combiner, "rgb_D_1")
            box.prop(mat_rdpq.combiner, "alpha_A_1")
            box.prop(mat_rdpq.combiner, "alpha_B_1")
            box.prop(mat_rdpq.combiner, "alpha_C_1")
            box.prop(mat_rdpq.combiner, "alpha_D_1")

        box = layout.box()
        prop_split(box, mat_rdpq.blender, "preset")
        if mat_rdpq.blender.preset == "CUSTOM_1_PASS":
            box.prop(mat_rdpq.blender, "p")
            box.prop(mat_rdpq.blender, "a")
            box.prop(mat_rdpq.blender, "q")
            box.prop(mat_rdpq.blender, "b")
        if mat_rdpq.blender.preset == "CUSTOM_2_PASSES":
            box.prop(mat_rdpq.blender, "p_0")
            box.prop(mat_rdpq.blender, "a_0")
            box.prop(mat_rdpq.blender, "q_0")
            box.prop(mat_rdpq.blender, "b_0")
            box.prop(mat_rdpq.blender, "p_1")
            box.prop(mat_rdpq.blender, "a_1")
            box.prop(mat_rdpq.blender, "q_1")
            box.prop(mat_rdpq.blender, "b_1")
        prop_split(box, mat_rdpq.blender, "blend_color")
        prop_split(box, mat_rdpq.blender, "fog_color")

        box = layout.box()

        def prop_override(override_prop_name: str, *props_names: str):
            row = box.row()
            row.prop(mat_rdpq.override_render_mode, override_prop_name, text="")
            col = row.column()
            for prop_name in props_names:
                col.prop(mat_rdpq.override_render_mode, prop_name)
            col.enabled = getattr(mat_rdpq.override_render_mode, override_prop_name)

        prop_override("override_antialias", "antialias")
        prop_override("override_fog", "fog")
        prop_override("override_dithering", "dithering")
        prop_override("override_texture_filtering", "texture_filtering")
        prop_override(
            "override_texture_perspective_correction", "texture_perspective_correction"
        )
        prop_override("override_alpha_compare", "alpha_compare_threshold")
        prop_override("override_z_compare_and_z_update", "z_compare", "z_update")
        prop_override("override_fixed_z", "fixed_z", "fixed_z_deltaz")


class RDPQSceneProperties(bpy.types.PropertyGroup):
    gltf_extension: bpy.props.PointerProperty(
        type=gltf_extension.glTFExtensionProperties
    )


classes = (
    gltf_extension.glTFExtensionProperties,
    RDPQSceneProperties,
    RDPQWorldDefaultsPlaceholderProperties,
    RDPQWorldDefaultsProperties,
    RDPQWorldProperties,
    rdpq_material_props.RDPQMaterialTextureAxisProperties,
    rdpq_material_props.RDPQMaterialTextureProperties,
    rdpq_material_props.RDPQMaterialCombinerProperties,
    rdpq_material_props.RDPQMaterialBlenderProperties,
    rdpq_material_props.RDPQMaterialOverrideRenderModeProperties,
    rdpq_material_props.RDPQMaterialProperties,
    sync_to_fast64.RDPQMaterialPropsToFast64Operator,
    sync_to_fast64.RDPQMaterialRecreateAsFast64Operator,
    export_to_mkmaterial.RDPQMaterialExportOperator,
    RDPQWorldDefaultsPlaceholderAddOperator,
    RDPQWorldDefaultsPlaceholderRemoveOperator,
    RDPQWorldPanel,
    RDPQMaterialPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.libdragon_rdpq = (  # type: ignore
        bpy.props.PointerProperty(type=RDPQSceneProperties)
    )
    bpy.types.Material.libdragon_rdpq = (  # type: ignore
        bpy.props.PointerProperty(type=rdpq_material_props.RDPQMaterialProperties)
    )
    bpy.types.World.libdragon_rdpq = (  # type: ignore
        bpy.props.PointerProperty(type=RDPQWorldProperties)
    )
    bpy.app.handlers.load_post.append(
        sync_to_fast64.handler_load_post_start_materials_auto_sync_to_fast64
    )
    bpy.app.timers.register(
        lambda: sync_to_fast64.handler_load_post_start_materials_auto_sync_to_fast64()
    )

    if gltf_extension.gltf_export_props_use_exporter_extension_layout_draw:
        from io_scene_gltf2 import exporter_extension_layout_draw  # type: ignore

        exporter_extension_layout_draw["libdragon RDPQ materials"] = (
            gltf_extension.draw_gltf_extension_props
        )


def unregister():
    if gltf_extension.gltf_export_props_use_exporter_extension_layout_draw:
        from io_scene_gltf2 import exporter_extension_layout_draw  # type: ignore

        del exporter_extension_layout_draw["libdragon RDPQ materials"]

    try:
        bpy.app.handlers.load_post.remove(
            sync_to_fast64.handler_load_post_start_materials_auto_sync_to_fast64
        )
    except ValueError:
        pass
    del bpy.types.Scene.libdragon_rdpq  # type: ignore
    del bpy.types.Material.libdragon_rdpq  # type: ignore
    del bpy.types.World.libdragon_rdpq  # type: ignore
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
