# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AhnDownloaderDockWidget
                                 A QGIS plugin
 Select and download tiled dataset of Dutch elevation maps
                             -------------------
        begin                : 2016-12-18
        git sha              : $Format:%H$
        copyright            : (C) 2016 by gisplein
        email                : info@gisplein.nl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal

FORM_CLASS, _ = uic.loadUiType(os.path.join(
os.path.dirname(__file__), 'ahn_downloader_dockwidget_base.ui'))



class AhnDownloaderDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(AhnDownloaderDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

PopupUI, PopupBase = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'popup_dialog_base.ui'))

class PopupDialog(QtGui.QDialog, PopupUI):
    def __init__(self, parent=None):
        """Constructor."""
        super(PopupDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)


HelpUI, HelpBase = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'help_dialog_base.ui'))

class HelpDialog(QtGui.QScrollArea, HelpUI):
    def __init__(self, parent=None):
        """Constructor."""
        super(HelpDialog, self).__init__(parent)
        self.setupUi(self)