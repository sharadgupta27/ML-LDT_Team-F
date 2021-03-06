# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Level1_Focus_on_mode
                                 A QGIS plugin
 Calculate hierarchical LD map using multi-resolution LD maps from single component mode

 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-02-28
        copyright            : (C) 2021 by Sharad
        email                : email@email.com
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
    """Load Level1_Focus_on_mode class from file Level1_Focus_on_mode.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .level1_focus_on_mode import Level1_Focus_on_mode
    return Level1_Focus_on_mode(iface)
