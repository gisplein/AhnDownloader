# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AhnDownloader
                                 A QGIS plugin
 Deze plugin kan gebruikt worden om op eenvoudige wijze de juiste kaartbladen van de AHN op te halen.
                              -------------------
        begin                : 2016-12-10
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Michiel Bootsma / GISplein
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
import worker

# Import the code for the dialog
from ahn_downloader_dockwidget import AhnDownloaderDockWidget
from ahn_downloader_dockwidget import PopupDialog
from ahn_downloader_dockwidget import HelpDialog

import os.path
from os.path import expanduser

import traceback
import urllib

import zipfile
import webbrowser
from worker import Worker

from qgis.gui import *
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *


# for new download function
import urllib2
from urllib2 import urlopen, URLError, HTTPError

class AhnDownloader:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.tmplayer = None
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'AhnDownloader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&AhnDownloader')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'AhnDownloader')
        self.toolbar.setObjectName(u'AhnDownloader')

        self.pluginIsActive = False
        self.dockwidget = None


  #      self.dockwidget = AhnDownloaderDockWidget()
  #      self.popup = PopupDialog()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('AhnDownloader', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        # Create the dialog (after translation) and keep reference
        # @        self.dlg = AhnDownloaderDialog()
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def f_connect_widgets(self):
        # self.popup = PopupDialog()
        # fill combo's
        self.popup.combo_service.clear()
        self.popup.combo_version.clear()
        services = ["WFS","WMS","WCS"]
        self.popup.combo_service.addItems(services)
        versions=["1.0.0","1.1.1","1.2.0","1.3.0"]
        self.popup.combo_version.addItems(versions)

        # fill combo's
        self.popup.combo_service.clear()
        self.popup.combo_version.clear()
        services = ["WFS","WMS","WCS"]
        self.popup.combo_service.addItems(services)
        versions=["1.0.0","1.1.1","1.2.0","1.3.0"]
        self.popup.combo_version.addItems(versions)

        legend = self.iface.legendInterface()

        self.dockwidget.pb_help.clicked.connect(self.f_help)
        self.dockwidget.pb_cancel.clicked.connect(self.f_cancel)
        self.dockwidget.pb_ok.clicked.connect(self.f_ok)
        self.dockwidget.pb_afsluiten.clicked.connect(self.f_afsluiten)

        self.dockwidget.pb_close.clicked.connect(self.f_cancel)
        self.dockwidget.pb_reset.clicked.connect(self.f_reset)

        self.dockwidget.pb_connect.clicked.connect(self.f_connect)
        self.dockwidget.pb_new.clicked.connect(self.f_addwfs)
        self.dockwidget.pb_edit.clicked.connect(self.f_edit)
        self.dockwidget.pb_delete_wfs.clicked.connect(self.f_delete_wfs)


        self.dockwidget.pb_folder.clicked.connect(self.select_output_file)
        self.dockwidget.pb_delete.clicked.connect(self.f_delete_url)
        self.dockwidget.pb_gisplein.clicked.connect(self.f_followLink)

#        self.dockwidget.combo_wfs.activated.connect(self.f_select_wfs)
        self.dockwidget.combo_layer.setFilters(QgsMapLayerProxyModel.HasGeometry)



## connection popup dialog
       # self.popup.le_name.textChanged.connect(self.f_changed)
        self.popup.le_name.textEdited.connect(self.f_changed)
        self.popup.le_url.textEdited.connect(self.f_changed)
        self.popup.le_request.textEdited.connect(self.f_changed)
        self.popup.le_typename.textEdited.connect(self.f_changed)
        self.popup.le_srsname.textEdited.connect(self.f_changed)

        #kbuttons popup
        self.popup.pb_save.clicked.connect(self.f_save)
        self.popup.pb_cancel.clicked.connect(self.f_cancel_popup)


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/AhnDownloader/img/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Download AHN tiles'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING AhnDownloader"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False
        self.f_reset()


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD AhnDownloader"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&ahndownloader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

###############################################################################################
##                                                   < END standard functions Dockwidget     ##
###############################################################################################


    def f_connect(self):
        data = self.f_getrecord(self.base_folder + "\config\wfs.txt",self.dockwidget.combo_wfs.currentIndex())
        params = {}
        params.update({'request': data[2]})
        params.update({'typename': data[3]})
        params.update({'srsname': data[4]})
        params.update({'service': data[5]})
        params.update({'version': data[6]})

        uri =data[1]+ urllib.unquote(urllib.urlencode(params))

        vlayer = QgsVectorLayer(uri, data[0], "WFS")

        QgsMapLayerRegistry.instance().addMapLayer(vlayer)


    def f_help(self):
        self.help.show()


    def f_addwfs(self):
        self.f_clearpopup()
        self.popup.recno=-1
        self.popup.show()

    def f_save(self):
        valid, rec=self.f_saverecord(self.base_folder+"\config\wfs.txt",self.popup)
        if valid == True:
            self.popup.close()
            self.f_reset_color(self.popup)
            a = self.f_update_combo(rec)





    def f_delete_wfs(self):
        reply = QMessageBox.question(None, 'Message',"Are you sure to delete service: "+self.dockwidget.combo_wfs.currentText()+"?", QMessageBox.Yes, QMessageBox.No)

        if reply==QMessageBox.No:
            return

        self.f_clearpopup()
        filename = self.base_folder+"\config\wfs.txt"
        file = open(filename, 'r')
        var = []
        for line in file:
            var.append(line.strip().split(","))
        file.close()

        file2 = open(filename, 'w')
        new_line = ""
        for n in var:
            if (self.dockwidget.combo_wfs.currentText()!=n[0].strip('"')):
                for item in n:
                     if (len(new_line)>0):
                         new_line=new_line + ','
                     new_line = new_line +item
                file2.write(new_line + "\n")
                new_line=""

        file2.close()
        self.f_update_combo(0)



###############################################################################################
##  BEGIN custom functions WORKER                                                            ##
###############################################################################################

    def startWorker(self, dialog, laag,veld,url,folder, unzip):

        self.canvas = self.iface.mapCanvas()
        self.proj=laag.crs().authid()
        # TMP layer aanmaken
        tmplayer = QgsVectorLayer("Polygon" + "?crs=" + self.proj, "temp_index", "memory")

        # create a new worker instance
        worker = Worker(laag,veld,url,folder, unzip, dialog,tmplayer)
        # verbindt de cancel button met killmethode

        self.dockwidget.pb_cancel.clicked.connect(worker.kill)
        #self.dockwidget.button_box.rejected.connect(worker.kill)

        # start the worker in a new thread
        thread = QThread() #self
        worker.moveToThread(thread)
        worker.finished.connect(self.workerFinished)
        # worker.tmplayer.connect(self.workerTmpLayer)
        worker.error.connect(self.workerError)

        worker.progress.connect(dialog.progressBar.setValue)
        #worker.progress.connect(progressBar.setValue)
        thread.started.connect(worker.run)
        thread.start()

        self.thread = thread
        self.worker = worker




    def workerFinished(self, ret,vl):
        # clean up the worker and thread
        answer = ""

        for r in ret:
            answer = answer + r[0].rstrip() +" -> "+ r[1].rstrip() +" : "+ r[2].rstrip() +"\n"

        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()

        if ret is not None:
            # report the result
            # layer, files = ret
            self.dockwidget.textBrowser_results.setText(answer)
            self.dockwidget.tabWidget.setCurrentIndex(1)
            self.dockwidget.tabWidget.setTabEnabled(0,False)
            self.dockwidget.pb_ok.setEnabled(True)
            #self.dockwidget.close()

            self.canvas = self.iface.mapCanvas()
            QgsMapLayerRegistry.instance().addMapLayer(vl)
            # self.canvas.setExtent(vl.extent())

            vl.loadNamedStyle(self.base_folder + '\\config\\result.qml')

            self.canvas.refresh()

        else:
            # notify the user that something went wrong
            self.dockwidget.textBrowser_results.setText('Something went wrong! See the message log for more information.')
            self.dockwidget.tabWidget.setTabEnabled(0,False)
            self.dockwidget.tabWidget.setCurrentIndex(1)


    def workerError(self, e, exception_string):
        QgsMessageLog.logMessage('Worker thread raised an exception:\n'.format(exception_string))
        QMessageBox.information(None, "resultaat",'Worker thread raised an exception:\n'.format(exception_string))


###############################################################################################
##                                                          < END custom functions WORKER    ##
###############################################################################################

    def f_clearall(self):
        self.dockwidget.pb_ok.setEnabled(True)
        self.dockwidget.tabWidget.setCurrentIndex(0)
        self.dockwidget.tabWidget.setTabEnabled(0, True)
        self.dockwidget.textBrowser_results.setText("")
        self.dockwidget.lineEdit_2.setText("")
        self.dockwidget.cb_unzip.setChecked(False)
        self.dockwidget.progressBar.setValue(0)
    #    self.dockwidget.combo_layer.clear()
    #    self.dockwidget.combo_field.clear()

    def f_herstart(self):
        self.dockwidget.pb_ok.setEnabled(True)


    def select_output_file(self):
        foldername = QFileDialog.getExistingDirectory(self.dockwidget, "select folder for downloads", expanduser("~"),
                                                      QFileDialog.ShowDirsOnly)
        #        foldername = QFileDialog.getSaveFileName(self.dockwidget, "Select output file ","", '*.txt')
        self.dockwidget.lineEdit_2.setText(foldername)

    def f_followLink(self):
        # open browser en volg link
        new = 2  # open in a new tab, if possible

        # open a public URL, in this case, the webbrowser docs
        url = "http://www.gisplein.nl"
        webbrowser.open(url, new=new)

        # open an HTML file on my own (Windows) computer
        # url = "file://X:/MiscDev/language_links.html"
        # webbrowser.open(url, new=new)

    def f_afsluiten(self):
        # nadat bestanden zijn opgehaald wordt tool afgesloten
        a=self.f_clearall()
        self.dockwidget.close()

    def f_cancel_popup(self):
        self.popup.close()
        self.f_reset_color(self.popup)


    def f_cancel(self):
        # some code for your algorithm
        # connections worden in de dialog class gemaakt regel 200)
        a=self.f_clearall()
        self.dockwidget.close()

    def f_reset(self):

        a=self.f_clearall()
        a = self.f_update_combo(0)
        self.popup.recno = 0




    def f_ok(self):
        # some code for your algorithm
        # wordt uitgevoerd zodra op OK wordt gedrukt
        # eerst enkele controles of alle waarden beschikbaar zijn
        self.dockwidget.pb_ok.setEnabled(False)
        if self.dockwidget.combo_layer.count() == 0:
            QMessageBox.information(None, "warning", "No layer selected")
            a=self.f_herstart()
            #self.dockwidget.show()
            self.dockwidget.combo_layer.setFocus()
            return

        if self.dockwidget.combo_field.currentText() == "":
            QMessageBox.information(None, "warning", "No field selected")
            a=self.f_herstart()
            self.dockwidget.combo_field.setFocus()
            return

#wijzigingen in url combo worden altijd bewaard, maar kunnen ook altijd worden verwijderd
        a = self.f_update_urls()
        #a = self.f_update_combo(0)

        self.dockwidget.progressBar.setValue(0)

        layers = self.iface.legendInterface().layers()

        for layer in layers:
            if layer.name() == self.dockwidget.combo_layer.currentText():
                laag = layer
                break

        for field in layer.pendingFields():
            if field.name() == self.dockwidget.combo_field.currentText():
                veld = field.name()
                break

        # start hoofdproces en stuur complete dialog mee
        folder = self.dockwidget.lineEdit_2.text()
        if not os.path.isdir(folder):
            QMessageBox.information(None, "warning!",'destination folder does not exist')
            a=self.f_herstart()
            self.dockwidget.lineEdit_2.setFocus()
            return

        url = self.dockwidget.comboBox.currentText()
        if not "[ifield]" in url:
            QMessageBox.information(None, "warning",'given url does not contain wildcart "[ifield]"')
            a=self.f_herstart()
            self.dockwidget.comboBox.setFocus()
            return

        if self.dockwidget.cb_unzip.isChecked():
            unzip = 1
        else:
            unzip = 0

        features = layer.selectedFeatures()
        feature_count = layer.featureCount()
        feature_count_selected=layer.selectedFeatureCount()

        if (feature_count_selected < 1):
            QMessageBox.information(None, "warning",'No features selected')
            a=self.f_herstart()
            return

        a = self.startWorker(self.dockwidget, laag, veld, url, folder, unzip)


        ###############################################################################################
        ##  Start custom methods COMBOBOX >                                                          ##
        ###############################################################################################

    def f_select_layer(self):
        QMessageBox.information(None, "Aantal Lagen", "f_select_layer")


    def f_populate_layer(self):
        QMessageBox.information(None, "Aantal Lagen", "f_polulate layer")


    def f_update_urls(self):
        # schrijft alle aanpassingen in de combo naar configuratiefile

        fname = self.base_folder + "\config\urls.txt"
        if os.path.isfile(fname):
            # QMessageBox.information(None, "fname",fname)
            os.remove(fname)  # remove the current file, otherwise create just a new one.
        f = open(fname, 'w')
        new = 1
        for url in self.url_list:
            if (self.dockwidget.comboBox.currentText() == url):
                new = 0
                # QMessageBox.information(None, "new url?",url)
        if (new > 0):
            f.write(self.dockwidget.comboBox.currentText() + "\n")  # new url as first item

        for url in self.url_list:
            f.write(url + "\n")  # python will convert \n to os.linesep
            # QMessageBox.information(None, "url",url)
        f.close()  # you can omit in most cases as the destructor will call it

    def f_delete_url(self):
        # delete selected url from config file

        reply = QMessageBox.question(None, 'Message',"Are you sure to delete url: "+self.dockwidget.comboBox.currentText()+"?", QMessageBox.Yes, QMessageBox.No)

        if reply==QMessageBox.No:
            return

        fname = self.base_folder + "\config\urls.txt"
        if os.path.isfile(fname):
            os.remove(fname)  # remove the current file, otherwise create just a new one.
        f = open(fname, 'w')

        for i in range(self.dockwidget.comboBox.count()):
            if self.dockwidget.comboBox.itemText(i) != self.dockwidget.comboBox.currentText():
                f.write(self.dockwidget.comboBox.itemText(i) + "\n")

        f.close()  # you can omit in most cases as the destructor will call it
        a = self.f_update_combo(0)

    def f_update_combo(self,rec):
        # refresh the items of the combobox from WFS layers and url's
        self.url_list = []
        self.dockwidget.comboBox.clear()

        with open(self.base_folder + "\config\urls.txt") as f:
            for line in f:  # create a list of lists
                self.url_list.append(line.rstrip())

        self.dockwidget.comboBox.addItems(self.url_list)

        file = open(self.base_folder + "\config\wfs.txt", "r")
        var = []
        for line in file:
            var.append(line.strip().split(","))
        file.close()

        self.dockwidget.combo_wfs.clear()
        for n in var:
            self.dockwidget.combo_wfs.addItem(n[0].strip('"'))
        self.dockwidget.combo_wfs.setCurrentIndex(rec)


###############################################################################################
##                                                            < END custom methods COMBOBOX  ##
###############################################################################################


###############################################################################################
##  Start custom methods COMBOBOX POPUP >                                                    ##
###############################################################################################
    def f_clearpopup(self):
        # velden van de popup dialog worden gereset
        self.popup.combo_service.setCurrentIndex(0)
        self.popup.combo_version.setCurrentIndex(0)
        self.popup.le_name.clear()
        self.popup.le_url.clear()
        self.popup.le_request.clear()
        self.popup.le_typename.clear()
        self.popup.le_srsname.clear()

    def f_changed(self):
        # gewijzigde velden in de popup krijgen andere achtergrondkleur
        self.popup.sender().setStyleSheet("background-color: rgb(255, 255, 210);")


    def f_reset_color(self,dialog):
        # herstellen van standaard achtergrondkleur line edits
        lineEdits = dialog.findChildren(QLineEdit)
        for le in lineEdits:
            le.setStyleSheet("background-color: rgb(255, 255, 255);")

    def f_edit(self):
        # record van geselecteerde item van services wordt uit file gehaald
        # vervolgens wordt de popup gevuld met deze data
        recno=self.dockwidget.combo_wfs.currentIndex()
        self.popup.recno=recno
        data = self.f_getrecord(self.base_folder + "\config\wfs.txt",recno)
        self.f_fillpopup(self.popup,data,recno)
        self.popup.show()

    def f_getrecord(self,filename, recordnr):
        # gevraagde record wordt uit file geladen
        file = open(filename, "r")
        var = []
        for line in file:
            var.append(line.strip().split(","))
        file.close()
        if (len(var)<1):
            return var

        return var[recordnr]


    def f_validate(self,data,valtype):
        a = 1


    def f_testUrl(self,url):
        request = urllib2.Request(url)
        try:
            response = urllib2.urlopen(request)
            return True
        except:
            return False


    def f_saverecord(self,filename, dialog):
        # huidige record wordt naarfile geschreven, wanneer bestaand recordnr, dan overschreven
        # anders nieuw record onder aan de lijst
        # validatie toevoegen
        file = open(filename, "r")
        var = []
        for line in file:
            var.append(line.strip().split(","))
        file.close()
        if (len(var)<1):
            return var
        i=0
        ret=0
        data=self.f_collectdata(self.popup)
        # added validation
        if data==None:
            return False, 0
        else:
        # self.f_validate(data,[('text',1),('url','url'),('text',2),('text',2),('text',2)])

            file2 = open(filename, 'w')
            new_line = ""
            for line in var:
                if i==dialog.recno:
                    ret=dialog.recno
                    for item in data:
                         if (len(new_line)>0):
                             new_line=new_line + ','
                         new_line = new_line +item
                    file2.write(new_line + "\n")
                    new_line=""
                else:
                    for item in line:
                         if (len(new_line)>0):
                             new_line=new_line + ','
                         new_line = new_line +item
                    file2.write(new_line + "\n")
                    new_line=""
                i=i+1

            if dialog.recno==-1:
                for item in data:
                     if (len(new_line)>0):
                         new_line=new_line + ','
                     new_line = new_line +item
                file2.write(new_line + "\n")
                ret=i
            file2.close()
            return True, ret

    def f_fillpopup(self,dialog,data,recno):
        # popup dialog wordt gevuld met aangeleverde data
        lineEdits = dialog.findChildren(QLineEdit)
        i=0
        for le in lineEdits:
            le.setText(data[i].strip('"'))
            #QMessageBox.information(None, "aantal", le.text())
            i=i+1

        comboBoxes = dialog.findChildren(QComboBox)
        for cb in comboBoxes:
            #QMessageBox.information(None, "aantal", data[i])
            index = cb.findText(data[i].strip('"'), Qt.MatchFixedString)
            i=i+1
            #QMessageBox.information(None, "aantal", str(index))
            if index >= 0:
                cb.setCurrentIndex(index)


    def f_collectdata(self,dialog):
        # data uit popup wordt verzameld en geretourneerd als lijst
        lineEdits = dialog.findChildren(QLineEdit)
        i=0
        data=[]
        for le in lineEdits:
            if len(le.text())<1:
                l = dir(le)
                # QgsMessageLog.logMessage(str(l))
                le.setFocus()
                return None

            data.append(le.text())
            i=i+1

        comboBoxes = dialog.findChildren(QComboBox)
        for cb in comboBoxes:
            data.append(cb.currentText())
            i=i+1

        return data



###############################################################################################
##                                                            < END custom methods COMBOBOX  ##
###############################################################################################

    def run(self):

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING AhnDownloader"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = AhnDownloaderDockWidget()
                self.popup=PopupDialog()
                self.help=HelpDialog()
                self.f_connect_widgets()

            #van
                self.base_folder = os.path.dirname(os.path.realpath(__file__))
                a = self.f_update_combo(0)
                self.popup.recno = 0

            #tot

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()









