from typing import Optional

import bpy

from . import rdpq_material_props
from . import util


SYNCED_MATERIALS: dict[bpy.types.Material, object] = {}


def start_auto_sync_to_fast64(mat: bpy.types.Material):
    mat_rdpq = util.LIBDRAGON_RDPQ(mat)
    assert mat not in SYNCED_MATERIALS
    owner = object()
    SYNCED_MATERIALS[mat] = owner
    try:
        msgbus_sync_rdpq_material_props_to_fast64_props(owner, mat)
    except:
        mat_rdpq.auto_sync_to_fast64 = False
        raise


def on_update_auto_sync_to_fast64(self, context: bpy.types.Context):
    mat = context.material
    assert mat is not None
    mat_rdpq = util.LIBDRAGON_RDPQ(mat)

    if mat_rdpq.auto_sync_to_fast64:
        scene = bpy.context.scene
        assert scene is not None
        world = scene.world
        start_auto_sync_to_fast64(mat)
        rdpq_material_props_to_fast64_props(mat, world)
    else:
        assert mat in SYNCED_MATERIALS
        owner = SYNCED_MATERIALS[mat]
        bpy.msgbus.clear_by_owner(owner)
        del SYNCED_MATERIALS[mat]


@bpy.app.handlers.persistent
def handler_load_post_start_materials_auto_sync_to_fast64(*_):
    for mat in bpy.data.materials.values():
        assert mat is not None
        mat_rdpq = util.LIBDRAGON_RDPQ(mat)
        if mat_rdpq.auto_sync_to_fast64:
            start_auto_sync_to_fast64(mat)


def is_fast64_available():
    return hasattr(bpy.context.scene, "f3d_type")


def is_fast64_material(mat: bpy.types.Material):
    return getattr(mat, "is_f3d", False)


BLENDER_MUXES_FAST64_MAP = {
    "IN_RGB": "G_BL_CLR_IN",
    "CYCLE1_RGB": "G_BL_CLR_IN",
    "MEMORY_RGB": "G_BL_CLR_MEM",
    "BLEND_RGB": "G_BL_CLR_BL",
    "FOG_RGB": "G_BL_CLR_FOG",
    "IN_ALPHA": "G_BL_A_IN",
    "FOG_ALPHA": "G_BL_A_FOG",
    "SHADE_ALPHA": "G_BL_A_SHADE",
    "INV_MUX_ALPHA": "G_BL_1MA",
    "MEMORY_CVG": "G_BL_A_MEM",
    "1": "G_BL_1",
    "0": "G_BL_0",
}

COMBINER_0_MUXES_FAST64_MAP = {
    "TEX0": "TEXEL0",
    "TEX1": "TEXEL1",
    "PRIM": "PRIMITIVE",
    "SHADE": "SHADE",
    "ENV": "ENVIRONMENT",
    "1": "1",
    "NOISE": "NOISE",
    "0": "0",
    "KEYCENTER": "CENTER",
    "K4": "K4",
    "SCALE": "SCALE",
    "TEX0_ALPHA": "TEXEL0_ALPHA",
    "TEX1_ALPHA": "TEXEL1_ALPHA",
    "PRIM_ALPHA": "PRIMITIVE_ALPHA",
    "SHADE_ALPHA": "SHADE_ALPHA",
    "ENV_ALPHA": "ENV_ALPHA",
    "LOD_FRACTION": "LOD_FRACTION",
    "PRIM_LOD_FRAC": "PRIM_LOD_FRAC",
    "K5": "K5",
}
COMBINER_1_MUXES_FAST64_MAP = COMBINER_0_MUXES_FAST64_MAP.copy()
del COMBINER_1_MUXES_FAST64_MAP["TEX0"]
del COMBINER_1_MUXES_FAST64_MAP["TEX1"]
COMBINER_1_MUXES_FAST64_MAP.update(
    {
        "COMBINED": "COMBINED",
        "COMBINED_ALPHA": "COMBINED_ALPHA",
        "TEX0_BUG": "TEXEL1",
        "TEX1": "TEXEL0",
    }
)


class WORLD_RDPQ_DEFAULTS_DEFAULTS:
    antialias = "STANDARD"
    fog = "STANDARD"
    dithering = "RGB_SQUARE_A_SQUARE"
    texture_filtering = "BILINEAR"
    texture_perspective_correction = True
    alpha_compare = False
    alpha_compare_threshold = 127
    z_compare = True
    z_update = True
    fixed_z = False
    fixed_z_value = 0
    fixed_z_deltaz = 0
    placeholders = []


def rdpq_material_props_to_fast64_props(
    mat: bpy.types.Material, world: Optional[bpy.types.World]
):
    mat_rdpq = util.LIBDRAGON_RDPQ(mat)
    mat_fast64 = mat.f3d_mat  # type: ignore
    if world is not None:
        world_rdpq_defaults = util.LIBDRAGON_RDPQ(world).defaults
    else:
        world_rdpq_defaults = WORLD_RDPQ_DEFAULTS_DEFAULTS

    # Texture

    def handle_texture_axis_props(
        texture_axis_props: rdpq_material_props.RDPQMaterialTextureAxisProperties,
        tex_axis_fast64_props,
        image_axis_len: int | None,
    ):
        tex_axis_fast64_props.clamp = not texture_axis_props.repeats_inf
        tex_axis_fast64_props.mirror = texture_axis_props.mirror
        if image_axis_len is None:
            tex_axis_fast64_props.low = 0
            tex_axis_fast64_props.high = 0
            tex_axis_fast64_props.mask = 0
        else:
            # TODO low and high computation may be wrong
            translate = texture_axis_props.translate
            if translate < 0:
                translate %= image_axis_len
            tex_axis_fast64_props.low = translate
            tex_axis_fast64_props.high = (
                translate
                + (
                    image_axis_len
                    * (
                        1
                        if texture_axis_props.repeats_inf
                        else texture_axis_props.repeats
                    )
                )
                - 1
            )
            # TODO what if dimension is not a power of 2?
            image_axis_len_intlog2 = util.intlog2(image_axis_len)
            tex_axis_fast64_props.mask = (
                0 if image_axis_len_intlog2 is None else image_axis_len_intlog2
            )
        tex_axis_fast64_props.shift = texture_axis_props.scale

    def handle_texture_props(
        texture_props: rdpq_material_props.RDPQMaterialTextureProperties,
        tex_fast64_props,
    ):
        tex_fast64_props.tex_set = True
        if texture_props.use_placeholder:
            image = None
            for default_placeholder in world_rdpq_defaults.placeholders:
                if default_placeholder.slot_index == texture_props.placeholder:
                    image = default_placeholder.image
                    # TODO do libdragon placeholders also contain ST information?
                    break
            tex_fast64_props.tex = image
            tex_fast64_props.use_tex_reference = True
            tex_fast64_props.tex_reference = str(texture_props.placeholder)
            tex_fast64_props.tex_reference_size = (
                (32, 32) if image is None else image.size
            )
        else:
            tex_fast64_props.tex = texture_props.image
            tex_fast64_props.use_tex_reference = False
        texture_format = texture_props.format
        if texture_format == "AUTO":
            # TODO invoke mksprite to guess a format?
            texture_format = "RGBA16"
        if texture_format == "SHQ":
            # TODO
            texture_format = "RGBA16"
        if texture_format == "IHQ":
            # TODO
            texture_format = "RGBA16"
        tex_fast64_props.tex_format = texture_format
        tex_fast64_props.ci_format = "RGBA16"
        tex_fast64_props.autoprop = False
        handle_texture_axis_props(
            texture_props.s,
            tex_fast64_props.S,
            None if texture_props.image is None else texture_props.image.size[0],
        )
        handle_texture_axis_props(
            texture_props.t,
            tex_fast64_props.T,
            None if texture_props.image is None else texture_props.image.size[1],
        )

    if mat_rdpq.use_texture0:
        handle_texture_props(mat_rdpq.texture0, mat_fast64.tex0)
    if mat_rdpq.use_texture1:
        handle_texture_props(mat_rdpq.texture1, mat_fast64.tex1)

    # TODO handle one-cycle
    mat_fast64.rdp_settings.g_mdsft_cycletype = "G_CYC_2CYCLE"

    # For controlling the render mode (blender and other properties)
    mat_fast64.rdp_settings.set_rendermode = True
    mat_fast64.rdp_settings.rendermode_advanced_enabled = True

    # Combiner

    mat_fast64.combiner1.A = COMBINER_0_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_A_0]
    mat_fast64.combiner1.B = COMBINER_0_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_B_0]
    mat_fast64.combiner1.C = COMBINER_0_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_C_0]
    mat_fast64.combiner1.D = COMBINER_0_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_D_0]

    mat_fast64.combiner1.A_alpha = COMBINER_0_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_A_0
    ]
    mat_fast64.combiner1.B_alpha = COMBINER_0_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_B_0
    ]
    mat_fast64.combiner1.C_alpha = COMBINER_0_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_C_0
    ]
    mat_fast64.combiner1.D_alpha = COMBINER_0_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_D_0
    ]

    mat_fast64.combiner2.A = COMBINER_1_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_A_1]
    mat_fast64.combiner2.B = COMBINER_1_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_B_1]
    mat_fast64.combiner2.C = COMBINER_1_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_C_1]
    mat_fast64.combiner2.D = COMBINER_1_MUXES_FAST64_MAP[mat_rdpq.combiner.rgb_D_1]

    mat_fast64.combiner2.A_alpha = COMBINER_1_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_A_1
    ]
    mat_fast64.combiner2.B_alpha = COMBINER_1_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_B_1
    ]
    mat_fast64.combiner2.C_alpha = COMBINER_1_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_C_1
    ]
    mat_fast64.combiner2.D_alpha = COMBINER_1_MUXES_FAST64_MAP[
        mat_rdpq.combiner.alpha_D_1
    ]

    # Registers

    mat_fast64.set_k0_5 = mat_rdpq.registers.set_k4 or mat_rdpq.registers.set_k5
    mat_fast64.k4 = mat_rdpq.registers.k4 if mat_rdpq.registers.set_k4 else 0
    mat_fast64.k5 = mat_rdpq.registers.k5 if mat_rdpq.registers.set_k5 else 0
    mat_fast64.set_prim = mat_rdpq.registers.set_prim_lod_frac or mat_rdpq.registers.set_prim_color
    mat_fast64.prim_lod_frac = mat_rdpq.registers.prim_lod_frac if mat_rdpq.registers.set_prim_lod_frac else 0
    mat_fast64.prim_color = mat_rdpq.registers.prim_color if mat_rdpq.registers.set_prim_color else (1, 1, 1, 1)
    mat_fast64.set_env = mat_rdpq.registers.set_env_color
    mat_fast64.env_color = mat_rdpq.registers.env_color
    # TODO: key scale, key center

    # Blender

    # TODO handle one-cycle props

    mat_fast64.rdp_settings.blend_p1 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.p_0]
    mat_fast64.rdp_settings.blend_a1 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.a_0]
    mat_fast64.rdp_settings.blend_m1 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.q_0]
    mat_fast64.rdp_settings.blend_b1 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.b_0]

    mat_fast64.rdp_settings.blend_p2 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.p_1]
    mat_fast64.rdp_settings.blend_a2 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.a_1]
    mat_fast64.rdp_settings.blend_m2 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.q_1]
    mat_fast64.rdp_settings.blend_b2 = BLENDER_MUXES_FAST64_MAP[mat_rdpq.blender.b_1]

    # blend_color is set below
    mat_fast64.set_fog = True
    mat_fast64.fog_color = mat_rdpq.blender.fog_color

    # Overrides

    # TODO
    if mat_rdpq.override_render_mode.override_antialias:
        mat_rdpq.override_render_mode.antialias
    else:
        world_rdpq_defaults.antialias

    # TODO
    if mat_rdpq.override_render_mode.override_fog:
        mat_rdpq.override_render_mode.fog
    else:
        world_rdpq_defaults.fog

    (
        mat_fast64.rdp_settings.g_mdsft_rgb_dither,
        mat_fast64.rdp_settings.g_mdsft_alpha_dither,
    ) = {
        # TODO check these mappings are correct (I guessed)
        "RGB_SQUARE_A_SQUARE": ("G_CD_MAGICSQ", "G_AD_PATTERN"),
        "RGB_SQUARE_A_INVSQUARE": ("G_CD_MAGICSQ", "G_AD_NOTPATTERN"),
        "RGB_SQUARE_A_NOISE": ("G_CD_MAGICSQ", "G_AD_NOISE"),
        "RGB_SQUARE_A_NONE": ("G_CD_MAGICSQ", "G_AD_DISABLE"),
        "RGB_BAYER_A_BAYER": ("G_CD_BAYER", "G_AD_PATTERN"),
        "RGB_BAYER_A_INVBAYER": ("G_CD_BAYER", "G_AD_NOTPATTERN"),
        "RGB_BAYER_A_NOISE": ("G_CD_BAYER", "G_AD_NOISE"),
        "RGB_BAYER_A_NONE": ("G_CD_BAYER", "G_AD_DISABLE"),
        "RGB_NOISE_A_SQUARE": ("G_CD_NOISE", "G_AD_PATTERN"),
        "RGB_NOISE_A_INVSQUARE": ("G_CD_NOISE", "G_AD_NOTPATTERN"),
        "RGB_NOISE_A_NOISE": ("G_CD_NOISE", "G_AD_NOISE"),
        "RGB_NOISE_A_NONE": ("G_CD_NOISE", "G_AD_DISABLE"),
        "RGB_NONE_A_BAYER": ("G_CD_DISABLE", "G_AD_PATTERN"),
        "RGB_NONE_A_INVBAYER": ("G_CD_DISABLE", "G_AD_NOTPATTERN"),
        "RGB_NONE_A_NOISE": ("G_CD_DISABLE", "G_AD_NOISE"),
        "RGB_NONE_A_NONE": ("G_CD_DISABLE", "G_AD_DISABLE"),
    }[
        (
            mat_rdpq.override_render_mode.dithering
            if mat_rdpq.override_render_mode.override_dithering
            else world_rdpq_defaults.dithering
        )
    ]

    mat_fast64.rdp_settings.g_mdsft_text_filt = {
        "POINT": "G_TF_POINT",
        "BILINEAR": "G_TF_BILERP",
        "MEDIAN": "G_TF_AVERAGE",
    }[
        (
            mat_rdpq.override_render_mode.texture_filtering
            if mat_rdpq.override_render_mode.override_texture_filtering
            else world_rdpq_defaults.texture_filtering
        )
    ]

    mat_fast64.rdp_settings.g_mdsft_textpersp = (
        "G_TP_PERSP"
        if (
            mat_rdpq.override_render_mode.texture_perspective_correction
            if mat_rdpq.override_render_mode.override_texture_perspective_correction
            else world_rdpq_defaults.texture_perspective_correction
        )
        else "G_TP_NONE"
    )

    if mat_rdpq.override_render_mode.override_alpha_compare:
        mat_fast64.rdp_settings.g_mdsft_alpha_compare = "G_AC_THRESHOLD"
        alpha_compare_threshold = mat_rdpq.override_render_mode.alpha_compare_threshold
    else:
        if world_rdpq_defaults.alpha_compare:
            mat_fast64.rdp_settings.g_mdsft_alpha_compare = "G_AC_THRESHOLD"
            alpha_compare_threshold = world_rdpq_defaults.alpha_compare_threshold
        else:
            mat_fast64.rdp_settings.g_mdsft_alpha_compare = "G_AC_NONE"
            alpha_compare_threshold = None

    mat_fast64.set_blend = True
    mat_fast64.blend_color = (
        *mat_rdpq.blender.blend_color,
        1 if alpha_compare_threshold is None else (alpha_compare_threshold / 255),
    )

    mat_fast64.rdp_settings.z_cmp = (
        mat_rdpq.override_render_mode.z_compare
        if mat_rdpq.override_render_mode.override_z_compare_and_z_update
        else world_rdpq_defaults.z_compare
    )

    mat_fast64.rdp_settings.z_upd = (
        mat_rdpq.override_render_mode.z_update
        if mat_rdpq.override_render_mode.override_z_compare_and_z_update
        else world_rdpq_defaults.z_update
    )

    if mat_rdpq.override_render_mode.override_fixed_z:
        mat_fast64.rdp_settings.g_mdsft_zsrcsel = "G_ZS_PRIM"
        mat_fast64.rdp_settings.prim_depth.z = mat_rdpq.override_render_mode.fixed_z
        mat_fast64.rdp_settings.prim_depth.dz = (
            mat_rdpq.override_render_mode.fixed_z_deltaz
        )
    else:
        if world_rdpq_defaults.fixed_z:
            mat_fast64.rdp_settings.g_mdsft_zsrcsel = "G_ZS_PRIM"
            mat_fast64.rdp_settings.prim_depth.z = world_rdpq_defaults.fixed_z_value
            mat_fast64.rdp_settings.prim_depth.dz = world_rdpq_defaults.fixed_z_deltaz
        else:
            mat_fast64.rdp_settings.g_mdsft_zsrcsel = "G_ZS_PIXEL"

    # Other

    mat_fast64.uv_basis = "TEXEL0"
    mat_fast64.rdp_settings.g_shade_smooth = True
    mat_fast64.rdp_settings.g_lighting = False
    mat_fast64.rdp_settings.g_cull_front = False
    mat_fast64.rdp_settings.g_cull_back = True
    mat_fast64.rdp_settings.g_zbuffer = True
    mat_fast64.rdp_settings.g_shade = True


QUEUED_UPDATES = set()


def msgbus_sync_rdpq_material_props_to_fast64_props(
    owner: object,
    mat: bpy.types.Material,
):

    def sync_callback():
        if mat in QUEUED_UPDATES:
            return
        scene = bpy.context.scene
        if scene is None:
            return
        world = scene.world

        def delayed_callback():
            QUEUED_UPDATES.discard(mat)
            with bpy.context.temp_override(material=mat):  # type: ignore
                rdpq_material_props_to_fast64_props(mat, world)

        QUEUED_UPDATES.add(mat)
        bpy.app.timers.register(delayed_callback, first_interval=0.2)

    def sync_subscribe(
        thing: bpy.types.bpy_struct,
        props_list: rdpq_material_props.RecursivePropsList,
    ):
        for prop_name in props_list.props:
            bpy.msgbus.subscribe_rna(
                key=thing.path_resolve(prop_name, False),
                owner=owner,
                args=(),
                notify=sync_callback,
            )
        for group_prop_name, group_prop_list in props_list.groups.items():
            sync_subscribe(getattr(thing, group_prop_name), group_prop_list)

    sync_subscribe(mat, rdpq_material_props.LIBDRAGON_RDPQ_PROPS_LIST)


class RDPQMaterialPropsToFast64Operator(bpy.types.Operator):
    bl_idname = "libdragon_rdpq.rdpq_material_props_to_fast64"
    bl_label = "RDPQ properties to Fast64"

    @classmethod
    def poll(cls, context):
        return (
            hasattr(context, "material")
            and context.material is not None
            and is_fast64_material(context.material)
            and context.scene is not None
        )

    def execute(self, context):  # type: ignore
        mat = context.material
        assert mat is not None
        assert context.scene is not None
        world = context.scene.world
        rdpq_material_props_to_fast64_props(mat, world)
        return {"FINISHED"}


def copy_props(f, t, props_list: rdpq_material_props.RecursivePropsList):
    for prop_name in props_list.props:
        setattr(t, prop_name, getattr(f, prop_name))
    for group_name, group_props_list in props_list.groups.items():
        copy_props(getattr(f, group_name), getattr(t, group_name), group_props_list)


def rdpq_material_copy_props(
    from_mat: bpy.types.Material,
    to_mat: bpy.types.Material,
):
    copy_props(from_mat, to_mat, rdpq_material_props.LIBDRAGON_RDPQ_PROPS_LIST)


def rdpq_material_recreate_as_fast64(
    mat: bpy.types.Material, world: Optional[bpy.types.World]
):
    # Create a fast64 material and find it
    keys_before = set(bpy.data.materials.keys())
    bpy.ops.object.create_f3d_mat()  # type: ignore
    keys_after = set(bpy.data.materials.keys())
    assert keys_after.issuperset(keys_before)
    keys_added = keys_after - keys_before
    assert len(keys_added) == 1
    (key_added,) = keys_added
    new_mat = bpy.data.materials[key_added]

    # Transfer properties from mat to new_mat and to fast64 properties
    rdpq_material_copy_props(mat, new_mat)
    rdpq_material_props_to_fast64_props(new_mat, world)

    # Replace mat with new_mat in all slots where mat is used
    for obj in bpy.data.objects:
        for i in range(len(obj.material_slots)):
            if obj.material_slots[i].material == mat:
                obj.material_slots[i].material = new_mat

    mat_name = mat.name
    mat.name = mat.name + " old"
    new_mat.name = mat_name

    # Delete the new material slot fast64 created for new_mat
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.material_slot_remove()


class RDPQMaterialRecreateAsFast64Operator(bpy.types.Operator):
    bl_idname = "libdragon_rdpq.rdpq_material_recreate_as_fast64"
    bl_label = "Recreate RDPQ material as Fast64 material"

    @classmethod
    def poll(cls, context):
        return (
            hasattr(context, "material")
            and context.material is not None
            and context.scene is not None
        )

    def execute(self, context):  # type: ignore
        mat = context.material
        assert mat is not None
        assert context.scene is not None
        world = context.scene.world
        rdpq_material_recreate_as_fast64(mat, world)
        return {"FINISHED"}
