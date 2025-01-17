# Import and Export Virtools Document

!!! info "Not latest version"
    This translated page is not the latest version because the modification of source page. Please see source page of the latest version.

!!! warning "This is experimental content"
    Native importing and exporting of Virtools documents is experimental content for the BBP plugin, it may have many problems, see the [Report Issue](./report-bugs.md) section to learn more. When problems are encountered, please report them. the authors of the BBP plugin are not responsible for any consequences resulting from problems with the BBP plugin.

## Import Virtools File

Virtools files can be imported by clicking `File - Import - Virtools File`. Importing supports CMO, VMO and NMO files. Clicking on it will bring up the file opening window and show the import settings in the sidebar. First of all, you need to select the Virtools file to be imported, and then configure the import settings in the sidebar. After configuring the import settings, you can click Import to start the import, and wait for the status bar at the bottom of Blender to indicate that the import is complete.

### Conflict Options

The Conflict Options section indicates what to do when the importer encounters duplicate object names. There are 4 levels, for Object, Mesh, Material and Texture. There are 2 ways to handle it: Rename and Use Current. When Rename is selected and a duplicate name is encountered, a suffix will be added to the name to make it unique. By choosing Use Current, the import of the item from the file will be ignored and the item with the same name will be used instead, which already exists in the Blender document.

!!! info "Differences from Virtools conflict resolution"
    Compared to the conflict resolution dialog in Virtools, the conflict resolution options provided by the BBP plugin do not support replacement, and the granularity is not fine-tuned to individual instances, but only for an entire type. So you can't set a different conflict resolution for each instance of a conflict individually. However, this setting is sufficient for most scenarios.

The default values for the options in the Conflict Options section are the solutions that are usually selected for import. Of course, special settings are needed for special import situations, e.g. if you are importing an externally exported element model from the original version, you may be able to use Use Current option in material options instead of making a copy. The correct use of the conflict options is a matter of mapping experience and is not taught in this manual.

### Virtools Params

It is well known that Virtools uses a system-based multi-byte character encoding to process documents, and is therefore prone to what is known as garbling; Blender itself does not suffer from garbling, however, if we do not read a Virtools document with the correct encoding, the characters stored in it may still appear garbled when the Virtools document is imported into Blender. The Encodings property in the Virtools Params section specifies the encodings for reading Virtools documents. Multiple encodings can be specified, separated by a `;` (semicolon). Some common encodings are listed below:

* cp1252: Western European encoding used by Ballance.
* gbk: The default encoding for Chinese Windows system.

The encoding attribute is very important. If the wrong encoding is set, the names of the various objects imported into Blender will be unrecognizable, or will cause the program to make an error.

!!! info "What encodings are available?"
    Since BBP version 4.1, the names of the encodings we use are basically just copied from the Python encoding names. Most of the commonly used encoding names in Most of the commonly used encoding names in Python are mapped, with only a few particularly rare encodings unsupported, and for specific supported encodings it is necessary to check the source code. See [Python documentation](https://docs.python.org/3/library/codecs.html#standard-encodings) for information on Python's supported encodings. Encodings are not case-sensitive.

!!! warning "Warning about migration from older versions"
    Starting with BBP version 4.1, the version number of LibCmo, the underlying library used by BBP's Virtools document import module, has been bumped to 0.2. Before this version, the encoding attribute was a platform-dependent setting. Under Windows, the [Windows Code Page](https://learn.microsoft.com/en-us/windows/win32/intl/code-page-identifiers) number is required here. Under other operating systems, LibCmo uses iconv for character encoding decoding, so the legal [iconv encoding identifier](hhttps://www.gnu.org/software/libiconv/) is required.

    This all changed with LibCmo 0.2, from which LibCmo uses Python-like universal encoding names. It is platform-independent, you no longer need to check whether the operating system you are using is Windows or Linux, the encoded characters are the same string for all platforms. This also means that if you have customized your encoding settings before, you need to be careful to convert them to the new universal encoding name, because the old encoding name may not have a corresponding mapping under the universal encoding name system, for example, `1252` specified on Windows before should be written as `cp1252` under the new universal encoding name, and the original encoding name won't be recognized correctly on the new system.

## Export Virtools File

Virtools files can be exported by clicking `File - Export - Virtools File`. Clicking on it will bring up the file opening window and show you the export settings in the sidebar. First of all, you need to select the location of the exported Virtools file, then configure the export settings in the sidebar, after configuring the export settings, you can click Export to start the export, and wait for the status bar at the bottom of Blender to indicate that the export is complete.

### Export Target

The Export Target section is used to determine which objects you need to export to a Virtools document. You can choose to export a collection or an object and select the corresponding collection or object below. Note that selecting a collection will export the objects in the internal collection as well, i.e. exporting nested collections is supported.

### Virtools Params

The Virtools Params section is similar to the one in the importing Virtools document; the Encodings property determines the encoding used when exporting a Virtools document.

The Global Texture Save Option determines how textures that are set to Use Global are actually saved. In general, setting it to Raw Data will 100% guarantee that the saved Virtools document will contain the correct texture, but it may be larger, while setting it to External will minimize the size of the file, but there may be problems with the exported document not finding the texture file. We recommend that you specify how each material should be saved individually when you set it up, rather than relying on the global option to set it up. This option is for re-editing old maps that rely on the Global Texture Saving Option. It should also be noted that even though there is a Use Global option in this option, please **don't** select it or it will result in an error, because obviously you can't have a global option that then uses the global option's settings.

The Use Compress property specifies whether saved documents are stored compressed. Compression can significantly reduce the size of a document, and on modern computer platforms, the performance loss caused by compression is almost negligible. When Use Compress is selected, an additional Compress Level attribute is displayed, which specifies the level of compression; the higher the value, the greater the compression rate and the smaller the file.

### Ballance Params

The Ballance Params section contains parameters that optimize the export process for Ballance-specific content.

Successive Sector is an option to work around a bug that occurs when exporting groups of sectors. For some reason, if there are no elements in a sector (actually, no objects are grouped in a sector group), the export plugin thinks that the sector group doesn't exist and misses the export. And since Ballance determines the final sector, i.e. the sector where the spaceships appears, by incrementing the number of sectors from 1 to the last sector group that exists, the combination of the two causes Ballance to incorrectly determine the number of sectors in the map, and thus display the spaceships in the wrong sector, which is an export bug. when this option is checked, the exported document will be pre-defined according to the number of sectors specified in the Ballance Map information in the current Blender file. When this option is checked, the exported document will pre-create all of the sectors according to the number of sectors specified in the Ballance map information in the current Blender file before exporting, so that you don't miss creating some sector groups, and the spaceships will be displayed in the correct sectors.

This option is usually checked when exporting playable maps, if you just want to export some models then you need to turn this option off, otherwise it will create a lot of useless sector groups in the final file.
