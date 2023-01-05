import json
import os
import re

bmfile_currentVersion = 14
bmfile_flagUnicode = 0x800
bmfile_flagDeflatedMaximum = 0x2
bmfile_globalComment = 'Use BM Spec 1.4'.encode('utf-8')

class BmfileInfoType():
    OBJECT = 0
    MESH = 1
    MATERIAL = 2
    TEXTURE = 3

bmfile_externalTextureSet = set([
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

bmfile_componentList = [
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
floor_expandDirectionMap = {
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

floor_textureReflactionMap = {
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

# WARNING: this data is shared with `BallanceVirtoolsPlugin/bvh/features/mapping/fix_texture.cpp`
floor_materialStatistic = [
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
                "FloorTopProfil",
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

floor_blockDict = {}
floor_basicBlockList = []
floor_derivedBlockList = []
# read from json
for walk_root, walk_dirs, walk_files in os.walk(os.path.join(os.path.dirname(__file__), "json", "basic_blocks")):
    for relfile in walk_files:
        if not relfile.endswith('.json'): continue
        with open(os.path.join(walk_root, relfile)) as fp:
            for item in json.load(fp):
                floor_basicBlockList.append(item["Type"])
                floor_blockDict[item["Type"]] = item
for walk_root, walk_dirs, walk_files in os.walk(os.path.join(os.path.dirname(__file__), "json", "derived_blocks")):
    for relfile in walk_files:
        if not relfile.endswith('.json'): continue
        with open(os.path.join(walk_root, relfile)) as fp:
            for item in json.load(fp):
                floor_derivedBlockList.append(item["Type"])
                floor_blockDict[item["Type"]] = item

icons_floor = None
icons_floorDict = {}
# blenderIcon_elements = None
# blenderIcon_elements_dict = {}

rename_normalComponentsGroupName = set([
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
    "P_Modul_41"
])

rename_uniqueComponentsGroupName = set([
    "PS_Levelstart",
    "PE_Levelende",
    "PC_Checkpoints",
    "PR_Resetpoints"
])

rename_floorGroupTester = set([
    "Sound_HitID_01",
    "Sound_RollID_01"
])

rename_woodGroupTester = set([
    "Sound_HitID_02",
    "Sound_RollID_02"
])

# 61 mark: Sector_(0[1-8]|[1-9][0-9]{1,2}|9) may also work
rename_regexCKGroupSector = re.compile('^Sector_([123456789]{1}[0123456789]{1}[0123456789]{1}|[123456789]{1}[0123456789]{1}|0[12345678]{1}|9)$')
rename_regexYYCComponent = re.compile('^(' + '|'.join(rename_normalComponentsGroupName) + ')_(0[1-9]|[1-9][0-9])_.*$')
rename_regexYYCPC = re.compile('^PC_TwoFlames_(0[1-7])$')
rename_regexYYCPR = re.compile('^PR_Resetpoint_(0[1-8])$')
rename_regexImengyuComponent = re.compile('^(' + '|'.join(rename_normalComponentsGroupName) + '):[^:]*:([1-9]|[1-9][0-9])$')
rename_regexImengyuPCRComp = re.compile('^(PC_CheckPoint|PR_ResetPoint):([0-9]+)$')

propsVtGroups_availableGroups = (
    "Sector_01",
    "Sector_02",
    "Sector_03",
    "Sector_04",
    "Sector_05",
    "Sector_06",
    "Sector_07",
    "Sector_08",

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

    "PS_Levelstart",
    "PE_Levelende",
    "PC_Checkpoints",
    "PR_Resetpoints",

    "Sound_HitID_01",
    "Sound_RollID_01",
    "Sound_HitID_02",
    "Sound_RollID_02",
    "Sound_HitID_03",
    "Sound_RollID_03",

    "DepthTestCubes",

    "Phys_Floors",
    "Phys_FloorRails",
    "Phys_FloorStopper",
    
    "Shadow"
)


