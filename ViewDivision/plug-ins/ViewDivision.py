import sys
import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om

def maya_useNewAPI():
    pass

# try:
#     import cv2
# except:
#     cmds.error('OpenCVがインポートできませんでした。')

class ViewDivisionCmd(om.MPxCommand):
    kPluginCmdName = "viewDivision"
    def __init__(self):
        om.MPxCommand.__init__(self)
        self.camera = ''
        self.horizontal = 3
        self.vertical = 3

    @staticmethod
    def cmdCreator():
        return ViewDivisionCmd()

    @staticmethod
    def createSyntax():
        syntax = om.MSyntax()
        syntax.addFlag('-c', '-camera', om.MSyntax.kString)
        syntax.addFlag('-h', '-horizontal', om.MSyntax.kLong)
        syntax.addFlag('-v', '-vertical', om.MSyntax.kLong)
        return syntax

    def doIt(self, args):
        try:
            argData = om.MArgParser(self.syntax(), args)
            if argData.isFlagSet('-c'):
                self.camera = argData.flagArgumentString('-c', 0)
            if argData.isFlagSet('-h'):
                self.horizontal = argData.flagArgumentInt('-h', 0)
            if argData.isFlagSet('-v'):
                self.vertical = argData.flagArgumentInt('-v', 0)
            self.redoIt()
        except:
            cmds.warning('エラーが発生しました。')

    def redoIt(self):
        active_panel = cmds.getPanel(withFocus=True)
        print(str(active_panel))

    # def undoIt(self):

    # def isUndoable(self):
        # return True

def initializePlugin(plugin):
    vendor = "Kakoi Keisuke"
    version = "1.0.0"
    pluginFn = om.MFnPlugin(plugin, vendor, version)

    try:
        pluginFn.registerCommand(
            ViewDivisionCmd.kPluginCmdName,
            ViewDivisionCmd.cmdCreator,
            ViewDivisionCmd.createSyntax
        )
    except:
        sys.stderr.write('コマンドの登録に失敗しました。')
    try:
        create_ui()
    except:
        sys.stderr.write('メニューの作成に失敗しました。')

def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.deregisterCommand(ViewDivisionCmd.kPluginCmdName)
    except:
        sys.stderr.write('コマンドの除去に失敗しました')
    try:
        delete_ui()
    except:
        sys.stderr.write('メニューの削除に失敗しました。')

def create_ui():
    main_window = mel.eval('$gmw = $gMainWindow')
    if cmds.menu('ViewDivision', exists=True):
        cmds.deleteUI('ViewDivision')
    custom_menu = cmds.menu('ViewDivision', parent=main_window)
    cmds.menuItem(
        label='分割線を配置',
        parent=custom_menu,
        command=lambda x: new_window_for_view_division(),
        image='ViewDivisionMenuItemIcon.svg',
        annotation='カメラに分割線のイメージプレーンを接続します。'
    )

def delete_ui():
    if cmds.menu('ViewDivision', exists=True):
        cmds.deleteUI('ViewDivision')

def new_window_for_view_division():
    if cmds.window('viewDivisionWindow', exists=True):
        cmds.deleteUI('viewDivisionWindow')

    window = cmds.window(
        'viewDivisionWindow',
        title='分割線イメージプレーンの作成',
        widthHeight=(500, 500)
    )
    cmds.showWindow(window)