import os
import sys

import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om

def maya_useNewAPI():
    pass

try:
    import numpy as np
except:
    cmds.error('NumPyがインポートできませんでした。')

try:
    import cv2
except:
    cmds.error('OpenCVがインポートできませんでした。')

class ViewDivisionCmd(om.MPxCommand):
    kPluginCmdName = "viewDivision"
    def __init__(self):
        om.MPxCommand.__init__(self)
        self.camera = 'perspShape'
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
        width_resolution = cmds.getAttr("defaultResolution.width")
        height_resolution = cmds.getAttr("defaultResolution.height")
        camera_shape = self.camera
        horizontal_division = self.horizontal
        vertical_division = self.vertical

        width_division_pixel = int(width_resolution / horizontal_division)
        height_division_pixel = int(height_resolution / vertical_division)

        img = np.zeros((height_resolution, width_resolution, 4), dtype=np.uint8)

        for i in range(vertical_division - 1):
            img[height_division_pixel * (i + 1), :, :4] = 255
        for j in range(horizontal_division - 1):
            img[:, width_division_pixel * (j + 1), :4] = 255
        sourceimages_path = cmds.workspace(query=True, rootDirectory=True) + 'sourceimages/'
        if not os.path.exists(sourceimages_path):
            cmds.error('プロジェクトフォルダ内にsourceimagesフォルダが存在しないため, 中断しました。')
        try:
            cv2.imwrite(sourceimages_path + 'ViewDivisionImagePlane.png', img)
        except:
            cmds.error('イメージプレーン画像の生成に失敗したため, 中断しました。')
            sys.exit()

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
        widthHeight=(300, 100)
    )
    cmds.columnLayout()
    cmds.optionMenu(
        'camera_option_menu',
        label='接続するカメラ'
    )
    camera_list = cmds.ls(cameras=True)
    for i in range(len(camera_list)):
        cmds.menuItem(label=camera_list[i])
    cmds.intSliderGrp(
        'horizontal_slider',
        label='水平方向の分割数',
        field=True,
        minValue=1,
        maxValue=10,
        value=3,
        step=1
    )
    cmds.intSliderGrp(
        'vertical_slider',
        label='垂直方向の分割数',
        field=True,
        minValue=1,
        maxValue=10,
        value=3,
        step=1
    )
    cmds.button(
        label='適用',
        command=lambda x:get_ui_value()
    )

    cmds.showWindow(window)

    def get_ui_value():
        camera = cmds.optionMenu('camera_option_menu', query=True, value=True)
        horizontal = cmds.intSliderGrp('horizontal_slider', query=True, value=True)
        vertical = cmds.intSliderGrp('vertical_slider', query=True, value=True)
        cmds.viewDivision(camera=camera, horizontal=horizontal, vertical=vertical)