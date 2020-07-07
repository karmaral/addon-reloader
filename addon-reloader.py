bl_info = {
    "name": "Addon Reloader",
    "description": "Save all the hassle of opening Preferences a thousand times when reloading your addon for testing.",
    "author": "Amaral Krichman",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Global/Text Editor",
    "warning": "",
    "wiki_url": "",
    "category": "Development",
}
import bpy
import time

from pathlib import Path
from bpy_extras.io_utils import ImportHelper


#----------------------------------- RELOAD ADDON -----------------------------------    
class ReloadAddonOperator(bpy.types.Operator):
    bl_idname = "wm.addon_reload"
    bl_label = "Reload Addon"
    bl_options = {'REGISTER'}

    def clean_path(self, context):
        p = context.preferences.addons[__name__].preferences.bookmark
        name = Path(p).stem
        return name

    def execute(self, context):
        p = context.preferences.addons[__name__].preferences.bookmark
        name = self.clean_path(context)
        
        bpy.ops.preferences.addon_disable(module=name)
        time.sleep(0.05)
        bpy.ops.preferences.addon_remove(module=name)
        time.sleep(0.05)
        bpy.ops.preferences.addon_install(filepath=p)
        time.sleep(0.05)
        bpy.ops.preferences.addon_enable(module=name)
        time.sleep(0.05)
        return {'FINISHED'}

    def invoke(self, context, event):
        if context.preferences.addons[__name__].preferences.bookmark == "":
            bpy.ops.wm.microwave_select_addon_path('INVOKE_DEFAULT')
            self.execute(context)
            return {'FINISHED'}
        else:
            self.execute(context)
            return {'FINISHED'}
        

#----------------------------------- FILEBROWSER -----------------------------------
class SelectAddonPathFileBrowser(bpy.types.Operator, ImportHelper):
    bl_idname = "wm.addon_reloader_select_addon_path"
    bl_label = "Select Addon Path"
    
    filter_glob: bpy.props.StringProperty( default='*py', options={'HIDDEN'} )

    def execute(self, context):
        context.preferences.addons[__name__].preferences.bookmark = self.filepath
        self.report({'INFO'}, "Selected file: " + self.filepath)
        return {'FINISHED'}

#----------------------------------- PANEL -----------------------------------
class AddonReloaderPanel(bpy.types.Panel):
    bl_label = "Addon Reloader"
    bl_idname = "TEXT_PT_addon_reloader"
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Dev"

    def draw(self, context):
        bk = context.preferences.addons[__name__].preferences.bookmark
        bk_n = Path(bk).stem

        layout = self.layout
        row = layout.row()
        if bk == "":
            row.alignment = 'CENTER'
            row.label(text="Select an addon!", icon='ERROR')
        else:
            layout.label(text="Editing: {}".format(bk_n), icon='INFO')

        if bk == "":
            col = layout.column()
            col.operator("wm.addon_reloader_select_addon_path", text="", icon='FILEBROWSER')
            col.scale_y = 2
        else:
            row = layout.row(align=True)
            row.operator("wm.addon_reload", text="Reload Addon", icon='FILE_REFRESH')
            row.operator("wm.addon_reloader_select_addon_path", text="", icon='FILEBROWSER')
            row.scale_y = 2

        layout.operator("screen.userpref_show",text="", icon='PREFERENCES')
        
#----------------------------------- PREFERENCES -----------------------------------  
class AddonReloaderPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    bookmark: bpy.props.StringProperty(name="Selected Addon's Path", options={'TEXTEDIT_UPDATE'}, default="")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Path to addon is: ")
        row = layout.row()
        if self.bookmark == "":
            row.label(text="No path selected!")
            row = layout.row()
            row.operator("wm.addon_reloader_select_addon_path", text="Select Addon's Path")
        else:
            row.label(text=self.bookmark)
            row = layout.row()
            row.operator("wm.addon_reloader_select_addon_path", text="Change Addon's Path")

#####################################################################

classes = (
    ReloadAddonOperator,
    SelectAddonPathFileBrowser,
    AddonReloaderPanel,
    AddonReloaderPreferences,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)
        


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
