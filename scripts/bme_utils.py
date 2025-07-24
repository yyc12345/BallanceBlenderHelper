import typing
import collections
import termcolor

class Reporter():
    """
    General reporter with context support for convenient logging.
    """

    def __init__(self):
        pass

    def __report(self, type: str, msg: str, context: str | None, color: str) -> None:
        # build message
        strl: str = f'[{type}]'
        if context is not None:
            strl += f'[{context}]'
        strl += ' ' + msg
        # output with color
        termcolor.cprint(strl, color)

    def error(self, msg: str, context: str | None = None) -> None:
        """
        @brief Report an error.
        @param[in] msg The message to show.
        @param[in] context The context of this message, e.g. the file path. None if no context.
        """
        self.__report('Error', msg, context, 'red')

    def warning(self, msg: str, context: str | None = None) -> None:
        """
        @brief Report a warning.
        @param[in] msg The message to show.
        @param[in] context The context of this message, e.g. the file path. None if no context.
        """
        self.__report('Warning', msg, context, 'yellow')

    def info(self, msg: str, context: str | None = None) -> None:
        """
        @brief Report a info.
        @param[in] msg The message to show.
        @param[in] context The context of this message, e.g. the file path. None if no context.
        """
        self.__report('Info', msg, context, 'white')

class Hierarchy():
    """
    The hierarchy for BME validator and BME extractor.
    In BME validator, it build human-readable string representing the location where error happen.
    In BME extractor, it build the string used as the context of translation.
    """

    __mStack: collections.deque[str]

    def __init__(self):
        self.__mStack = collections.deque()

    def push(self, item: str | int) -> None:
        """
        @brief Add an item into the top of this hierarchy.
        @details
        If given item is string, it will be push into hierarchy directly.
        If given item is integer, this function will treat it as a special case, the index.
        Function will push it into hierarchy after formatting it (add a pair of bracket around it).
        @param[in] item New added item.
        """
        if isinstance(item, str):
            self.__mStack.append(item)
        elif isinstance(item, int):
            self.__mStack.append(f'[{item}]')
        else:
            raise Exception('Unexpected type of item when pushing into hierarchy.')

    def pop(self) -> None:
        """
        @brief Remove the top item from hierarchy
        """
        self.__mStack.pop()

    def safe_push(self, item: str | int) -> 'HierarchyLayer':
        """
        @brief The safe version of push function.
        @return A with-context-supported instance which can make sure pushed item popped when leaving scope.
        """
        return HierarchyLayer(self, item)

    def clear(self) -> None:
        """
        @brief Clear this hierarchy.
        """
        self.__mStack.clear()

    def depth(self) -> int:
        """
        @brief Return the depth of this hierarchy.
        @return The depth of this hierarchy.
        """
        return len(self.__mStack)

    def build_hierarchy_string(self) -> str:
        """
        @brief Build the string which can represent this hierarchy.
        @details It just join every items with `/` as separator.
        @return The built string representing this hierarchy.
        """
        return '/'.join(self.__mStack)

class HierarchyLayer():
    """
    An with-context-supported class for Hierarchy which can automatically pop item when leaving scope.
    This is convenient for keeping the balance of Hierarchy (avoid programmer accidently forgetting to pop item).
    """
    
    __mHasPop: bool
    __mAssocHierarchy: Hierarchy

    def __init__(self, assoc_hierarchy: Hierarchy, item: str | int):
        self.__mAssocHierarchy = assoc_hierarchy
        self.__mHasPop = False
        self.__mAssocHierarchy.push(item)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def close(self) -> None:
        if not self.__mHasPop:
            self.__mAssocHierarchy.pop()
            self.__mHasPop = True

    def emplace(self, new_item: str | int) -> None:
        """
        @brief Replace the content of top item in-place.
        @details
        In some cases, caller need to replace the content of top item.
        For example, at the beginning, we only have index info.
        After validating something, we can fetching a more human-readable info, such as name,
        now we need replace the content of top item.
        @param[in] new_item The new content of top item.
        """
        self.__mAssocHierarchy.pop()
        self.__mAssocHierarchy.push(new_item)
