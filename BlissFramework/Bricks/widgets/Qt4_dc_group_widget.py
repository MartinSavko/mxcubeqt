#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

import os
import logging

from QtImport import *

import Qt4_queue_item
from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from widgets.Qt4_matplot_widget import PolarScaterWidget

import traceback


class DCGroupWidget(QWidget):
    def __init__(self, parent = None, name = "dc_group_widget"):

        QWidget.__init__(self, parent)
        if name is not None:
            self.setObjectName(name) 

        # Properties ----------------------------------------------------------

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Hardware objects ----------------------------------------------------
        self._beamline_setup_hwobj = None

        # Internal variables --------------------------------------------------
        self._data_collection = None
        self.add_dc_cb = None
        self._tree_view_item = None

        _subwedge_widget = QGroupBox("Summary", self) 
        self.polar_scater_widget = PolarScaterWidget()
        self.subwedge_table = QTableWidget(_subwedge_widget)
        _snapshot_widget = QWidget(self)
        self.position_widget = loadUi(os.path.join(os.path.dirname(__file__),
                                      'ui_files/Qt4_snapshot_widget_layout.ui'))
        
        # Layout --------------------------------------------------------------
        _subwedge_widget_vlayout = QVBoxLayout(_subwedge_widget)
        _subwedge_widget_vlayout.addWidget(self.polar_scater_widget)
        _subwedge_widget_vlayout.addWidget(self.subwedge_table)
        _subwedge_widget_vlayout.setContentsMargins(0, 4, 0, 0)
        _subwedge_widget_vlayout.setSpacing(6)
        _subwedge_widget_vlayout.addStretch(0)

        _main_hlayout = QHBoxLayout(self)
        _main_hlayout.addWidget(_subwedge_widget)
        _main_hlayout.setContentsMargins(0, 0, 0, 0)
        _main_hlayout.setSpacing(2)
        _main_hlayout.addStretch(0)

        # SizePolicies --------------------------------------------------------
        
        # Qt signal/slot connections ------------------------------------------

        # Other ---------------------------------------------------------------
        #self.polar_scater_widget.setFixedSize(600, 600)
        font = self.subwedge_table.font()
        font.setPointSize(8)
        self.subwedge_table.setFont(font)
        self.subwedge_table.setEditTriggers(\
             QAbstractItemView.NoEditTriggers)
        self.subwedge_table.setColumnCount(7)
        self.subwedge_table.horizontalHeader().setStretchLastSection(False)

        horizontal_headers = ["Osc start", "Osc range", "Images", 
                              "Exposure time", 
                              "Energy", "Transmission", "Resolution"]
        for index, header in enumerate(horizontal_headers):
            self.subwedge_table.setHorizontalHeaderItem(index, 
                 QTableWidgetItem(header))
        #self.subwedge_table.setSizePolicy(QtGui.QSizePolicy.Fixed,
        #                                  QtGui.QSizePolicy.Fixed)

    def populate_widget(self, item):
        dcg_queue_item = item.get_queue_entry()
        dcg_data_model = item.get_model()

        dcg_child_list = []
        sw_list = []
         
        if dcg_queue_item.interleave_sw_list:
            sw_list = dcg_queue_item.interleave_sw_list
            for child in dcg_queue_item.interleave_items: 
                dcg_child_list.append(child['data_model'])
        else:
            for index, children in enumerate(dcg_queue_item._queue_entry_list):
                if isinstance(children.get_view(), Qt4_queue_item.DataCollectionQueueItem):
                    dcg_child_list.append(children.get_data_model())
                    acq_par = children.get_data_model().acquisitions[0].acquisition_parameters
                    sw_list.append([len(sw_list), 0, acq_par.first_image, 
                       acq_par.num_images, acq_par.osc_start, 
                       acq_par.osc_range * acq_par.num_images]) 
        
        for sw in sw_list:
            color = Qt4_widget_colors.get_random_numpy_color(alpha=50)
            if type(sw) is list:
                sw.append(color)
            elif type(sw) is dict:
                sw['color'] = color

        self.subwedge_table.setRowCount(0) 
        for sw in sw_list:
            row = self.subwedge_table.rowCount()
            self.subwedge_table.setRowCount(row + 1)
            if type(sw) is list:
                acq_par = dcg_child_list[sw[0]].acquisitions[0].acquisition_parameters
                
            elif type(sw) is dict:
                acq_par = dcg_child_list[sw['collect_index']].acquisitions[0].acquisition_parameters

            param_list = (str(acq_par.osc_start),
                          str(acq_par.osc_range),
                          str(acq_par.num_images),
                          str(acq_par.exp_time),
                          str(acq_par.energy),
                          str(acq_par.transmission),
                          str(acq_par.resolution)) 
            #color = Qt4_widget_colors.get_random_color()
            #sw.append(color)
            for col in range(7):
                self.subwedge_table.setItem(row, col, QTableWidgetItem(param_list[col]))
                if type(sw) is list:
                    color = QColor(int(sw[-1][0] * 255),
                                int(sw[-1][0] * 255),
                                int(sw[-1][0] * 255))
                elif type(sw) is dict:
                    color = QColor(int(sw['color'][0] * 255),
                                   int(sw['color'][0] * 255),
                                   int(sw['color'][0] * 255))
                color.setAlpha(100)
                
                self.subwedge_table.item(row, col).setBackground(color)
                #     QtGui.QColor(Qt4_widget_colors.TASK_GROUP[sw[0]]))

        self.polar_scater_widget.draw_multiwedge_scater(sw_list)
