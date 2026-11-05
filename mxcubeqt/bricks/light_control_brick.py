#
#  Project: MXCuBE
#  https://github.com/mxcube
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE. If not, see <http://www.gnu.org/licenses/>.

import logging

from mxcubeqt.utils import icons, qt_import
from mxcubeqt.bricks.motor_spinbox_brick import MotorSpinboxBrick

"""
Controls both the light on/off (light_actuator) and intensity (motor)
"""

__category__ = "General"

STATE_OUT, STATE_IN, STATE_MOVING, STATE_FAULT, STATE_ALARM, STATE_UNKNOWN = (
    0,
    1,
    9,
    11,
    13,
    23,
)


class LightControlBrick(MotorSpinboxBrick):
    def __init__(self, *args):

        MotorSpinboxBrick.__init__(self, *args)

        self.light_actuator_hwo = None
        self.light_saved_pos = None

        self._icon_off = icons.load_icon("lightoff")
        self._icon_on = icons.load_icon("lighton")
        
        self.light_button = qt_import.QPushButton(self.main_gbox)
        self.light_button.setIcon(self._icon_off)
        self.light_button.setDown(False)
        self.light_button.setFixedSize(27, 27)
        
        self.light_button.clicked.connect(self.light_button_clicked)
        self._gbox_hbox_layout.addWidget(self.light_button)
        
        self.light_button.setToolTip(
            "Switches the light on or off"
        )
        
        self.light_button.setSizePolicy(
            qt_import.QSizePolicy.Fixed, qt_import.QSizePolicy.Minimum
        )
    
    
    def light_button_clicked(self):
        if self.motor_hwobj is not None and hasattr(self.motor_hwobj, "move_in"):
            if not self.motor_hwobj.chan_light_is_on.get_value():
                self.motor_hwobj.move_in()
                self.light_button.setDown(True)
                self.light_button.setIcon(self._icon_on)
            else:
                self.motor_hwobj.move_out()
                self.light_button.setDown(False)
                self.light_button.setIcon(self._icon_off)
       
    # Wago light events
    def light_state_changed(self, state):
        print("light state changed", state)
        # print "LightControlBrick.wagoLightStateChanged",state
        if state == STATE_IN:
            self.light_button.setDown(True)
            self.light_button.setIcon(self._icon_on)
            self.move_left_button.setEnabled(True)
            self.move_right_button.setEnabled(True)
        elif state == STATE_OUT:
            self.light_button.setDown(False)
            self.light_button.setIcon(self._icon_off)
            self.move_left_button.setEnabled(False)
            self.move_right_button.setEnabled(False)
        else:
            self.light_button.setDown(False)

    def property_changed(self, property_name, old_value, new_value):
        if property_name == "mnemonic":
            MotorSpinboxBrick.property_changed(
                self, property_name, old_value, new_value
            )
            if self.motor_hwobj is not None:
                self["delta"] = 1.0
                if self.motor_hwobj.is_ready():
                    limits = self.motor_hwobj.get_limits()
                    if limits[0] is not None and limits[1] is not None:  
                        motor_range = float(limits[1] - limits[0])
                        self["delta"] = str(motor_range / 10.0)
                    
                if hasattr(self.motor_hwobj, "light_is_out") and not self.motor_hwobj.light_is_out():
                    self.light_button.setDown(True)
                    self.light_button.setIcon(self._icon_on)
                else:
                    self.light_button.setDown(False)
                    self.light_button.setIcon(self._icon_off)
                
                self.connect(self.motor_hwobj, "valueChanged", self.light_state_changed)
        
        else:
            MotorSpinboxBrick.property_changed(
                self, property_name, old_value, new_value
            )
