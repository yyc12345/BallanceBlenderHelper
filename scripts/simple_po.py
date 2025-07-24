import typing
import io
import datetime

class PoWriter():
    """
    The simple PO file writer.
    This class is just served for writing POT files.
    It may be convenient when exporting PO file for thoese whose format can not be parsed by formal tools.
    """

    __cEscapeCharsDict: typing.ClassVar[dict[str, str]] = {
        '\\': '\\\\',
        '"': '\\"',
        '\n': '\\n',
        '\t': '\\t',
    }
    __cEscapeCharsTable: typing.ClassVar[dict] = str.maketrans(__cEscapeCharsDict)
    __mPoFile: io.TextIOWrapper

    def __init__(self, po_file_path: str, project_name: str):
        # open file
        self.__mPoFile = open(po_file_path, 'w', encoding = 'utf-8')
        # add default header
        self.__add_header(project_name)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def close(self) -> None:
        self.__mPoFile.close()

    def __write_line(self, val: str) -> None:
        self.__mPoFile.write(val)
        self.__mPoFile.write('\n')

    def __escape_str(self, val: str) -> str:
        """
        This function escapes a given string to make it safe to use as a C++ string literal.
        @param[in] val Original string
        @return Escaped string
        """
        return val.translate(PoWriter.__cEscapeCharsTable)

    def __add_header(self, project_name: str) -> None:
        """
        Add default header for PO file.
        @param[in] project_name The project name written in file.
        """
        now_datetime = datetime.datetime.now()
        self.__write_line('# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.')
        self.__write_line('msgid ""')
        self.__write_line('msgstr ""')
        self.__write_line(f'"Project-Id-Version: {self.__escape_str(project_name)}\\n"')
        self.__write_line(f'"POT-Creation-Date: {now_datetime.strftime("%Y-%m-%d %H:%M%Z")}\\n"')
        self.__write_line('"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"')
        self.__write_line('"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"')
        self.__write_line('"Language-Team: LANGUAGE <LL@li.org>\\n"')
        self.__write_line('"Language: __POT__\\n"')
        self.__write_line('"MIME-Version: 1.0\\n"')
        self.__write_line('"Content-Type: text/plain; charset=UTF-8\\n"')
        self.__write_line('"Content-Transfer-Encoding: 8bit\\n"')
        self.__write_line('"X-Generator: simple_po.PoWriter\\n"')

    def add_entry(self, msg: str, msg_context: str | None = None, extracted_comment: str | None = None, reference: str | None = None) -> None:
        """
        @brief Write an entry into PO file with given arguments.
        @details
        Please note this function will NOT check whether there already is a duplicated entry which has been written.
        You must check this on your own.
        @param[in] msg The message string need to be translated.
        @param[in] msg_context The context of this message.
        @param[in] extracted_comment The extracted comment of this message. None if no reference. Line breaker is not allowed.
        @param[in] reference The code refernece of this message. None if no reference. Line breaker is not allowed.
        """
        # empty string will not be translated
        if msg == '': return

        # write blank line first
        self.__write_line('')
        if extracted_comment:
            self.__write_line(f'#. {extracted_comment}')
        if reference:
            self.__write_line(f'#: {reference}')
        if msg_context:
            self.__write_line(f'msgctxt "{self.__escape_str(msg_context)}"')
        self.__write_line(f'msgid "{self.__escape_str(msg)}"')
        self.__write_line('msgstr ""')

    def build_code_reference(self, code_file_path: str, code_line_number: int) -> str:
        """
        A convenient function to build code reference string used when adding entry.
        @param[in] code_file_path The path to associated code file.
        @param[in] code_line_number The line number of associated code within given file.
        """
        return f'{code_file_path}:{code_line_number}'
