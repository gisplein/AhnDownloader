# WORKER DEFAULT #

from qgis.gui import *
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import os.path
import os
import traceback
# for new download function
import zipfile
import urllib2
import inspect
# requests
from urllib2 import urlopen, URLError, HTTPError

class Worker(QObject):
    '''Example worker for calculating the total area of all features in a layer'''

    def __init__(self, layer, field, url, folder, unzip, dialog,vl):
        QObject.__init__(self)
        if isinstance(layer, QgsVectorLayer) is False:
            raise TypeError('Worker expected a QgsVectorLayer, got a {} instead'.format(type(layer)))
        self.layer = layer
        self.field = field
        self.folder = folder
        self.url = url
        self.unzip = unzip
        self.killed = False
        self.dialog = dialog
        self.tmplayer=None
        self.vl = vl

    def lineno(self):
        """Returns the current line number in our program."""
        return inspect.currentframe().f_back.f_lineno

    def run(self):
        ret = None
        result=None
        vl=None

        try:
            # features = self.layer.getFeatures()
            features = self.layer.selectedFeatures()
            feature_count = self.layer.featureCount()
            feature_count_selected = self.layer.selectedFeatureCount()

            pr = self.vl.dataProvider()
            self.vl.startEditing()
            pr.addAttributes([QgsField("unit", QVariant.String), QgsField("result", QVariant.String)])
            self.vl.updateFields()

            progress_count = 0
            step = 1
            result = []
            for feature in features:
                geom = feature.geometry()
                if self.killed is True:
                    # kill request received, exit loop early
                    break
                geom = feature.geometry()

                idx = self.layer.fieldNameIndex(self.field)
                iblad = (feature.attributes()[idx])
                stap = float(100/feature_count_selected)

                a = self.retrieve(self.url, iblad, self.folder,stap,progress_count)
                result.append(a)
                QgsMessageLog.logMessage('result: ' + str(a))  #debug

                fet = QgsFeature()
                fet.setGeometry(geom)
                fet.setAttributes([iblad,a[2]])
                pr.addFeatures([fet])

                # increment progress
                progress_count += 1
                if step == 0 or progress_count % step == 0:
                    self.progress.emit(100 * (progress_count / float(feature_count_selected)))
            if self.killed is False:
                self.progress.emit(100)
                # ret = (self.layer, feature_count)
                ret = result
        except Exception, e:
            # forward the exception upstream
            QMessageBox.information(None, "Error", str(e))
            self.error.emit(e, traceback.format_exc())

        self.vl.commitChanges()
        if (self.unzip > 0):
             a = self.f_unzip(result)

        self.finished.emit(result,self.vl)

    def kill(self):
        self.killed = True
        # QMessageBox.information(None, "result",'process killed.')
    #tmplayer = pyqtSignal(object)
    finished = pyqtSignal(object,object)
    error = pyqtSignal(Exception, basestring)
    progress = pyqtSignal(float)

    def retrieve(self, url, iblad, folder, stap, progress_count):
        iurl = url.replace("[ifield]", iblad)
        file_name = iurl.split('/')[-1]
        dstblad = folder + "/" + file_name

        QgsMessageLog.logMessage('iurl: '+iurl+' -> '+dstblad)

        try:
            request=urllib2.Request(iurl)
            request.get_method = lambda: 'HEAD'
            response = urllib2.urlopen(request)

#            QgsMessageLog.logMessage('response: ' + str(response.info()))

            if "Content-Length" in response.info():
                file_size = int(response.info()["Content-Length"])
            if "content-length" in response.info():
                file_size = int(response.info()["content-length"])

            QgsMessageLog.logMessage('file_size: ' + str(file_size))
#            QgsMessageLog.logMessage('line: ' + str(self.lineno()))

            u = urllib2.urlopen(iurl)
            f = open(dstblad, 'wb')

            file_size_dl = 0
            block_sz = 8192


            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)
                self.progress.emit(progress_count * stap+stap*file_size_dl/file_size)

            f.close()
            # handle errors
            return [iurl, dstblad, "succes"]
        except HTTPError, e:
            return [iurl, dstblad, "HTTP Error " + str(e.code)]
        except URLError, e:
            return [iurl, dstblad, "URL Error " + str(e.reason)]


    def f_unzip(self,ret):
        self.progress.emit(0)
        progress_count = 0
        step = 1
        for r in ret:
            #QMessageBox.information(None, "unzip", r[1])
            # increment progress
            progress_count += 1
            if step == 0 or progress_count % step == 0:
                self.progress.emit(100 * (progress_count / float(len(ret))))

            if os.path.isfile(r[1]):
                try:
                   # if not os.path.isfile(doel):
                        #logging.info('Blad: ' + iblad + ' wordt uitgepakt.')
                    with zipfile.ZipFile(r[1], "r") as z:
                        QgsMessageLog.logMessage('Extracting: ' + r[1])
                        z.extractall(self.folder)
                    continue
                except Exception, e:
                    #QMessageBox.information(None, "foutmelding", r[1]+": "+ str(e))
                    #logging.error('Er is een fout opgetreden bij de download van blad: ' + iblad)
                    #logging.error(e)
                    QgsMessageLog.logMessage('An error occured extracting: ' +r[1])
                    continue


