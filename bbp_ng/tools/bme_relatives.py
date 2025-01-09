import typing
import collections
import simple_po

#region Translation Constant

## TODO:
#  This translation context string prefix is cpoied from UTIL_translation.py.
#  If the context string of translation changed, please synchronize it.

CTX_TRANSLATION: str = 'BBP/BME'

#endregion

#region BME Tokens

## TODO:
#  These token are copied from UTIL_bme.py.
#  If anything changed, such as BME standard, these tokens should be synchronized between these 2 modules.

TOKEN_IDENTIFIER: str = 'identifier'

TOKEN_SHOWCASE: str = 'showcase'
TOKEN_SHOWCASE_TITLE: str = 'title'
TOKEN_SHOWCASE_ICON: str = 'icon'
TOKEN_SHOWCASE_TYPE: str = 'type'
TOKEN_SHOWCASE_CFGS: str = 'cfgs'
TOKEN_SHOWCASE_CFGS_FIELD: str = 'field'
TOKEN_SHOWCASE_CFGS_TYPE: str = 'type'
TOKEN_SHOWCASE_CFGS_TITLE: str = 'title'
TOKEN_SHOWCASE_CFGS_DESC: str = 'desc'
TOKEN_SHOWCASE_CFGS_DEFAULT: str = 'default'

TOKEN_SKIP: str = 'skip'

TOKEN_PARAMS: str = 'params'
TOKEN_PARAMS_FIELD: str = 'field'
TOKEN_PARAMS_DATA: str = 'data'

TOKEN_VARS: str = 'vars'
TOKEN_VARS_FIELD: str = 'field'
TOKEN_VARS_DATA: str = 'data'

TOKEN_VERTICES: str = 'vertices'
TOKEN_VERTICES_SKIP: str = 'skip'
TOKEN_VERTICES_DATA: str = 'data'

TOKEN_FACES: str = 'faces'
TOKEN_FACES_SKIP: str = 'skip'
TOKEN_FACES_TEXTURE: str = 'texture'
TOKEN_FACES_INDICES: str = 'indices'
TOKEN_FACES_UVS: str = 'uvs'
TOKEN_FACES_NORMALS: str = 'normals'

TOKEN_INSTANCES: str = 'instances'
TOKEN_INSTANCES_IDENTIFIER: str = 'identifier'
TOKEN_INSTANCES_SKIP: str = 'skip'
TOKEN_INSTANCES_PARAMS: str = 'params'
TOKEN_INSTANCES_TRANSFORM: str = 'transform'

#endregion

class Reporter():
    """
    General reporter commonly used by BME validator.
    """

    def __init__(self):
        pass

    def __report(self, type: str, msg: str, context: str | None) -> None:
        strl: str = f'[{type}]'
        if context is not None:
            strl += f'[{context}]'
        strl += ' ' + msg
        print(strl)

    def error(self, msg: str, context: str | None = None) -> None:
        """
        @brief Report an error.
        @param[in] msg The message to show.
        @param[in] context The context of this message, e.g. the file path. None if no context.
        """
        self.__report('Error', msg, context)

    def warning(self, msg: str, context: str | None = None) -> None:
        """
        @brief Report a warning.
        @param[in] msg The message to show.
        @param[in] context The context of this message, e.g. the file path. None if no context.
        """
        self.__report('Warning', msg, context)

    def info(self, msg: str, context: str | None = None) -> None:
        """
        @brief Report a info.
        @param[in] msg The message to show.
        @param[in] context The context of this message, e.g. the file path. None if no context.
        """
        self.__report('Info', msg, context)

class Hierarchy():
    """
    The hierarchy builder for BME validator to build context string representing the location where error happen.
    And it can be utilized by BME extractor to generate the context of translation.
    """

    __mStack: collections.deque[str]

    def __init__(self):
        self.__mStack = collections.deque()

    def push(self, item: str) -> None:
        """
        @brief Add an item into this hierarchy.
        @param[in] item New added item.
        """
        self.__mStack.append(item)

    def push_index(self, index: int) -> None:
        """
        @brief Add an integral index into this hierarchy.
        @details
        The difference between this and normal push function is that added item is integral index.
        This function will automatically convert it to string with a special format first, then push it into hierarchy.
        @param[in] item New added index.
        """
        self.__mStack.append(f'[{index}]')

    def pop(self) -> None:
        """
        @brief Remove the top item from hierarchy
        """
        self.__mStack.pop()

    def build_hierarchy_string(self) -> str:
        """
        Build the string which can represent this hierarchy.
        @return The built string representing this hierarchy.
        """
        return '/'.join(self.__mStack)

class BMEValidator():
    """
    The validator for BME prototype declarartions.
    This validator will validate given prototype declaration JSON structure,
    to check then whether have all essential fields BME standard required and whether have any unknown fields.
    """

    __mPrototypeSet: set[str]
    __mHierarchy: Hierarchy
    __mReporter: Reporter

    def __init__(self, reporter: Reporter):
        self.__mPrototypeSet = set()
        self.__mHierarchy = Hierarchy()
        self.__mReporter = reporter

    def validate(self, assoc_file: str, prototypes: typing.Any) -> None:
        self.__mHierarchy.push(assoc_file)

        self.__mHierarchy.pop()

class BMEExtractor():
    """
    A GetText extractor for BME prototype declarations.
    This extractor can extract all UI infomations which will be shown on Blender first.
    Then write them into caller given PO file. So that translator can translate them.

    Blender default I18N plugin can not recognise these dynamic loaded content,
    so that's the reason why this class invented.

    Please note all data should be validate first, then pass to this class.
    Otherwise it is undefined behavior.
    """

    __mAssocFile: str
    __mHierarchy: Hierarchy
    __mPoWriter: simple_po.PoWriter

    def __init__(self, po_writer: simple_po.PoWriter):
        self.__mAssocFile = ''
        self.__mHierarchy = Hierarchy()
        self.__mPoWriter = po_writer

    def extract(self, assoc_file: str, prototypes: list[dict[str, typing.Any]]) -> None:
        self.__mAssocFile = assoc_file
        for prototype in prototypes:
            self.__extract_prototype(prototype)

    def __add_translation(self, strl: str) -> None:
        self.__mPoWriter.add_entry(
            strl,
            CTX_TRANSLATION + '/' + self.__mHierarchy.build_hierarchy_string(),
            self.__mAssocFile
        )

    def __extract_prototype(self, prototype: dict[str, typing.Any]) -> None:
        # get identifier first
        identifier: str = prototype[TOKEN_IDENTIFIER]
        self.__mHierarchy.push(identifier)

        # get showcase node and only write PO file if it is not template prototype
        showcase: dict[str, typing.Any] | None = prototype[TOKEN_SHOWCASE]
        if showcase is not None:
            self.__extract_showcase(showcase)

        self.__mHierarchy.pop()

    def __extract_showcase(self, showcase: dict[str, typing.Any]) -> None:
        # export self name first
        self.__add_translation(showcase[TOKEN_SHOWCASE_TITLE])

        # iterate cfgs
        cfgs: list[dict[str, typing.Any]] = showcase[TOKEN_SHOWCASE_CFGS]
        for cfg_index, cfg in enumerate(cfgs):
            self.__extract_showcase_cfg(cfg_index, cfg)

    def __extract_showcase_cfg(self, index: int, cfg: dict[str, typing.Any]) -> None:
        self.__mHierarchy.push_index(index)

        # extract field title and description
        title: str = cfg[TOKEN_SHOWCASE_CFGS_TITLE]
        desc: str = cfg[TOKEN_SHOWCASE_CFGS_DESC]

        # and export them respectively
        self.__add_translation(title)
        self.__add_translation(desc)

        self.__mHierarchy.pop()
