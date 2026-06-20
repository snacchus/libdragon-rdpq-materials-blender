from pathlib import Path

import bpy

from . import rdpq_material_props
from . import util

COMBINER_MUXES_MKMATERIAL_MAP = {
    "COMBINED": "combined",
    "COMBINED_ALPHA": "combined.a",
    "TEX0": "tex0",
    "TEX0_BUG": "tex0",
    "TEX1": "tex1",
    "SHADE": "shade",
    "PRIM": "prim",
    "ENV": "env",
    "NOISE": "noise",
    "1": "1",
    "0": "0",
    "K4": "k4",
    "K5": "k5",
    "TEX0_ALPHA": "tex0.a",
    "TEX1_ALPHA": "tex1.a",
    "SHADE_ALPHA": "shade.a",
    "PRIM_ALPHA": "prim.a",
    "ENV_ALPHA": "env.a",
    "LOD_FRAC": "lod_frac",
    "PRIM_LOD_FRAC": "prim_lod_frac",
    "KEYCENTER": "keycenter",
    "KEYSCALE": "keyscale",
}


def rdpq_material_properties_to_dict(
    mat_rdpq: rdpq_material_props.RDPQMaterialProperties,
):
    mat_data = {}
    mat_textures: dict[int, bpy.types.Image] = {}

    def handle_texture_axis(
        tex_i: int,
        axis: str,
        texture_axis_props: rdpq_material_props.RDPQMaterialTextureAxisProperties,
    ):
        mat_data.update(
            {
                f"tex{tex_i}.{axis}.translate": str(texture_axis_props.translate),
                f"tex{tex_i}.{axis}.scale": str(texture_axis_props.scale),
                f"tex{tex_i}.{axis}.repeats": (
                    "inf"
                    if texture_axis_props.repeats_inf
                    else str(texture_axis_props.repeats)
                ),
                f"tex{tex_i}.{axis}.mirror": str(texture_axis_props.mirror),
            }
        )

    def handle_texture(
        tex_i: int,
        texture_props: rdpq_material_props.RDPQMaterialTextureProperties,
    ):
        if texture_props.use_placeholder:
            raise NotImplementedError("mkmaterial doesn't implement placeholders yet?")
            # mat_data[f"tex{tex_i}.placeholder"] = str(texture_props.placeholder)
        else:
            if texture_props.image is not None:
                mat_textures[tex_i] = texture_props.image
            mat_data.update(
                {
                    f"tex{tex_i}.fmt": texture_props.format,
                    f"tex{tex_i}.mipmap": texture_props.mipmap,
                    f"tex{tex_i}.dithering": texture_props.dithering,
                }
            )
        # TODO do libdragon placeholders also contain ST information?
        # aka should ST props only be exported if not a placeholder?
        handle_texture_axis(tex_i, "s", texture_props.s)
        handle_texture_axis(tex_i, "t", texture_props.t)

    if mat_rdpq.use_texture0:
        handle_texture(0, mat_rdpq.texture0)
    if mat_rdpq.use_texture1:
        handle_texture(1, mat_rdpq.texture1)

    map = COMBINER_MUXES_MKMATERIAL_MAP

    if mat_rdpq.combiner.preset == "CUSTOM_1_PASS":
        combiner_rgb = (
            f"({map[mat_rdpq.combiner.rgb_A]},{map[mat_rdpq.combiner.rgb_B]},"
            f"{map[mat_rdpq.combiner.rgb_C]},{map[mat_rdpq.combiner.rgb_D]})"
        )
        combiner_alpha = (
            f"({map[mat_rdpq.combiner.alpha_A]},{map[mat_rdpq.combiner.alpha_B]},"
            f"{map[mat_rdpq.combiner.alpha_C]},{map[mat_rdpq.combiner.alpha_D]})"
        )
    elif mat_rdpq.combiner.preset == "CUSTOM_2_PASSES":
        combiner_rgb = (
            f"({map[mat_rdpq.combiner.rgb_A_0]},{map[mat_rdpq.combiner.rgb_B_0]},"
            f"{map[mat_rdpq.combiner.rgb_C_0]},{map[mat_rdpq.combiner.rgb_D_0]})"
            ","
            f"({map[mat_rdpq.combiner.rgb_A_1]},{map[mat_rdpq.combiner.rgb_B_1]},"
            f"{map[mat_rdpq.combiner.rgb_C_1]},{map[mat_rdpq.combiner.rgb_D_1]})"
        )
        combiner_alpha = (
            f"({map[mat_rdpq.combiner.alpha_A_0]},{map[mat_rdpq.combiner.alpha_B_0]},"
            f"{map[mat_rdpq.combiner.alpha_C_0]},{map[mat_rdpq.combiner.alpha_D_0]})"
            ","
            f"({map[mat_rdpq.combiner.alpha_A_1]},{map[mat_rdpq.combiner.alpha_B_1]},"
            f"{map[mat_rdpq.combiner.alpha_C_1]},{map[mat_rdpq.combiner.alpha_D_1]})"
        )
    else:
        combiner_rgb, combiner_alpha = {
            "FLAT": (
                "(0,0,0,prim)",
                "(0,0,0,prim)",
            ),
            "SHADE": (
                "(0,0,0,shade)",
                "(0,0,0,shade)",
            ),
            "TEX": (
                "(0,0,0,tex0)",
                "(0,0,0,tex0)",
            ),
            "TEX_FLAT": (
                "(tex0,0,prim,0)",
                "(tex0,0,prim,0)",
            ),
            "TEX_SHADE": (
                "(tex0,0,shade,0)",
                "(tex0,0,shade,0)",
            ),
        }[mat_rdpq.combiner.preset]

    mat_data.update(
        {
            "combiner.rgb.raw": combiner_rgb,
            "combiner.alpha.raw": combiner_alpha,
        }
    )

    if mat_rdpq.registers.set_k4:
        mat_data["combiner.reg.k4"] = str(mat_rdpq.registers.k4);
    if mat_rdpq.registers.set_k5:
        mat_data["combiner.reg.k5"] = str(mat_rdpq.registers.k5);
    if mat_rdpq.registers.set_keyscale:
        mat_data["combiner.reg.keyscale"] = str(mat_rdpq.registers.keyscale);
    if mat_rdpq.registers.set_keycenter:
        mat_data["combiner.reg.keycenter"] = str(mat_rdpq.registers.keycenter);
    if mat_rdpq.registers.set_prim_lod_frac:
        mat_data["combiner.reg.prim_lod_frac"] = str(mat_rdpq.registers.prim_lod_frac);
    if mat_rdpq.registers.set_env_color:
        e = mat_rdpq.registers.env_color
        mat_data["combiner.reg.env"] = f"{e[0]},{e[1]},{e[2]},{e[3]}"
    if mat_rdpq.registers.set_prim_color:
        p = mat_rdpq.registers.prim_color
        mat_data["combiner.reg.prim"] = f"{p[0]},{p[1]},{p[2]},{p[3]}"

    if mat_rdpq.blender.preset == "CUSTOM_1_PASS":
        raise NotImplementedError()
    elif mat_rdpq.blender.preset == "CUSTOM_2_PASSES":
        raise NotImplementedError()
    else:
        mat_data["blender.mode"] = mat_rdpq.blender.preset.lower()
        if mat_rdpq.blender.preset == "MULTIPLY_CONST":
            mat_data["blender.const"] = str(mat_rdpq.blender.fog_color[3])

    if mat_rdpq.override_render_mode.override_antialias:
        mat_data["rm.antialias"] = mat_rdpq.override_render_mode.antialias.lower()
    if mat_rdpq.override_render_mode.override_fog:
        mat_data["rm.fog"] = mat_rdpq.override_render_mode.fog.lower()
    if mat_rdpq.override_render_mode.override_dithering:
        mat_data["rm.dither.rgb"], mat_data["rm.dither.alpha"] = {
            "RGB_SQUARE_A_SQUARE": ("square", "square"),
            "RGB_SQUARE_A_INVSQUARE": ("square", "invsquare"),
            "RGB_SQUARE_A_NOISE": ("square", "noise"),
            "RGB_SQUARE_A_NONE": ("square", "none"),
            "RGB_BAYER_A_BAYER": ("bayer", "bayer"),
            "RGB_BAYER_A_INVBAYER": ("bayer", "invbayer"),
            "RGB_BAYER_A_NOISE": ("bayer", "noise"),
            "RGB_BAYER_A_NONE": ("bayer", "none"),
            "RGB_NOISE_A_SQUARE": ("noise", "square"),
            "RGB_NOISE_A_INVSQUARE": ("noise", "invsquare"),
            "RGB_NOISE_A_NOISE": ("noise", "noise"),
            "RGB_NOISE_A_NONE": ("noise", "none"),
            "RGB_NONE_A_BAYER": ("none", "bayer"),
            "RGB_NONE_A_INVBAYER": ("none", "invbayer"),
            "RGB_NONE_A_NOISE": ("none", "noise"),
            "RGB_NONE_A_NONE": ("none", "none"),
        }[(mat_rdpq.override_render_mode.dithering)]
    if mat_rdpq.override_render_mode.override_texture_filtering:
        mat_data["rm.filtering"] = (
            mat_rdpq.override_render_mode.texture_filtering.lower()
        )
    if mat_rdpq.override_render_mode.override_texture_perspective_correction:
        mat_data["rm.perspective"] = str(
            mat_rdpq.override_render_mode.texture_perspective_correction
        )
    if mat_rdpq.override_render_mode.override_alpha_compare:
        mat_data["rm.alpha_compare"] = str(
            mat_rdpq.override_render_mode.alpha_compare_threshold
        )
    if mat_rdpq.override_render_mode.override_z_compare_and_z_update:
        mat_data["rm.zmode"] = {
            (False, False): "none",
            (True, False): "compare",
            (False, True): "update",
            (True, True): "compare+update",
        }[
            (
                mat_rdpq.override_render_mode.z_compare,
                mat_rdpq.override_render_mode.z_update,
            )
        ]
    if mat_rdpq.override_render_mode.override_fixed_z:
        mat_data["rm.z_override"] = str(mat_rdpq.override_render_mode.fixed_z)
        mat_data["rm.deltaz_override"] = str(
            mat_rdpq.override_render_mode.fixed_z_deltaz
        )

    return mat_data, mat_textures


class RDPQMaterialExportOperator(bpy.types.Operator):
    bl_idname = "libdragon_rdpq.rdpq_material_export"
    bl_label = "Export RDPQ material"

    out_file: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return hasattr(context, "material") and context.material is not None

    def execute(self, context):  # type: ignore
        mat = context.material
        assert mat is not None
        mat_rdpq = util.LIBDRAGON_RDPQ(mat)

        mat_data, mat_textures = rdpq_material_properties_to_dict(mat_rdpq)

        for i in (0, 1):
            if i in mat_textures:
                img = mat_textures[i]
                saved_filepath = img.filepath
                try:
                    img.filepath = str(Path(self.out_file).parent / f"{img.name}.png")
                    mat_data[f"tex{i}.name"] = img.filepath
                    img.save()
                finally:
                    img.filepath = saved_filepath

        import json

        mat_library_json = json.dumps({mat.name: mat_data}, indent=0)

        Path(self.out_file).write_text(mat_library_json)

        return {"FINISHED"}
