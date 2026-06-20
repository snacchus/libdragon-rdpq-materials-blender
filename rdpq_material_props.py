import dataclasses

import bpy

from . import rdpq_material_props_logic


class RDPQMaterialTextureAxisProperties(bpy.types.PropertyGroup):
    translate: bpy.props.FloatProperty(
        name="Translate",
        description="",
        default=0,
        min=-1024,
        max=1024,
    )
    scale: bpy.props.IntProperty(
        name="Scale",
        description="",
        default=0,
        min=-5,
        max=10,
    )
    repeats_inf: bpy.props.BoolProperty(
        name="Repeats Infinitely",
        description="",
        default=False,
    )
    repeats: bpy.props.FloatProperty(
        name="Repeats",
        description="",
        default=1,
        min=0,
        max=1024,
    )
    mirror: bpy.props.BoolProperty(
        name="Mirror",
        description="",
        default=False,
    )


class RDPQMaterialTextureProperties(bpy.types.PropertyGroup):
    use_placeholder: bpy.props.BoolProperty(
        name="Use Placeholder",
        description="",
        default=False,
    )
    placeholder: bpy.props.IntProperty(
        name="Placeholder",
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
    format: bpy.props.EnumProperty(
        name="Format",
        description="",
        items=(
            ("AUTO", "Auto", ""),
            ("RGBA16", "RGBA16", ""),
            ("RGBA32", "RGBA32", ""),
            ("CI4", "CI4", ""),
            ("CI8", "CI8", ""),
            ("IA4", "IA4", ""),
            ("IA8", "IA8", ""),
            ("IA16", "IA16", ""),
            ("I4", "I4", ""),
            ("I8", "I8", ""),
            ("SHQ", "SHQ", ""),
            ("IHQ", "IHQ", ""),
        ),
        default="AUTO",
    )
    mipmap: bpy.props.EnumProperty(
        name="Mipmap",
        description="",
        items=(
            ("NONE", "None", ""),
            ("BOX", "Box", ""),
        ),
        default="NONE",
    )
    dithering: bpy.props.EnumProperty(
        name="Dithering",
        description="",
        items=(
            ("NONE", "None", ""),
            ("RANDOM", "Random", ""),
            ("ORDERED", "Ordered", ""),
        ),
        default="NONE",
    )
    s_: bpy.props.PointerProperty(type=RDPQMaterialTextureAxisProperties)
    t_: bpy.props.PointerProperty(type=RDPQMaterialTextureAxisProperties)

    @property
    def s(self) -> RDPQMaterialTextureAxisProperties:
        return self.s_

    @property
    def t(self) -> RDPQMaterialTextureAxisProperties:
        return self.t_


# One-cycle combiner slots

COMB1_RGB_SUBA_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("NOISE", "NOISE", ""),
    ("0", "0", ""),
)
COMB1_RGB_SUBB_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("KEYCENTER", "KEYCENTER", ""),
    ("K4", "K4", ""),
    ("0", "0", ""),
)
COMB1_RGB_MUL_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("KEYSCALE", "KEYSCALE", ""),
    ("TEX0_ALPHA", "TEX0_ALPHA", ""),
    ("PRIM_ALPHA", "PRIM_ALPHA", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("ENV_ALPHA", "ENV_ALPHA", ""),
    ("LOD_FRAC", "LOD_FRAC", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
    ("K5", "K5", ""),
    ("0", "0", ""),
)
COMB1_RGB_ADD_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)

COMB1_ALPHA_ADDSUB_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)
COMB1_ALPHA_MUL_ITEMS = (
    ("LOD_FRAC", "LOD_FRAC", ""),
    ("TEX0", "TEX0", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
    ("0", "0", ""),
)

# Two-cycle combiner slots

COMB2A_RGB_SUBA_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("NOISE", "NOISE", ""),
    ("0", "0", ""),
)
COMB2A_RGB_SUBB_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("KEYCENTER", "KEYCENTER", ""),
    ("K4", "K4", ""),
    ("0", "0", ""),
)
COMB2A_RGB_MUL_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("KEYSCALE", "KEYSCALE", ""),
    ("TEX0_ALPHA", "TEX0_ALPHA", ""),
    ("TEX1_ALPHA", "TEX1_ALPHA", ""),
    ("PRIM_ALPHA", "PRIM_ALPHA", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("ENV_ALPHA", "ENV_ALPHA", ""),
    ("LOD_FRAC", "LOD_FRAC", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
    ("K5", "K5", ""),
    ("0", "0", ""),
)
COMB2A_RGB_ADD_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)

COMB2A_ALPHA_ADDSUB_ITEMS = (
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)
COMB2A_ALPHA_MUL_ITEMS = (
    ("LOD_FRAC", "LOD_FRAC", ""),
    ("TEX0", "TEX0", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
    ("0", "0", ""),
)

COMB2B_RGB_SUBA_ITEMS = (
    ("COMBINED", "COMBINED", ""),
    ("TEX1", "TEX1", ""),
    ("TEX0_BUG", "TEX0_BUG", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("NOISE", "NOISE", ""),
    ("0", "0", ""),
)
COMB2B_RGB_SUBB_ITEMS = (
    ("COMBINED", "COMBINED", ""),
    ("TEX1", "TEX1", ""),
    ("TEX0_BUG", "TEX0_BUG", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("KEYCENTER", "KEYCENTER", ""),
    ("K4", "K4", ""),
    ("0", "0", ""),
)
COMB2B_RGB_MUL_ITEMS = (
    ("COMBINED", "COMBINED", ""),
    ("TEX1", "TEX1", ""),
    ("TEX0_BUG", "TEX0_BUG", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("KEYSCALE", "KEYSCALE", ""),
    ("COMBINED_ALPHA", "COMBINED_ALPHA", ""),
    ("TEX1_ALPHA", "TEX1_ALPHA", ""),
    ("TEX0_ALPHA", "TEX0_ALPHA", ""),
    ("PRIM_ALPHA", "PRIM_ALPHA", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("ENV_ALPHA", "ENV_ALPHA", ""),
    ("LOD_FRAC", "LOD_FRAC", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
    ("K5", "K5", ""),
    ("0", "0", ""),
)
COMB2B_RGB_ADD_ITEMS = (
    ("COMBINED", "COMBINED", ""),
    ("TEX1", "TEX1", ""),
    ("TEX0_BUG", "TEX0_BUG", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)

COMB2B_ALPHA_ADDSUB_ITEMS = (
    ("COMBINED", "COMBINED", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)
COMB2B_ALPHA_MUL_ITEMS = (
    ("LOD_FRAC", "LOD_FRAC", ""),
    ("TEX1", "TEX1", ""),
    ("PRIM", "PRIM", ""),
    ("SHADE", "SHADE", ""),
    ("ENV", "ENV", ""),
    ("PRIM_LOD_FRAC", "PRIM_LOD_FRAC", ""),
    ("0", "0", ""),
)


class RDPQMaterialCombinerProperties(bpy.types.PropertyGroup):
    preset: bpy.props.EnumProperty(
        name="Combiner Preset",
        description="",
        items=(
            ("FLAT", "Flat", ""),
            ("SHADE", "Shade", ""),
            ("TEX", "Tex", ""),
            ("TEX_FLAT", "Tex Flat", ""),
            ("TEX_SHADE", "Tex Shade", ""),
            ("CUSTOM_1_PASS", "Custom 1 Pass", ""),
            ("CUSTOM_2_PASSES", "Custom 2 Passes", ""),
        ),
        default="TEX",
        update=rdpq_material_props_logic.on_update_combiner_preset,
    )

    # One-cycle

    rgb_A: bpy.props.EnumProperty(
        name="RGB A",
        description="RGB A Input",
        items=COMB1_RGB_SUBA_ITEMS,
    )
    rgb_B: bpy.props.EnumProperty(
        name="RGB B",
        description="RGB B Input",
        items=COMB1_RGB_SUBB_ITEMS,
    )
    rgb_C: bpy.props.EnumProperty(
        name="RGB C",
        description="RGB C Input",
        items=COMB1_RGB_MUL_ITEMS,
    )
    rgb_D: bpy.props.EnumProperty(
        name="RGB D",
        description="RGB D Input",
        items=COMB1_RGB_ADD_ITEMS,
    )

    alpha_A: bpy.props.EnumProperty(
        name="Alpha A",
        description="RGB A Input",
        items=COMB1_ALPHA_ADDSUB_ITEMS,
    )
    alpha_B: bpy.props.EnumProperty(
        name="Alpha B",
        description="RGB B Input",
        items=COMB1_ALPHA_ADDSUB_ITEMS,
    )
    alpha_C: bpy.props.EnumProperty(
        name="Alpha C",
        description="RGB C Input",
        items=COMB1_ALPHA_MUL_ITEMS,
    )
    alpha_D: bpy.props.EnumProperty(
        name="Alpha D",
        description="RGB D Input",
        items=COMB1_ALPHA_ADDSUB_ITEMS,
    )

    # Two-cycle

    # First Cycle

    rgb_A_0: bpy.props.EnumProperty(
        name="RGB A 1",
        description="RGB A Input (First Cycle)",
        items=COMB2A_RGB_SUBA_ITEMS,
    )
    rgb_B_0: bpy.props.EnumProperty(
        name="RGB B 1",
        description="RGB B Input (First Cycle)",
        items=COMB2A_RGB_SUBB_ITEMS,
    )
    rgb_C_0: bpy.props.EnumProperty(
        name="RGB C 1",
        description="RGB C Input (First Cycle)",
        items=COMB2A_RGB_MUL_ITEMS,
    )
    rgb_D_0: bpy.props.EnumProperty(
        name="RGB D 1",
        description="RGB D Input (First Cycle)",
        items=COMB2A_RGB_ADD_ITEMS,
    )

    alpha_A_0: bpy.props.EnumProperty(
        name="Alpha A 1",
        description="Alpha A Input (First Cycle)",
        items=COMB2A_ALPHA_ADDSUB_ITEMS,
    )
    alpha_B_0: bpy.props.EnumProperty(
        name="Alpha B 1",
        description="Alpha B Input (First Cycle)",
        items=COMB2A_ALPHA_ADDSUB_ITEMS,
    )
    alpha_C_0: bpy.props.EnumProperty(
        name="Alpha C 1",
        description="Alpha C Input (First Cycle)",
        items=COMB2A_ALPHA_MUL_ITEMS,
    )
    alpha_D_0: bpy.props.EnumProperty(
        name="Alpha D 1",
        description="Alpha D Input (First Cycle)",
        items=COMB2A_ALPHA_ADDSUB_ITEMS,
    )

    # Second Cycle

    rgb_A_1: bpy.props.EnumProperty(
        name="RGB A 2",
        description="RGB A Input (Second Cycle)",
        items=COMB2B_RGB_SUBA_ITEMS,
    )
    rgb_B_1: bpy.props.EnumProperty(
        name="RGB B 2",
        description="RGB B Input (Second Cycle)",
        items=COMB2B_RGB_SUBB_ITEMS,
    )
    rgb_C_1: bpy.props.EnumProperty(
        name="RGB C 2",
        description="RGB C Input (Second Cycle)",
        items=COMB2B_RGB_MUL_ITEMS,
    )
    rgb_D_1: bpy.props.EnumProperty(
        name="RGB D 2",
        description="RGB D Input (Second Cycle)",
        items=COMB2B_RGB_ADD_ITEMS,
    )

    alpha_A_1: bpy.props.EnumProperty(
        name="Alpha A 2",
        description="Alpha A Input (Second Cycle)",
        items=COMB2B_ALPHA_ADDSUB_ITEMS,
    )
    alpha_B_1: bpy.props.EnumProperty(
        name="Alpha B 2",
        description="Alpha B Input (Second Cycle)",
        items=COMB2B_ALPHA_ADDSUB_ITEMS,
    )
    alpha_C_1: bpy.props.EnumProperty(
        name="Alpha C 2",
        description="Alpha C Input (Second Cycle)",
        items=COMB2B_ALPHA_MUL_ITEMS,
    )
    alpha_D_1: bpy.props.EnumProperty(
        name="Alpha D 2",
        description="Alpha D Input (Second Cycle)",
        items=COMB2B_ALPHA_ADDSUB_ITEMS,
    )


class RDPQMaterialRegistersProperties(bpy.types.PropertyGroup):
    set_k4: bpy.props.BoolProperty(
        name="Set K4",
        description="",
        default=False,
    )
    k4: bpy.props.FloatProperty(
        name="K4",
        description="",
        default=0,
        min=0,
        max=1,
        subtype="FACTOR",
    )
    set_k5: bpy.props.BoolProperty(
        name="Set K5",
        description="",
        default=False,
    )
    k5: bpy.props.FloatProperty(
        name="K5",
        description="",
        default=0,
        min=0,
        max=1,
        subtype="FACTOR",
    )
    set_keyscale: bpy.props.BoolProperty(
        name="Set Key Scale",
        description="",
        default=False,
    )
    keyscale: bpy.props.FloatProperty(
        name="Key Scale",
        description="",
        default=0,
        min=0,
        max=1,
        subtype="FACTOR",
    )
    set_keycenter: bpy.props.BoolProperty(
        name="Set Key Center",
        description="",
        default=False,
    )
    keycenter: bpy.props.FloatProperty(
        name="Key Center",
        description="",
        default=0,
        min=0,
        max=1,
        subtype="FACTOR",
    )
    set_prim_lod_frac: bpy.props.BoolProperty(
        name="Set Prim LOD Frac",
        description="",
        default=False,
    )
    prim_lod_frac: bpy.props.FloatProperty(
        name="Prim LOD Frac",
        description="",
        default=0,
        min=0,
        max=1,
        subtype="FACTOR",
    )
    set_env_color: bpy.props.BoolProperty(
        name="Set Env Color",
        description="",
        default=False,
    )
    env_color: bpy.props.FloatVectorProperty(
        name="Env Color",
        description="",
        default=(1, 1, 1, 1),
        min=0,
        max=1,
        subtype="COLOR",
        size=4,
    )
    set_prim_color: bpy.props.BoolProperty(
        name="Set Prim Color",
        description="",
        default=False,
    )
    prim_color: bpy.props.FloatVectorProperty(
        name="Prim Color",
        description="",
        default=(1, 1, 1, 1),
        min=0,
        max=1,
        subtype="COLOR",
        size=4,
    )


BLEND1_A_ITEMS = (
    ("IN_RGB", "IN_RGB", ""),
    ("MEMORY_RGB", "MEMORY_RGB", ""),
    ("BLEND_RGB", "BLEND_RGB", ""),
    ("FOG_RGB", "FOG_RGB", ""),
)
BLEND1_B1_ITEMS = (
    ("IN_ALPHA", "IN_ALPHA", ""),
    ("FOG_ALPHA", "FOG_ALPHA", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("0", "0", ""),
)
BLEND1_B2_ITEMS = (
    ("INV_MUX_ALPHA", "INV_MUX_ALPHA", ""),
    ("MEMORY_CVG", "MEMORY_CVG", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)

BLEND2A_A_ITEMS = (
    ("IN_RGB", "IN_RGB", ""),
    ("BLEND_RGB", "BLEND_RGB", ""),
    ("FOG_RGB", "FOG_RGB", ""),
)
BLEND2A_B1_ITEMS = (
    ("IN_ALPHA", "IN_ALPHA", ""),
    ("FOG_ALPHA", "FOG_ALPHA", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("0", "0", ""),
)
BLEND2A_B2_ITEMS = (("INV_MUX_ALPHA", "INV_MUX_ALPHA", ""),)
BLEND2B_A_ITEMS = (
    ("CYCLE1_RGB", "CYCLE1_RGB", ""),
    ("MEMORY_RGB", "MEMORY_RGB", ""),
    ("BLEND_RGB", "BLEND_RGB", ""),
    ("FOG_RGB", "FOG_RGB", ""),
)
BLEND2B_B1_ITEMS = (
    ("IN_ALPHA", "IN_ALPHA", ""),
    ("FOG_ALPHA", "FOG_ALPHA", ""),
    ("SHADE_ALPHA", "SHADE_ALPHA", ""),
    ("0", "0", ""),
)
BLEND2B_B2_ITEMS = (
    ("INV_MUX_ALPHA", "INV_MUX_ALPHA", ""),
    ("MEMORY_CVG", "MEMORY_CVG", ""),
    ("1", "1", ""),
    ("0", "0", ""),
)


class RDPQMaterialBlenderProperties(bpy.types.PropertyGroup):
    preset: bpy.props.EnumProperty(
        name="Blender Preset",
        description="",
        items=(
            ("NONE", "None", ""),
            ("MULTIPLY", "Multiply", ""),
            ("MULTIPLY_CONST", "Multiply Const", ""),
            ("ADDITIVE", "Additive", ""),
            ("CUSTOM_1_PASS", "Custom 1 Pass", ""),
            ("CUSTOM_2_PASSES", "Custom 2 Passes", ""),
        ),
        update=rdpq_material_props_logic.on_update_blender_preset,
    )

    # One-cycle muxes
    p: bpy.props.EnumProperty(
        name="P",
        description="Blender input P",
        items=BLEND1_A_ITEMS,
    )
    a: bpy.props.EnumProperty(
        name="A",
        description="Blender input A (first cycle)",
        items=BLEND1_B1_ITEMS,
    )
    q: bpy.props.EnumProperty(
        name="Q",
        description="Blender input Q (first cycle)",
        items=BLEND1_A_ITEMS,
    )
    b: bpy.props.EnumProperty(
        name="B",
        description="Blender input B (first cycle)",
        items=BLEND1_B2_ITEMS,
    )

    # Two-cycle muxes
    # First cycle
    p_0: bpy.props.EnumProperty(
        name="P1",
        description="Blender input P (first cycle)",
        items=BLEND2A_A_ITEMS,
    )
    a_0: bpy.props.EnumProperty(
        name="A1",
        description="Blender input A (first cycle)",
        items=BLEND2A_B1_ITEMS,
    )
    q_0: bpy.props.EnumProperty(
        name="Q1",
        description="Blender input Q (first cycle)",
        items=BLEND2A_A_ITEMS,
    )
    b_0: bpy.props.EnumProperty(
        name="B1",
        description="Blender input B (first cycle)",
        items=BLEND2A_B2_ITEMS,
    )
    # Second cycle
    p_1: bpy.props.EnumProperty(
        name="P2",
        description="Blender input P (second cycle)",
        items=BLEND2B_A_ITEMS,
    )
    a_1: bpy.props.EnumProperty(
        name="A2",
        description="Blender input A (second cycle)",
        items=BLEND2B_B1_ITEMS,
    )
    q_1: bpy.props.EnumProperty(
        name="Q2",
        description="Blender input Q (second cycle)",
        items=BLEND2B_A_ITEMS,
    )
    b_1: bpy.props.EnumProperty(
        name="B2",
        description="Blender input B (second cycle)",
        items=BLEND2B_B2_ITEMS,
    )

    blend_color: bpy.props.FloatVectorProperty(
        name="Blend Color",
        description="",
        default=(1, 1, 1),
        min=0,
        max=1,
        subtype="COLOR",
        size=3,
    )
    fog_color: bpy.props.FloatVectorProperty(
        name="Fog Color",
        description="",
        default=(1, 1, 1, 1),
        min=0,
        max=1,
        subtype="COLOR",
        size=4,
    )


class RDPQMaterialOverrideRenderModeProperties(bpy.types.PropertyGroup):
    override_antialias: bpy.props.BoolProperty(
        name="Override Antialias",
        description="",
    )
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

    override_fog: bpy.props.BoolProperty(
        name="Override Fog",
        description="",
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

    override_dithering: bpy.props.BoolProperty(
        name="Override Dithering",
        description="",
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

    override_texture_filtering: bpy.props.BoolProperty(
        name="Override Texture Filtering",
        description="",
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

    override_texture_perspective_correction: bpy.props.BoolProperty(
        name="Override Texture Perspective Correction",
        description="",
    )
    texture_perspective_correction: bpy.props.BoolProperty(
        name="Texture Perspective Correction",
        description="",
        default=True,
    )

    override_alpha_compare: bpy.props.BoolProperty(
        name="Override Alpha Compare",
        description="",
    )
    alpha_compare_threshold: bpy.props.IntProperty(
        name="Alpha Compare Threshold",
        description="",
        default=127,
        min=0,
        max=255,
    )

    override_z_compare_and_z_update: bpy.props.BoolProperty(
        name="Override Z Compare and Z Update",
        description="",
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

    override_fixed_z: bpy.props.BoolProperty(
        name="Override Fixed Z",
        description="",
    )
    fixed_z: bpy.props.IntProperty(
        name="Fixed Z",
        description="",
    )
    fixed_z_deltaz: bpy.props.IntProperty(
        name="Fixed Z deltaz",
        description="",
    )


def on_update_auto_sync_to_fast64_wrapper(self, context):
    from . import sync_to_fast64

    return sync_to_fast64.on_update_auto_sync_to_fast64(self, context)


class RDPQMaterialProperties(bpy.types.PropertyGroup):
    auto_sync_to_fast64: bpy.props.BoolProperty(
        name="Auto Sync To Fast64",
        description=(
            "Automatically set Fast64 material properties"
            " based on the libdragon RDPQ material properties"
        ),
        update=on_update_auto_sync_to_fast64_wrapper,
    )

    use_texture0: bpy.props.BoolProperty(
        name="Use Texture 0",
        description="",
        default=True,
    )
    use_texture1: bpy.props.BoolProperty(
        name="Use Texture 1",
        description="",
        default=False,
    )
    texture0_: bpy.props.PointerProperty(type=RDPQMaterialTextureProperties)
    texture1_: bpy.props.PointerProperty(type=RDPQMaterialTextureProperties)
    combiner_: bpy.props.PointerProperty(type=RDPQMaterialCombinerProperties)
    registers_: bpy.props.PointerProperty(type=RDPQMaterialRegistersProperties)
    blender_: bpy.props.PointerProperty(type=RDPQMaterialBlenderProperties)
    override_render_mode_: bpy.props.PointerProperty(
        type=RDPQMaterialOverrideRenderModeProperties
    )

    @property
    def texture0(self) -> RDPQMaterialTextureProperties:
        return self.texture0_

    @property
    def texture1(self) -> RDPQMaterialTextureProperties:
        return self.texture1_

    @property
    def combiner(self) -> RDPQMaterialCombinerProperties:
        return self.combiner_

    @property
    def registers(self) -> RDPQMaterialRegistersProperties:
        return self.registers_

    @property
    def blender(self) -> RDPQMaterialBlenderProperties:
        return self.blender_

    @property
    def override_render_mode(self) -> RDPQMaterialOverrideRenderModeProperties:
        return self.override_render_mode_


@dataclasses.dataclass
class RecursivePropsList:
    props: tuple[str, ...]
    groups: dict[str, "RecursivePropsList"]


LIBDRAGON_RDPQ_TEXTURE_AXIS_PROPS_LIST = RecursivePropsList(
    (
        "translate",
        "scale",
        "repeats_inf",
        "repeats",
        "mirror",
    ),
    {},
)
LIBDRAGON_RDPQ_TEXTURE_PROPS_LIST = RecursivePropsList(
    (
        "use_placeholder",
        "placeholder",
        "image",
        "format",
        "mipmap",
        "dithering",
    ),
    {
        "s": LIBDRAGON_RDPQ_TEXTURE_AXIS_PROPS_LIST,
        "t": LIBDRAGON_RDPQ_TEXTURE_AXIS_PROPS_LIST,
    },
)
LIBDRAGON_RDPQ_PROPS_LIST = RecursivePropsList(
    (),
    {
        "libdragon_rdpq": RecursivePropsList(
            (
                # "auto_sync_to_fast64",  # left out on purpose
                "use_texture0",
                "use_texture1",
            ),
            {
                "texture0": LIBDRAGON_RDPQ_TEXTURE_PROPS_LIST,
                "combiner": RecursivePropsList(
                    (
                        "preset",
                        "rgb_A",
                        "rgb_B",
                        "rgb_C",
                        "rgb_D",
                        "alpha_A",
                        "alpha_B",
                        "alpha_C",
                        "alpha_D",
                        "rgb_A_0",
                        "rgb_B_0",
                        "rgb_C_0",
                        "rgb_D_0",
                        "alpha_A_0",
                        "alpha_B_0",
                        "alpha_C_0",
                        "alpha_D_0",
                        "rgb_A_1",
                        "rgb_B_1",
                        "rgb_C_1",
                        "rgb_D_1",
                        "alpha_A_1",
                        "alpha_B_1",
                        "alpha_C_1",
                        "alpha_D_1",
                    ),
                    {},
                ),
                "registers": RecursivePropsList(
                    (
                        "set_k4",
                        "k4",
                        "set_k5",
                        "k5",
                        "set_keyscale",
                        "keyscale",
                        "set_keycenter",
                        "keycenter",
                        "set_prim_lod_frac",
                        "prim_lod_frac",
                        "set_env_color",
                        "env_color",
                        "set_prim_color",
                        "prim_color",
                    ),
                    {},
                ),
                "blender": RecursivePropsList(
                    (
                        "preset",
                        "p",
                        "a",
                        "q",
                        "b",
                        "p_0",
                        "a_0",
                        "q_0",
                        "b_0",
                        "p_1",
                        "a_1",
                        "q_1",
                        "b_1",
                        "blend_color",
                        "fog_color",
                    ),
                    {},
                ),
                "override_render_mode": RecursivePropsList(
                    (
                        "override_antialias",
                        "antialias",
                        "override_fog",
                        "fog",
                        "override_dithering",
                        "dithering",
                        "override_texture_filtering",
                        "texture_filtering",
                        "override_texture_perspective_correction",
                        "texture_perspective_correction",
                        "override_alpha_compare",
                        "alpha_compare_threshold",
                        "override_z_compare_and_z_update",
                        "z_compare",
                        "z_update",
                        "override_fixed_z",
                        "fixed_z",
                        "fixed_z_deltaz",
                    ),
                    {},
                ),
            },
        ),
    },
)
