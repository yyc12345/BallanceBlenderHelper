import bpy
from . import UTILS_constants, UTILS_functions

class rename_system_props(bpy.types.Operator):
    name_standard: bpy.props.EnumProperty(
        name="Name Standard",
        description="Choose your name standard",
        items=(
            ("YYC", "YYC Tools Chains", "YYC Tools Chains name standard."),
            ("IMENGYU", "Imengyu Ballance", "Auto grouping name standard for Imengyu/Ballance")
            ),
    )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name_standard")

class BALLANCE_OT_rename_by_group(rename_system_props):
    """Rename object by Virtools groups"""
    bl_idname = "ballance.rename_by_group"
    bl_label = "Rename by Group"
    bl_options = {'UNDO'}

    def execute(self, context):
        _rename_core(_NameStandard.CKGROUP, _NameStandard.cvt_std_from_str_to_int(self.name_standard))
        return {'FINISHED'}

class BALLANCE_OT_convert_name(rename_system_props):
    """Convert name from one name standard to another one."""
    bl_idname = "ballance.convert_name"
    bl_label = "Convert Name"
    bl_options = {'UNDO'}

    dest_name_standard: bpy.props.EnumProperty(
        name="Destination Name Standard",
        description="Choose your name standard",
        items=(
            ("YYC", "YYC Tools Chains", "YYC Tools Chains name standard."),
            ("IMENGYU", "Imengyu Ballance", "Auto grouping name standard for Imengyu/Ballance")
            ),
    )

    def execute(self, context):
        _rename_core(
            _NameStandard.cvt_std_from_str_to_int(self.name_standard),
            _NameStandard.cvt_std_from_str_to_int(self.dest_name_standard))
        return {'FINISHED'}

    # rewrite draw func
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name_standard")
        layout.prop(self, "dest_name_standard")

class BALLANCE_OT_auto_grouping(rename_system_props):
    """Auto Grouping object according to specific name standard."""
    bl_idname = "ballance.auto_grouping"
    bl_label = "Auto Grouping"
    bl_options = {'UNDO'}

    def execute(self, context):
        _rename_core(_NameStandard.cvt_std_from_str_to_int(self.name_standard), _NameStandard.CKGROUP)
        return {'FINISHED'}

# ========================================== 
# rename misc funcs

class _ObjectBasicType():
    COMPONENT = 0

    FLOOR = 1
    RAIL = 2
    WOOD = 3
    STOPPER = 4

    DEPTH_CUBE = 5

    DECORATION = 6

    LEVEL_START = 7
    LEVEL_END = 8
    CHECKPOINT = 9
    RESETPOINT = 10

class _NameStandard():
    CKGROUP = 0
    YYC = 1
    IMENGYU = 2

    @staticmethod
    def cvt_std_from_str_to_int(std_str):
        if std_str == "YYC":
            return _NameStandard.YYC
        elif std_str == "IMENGYU":
            return _NameStandard.IMENGYU
        else:
            raise Exception("Unknow name standard.")

class _NameInfoHelper():
    def __init__(self, _basic_type):
        self.basic_type = _basic_type

    # extra field notes:
    # COMPONENT: 
    #       component_type(string)
    #       sector(int)
    # CHECKPOINT, RESETPOINT:
    #       sector(int)(following Ballance index, checkpoint starts with 1)

def _get_selected_objects():
    return bpy.context.view_layer.active_layer_collection.collection.objects

def _try_get_custom_property(obj, field):
    try:
        return obj[field]
    except:
        return None

def _get_sector_from_ckgroup(group_set):
    # this counter is served for stupid 
    # multi-sector-grouping accident.
    counter = 0
    last_matched_sector = ''
    for i in group_set:
        regex_result = UTILS_constants.rename_regexCKGroupSector.match(i)
        if regex_result is not None:
            last_matched_sector = regex_result.group(1)
            counter += 1
            
    if counter != 1:
        return None
    else:
        return last_matched_sector


# ========================================== 
# rename core funcs

# NOTE: the implement of this function are copied from 
# BallanceVirtoolsHelper/bvh/features/mapping/grouping.cpp
# ---
# YYC Tools Chains name standard is Ballance-compatible name standard.
# So this functions also serving for `_get_name_info_from_group` function
# to help get sector field from PC/PR elements. In ordinary call(external call)
# The final error output should be outputed nromally. But in the call from 
# `_get_name_info_from_group`, this function should not output any error.
# So parameter `call_internal` is served for this work. In common it is False
# to let function output error str normally. But only set it to True in 
# the call from `_get_name_info_from_group` to disable error output.
def _get_name_info_from_yyc_name(obj_name, call_internal = False):
    
    # check component first
    regex_result = UTILS_constants.rename_regexYYCComponent.match(obj_name)
    if regex_result is not None:
        data = _NameInfoHelper(_ObjectBasicType.COMPONENT)
        data.component_type = regex_result.group(1)
        data.sector = int(regex_result.group(2))
        return data

    # check PC PR elements
    regex_result = UTILS_constants.rename_regexYYCPC.match(obj_name)
    if regex_result is not None:
        data = _NameInfoHelper(_ObjectBasicType.CHECKPOINT)
        data.sector = int(regex_result.group(1))
        return data
    regex_result = UTILS_constants.rename_regexYYCPR.match(obj_name)
    if regex_result is not None:
        data = _NameInfoHelper(_ObjectBasicType.RESETPOINT)
        data.sector = int(regex_result.group(1))
        return data

    # check other unique elements
    if obj_name == "PS_FourFlames_01":
        return _NameInfoHelper(_ObjectBasicType.LEVEL_START)
    if obj_name == "PE_Balloon_01":
        return _NameInfoHelper(_ObjectBasicType.LEVEL_END)

    # process floors
    if obj_name.startswith("A_Floor"):
        return _NameInfoHelper(_ObjectBasicType.FLOOR)
    if obj_name.startswith("A_Wood"):
        return _NameInfoHelper(_ObjectBasicType.WOOD)
    if obj_name.startswith("A_Rail"):
        return _NameInfoHelper(_ObjectBasicType.RAIL)
    if obj_name.startswith("A_Stopper"):
        return _NameInfoHelper(_ObjectBasicType.STOPPER)

    # process others
    if obj_name.startswith("DepthCubes"):
        return _NameInfoHelper(_ObjectBasicType.DEPTH_CUBE)
    if obj_name.startswith("D_"):
        return _NameInfoHelper(_ObjectBasicType.DECORATION)

    # only output in external calling
    if not call_internal:
        print("[ERROR]\t{}:\tName match lost.".format(obj_name))

    return None

def _get_name_info_from_imengyu_name(obj_name):

    # check component first
    regex_result = UTILS_constants.rename_regexImengyuComponent.match(obj_name)
    if regex_result is not None:
        data = _NameInfoHelper(_ObjectBasicType.COMPONENT)
        data.component_type = regex_result.group(1)
        data.sector = int(regex_result.group(2))
        return data

    # check PC PR elements
    regex_result = UTILS_constants.rename_regexImengyuPCRComp.match(obj_name)
    if regex_result is not None:
        eles_name = regex_result.group(1)
        if eles_name == 'PC_CheckPoint':
            data = _NameInfoHelper(_ObjectBasicType.CHECKPOINT)
        elif eles_name == 'PR_ResetPoint':
            data = _NameInfoHelper(_ObjectBasicType.RESETPOINT)
        data.sector = int(regex_result.group(2))
        return data

    # check other unique elements
    if obj_name == "PS_LevelStart":
        return _NameInfoHelper(_ObjectBasicType.LEVEL_START)
    if obj_name == "PE_LevelEnd":
        return _NameInfoHelper(_ObjectBasicType.LEVEL_END)

    # process floors
    if obj_name.startswith("S_Floors"):
        return _NameInfoHelper(_ObjectBasicType.FLOOR)
    if obj_name.startswith("S_FloorWoods"):
        return _NameInfoHelper(_ObjectBasicType.WOOD)
    if obj_name.startswith("S_FloorRails"):
        return _NameInfoHelper(_ObjectBasicType.RAIL)
    if obj_name.startswith("S_FloorStopper"):
        return _NameInfoHelper(_ObjectBasicType.STOPPER)

    # process others
    if obj_name.startswith("DepthTestCubes"):
        return _NameInfoHelper(_ObjectBasicType.DEPTH_CUBE)
    if obj_name.startswith("O_"):
        return _NameInfoHelper(_ObjectBasicType.DECORATION)

    print("[ERROR]\t{}:\tName match lost.".format(obj_name))
    return None

def _get_name_info_from_group(obj):
    group_list = _try_get_custom_property(obj, 'virtools-group')
    if group_list is None:
        # name it as a decoration
        return _NameInfoHelper(_ObjectBasicType.DECORATION)

    group_set = set(group_list)

    # try to filter unique elements first
    set_result = UTILS_constants.rename_uniqueComponentsGroupName.intersection(group_set)
    if len(set_result) == 1:
        # get it
        gotten_group_name = (list(set_result))[0]
        if gotten_group_name == 'PS_Levelstart':
            return _NameInfoHelper(_ObjectBasicType.LEVEL_START)
        elif gotten_group_name == 'PE_Levelende':
            return _NameInfoHelper(_ObjectBasicType.LEVEL_END)
        elif gotten_group_name == 'PC_Checkpoints' or gotten_group_name == 'PR_Resetpoints':
            # these type's data should be gotten from its name
            # use _get_name_info_from_yyc_name to get it
            # _get_name_info_from_yyc_name is Ballance-compatible name standard
            data = _get_name_info_from_yyc_name(obj.name, call_internal=True)
            if data is None:
                print("[ERROR]\t{}:\tPC_Checkpoints or PR_Resetpoints detected. But couldn't get sector from name.".format(obj.name))
                return None
            if data.basic_type != _ObjectBasicType.CHECKPOINT and data.basic_type != _ObjectBasicType.RESETPOINT:
                # check whether it is checkpoint or resetpoint
                # if not, it mean that we got error data from name
                # return None instead
                print("[ERROR]\t{}:\tPC_Checkpoints or PR_Resetpoints detected. But name is illegal.".format(obj.name))
                return None
            # otherwise return data
            return data
        else:
            print("[ERROR]\t{}:\tThe match of Unique Component lost.".format(obj.name))
            return None
    elif len(set_result) != 0:
        # must be a weird grouping, report it
        print("[ERROR]\t{}:\tA Multi-grouping Unique Component.".format(obj.name))
        return None

    # distinguish normal elements
    set_result = UTILS_constants.rename_normalComponentsGroupName.intersection(group_set)
    if len(set_result) == 1:
        # get it
        # now try get its sector
        gotten_elements = (tuple(set_result))[0]
        gotten_sector = _get_sector_from_ckgroup(group_set)
        if gotten_sector is None:
            # fail to get sector
            print("[ERROR]\t{}:\tComponent detected. But couldn't get sector from CKGroup data.".format(obj.name))
            return None
        
        data = _NameInfoHelper(_ObjectBasicType.COMPONENT)
        data.component_type = gotten_elements
        data.sector = int(gotten_sector)
        return data
    elif len(set_result) != 0:
        # must be a weird grouping, report it
        print("[ERROR]\t{}:\tA Multi-grouping Component.".format(obj.name))
        return None

    # distinguish road
    if 'Phys_FloorRails' in group_set:
        # rail
        return _NameInfoHelper(_ObjectBasicType.RAIL)
    elif 'Phys_Floors' in group_set:
        # distinguish it between Floor and Wood
        floor_result =UTILS_constants.rename_floorGroupTester.intersection(group_set)
        rail_result = UTILS_constants.rename_woodGroupTester.intersection(group_set)
        if len(floor_result) > 0 and len(rail_result) == 0:
            return _NameInfoHelper(_ObjectBasicType.FLOOR)
        elif len(floor_result) == 0 and len(rail_result) > 0:
            return _NameInfoHelper(_ObjectBasicType.WOOD)
        else:
            print("[WARNING]\t{}:\tCan't distinguish between Floors and Rails. Suppose it is Floors".format(obj.name))
            return _NameInfoHelper(_ObjectBasicType.FLOOR)
    elif 'Phys_FloorStopper' in group_set:
        return _NameInfoHelper(_ObjectBasicType.STOPPER)
    elif 'DepthTestCubes' in group_set:
        return _NameInfoHelper(_ObjectBasicType.DEPTH_CUBE)

    # no matched
    print("[ERROR]\t{}:\tGroup match lost.".format(obj.name))
    return None

def _set_for_yyc_name(obj, name_info):
    basic_type = name_info.basic_type
    if basic_type == _ObjectBasicType.DECORATION:
        obj.name = "D_"

    elif basic_type == _ObjectBasicType.LEVEL_START:
        obj.name = "PS_FourFlames_01"
    elif basic_type == _ObjectBasicType.LEVEL_END:
        obj.name = "PE_Balloon_01"
    elif basic_type == _ObjectBasicType.RESETPOINT:
        obj.name = "PR_Resetpoint_{:0>2d}".format(name_info.sector)
    elif basic_type == _ObjectBasicType.CHECKPOINT:
        obj.name = "PC_TwoFlames_{:0>2d}".format(name_info.sector)

    elif basic_type == _ObjectBasicType.DEPTH_CUBE:
        obj.name = "DepthCubes_"

    elif basic_type == _ObjectBasicType.FLOOR:
        obj.name = "A_Floor_"
    elif basic_type == _ObjectBasicType.WOOD:
        obj.name = "A_Wood_"
    elif basic_type == _ObjectBasicType.RAIL:
        obj.name = "A_Rail_"
    elif basic_type == _ObjectBasicType.STOPPER:
        obj.name = "A_Stopper_"
    
    elif basic_type == _ObjectBasicType.COMPONENT:
        obj.name = "{}_{:0>2d}_".format(name_info.component_type, name_info.sector)
    

def _set_for_imengyu_name(obj, name_info):
    basic_type = name_info.basic_type
    if basic_type == _ObjectBasicType.DECORATION:
        obj.name = "O_"

    elif basic_type == _ObjectBasicType.LEVEL_START:
        obj.name = "PS_LevelStart"
    elif basic_type == _ObjectBasicType.LEVEL_END:
        obj.name = "PE_LevelEnd"
    elif basic_type == _ObjectBasicType.RESETPOINT:
        obj.name = "PR_ResetPoint:{:d}".format(name_info.sector)
    elif basic_type == _ObjectBasicType.CHECKPOINT:
        obj.name = "PC_CheckPoint:{:d}".format(name_info.sector + 1)

    elif basic_type == _ObjectBasicType.DEPTH_CUBE:
        obj.name = "DepthTestCubes"

    elif basic_type == _ObjectBasicType.FLOOR:
        obj.name = "S_Floors"
    elif basic_type == _ObjectBasicType.WOOD:
        obj.name = "S_FloorWoods"
    elif basic_type == _ObjectBasicType.RAIL:
        obj.name = "S_FloorRails"
    elif basic_type == _ObjectBasicType.STOPPER:
        obj.name = "S_FloorStopper"
    
    elif basic_type == _ObjectBasicType.COMPONENT:
        obj.name = "{}:{}:{:d}".format(name_info.component_type, obj.name.replace(":", "_"), name_info.sector)
    
# NOTE: the implement of this function are copied from 
# BallanceVirtoolsHelper/bvh/features/mapping/grouping.cpp
def _set_for_group(obj, name_info):
    gps = []
    basic_type = name_info.basic_type

    if basic_type == _ObjectBasicType.DECORATION:
        # decoration do not need grouping
        pass

    elif basic_type == _ObjectBasicType.LEVEL_START:
        gps.append("PS_Levelstart")
    elif basic_type == _ObjectBasicType.LEVEL_END:
        gps.append("PE_Levelende")
    elif basic_type == _ObjectBasicType.RESETPOINT:
        gps.append("PC_Checkpoints")
    elif basic_type == _ObjectBasicType.CHECKPOINT:
        gps.append("PR_Resetpoints")

    elif basic_type == _ObjectBasicType.DEPTH_CUBE:
        gps.append("DepthTestCubes")

    elif basic_type == _ObjectBasicType.FLOOR:
        gps.append("Phys_Floors")
        gps.append("Sound_HitID_01")
        gps.append("Sound_RollID_01")
        gps.append("Shadow")
    elif basic_type == _ObjectBasicType.WOOD:
        gps.append("Phys_FloorRails")
        gps.append("Sound_HitID_03")
        gps.append("Sound_RollID_03")
    elif basic_type == _ObjectBasicType.RAIL:
        gps.append("Phys_Floors")
        gps.append("Sound_HitID_02")
        gps.append("Sound_RollID_02")
        gps.append("Shadow")
    elif basic_type == _ObjectBasicType.STOPPER:
        gps.append("Phys_FloorStopper")
    
    elif basic_type == _ObjectBasicType.COMPONENT:
        gps.append(name_info.component_type)

        # set compabitility for 999 sector loader
        if (name_info.sector == 9):
            gps.append("Sector_9")
        else:
            gps.append("Sector_{:0>2d}".format(name_info.sector))
    

    # apply to custom property
    obj['virtools-group'] = tuple(gps)

# ========================================== 
# assemble funcs

def _get_data(obj, standard):
    if standard == _NameStandard.YYC:
        return _get_name_info_from_yyc_name(obj.name)
    elif standard == _NameStandard.IMENGYU:
        return _get_name_info_from_imengyu_name(obj.name)
    elif standard == _NameStandard.CKGROUP:
        return _get_name_info_from_group(obj)
    else:
        raise Exception("Unknow standard")

def _set_data(obj, name_info, standard):
    if standard == _NameStandard.YYC:
        return _set_for_yyc_name(obj, name_info)
    elif standard == _NameStandard.IMENGYU:
        return _set_for_imengyu_name(obj, name_info)
    elif standard == _NameStandard.CKGROUP:
        return _set_for_group(obj, name_info)
    else:
        raise Exception("Unknow standard")

def _rename_core(source_std, dest_std):
    if source_std == dest_std:
        # if source == dest
        # we do not to do anything
        return

    failed_obj_counter = 0
    all_obj_counter = 0

    print('============')
    print('Rename system report')
    print('------------')
    for obj in _get_selected_objects():
        all_obj_counter += 1
        info = _get_data(obj, source_std)
        if info is None:
            failed_obj_counter += 1
            continue

        _set_data(obj, info, dest_std)

    print('------------')
    print('All/failed - {}/{}'.format(all_obj_counter, failed_obj_counter))
    print('============')

    UTILS_functions.show_message_box(
        ('Rename system report',
        'View console to get more detail',
        'All: {}'.format(all_obj_counter),
        'Failed: {}'.format(failed_obj_counter)),
        "Info",
        "INFO"
    )
