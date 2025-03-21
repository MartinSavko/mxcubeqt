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

from QtImport import *

from BlissFramework import Qt4_Icons
from BlissFramework.Utils import Qt4_widget_colors
from BlissFramework.Qt4_BaseComponents import BlissWidget


__category__ = "General"
__version__ = 2.3

class Qt4_EnergyBrick(BlissWidget):
    """
    Descript. : EnergyBrick displays actual energy and wavelength.
    """
    def __init__(self, *args):
        """
        Descript. : Initiates BlissWidget Brick
        """
        BlissWidget.__init__(self, *args)

        # Properties ----------------------------------------------------------       
        self.addProperty('mnemonic', 'string', '')
        self.addProperty('defaultMode', 'combo', ('keV', 'Ang'), 'keV')
        self.addProperty('kevFormatString', 'formatString', '##.####')
        self.addProperty('angFormatString', 'formatString', '##.####')
        self.addProperty('displayStatus', 'boolean', False)

        # Signals ------------------------------------------------------------

        # Slots ---------------------------------------------------------------

        # Hardware objects ----------------------------------------------------
        self.energy_hwobj = None

        # Internal values -----------------------------------------------------
        self.energy_limits = None
        self.wavelength_limits = None

        # Graphic elements ----------------------------------------------------
        self.group_box = QGroupBox("Energy", self)
        energy_label = QLabel("Current:", self.group_box)
        energy_label.setFixedWidth(75)
        wavelength_label = QLabel("Wavelength: ", self.group_box)
        self.energy_ledit = QLineEdit(self.group_box)
        self.energy_ledit.setReadOnly(True)
        self.wavelength_ledit = QLineEdit(self.group_box)
        self.wavelength_ledit.setReadOnly(True)

        self.status_label = QLabel("Status:", self.group_box)
        self.status_ledit = QLineEdit(self.group_box)
        self.status_ledit.setEnabled(False)

        self.new_value_widget = QWidget(self)
        self.set_to_label = QLabel("Set to: ", self)
        self.new_value_ledit = QLineEdit(self.new_value_widget)
        #self.new_value_ledit.setMaximumWidth(60)
        self.units_combobox = QComboBox(self.new_value_widget)
        self.units_combobox.addItems(["keV", u"\u212B"]) 
        self.stop_button = QPushButton(self.new_value_widget)        
        self.stop_button.setIcon(Qt4_Icons.load_icon("Stop2"))
        self.stop_button.setEnabled(True)
        self.stop_button.setFixedWidth(25)
 
        # Layout --------------------------------------------------------------
        _new_value_widget_hlayout = QHBoxLayout(self.new_value_widget)
        _new_value_widget_hlayout.addWidget(self.new_value_ledit)
        _new_value_widget_hlayout.addWidget(self.units_combobox)
        _new_value_widget_hlayout.addWidget(self.stop_button)
        _new_value_widget_hlayout.setSpacing(0)
        _new_value_widget_hlayout.setContentsMargins(0, 0, 0, 0)

        _group_box_gridlayout = QGridLayout(self.group_box)
        _group_box_gridlayout.addWidget(energy_label, 0, 0)
        _group_box_gridlayout.addWidget(self.energy_ledit, 0, 1) 
        _group_box_gridlayout.addWidget(wavelength_label, 1, 0)
        _group_box_gridlayout.addWidget(self.wavelength_ledit, 1, 1)
        _group_box_gridlayout.addWidget(self.status_label, 2, 0)
        _group_box_gridlayout.addWidget(self.status_ledit, 2, 1)
        _group_box_gridlayout.addWidget(self.set_to_label, 3, 0) 
        _group_box_gridlayout.addWidget(self.new_value_widget, 3, 1)
        _group_box_gridlayout.setSpacing(0)
        _group_box_gridlayout.setContentsMargins(1, 1, 1, 1) 

        _main_vlayout = QVBoxLayout(self)
        _main_vlayout.setSpacing(0)
        _main_vlayout.setContentsMargins(0, 0, 2, 2)
        _main_vlayout.addWidget(self.group_box)

        # SizePolicies --------------------------------------------------------

        # Qt signal/slot connections ------------------------------------------
        self.new_value_ledit.returnPressed.connect(self.current_value_changed)
        self.new_value_ledit.textChanged.connect(self.input_field_changed)
        self.units_combobox.activated.connect(self.units_changed)
        self.stop_button.clicked.connect(self.stop_clicked)

        # Other --------------------------------------------------------------- 
        #self.group_box.setCheckable(True)
        #self.group_box.setChecked(True)
        self.new_value_validator = QDoubleValidator(\
             0, 15, 4, self.new_value_ledit)
        self.status_ledit.setEnabled(False)

        self.instance_synchronize("energy_ledit", "new_value_ledit")

    def propertyChanged(self, property_name, old_value, new_value):
        """
        Descript. : Event triggered when user property changed in the property
                    editor. 
        Args.     : property_name (string), old_value, new_value
        Return.   : None
        """
        if property_name == 'mnemonic':
            if self.energy_hwobj is not None:
                self.disconnect(self.energy_hwobj, 'deviceReady', self.connected)
                self.disconnect(self.energy_hwobj, 'deviceNotReady', self.disconnected)
                self.disconnect(self.energy_hwobj, 'energyChanged', self.energy_changed)
                self.disconnect(self.energy_hwobj, 'stateChanged', self.state_changed)
                self.disconnect(self.energy_hwobj, 'statusInfoChanged', self.status_info_changed)
            self.energy_hwobj = self.getHardwareObject(new_value)
            if self.energy_hwobj is not None:
                self.set_new_value_limits()
                self.connect(self.energy_hwobj, 'deviceReady', self.connected)
                self.connect(self.energy_hwobj, 'deviceNotReady', self.disconnected)
                self.connect(self.energy_hwobj, 'energyChanged', self.energy_changed)
                self.connect(self.energy_hwobj, 'stateChanged', self.state_changed)
                self.connect(self.energy_hwobj, 'statusInfoChanged', self.status_info_changed)
                self.energy_hwobj.update_values() 
                if self.energy_hwobj.isReady():
                    self.connected()
                else:
                    self.disconnected()
            else:
                self.disconnected()
        elif property_name == 'defaultMode':
            if new_value == "keV":
                self.units_combobox.setCurrentIndex(0)
            else:
                self.units_combobox.setCurrentIndex(1)

        elif property_name == 'displayStatus':
            self.status_label.setVisible(new_value)
            self.status_ledit.setVisible(new_value)
        else:
            BlissWidget.propertyChanged(self, property_name, old_value, new_value)

    def connected(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.setEnabled(True)
        tunable_energy = self.energy_hwobj.can_move_energy()
        if tunable_energy is None:
            tunable_energy = False 
        self.set_to_label.setEnabled(tunable_energy)
        self.new_value_ledit.setEnabled(tunable_energy)
        self.units_combobox.setEnabled(tunable_energy)
        if tunable_energy:
             Qt4_widget_colors.set_widget_color(\
                self.new_value_ledit,
                Qt4_widget_colors.LINE_EDIT_ACTIVE,
                QPalette.Base)
             #Qt4_widget_colors.set_widget_color(\
             #   self.units_combobox,
             #   Qt4_widget_colors.LIGHT_GREEN,
             #   QtGui.QPalette.Button) 

    def disconnected(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.setEnabled(False)

    def energy_changed(self, energy_value, wavelength_value):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        energy_value_str = self['kevFormatString'] % energy_value
        wavelength_value_str = self['angFormatString'] % wavelength_value
        self.energy_ledit.setText("%s keV" % energy_value_str)
        self.wavelength_ledit.setText("%s %s" % (wavelength_value_str, u"\u212B"))

    def state_changed(self, state):
        self.setEnabled(state == "ready")
        BlissWidget.set_status_info("status", "", "")

    def status_info_changed(self, status_info):
        self.status_ledit.setText(status_info)

    def current_value_changed(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        input_field_text = self.new_value_ledit.text()

        if self.new_value_validator.validate(input_field_text, 0)[0] == \
           QValidator.Acceptable:
            if self.units_combobox.currentIndex() == 0:
                BlissWidget.set_status_info("status", "Setting energy...", "running")
                self.energy_hwobj.move_energy(float(input_field_text))
            else:
                self.energy_hwobj.move_wavelength(float(input_field_text))
            self.new_value_ledit.setText("")
            Qt4_widget_colors.set_widget_color(\
                 self.new_value_ledit,
                 Qt4_widget_colors.LINE_EDIT_ACTIVE,
                 QPalette.Base)

    def input_field_changed(self, input_field_text):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.new_value_validator.validate(input_field_text, 0)[0] == \
           QValidator.Acceptable:
            Qt4_widget_colors.set_widget_color(\
                self.new_value_ledit,
                Qt4_widget_colors.LINE_EDIT_CHANGED,
                QPalette.Base)
        else:
           Qt4_widget_colors.set_widget_color(\
                self.new_value_ledit,
                Qt4_widget_colors.LINE_EDIT_ERROR,
                QPalette.Base)

    def units_changed(self, unit):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        self.set_new_value_limits()

    def set_new_value_limits(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        if self.units_combobox.currentIndex() == 0:
            value_limits = self.energy_hwobj.get_energy_limits()
            self.group_box.setTitle("Energy")
            self.new_value_ledit.setToolTip(\
                 "Energy limits %.4f : %.4f keV" % \
                 (value_limits[0], value_limits[1]))
        else:
            value_limits = self.energy_hwobj.get_wavelength_limits()
            self.group_box.setTitle("Wavelength")
            self.new_value_ledit.setToolTip(\
                 "Wavelength limits %.4f : %.4f %s" % \
                 (value_limits[0], value_limits[1], u"\u212B"))
        self.new_value_validator.setRange(value_limits[0], value_limits[1], 4)    
   
    def stop_clicked(self):
        """
        Descript. :
        Args.     :
        Return.   : 
        """
        print("stoped clicked")
