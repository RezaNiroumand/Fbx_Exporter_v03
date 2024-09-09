# 011################################################################################################################# -*- coding:UTF-8 -*-# @date: 13/03/2023# @file: transferOverrides.py# @version:1.3.0# @desctiption: Tool for light memebership/overrides/light_group transfer# @author_"Sumesh Khanana"import osimport maya.mel as melimport xml.etree.ElementTree as ET# from __builtin__ import longfrom PySide2 import QtCore, QtUiTools, QtWidgetsfrom maya import OpenMayaUI as omufrom shiboken2 import wrapInstanceimport maya.cmds as cmdsmainObject = omu.MQtUtil.mainWindow()mayaMainWind = wrapInstance(int(mainObject), QtWidgets.QWidget)# mayaMainWind=wrapInstance()class Fbx_Translator(QtWidgets.QWidget):    def __init__(self, parent=mayaMainWind):        super(Fbx_Translator, self).__init__(parent=parent)        self.setWindowFlags(QtCore.Qt.Window)        self.setWindowTitle('FBX Exporter Tool')        self.resize(600, 30)        self.ui = os.path.abspath(os.path.dirname(__file__) + "/UI/fbx_exporter.ui")        #self.ui = "D:/Sumesh/Python/Fbx_Exporter/UI/fbx_exporter.ui"        loader = QtUiTools.QUiLoader()        ui_file = QtCore.QFile(self.ui)        ui_file.open(QtCore.QFile.ReadOnly)        self.theMainWidget = loader.load(ui_file)        main_layout = QtWidgets.QVBoxLayout()        main_layout.addWidget(self.theMainWidget)        self.setLayout(main_layout)                self.set_edit = self.theMainWidget.findChild(QtWidgets.QLineEdit, 'lineEdit_2')        self.preset_search_edit = self.theMainWidget.findChild(QtWidgets.QLineEdit, 'lineEdit')        self.preset_browse_btn = self.theMainWidget.findChild(QtWidgets.QPushButton, 'pushButton')        self.preset_browse_btn.clicked.connect(self.selectPresetFolder)        self.export_selection_btn = self.theMainWidget.findChild(QtWidgets.QPushButton, 'pushButton_2')        self.export_selection_btn.clicked.connect(self.export_fbx)        self.joints_export_selection_btn = self.theMainWidget.findChild(QtWidgets.QPushButton, 'pushButton_3')        self.joints_export_selection_btn.clicked.connect(self.select_bakeJoints)    def selectPresetFolder(self):        self.presetFolderPath = cmds.fileDialog2(fileMode=1, dialogStyle=2,        fileFilter="fbxexportpreset files (*.fbxexportpreset)",dir = os.path.abspath(os.path.dirname(__file__) +'/Preset'))        if self.presetFolderPath:            self.set_path(self.presetFolderPath)    def selectFbxFolder(self):        self.fbxFolderPath = cmds.fileDialog2(fileMode=3, dialogStyle=2)        if self.fbxFolderPath:            return self.fbxFolderPath[0]    def set_path(self, file_path):        self.preset_search_edit.setText(self.presetFolderPath[0])    def diplay_layers(self):        flag = 0        fbx_file = open(self.fbx_export_path, 'r+')        filedata = fbx_file.readlines()        fbx_file.seek(0)              for i, line in enumerate(filedata):            if line.startswith("	CollectionExclusive:"):                flag = 1            if flag == 0:                fbx_file.write(line)            if line.startswith("	}"):                flag = 0          fbx_file.truncate()        fbx_file.close()    def remove_containers(self):        fbx_file = open(self.fbx_export_path, 'r+')        filedata = fbx_file.readlines()        fbx_file.seek(0)              for i, line in enumerate(filedata):            if line.startswith("	Container:"):                del filedata[i:i + 2]            else:                fbx_file.write(line)        fbx_file.truncate()        fbx_file.close()    def remove_namespaces(self, found_namespace):        fbx_file = open(self.fbx_export_path, 'r+')        filedata = fbx_file.readlines()        fbx_file.seek(0)        for i, line in enumerate(filedata):            if found_namespace in line:                new_line = line.replace(found_namespace+":", '')                fbx_file.write(new_line)            else:                fbx_file.write(line)        fbx_file.truncate()        fbx_file.close()    def find_namespace(self):        self.selection = cmds.ls(sl=1)        self.found_namespace = []        self.namespace_query_list = cmds.namespaceInfo(lon=True,r=True)        for sel in self.selection:            for query_name in self.namespace_query_list:                if query_name in sel:                    if query_name in self.found_namespace:                        pass                    else:                        self.found_namespace.append(query_name)        return self.found_namespace    def export_fbx(self):        self.edit_xml()        self.selected_item = self.preset_search_edit.text()        self.temp_sel = cmds.ls(sl=1)        if self.selected_item:            mel.eval("FBXResetExport;")            mel.eval('FBXLoadExportPresetFile -f "' + self.selected_item + '";')            if self.temp_sel and cmds.objectType(self.temp_sel[0]) == 'joint':                                self.fbx_export_dir = self.selectFbxFolder()                self.fbx_file_name =  self.find_namespace()[0]+'.fbx'                self.fbx_export_path = self.fbx_export_dir+'/'+self.fbx_file_name                mel.eval('FBXExport -f "' + self.fbx_export_path + '" -s;')                self.diplay_layers()                self.remove_containers()                if self.find_namespace():                    self.remove_namespaces(self.find_namespace()[-1])            else:                jnt_dailogue = QtWidgets.QMessageBox()                jnt_dailogue.setWindowTitle("Error")                jnt_dailogue.setText("Please Select Joints")                jnt_button = jnt_dailogue.exec_()        else:            error_dailogue = QtWidgets.QMessageBox()            error_dailogue.setWindowTitle("Error")            error_dailogue.setText("Please Select Presets")            button = error_dailogue.exec_()    # select bakeJoints    def select_bakeJoints(self):        self.edit_xml()        cmds.select(cl=True)        self.sets_name = self.set_edit.text()        object_sets = cmds.ls(type ='objectSet')        joint_sets =[]        self.selected_item = self.preset_search_edit.text()        self.fbx_export_dir = self.selectFbxFolder()         for item in object_sets:            if self.sets_name in item:                joint_sets.append(item)                        for joints in joint_sets:            cmds.select(cl=1)            cmds.select(joints)            for jnt in cmds.ls(sl=1):                cmds.setAttr(jnt+".drawStyle",0)            cmds.select(joints)            self.fbx_file_name =  self.find_namespace()[0]+'.fbx'            self.fbx_export_path = self.fbx_export_dir+'/'+self.fbx_file_name            mel.eval("FBXResetExport;")            mel.eval('FBXLoadExportPresetFile -f "' + self.selected_item + '";')            mel.eval('FBXExport -f "' + self.fbx_export_path + '" -s;')            self.diplay_layers()            self.remove_containers()            if self.find_namespace():                self.remove_namespaces(self.find_namespace()[-1])            cmds.select(cl=1)            cmds.select(joints)            for jnt in cmds.ls(sl=1):                cmds.setAttr(jnt+".drawStyle",2)        # Edit XML    def edit_xml(self):        self.xml_path = self.preset_search_edit.text()        max_frame = cmds.playbackOptions(q=True, max=True)        min_frame = cmds.playbackOptions(q=True, min=True)        self.source_xml = open(self.xml_path)        xml_tree = ET.parse(self.source_xml)        xml_root = xml_tree.getroot()        for xml_child in xml_root.iter('BakeFrameStart'):            xml_child.attrib['v'] = str(int(min_frame))        for xml_child in xml_root.iter('BakeFrameEnd'):            xml_child.attrib['v'] = str(int(max_frame))        xml_tree.write(self.xml_path, xml_declaration=True, method='xml', encoding="utf-8")        self.source_xml.close()