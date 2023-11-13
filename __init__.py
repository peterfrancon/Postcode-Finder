# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PostcodeFinder
                                 A QGIS plugin
 The plugin will find and zoom to a Postcode in an LLPG data file.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-10-10
        copyright            : (C) 2023 by GeoMapTric
        email                : info@GeoMapTric.co.uk
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PostcodeFinder class from file PostcodeFinder.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .postcode_finder import PostcodeFinder
    return PostcodeFinder(iface)
