import json
import os

external_texture_list = set([
    "atari.avi",
    "atari.bmp",
    "Ball_LightningSphere1.bmp",
    "Ball_LightningSphere2.bmp",
    "Ball_LightningSphere3.bmp",
    "Ball_Paper.bmp",
    "Ball_Stone.bmp",
    "Ball_Wood.bmp",
    "Brick.bmp",
    "Button01_deselect.tga",
    "Button01_select.tga",
    "Button01_special.tga",
    "Column_beige.bmp",
    "Column_beige_fade.tga",
    "Column_blue.bmp",
    "Cursor.tga",
    "Dome.bmp",
    "DomeEnvironment.bmp",
    "DomeShadow.tga",
    "ExtraBall.bmp",
    "ExtraParticle.bmp",
    "E_Holzbeschlag.bmp",
    "FloorGlow.bmp",
    "Floor_Side.bmp",
    "Floor_Top_Border.bmp",
    "Floor_Top_Borderless.bmp",
    "Floor_Top_Checkpoint.bmp",
    "Floor_Top_Flat.bmp",
    "Floor_Top_Profil.bmp",
    "Floor_Top_ProfilFlat.bmp",
    "Font_1.tga",
    "Gravitylogo_intro.bmp",
    "HardShadow.bmp",
    "Laterne_Glas.bmp",
    "Laterne_Schatten.tga",
    "Laterne_Verlauf.tga",
    "Logo.bmp",
    "Metal_stained.bmp",
    "Misc_Ufo.bmp",
    "Misc_UFO_Flash.bmp",
    "Modul03_Floor.bmp",
    "Modul03_Wall.bmp",
    "Modul11_13_Wood.bmp",
    "Modul11_Wood.bmp",
    "Modul15.bmp",
    "Modul16.bmp",
    "Modul18.bmp",
    "Modul18_Gitter.tga",
    "Modul30_d_Seiten.bmp",
    "Particle_Flames.bmp",
    "Particle_Smoke.bmp",
    "PE_Bal_balloons.bmp",
    "PE_Bal_platform.bmp",
    "PE_Ufo_env.bmp",
    "Pfeil.tga",
    "P_Extra_Life_Oil.bmp",
    "P_Extra_Life_Particle.bmp",
    "P_Extra_Life_Shadow.bmp",
    "Rail_Environment.bmp",
    "sandsack.bmp",
    "SkyLayer.bmp",
    "Sky_Vortex.bmp",
    "Stick_Bottom.tga",
    "Stick_Stripes.bmp",
    "Target.bmp",
    "Tower_Roof.bmp",
    "Trafo_Environment.bmp",
    "Trafo_FlashField.bmp",
    "Trafo_Shadow_Big.tga",
    "Tut_Pfeil01.tga",
    "Tut_Pfeil_Hoch.tga",
    "Wolken_intro.tga",
    "Wood_Metal.bmp",
    "Wood_MetalStripes.bmp",
    "Wood_Misc.bmp",
    "Wood_Nailed.bmp",
    "Wood_Old.bmp",
    "Wood_Panel.bmp",
    "Wood_Plain.bmp",
    "Wood_Plain2.bmp",
    "Wood_Raft.bmp"
])

component_list = [
    "P_Extra_Life",
    "P_Extra_Point",
    "P_Trafo_Paper",
    "P_Trafo_Stone",
    "P_Trafo_Wood",
    "P_Ball_Paper",
    "P_Ball_Stone",
    "P_Ball_Wood",
    "P_Box",
    "P_Dome",
    "P_Modul_01",
    "P_Modul_03",
    "P_Modul_08",
    "P_Modul_17",
    "P_Modul_18",
    "P_Modul_19",
    "P_Modul_25",
    "P_Modul_26",
    "P_Modul_29",
    "P_Modul_30",
    "P_Modul_34",
    "P_Modul_37",
    "P_Modul_41",
    "PC_TwoFlames",
    "PE_Balloon",
    "PR_Resetpoint",
    "PS_FourFlames"
]

'''
format: key is diection, value is a dict
dict's key is expand mode, value is a tuple
tuple always have 4 items, it means (TOP_STR, RIGHT_STR, BOTTOM_STR, LEFT_STR)
'''
floor_expand_direction_map = {
    "PositiveX": {
        "Static": ("X", "X", "X", "X"),
        "Column": ("X", "X", "D1", "X"),
        "Freedom": ("X", "X", "D1", "D2"),
    },
    "NegativeX": {
        "Static": ("X", "X", "X", "X"),
        "Column": ("D1", "X", "X", "X"),
        "Freedom": ("D1", "D2", "X", "X"),
    },
    "PositiveY": {
        "Static": ("X", "X", "X", "X"),
        "Column": ("X", "D1", "X", "X"),
        "Freedom": ("X", "D1", "D2", "X"),
    },
    "NegativeY": {
        "Static": ("X", "X", "X", "X"),
        "Column": ("X", "X", "X", "D1"),
        "Freedom": ("D2", "X", "X", "D1"),
    }
}

floor_texture_corresponding_map = {
    "FloorSide": "Floor_Side.bmp",
    "FloorTopBorder": "Floor_Top_Border.bmp",
    "FloorTopBorder_ForSide": "Floor_Top_Border.bmp",
    "FloorTopBorderless": "Floor_Top_Borderless.bmp",
    "FloorTopBorderless_ForSide": "Floor_Top_Borderless.bmp",
    "FloorTopFlat": "Floor_Top_Flat.bmp",
    "FloorTopProfil": "Floor_Top_Profil.bmp",
    "FloorTopProfilFlat": "Floor_Top_ProfilFlat.bmp",
    "BallWood": "Ball_Wood.bmp",
    "BallPaper": "Ball_Paper.bmp",
    "BallStone": "Ball_Stone.bmp"
}

# WARNING: this data is shared with BallanceVirtoolsPlugin - mapping_BM.cpp - fix_blender_texture
floor_material_statistic = [
    {
        "member": [
                "FloorSide",
                "FloorTopBorder_ForSide",
                "FloorTopBorderless_ForSide"
        ],
        "data": {
            "ambient": (0, 0, 0),
            "diffuse": (122 / 255.0, 122 / 255.0, 122 / 255.0),
            "specular": (0.0, 0.0, 0.0),
            "emissive": (104 / 255.0, 104 / 255.0, 104 / 255.0),
            "power": 0
        }
    },
    {
        "member": [
                "FloorTopBorder",
                "FloorTopBorderless",
                "FloorTopFlat",
                "FloorTopProfilFlat"
        ],
        "data": {
            "ambient": (0, 0, 0),
            "diffuse": (1.0, 1.0, 1.0),
            "specular": (80 / 255.0, 80 / 255.0, 80 / 255.0),
            "emissive": (0.0, 0.0, 0.0),
            "power": 100
        }
    },
    {
        "member": [
                "BallPaper"
        ],
        "data": {
            "ambient": (25 / 255.0, 25 / 255.0, 25 / 255.0),
            "diffuse": (1.0, 1.0, 1.0),
            "specular": (0.0, 0.0, 0.0),
            "emissive": (100 / 255.0, 100 / 255.0, 100 / 255.0),
            "power": 0
        }
    },
        {
        "member": [
                "BallStone",
                "BallWood"
        ],
        "data": {
            "ambient": (25 / 255.0, 25 / 255.0, 25 / 255.0),
            "diffuse": (1.0, 1.0, 1.0),
            "specular": (229 / 255.0, 229 / 255.0, 229 / 255.0),
            "emissive": (60 / 255.0, 60 / 255.0, 60 / 255.0),
            "power": 0
        }
    }
]

floor_block_dict = {}
floor_basic_block_list = []
floor_derived_block_list = []
with open(os.path.join(os.path.dirname(__file__), "json", "BasicBlock.json")) as fp:
    for item in json.load(fp):
        floor_basic_block_list.append(item["Type"])
        floor_block_dict[item["Type"]] = item
with open(os.path.join(os.path.dirname(__file__), "json", "DerivedBlock.json")) as fp:
    for item in json.load(fp):
        floor_derived_block_list.append(item["Type"])
        floor_block_dict[item["Type"]] = item

blenderIcon_floor = None
blenderIcon_floor_dict = {}
# blenderIcon_elements = None
# blenderIcon_elements_dict = {}