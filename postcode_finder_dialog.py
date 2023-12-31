# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PostcodeFinderDialog
                                 A QGIS plugin
 The plugin will find and zoom to a Postcode in an LLPG data file.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-10-10
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Peter Francon
        email                : peter@GeoMapTric.co.uk
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
import qgis.core
import re

# from qgis.PyQt.QtWidgets import QComboBox
from qgis.core import Qgis
from qgis.PyQt.QtCore import Qt  # Import Qt
from qgis.PyQt import QtWidgets, QtCore
from qgis.PyQt import uic
from qgis.core import QgsProject  # Added QgsRectangle to create zoomable extent
from qgis.core import QgsVectorLayer  # Import QgsVectorLayer
from qgis.utils import iface  # Import iface for user messages

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'postcode_finder_dialog_base.ui'))


def is_valid_postcode(postcode):
    # Regular expression pattern for UK postcodes
    pattern = r'^[A-Z]{1,2}[0-9R][0-9A-Z]? ?[0-9][A-Z]{2}$'

    return re.match(pattern, postcode) is not None


class PostcodeFinderDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None, canvas=None):
        # self.reset_fields()
        """Constructor."""
        super(PostcodeFinderDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        # Set the dialog to always stay on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setupUi(self)
        self.setWindowTitle("Postcode Finder")

        # Populate the ComboBox with layer names
        self.populate_layer_list()
        self.cb_selectdata.currentIndexChanged.connect(self.layer_changed)

        # Pass in the QgsMapCanvas instance when initializing this dialog
        self.canvas = canvas

        # Connect 'Enter' key press on le_postcode to a function
        self.le_postcode.returnPressed.connect(self.select_by_postcode)

        # Connect double-click event on the list widget to a function
        self.listWidget_uprns.itemDoubleClicked.connect(self.zoom_to_uprn)

        self.buttonBox.rejected.connect(self.on_cancel_clicked)
        self.buttonBox.accepted.connect(self.on_ok_clicked)

    def reset_fields(self):
        selected_layer_name = self.cb_selectdata.currentText()  # Get the name of the selected layer
        if selected_layer_name:
            layer = QgsProject.instance().mapLayersByName(selected_layer_name)[0]
            # Check if it's a vector layer before trying to remove selection
            if layer.type() == qgis.core.QgsMapLayer.VectorLayer:
                layer.removeSelection()  # Remove selection only if it's a vector layer

        self.le_postcode.clear()
        self.listWidget_uprns.clear()
        self.cb_selectdata.setCurrentIndex(0)

    def on_cancel_clicked(self):
        self.reset_fields()
        self.reject()  # This closes the dialog after resetting all fields

    def on_ok_clicked(self):
        selected_layer = self.cb_selectdata.currentText()
        if selected_layer:  # Ensure there is a selected layer
            layer = QgsProject.instance().mapLayersByName(selected_layer)[0]

            # Check if the layer is a vector layer and has selected features
            if layer.type() == qgis.core.QgsMapLayer.VectorLayer and layer.selectedFeatureCount() > 0:
                layer.removeSelection()

        self.reset_fields()
        self.close()

    # Add this function to your PostcodeFinderDialog class
    def keyPressEvent(self, e):
        if e.key() != QtCore.Qt.Key_Return and e.key() != QtCore.Qt.Key_Enter:
            super(PostcodeFinderDialog, self).keyPressEvent(e)

    def select_by_postcode(self):
        entered_postcode = self.le_postcode.text().upper()  # Convert to upper case
        selected_layer = self.cb_selectdata.currentText()  # Get selected layer name

        if not is_valid_postcode(entered_postcode):
            iface.messageBar().pushMessage("Error", "Invalid postcode format. Please enter a valid postcode.",
                                           level=Qgis.Warning)
            return  # Exit the function if the postcode is invalid

        if selected_layer:  # Ensure there is a selected layer
            layer = QgsProject.instance().mapLayersByName(selected_layer)[0]

            # Check if the layer is a vector layer
            if layer.type() == qgis.core.QgsMapLayer.VectorLayer:
                # Build the query string
                query = f"\"postcode\" = '{entered_postcode}'"  # Ensure your field name is correct

                # Select features based on the query
                layer.selectByExpression(query, QgsVectorLayer.SetSelection)  # Use SetSelection

                # Check if any features were selected
                if layer.selectedFeatureCount() > 0:

                    # Get a list of UPRNs from the selected features
                    uprns = [str(feature['uprn']) for feature in layer.selectedFeatures()]

                    # Sort the UPRNs numerically
                    uprns.sort()

                    # Update list widget with selected UPRNs
                    self.listWidget_uprns.clear()
                    self.listWidget_uprns.addItems(uprns)
                    self.canvas.zoomToSelected(layer)
                else:
                    iface.messageBar().pushMessage("Error", "No features found for the entered postcode.",
                                                   level=Qgis.Info)
            else:
                iface.messageBar().pushMessage("Error", "The layer selected is not an LLPG data layer.",
                                               level=Qgis.Critical)

    def zoom_to_uprn(self, item):
        selected_uprn = item.text()
        selected_layer = self.cb_selectdata.currentText()  # Get selected layer name
        layer = QgsProject.instance().mapLayersByName(selected_layer)[0]
        query = f"UPRN = '{selected_uprn}'"
        layer.selectByExpression(query, QgsVectorLayer.SetSelection)  # Use SetSelection

        # Inside zoom_to_uprn
        if layer.selectedFeatureCount() == 1:
            if self.canvas is not None:
                self.canvas.zoomToSelected(layer)
            else:
                print("Canvas is None. Unable to zoom.")

        # Zoom to selected feature
        if layer.selectedFeatureCount() == 1:
            self.canvas.zoomToSelected(layer)

    def populate_layer_list(self):
        layers = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        self.cb_selectdata.addItems(layers)

    def layer_changed(self):
        selected_layer = self.cb_selectdata.currentText()
        # Here, you can use 'selected_layer' for later queries