from specific_weapon_classes import * #Import specific wapon classes.
from skill_functions import * #Import skills, itens and canteen buffs
import wx #For the interface
import wx.lib.intctrl #For IntCtrl
import wx.grid #For grids
import wx.adv #For tooltips
import copy #For deepcopy

class MainWindow(wx.Panel):
    ''' The program's main window '''

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        #Default weapon and monster
        self.user_weapon=GreatSword()
        self.target_monster=Monster("Nargacuga")

        #Create a list of weapon types for the drop down menu
        # self.weapon_list=['Great Sword','Longsword','Sword & Shield','Dual Blades','Lance','Gunlance',
        #                  'Hammer','Hunting Horn','Switch Axe','Charge Blade']
        self.weapon_list=['Great Sword','Long Sword','Sword & Shield','Dual Blades','Lance','Hammer','Switch Axe','Charge Blade','Insect Glaive'] #only these two are implemented so far
        
        #Sharpness Colors list
        self.sharp_list=['Purple','White','Blue','Green','Yellow','Orange','Red']

        #Element list and label text
        self.elem_list=['No Element','Fire','Water','Thunder','Ice','Dragon']
        
        #Generic text for weapon w/ no specific choices
        self.specific_generic_text="N/A:"
        self.specific_generic_check="N/A\n"

        #Hammer check text
        self.specific_hammer_text='Power\nCharge?'

        #SA phial list and label text
        self.specific_sa_list=['Power','Elemental','Other'] #Dragon Phial not implemented
        self.specific_sa_text='Phial:'

        #CB Phial list
        self.specific_cb_list=['Impact','Elemental']
        self.specific_cb_text1='Phial:'
        self.specific_cb_text2='Shield\nCharge?'
        self.specific_cb_text3='Power\nAxe?'

        #IG extracts list
        self.specific_ig_list=['Triple Up','Double Up','No Combo']
        self.specific_ig_text='Extract:'
        
        #LS Spirit Gauge color list
        self.specific_ls_list=['Red','Yellow','White','No Color']
        self.specific_ls_text='Spirit Color:'

        #List of monsters for the drop down-menu
        self.monster_list=[] #Start empty

        #Then append all monsters
        with open("datafiles\\monster\\ragemods.csv") as file:
            monster_file=csv.reader(file)
            next(monster_file) #Skip the first line, header

            for row in monster_file:
                self.monster_list.append(row[0])
        
        #List of options for damage calculation
        self.damage_options = ['Average','Normal','Crit/Feeble']

        #Default to average damage when opening
        self.calc_type = 'average'

        #Make control buttons, binds and layout
        self.createControls()
        self.bindEvents()
        self.doLayout()
        
    def createControls(self):
        #Create controls for the calculator
        
        #Weapon type choice
        self.weapon_label = wx.StaticText(self, label="Weapon type:")
        self.weapon_choice = wx.Choice(self, choices=self.weapon_list)
        self.weapon_choice.SetSelection(0) 
        #Weapon specific Choices
        self.specific_label = wx.StaticText(self, label=self.specific_ls_text)
        self.specific_choice = wx.Choice(self, choices=[])
        #Will be hidden in DoLayout by default.

        #Weapon specific checkboxes
        self.specific_checkbox1 = wx.CheckBox(self,label=self.specific_cb_text2)
        self.specific_checkbox2 = wx.CheckBox(self,label=self.specific_cb_text3)
        poweraxe_tooltip = wx.ToolTip('Also referred to as Savage Axe in the community.')
        self.specific_checkbox2.SetToolTip(poweraxe_tooltip)
        #Will be hidden in DoLayout by default.

        #Element type choice                              
        self.elem_type_label = wx.StaticText(self, label="Element:")
        self.elem_type_choice = wx.Choice(self, choices=self.elem_list)
        self.elem_type_choice.SetSelection(0)

        #Create labels and inputs for raw, element and affinity values
        self.raw_label = wx.StaticText(self, label="Attack value:")
        self.raw_int_ctrl = wx.lib.intctrl.IntCtrl(self, value=1396,size=(50,-1),min=1,allow_none=False)
        self.elem_label = wx.StaticText(self,label='Element value:')
        self.elem_int_ctrl = wx.lib.intctrl.IntCtrl(self, value=0,size=(50,-1),min=0,allow_none=False)
        self.aff_label = wx.StaticText(self, label="Affinity:")
        self.aff_int_ctrl = wx.lib.intctrl.IntCtrl(self, value=0,size=(50,-1),min=-100,max=100,allow_none=False)
        self.aff_percent_label=wx.StaticText(self,label='%') #% sign for affinity value

        #Checkboxes for True Raw and Element values
        self.raw_checkbox=wx.CheckBox(self,label='True?')
        self.elem_checkbox=wx.CheckBox(self,label='True?')

        #Tool tip for the true value checkboxes and affinity
        raw_tip=wx.ToolTip('Check if supplying the True Raw value.\nIf unsure, leave unchecked.')
        elem_tip=wx.ToolTip('Check if supplying the True Element value.\nIf unsure, leave unchecked.')
        aff_tip=wx.ToolTip('Write the affinity value without the %.\nSo for 20%, input 20, etc.')
        self.raw_checkbox.SetToolTip(raw_tip)
        self.elem_checkbox.SetToolTip(elem_tip)
        self.aff_int_ctrl.SetToolTip(aff_tip)

        #Choosing sharpness color
        self.sharp_label = wx.StaticText(self, label="Sharpness:")
        self.sharp_choice = wx.Choice(self, choices=self.sharp_list)
        self.sharp_choice.SetSelection(1)

        #Label and drop-down for monster, checkbox for rage
        self.monster_label = wx.StaticText(self, label="Monster:")
        self.monster_choice = wx.Choice(self, choices=self.monster_list)
        self.monster_checkbox=wx.CheckBox(self,label='Enraged?')
        self.monster_choice.SetSelection(self.monster_list.index(self.target_monster.name))
        
        #Toltip for monster_checkbox about rage and damage
        monster_tip=wx.ToolTip("Most monsters take more damage when enraged.\nSome take less damage.\nAnd some take the same damage regardless of rage.")
        self.monster_checkbox.SetToolTip(monster_tip)
    
        #Grid for monster hitzones
        self.monster_grid=wx.grid.Grid(self)
        self.monster_grid.CreateGrid(12,12)
        
        
        #Change column names for damage types and resize
        dmg_types=['Name','State','Cut','Impact','Shot','Fire','Water','Thunder','Ice','Dragon','Stun','Group']

        for dmg_type,index in zip(dmg_types,range(13)):
            self.monster_grid.SetColLabelValue(index, dmg_type)

        #Adjust sizes
        self.monster_grid.SetRowLabelSize(25) #Adjust row labels
        self.monster_grid.SetColLabelSize(25) #Adjust col labels
        self.monster_grid.AutoSize() #Autosize columns (width)
        
        #Manually adjust name and state columns for longer text
        self.monster_grid.SetColSize(0,80)
        self.monster_grid.SetColSize(1,70)
        self.monster_grid.SetSelectionMode(wx.grid.Grid.GridSelectRows)
        self.monster_grid.EnableEditing(False)
        self.monster_grid.SelectRow(0)
        
        #Label and grid for the selected hitzone, checkbox for tenderizing
        self.hitzone_label=wx.StaticText(self, label="Selected Hitzone:")
        self.hitzone_grid=wx.grid.Grid(self)
        self.hitzone_grid.CreateGrid(1,2) #Just for Name and State
        self.hitzone_checkbox=wx.CheckBox(self,label='Tenderized?')

        #Tooltip for the self.hitzone_checkbox
        self.hitzone_checkbox.SetToolTip(wx.ToolTip('Hitzones in the same Group are tenderized together.\nHitzones in Group 0 CANNOT be tenderized.'))
        
        #Name and resize
        for label,index in zip(dmg_types,range(2)):
            self.hitzone_grid.SetColLabelValue(index,label)
            self.hitzone_grid.SetColSize(index,80)
        self.hitzone_grid.SetRowLabelSize(25) #Adjust row labels
        self.hitzone_grid.SetColLabelSize(25) 

        #Show EFR and EFE numbers. Also effective affinity (ie affinity bounded by -100% and 100%)
        self.efr_label=wx.StaticText(self,label='Effective Raw:')
        self.efr_int_ctrl=wx.lib.intctrl.IntCtrl(self, value=290,size=(60,-1),min=1,allow_none=False,style=wx.TE_READONLY)
        self.efe_label=wx.StaticText(self,label='Effective Element:')
        self.efe_int_ctrl=wx.lib.intctrl.IntCtrl(self, value=0,size=(60,-1),min=0,allow_none=False,style=wx.TE_READONLY)
        self.efa_label = wx.StaticText(self, label="Effective Affinity:")
        self.efa_int_ctrl = wx.lib.intctrl.IntCtrl(self, value=0,size=(40,-1),min=-100,max=100,allow_none=False,style=wx.TE_READONLY)
        self.efa_percent_label=wx.StaticText(self,label='%') #% sign for affinity value
        #Tooltip for effective parameters
        
        tooltip_text="Affinity from Weakness Exploit considers:\n-Currently selected hitzone.\n-Tenderizing selection.\n-LAST attack in the current combo.\nIf no attack is selected, it'll default to NO Weakness Exploit!\n\nAffinity from Agitator only applies for an enraged monster."
        efr_tooltip=wx.ToolTip(tooltip_text)
        efr_tooltip.SetAutoPop(10000)
        self.efr_int_ctrl.SetToolTip(efr_tooltip)
        efe_tooltip=wx.ToolTip(tooltip_text)
        efe_tooltip.SetAutoPop(10000)
        self.efe_int_ctrl.SetToolTip(wx.ToolTip(tooltip_text))
        efa_tooltip=wx.ToolTip(tooltip_text)
        efa_tooltip.SetAutoPop(10000)
        self.efa_int_ctrl.SetToolTip(wx.ToolTip(tooltip_text))
        
        #Label and dropdown for attack selection
        self.attack_label = wx.StaticText(self, label="Select an attack:")
        self.attack_choice = wx.Choice(self, choices=self.user_weapon.attack_list)

        #Label and drop down for damage selection
        self.damage_label = wx.StaticText(self,label="Damage to display:")
        self.damage_choice = wx.Choice(self,choices=self.damage_options)
        self.damage_choice.SetSelection(0) #Default to average damage

        #Create a tooltip for damage_choice
        damage_tip=wx.ToolTip('Select a way to display damage.\nNormal: displays regular non-critical damage.\nCrit/Feeble: displays damage from Critical (Affinity>0) or Feeble(Affinity<0) hits.\nAverage: An average between the two previous calculations, weighted by Afffinity.')
        self.damage_choice.SetToolTip(damage_tip)

        #Grid for damage calculations
        self.damage_grid=wx.grid.Grid(self)
        self.damage_grid.CreateGrid(20,4)
     
        #Change column names for damage types and resize
        number_types=['Attack Name','Raw/Fixed','Elemental','TOTAL']

        for number_type,index in zip(number_types,range(4)):
            self.damage_grid.SetColLabelValue(index, number_type)

        #Column widths 
        self.damage_grid.SetColSize(0,250)
        self.damage_grid.SetColSize(1,65)
        self.damage_grid.SetColSize(2,65)
        self.damage_grid.SetColSize(3,50)

        #Adjust label sizes
        self.damage_grid.SetRowLabelSize(25) #Adjust row labels
        self.damage_grid.SetColLabelSize(25) #Adjust col labels
        self.update_damage_grid()

        #Select rows only
        self.damage_grid.SetSelectionMode(wx.grid.Grid.GridSelectRows)
        self.damage_grid.EnableEditing(False)

        #Initialize paramaters with default choices
        self.weapon_select(None) #Initialize weapon selection; no event
        self.monster_select(None) #Monster selection; no event
        self.hitzone_select(None) #Hitzone selection with no event
        
        #Add a button to clear current combo, another to delete
        #selected rows only
        self.clear_combo=wx.Button(self,label='Delete\ncurrent\ncombo',size=(80,55))
        self.clear_selected=wx.Button(self,label='Delete\nselected\nattacks',size=(80,55))

        #Tooltip to clear combo button
        clear_tooltip=wx.ToolTip("This will delete ALL attacks\nfrom the current combo!")
        self.clear_combo.SetToolTip(clear_tooltip)

        #Buttons to save and load combos
        self.save_combo_button = wx.Button(self,label='Save\ncurrent\ncombo',size=(80,55))
        self.load_combo_button = wx.Button(self,label='Load\nsaved\ncombo',size=(80,55))

        #Tooltip to load combo button
        load_tooltip=wx.ToolTip("This will ADD the loaded combo\nto the current combo!")
        self.load_combo_button.SetToolTip(load_tooltip)
        
        #Buttons for skills and items
        self.skill_button = wx.Button(self,label='Set Buffs (Skills and Items)',size=(180,-1))
        self.skill_save = wx.Button(self,label='Save Buffs',size=(80,-1))
        self.skill_load = wx.Button(self,label='Load Buffs',size=(80,-1))
    
    def bindEvents(self):
        """
        Binds events to the controls on the main window.
        """

        self.monster_choice.Bind(wx.EVT_CHOICE,self.monster_select)
        self.weapon_choice.Bind(wx.EVT_CHOICE,self.weapon_select)
        self.raw_int_ctrl.Bind(wx.EVT_TEXT,self.set_attack)
        self.raw_checkbox.Bind(wx.EVT_CHECKBOX,self.set_attack)
        self.elem_int_ctrl.Bind(wx.EVT_TEXT,self.set_element)
        self.elem_checkbox.Bind(wx.EVT_CHECKBOX,self.set_element)
        self.elem_type_choice.Bind(wx.EVT_CHOICE,self.elem_type_select)
        self.aff_int_ctrl.Bind(wx.EVT_TEXT,self.set_affinity)
        self.sharp_choice.Bind(wx.EVT_CHOICE,self.sharp_select)
        self.monster_grid.Bind(wx.grid.EVT_GRID_SELECT_CELL,self.hitzone_select)
        self.monster_checkbox.Bind(wx.EVT_CHECKBOX,self.toggle_rage)
        self.hitzone_checkbox.Bind(wx.EVT_CHECKBOX,self.toggle_tenderize)
        self.attack_choice.Bind(wx.EVT_CHOICE,self.add_attack)
        self.clear_combo.Bind(wx.EVT_BUTTON,self.clear_all)
        self.damage_choice.Bind(wx.EVT_CHOICE,self.calculation_select)
        self.specific_choice.Bind(wx.EVT_CHOICE,self.specific_select)
        self.raw_checkbox.Bind(wx.EVT_CHECKBOX,self.convert_true_raw)
        self.elem_checkbox.Bind(wx.EVT_CHECKBOX,self.convert_true_elem)
        self.specific_checkbox1.Bind(wx.EVT_CHECKBOX,self.specific_check1)
        self.specific_checkbox2.Bind(wx.EVT_CHECKBOX,self.specific_check2)
        self.skill_button.Bind(wx.EVT_BUTTON,self.open_skill_window)
        self.save_combo_button.Bind(wx.EVT_BUTTON,self.save_combo)
        self.load_combo_button.Bind(wx.EVT_BUTTON,self.load_combo)
        self.clear_selected.Bind(wx.EVT_BUTTON,self.clear_selected_attacks)
        self.skill_save.Bind(wx.EVT_BUTTON,self.save_buffs)
        self.skill_load.Bind(wx.EVT_BUTTON,self.load_buffs)

    def doLayout(self):
        """
        Layout the controls by means of sizers. The main window is split in 3 parts
         
           WEAPON DATA     |    ATTACK SELECTION
                 &         |          &
        MONSTER SELECTION  |   DAMAGE CALCULATION
        
        A horizontal BoxSizer splits the left (Weapon Data & Monster Selection) part 
        from the right (Attack Selection & Damage Calculation). The left part is further
        split by a GridBagSizer.
        """

        #Main box splitting the window in two
        main_box=wx.BoxSizer(orient=wx.HORIZONTAL)

        #Two more boxes corresponding to each half (left/right) of main_box
        left_box = wx.GridBagSizer(vgap=10, hgap=5)
        right_box = wx.GridBagSizer(vgap=10, hgap=10)
        
        ##########################################    
        #LEFT BOX
        ##########################################
        row=0 #Count which row the buttons are being positioned at
        spacer='       ' #Blank text for spacing

        #Type of weapon label and choice
        left_box.Add(self.weapon_label,pos=(row,0))
        left_box.Add(self.weapon_choice,pos=(row,1),span=(1,2),flag=wx.EXPAND)
        left_box.Add(wx.StaticText(self,label=spacer),pos=(row,3))

        #Specific choices for specific weapons
        left_box.Add(self.specific_label,pos=(row,4))
        left_box.Add(self.specific_choice,pos=(row,5),flag=wx.EXPAND)
        left_box.Add(wx.StaticText(self,label=spacer),pos=(row,6))

        #EFR display
        left_box.Add(self.efr_label,pos=(row,7))
        left_box.Add(self.efr_int_ctrl,pos=(row,8),span=(1,2),flag=wx.EXPAND)
        left_box.Add(wx.StaticText(self,label=spacer),pos=(row,10))
        row+=1

        #Attack, Affinity Element and Element type
        #Raw label, input and true value checkbox
        left_box.Add(self.raw_label,pos=(row,0))
        left_box.Add(self.raw_int_ctrl,pos=(row,1))
        left_box.Add(self.raw_checkbox,pos=(row,2))
        left_box.Add(wx.StaticText(self,label=spacer),pos=(row,3))

        #Specific checkboxes for specific weapons
        left_box.Add(self.specific_checkbox1,pos=(row,4))
        left_box.Add(self.specific_checkbox2,pos=(row,5))
        left_box.Add(wx.StaticText(self,label=spacer),pos=(row,6))

        #EFE display
        left_box.Add(self.efe_label,pos=(row,7))
        left_box.Add(self.efe_int_ctrl,pos=(row,8),span=(1,2),flag=wx.EXPAND)
        row+=1

        #Affinity label, input and % sign
        left_box.Add(self.aff_label,pos=(row,0))
        left_box.Add(self.aff_int_ctrl,pos=(row,1))
        left_box.Add(self.aff_percent_label,pos=(row,2))
        left_box.Add(wx.StaticText(self,label=spacer),pos=(row,3))

        #Sharpness label and choice
        left_box.Add(self.sharp_label,pos=(row,4))
        left_box.Add(self.sharp_choice,pos=(row,5),flag=wx.EXPAND)
        left_box.Add(wx.StaticText(self,label=spacer),pos=(row,6))

        #Effective Affinity display
        left_box.Add(self.efa_label,pos=(row,7))
        left_box.Add(self.efa_int_ctrl,pos=(row,8),flag=wx.EXPAND)
        left_box.Add(self.efa_percent_label,pos=(row,9))
        row+=1

        #Element value label, input and true value checkbox
        left_box.Add(self.elem_label,pos=(row,0))
        left_box.Add(self.elem_int_ctrl,pos=(row,1))
        left_box.Add(self.elem_checkbox,pos=(row,2))
        left_box.Add(wx.StaticText(self,label=spacer),pos=(row,3))

        #Element type label and choice
        left_box.Add(self.elem_type_label,pos=(row,4))
        left_box.Add(self.elem_type_choice,pos=(row,5),flag=wx.EXPAND)
        left_box.Add(wx.StaticText(self,label=spacer),pos=(row,6))

        #Button to set buffs
        left_box.Add(self.skill_button,pos=(row,7),span=(1,4))
        row+=1

        #Monster label and choice   
        left_box.Add(self.monster_label,pos=(row,0))
        left_box.Add(self.monster_choice,pos=(row,1),span=(1,2),flag=wx.EXPAND)
        left_box.Add(wx.StaticText(self,label=spacer),pos=(row,3))

        #Checkboxes for Rage and Tenderizing
        left_box.Add(self.monster_checkbox,pos=(row,4))
        left_box.Add(self.hitzone_checkbox,pos=(row,5))
        left_box.Add(wx.StaticText(self,label=spacer),pos=(row,6))

        #Buttons to save and load buffs
        left_box.Add(self.skill_save,pos=(row,7))
        left_box.Add(self.skill_load,pos=(row,8))
        row+=1

        #Grid for all hitzones from the monster
        left_box.Add(self.monster_grid,pos=(row,0),span=(1,10))
        row+=1

        #Selected hitzone label and small grid
        #There are to the right of monster select
        left_box.Add(self.hitzone_label,pos=(row,0))
        left_box.Add(self.hitzone_grid,pos=(row,1),span=(2,5))

        #Add to main_box
        main_box.Add(left_box)
        ##########################################    
        #RIGHT BOX
        ##########################################
     
        #Attack label and drop-down menu        
        right_box.Add(self.attack_label,pos=(0,0))
        right_box.Add(self.attack_choice,pos=(0,1), flag=wx.EXPAND)
        right_box.Add(self.damage_label,pos=(0,2))
        right_box.Add(self.damage_choice,pos=(0,3), flag=wx.EXPAND)

        #Damage grid
        right_box.Add(self.damage_grid,pos=(1,0),span=(6,3))

        #Buttons next to the grid
        right_box.Add(self.save_combo_button,pos=(1,3))
        right_box.Add(self.load_combo_button,pos=(2,3))
        right_box.Add(self.clear_selected,pos=(3,3))
        right_box.Add(self.clear_combo,pos=(4,3))
        
        #Add to main box
        main_box.Add(right_box)
       
        ##########################################    
        #COMBINE BOXES
        ##########################################
        self.SetSizerAndFit(main_box) 


        ###########################################    
        #DISABLE SPECIFIC WEAPON ELEMENTS
        ###########################################

        self.update_specific_choice()
        self.update_specific_checkboxes()

    def monster_select(self, event):
        """
        Sets the target monster as the selected monster from self.monster_choice
        Also update the hitzone data grid accordingly
        """
        #Get the index of the list selection
        index=self.monster_choice.GetSelection()
        
        #Set self.target_monster as a new monster object
        self.target_monster.create_monster(self.monster_list[index])
        

        #Reset the tenderized checkbox, if needed
        if self.hitzone_checkbox.IsChecked(): #If checked
            self.hitzone_checkbox.SetValue(False) #Uncheck
    
        #Reset the enraged checkbox, if needed
        if self.monster_checkbox.IsChecked(): #If checked
            self.monster_checkbox.SetValue(False) #Uncheck

        #Get the number of different hitzones
        num_hitzones = len(self.target_monster.hitzones)
        
        #Get the number of rows in the current grid
        num_rows= self.monster_grid.GetNumberRows()

        #Adjust grid size for num_hitzones
        if num_rows < num_hitzones: #If there are not enough rows, insert more
            self.monster_grid.AppendRows(num_hitzones-num_rows)
        
        elif num_rows > num_hitzones:
            self.monster_grid.DeleteRows(num_hitzones,num_rows-num_hitzones)

        #Set values for the monster's hitzones
        for i in range(num_hitzones): #Goes through each row of the grid
            self.monster_grid.SetCellValue(i,0,self.target_monster.hitzones[i].name)
            self.monster_grid.SetCellValue(i,1,self.target_monster.hitzones[i].state)
            self.monster_grid.SetCellValue(i,2,str(self.target_monster.hitzones[i].raw['cut']))
            self.monster_grid.SetCellValue(i,3,str(self.target_monster.hitzones[i].raw['impact']))
            self.monster_grid.SetCellValue(i,4,str(self.target_monster.hitzones[i].raw['shot']))
            self.monster_grid.SetCellValue(i,5,str(self.target_monster.hitzones[i].elem['fire']))
            self.monster_grid.SetCellValue(i,6,str(self.target_monster.hitzones[i].elem['water']))
            self.monster_grid.SetCellValue(i,7,str(self.target_monster.hitzones[i].elem['thunder']))
            self.monster_grid.SetCellValue(i,8,str(self.target_monster.hitzones[i].elem['ice']))
            self.monster_grid.SetCellValue(i,9,str(self.target_monster.hitzones[i].elem['dragon']))
            self.monster_grid.SetCellValue(i,10,str(self.target_monster.hitzones[i].stun))
            self.monster_grid.SetCellValue(i,11,str(self.target_monster.hitzones[i].tender_group))
        
        #Refresh
        self.monster_grid.Refresh()

        #Reset Hitzone selection to default
        self.hitzone_select(None)

        #Update damage_grid
        self.update_damage_grid()
    
    def update_specific_choice(self,text="",specific_list=[]):
        """
        Updates the weapon-specific drop-down menu when
        changing weapons.

        For a default argument of an empty string for the label
        text, set the generic menu for generic weapons and disable
        it.
        """

        if text: #If there is text, setup specific menu, show and Enable.
            self.specific_label.SetLabel(text)
            self.specific_choice.Clear() #Clear old options
            self.specific_choice.AppendItems(specific_list)
            self.specific_choice.SetSelection(0) #Default to first choice
            self.specific_choice.Enable()

        else: #OTherwise, clear menu, Hide and Disable.
            self.specific_label.SetLabel(self.specific_generic_text)
            self.specific_choice.Clear() #Clear old options
            self.specific_choice.Disable()

    def update_specific_checkboxes(self,text1="",text2=""):
        """
        Updates the weapon-specific checkboxes when
        changing weapons.

        Empty strings will hide the corresponding checkbox.
        """

        if text1: #Relabel the checkbox, enable and default to select
            self.specific_checkbox1.SetLabel(text1)
            self.specific_checkbox1.SetValue(True)
            self.specific_checkbox1.Enable()
        else: #Otherwise, set generic text and disable
            self.specific_checkbox1.SetLabel(self.specific_generic_check)
            self.specific_checkbox1.Disable()
        
        if text2: #Relabel the checkbox,show and default do unselect
            self.specific_checkbox2.SetLabel(text2)
            self.specific_checkbox2.SetValue(False)
            self.specific_checkbox2.Enable()
        else: #Otherwise, hide
            self.specific_checkbox2.SetLabel(self.specific_generic_check)
            self.specific_checkbox2.Disable()

    def weapon_select(self,event,name_file='datafiles\\weapon\\weapon_names.csv'):
        """
        Updates the weapon_type attribute of self.user_weapon,
        then updates the true attack value

        Drop down menu gives full weapon names ("Great Sword, etc")
        but the class code uses short names ('gs', etc) so we have 
        to convert those.

        The weapon_names.csv file has these conversions. It is
        by default located at 'datafiles\\weapon\\weapon_names.csv'
        """

        #Get the index of the weapon choice list
        if event:
            index=self.weapon_choice.GetSelection()
        else: #Default to GS if no event
            index=0

        #Convert to a new weapon object
        self.user_weapon=self.convert_weapon(index)

        #Update the attack list
        self.attack_choice.Clear()
        self.attack_choice.AppendItems(self.user_weapon.attack_list)

        #Check true raw
        #Update the displayed bloated value
        if not self.raw_checkbox.IsChecked(): 
            #If the checkbox is unchecked it has a bloated value
            self.raw_int_ctrl.SetValue(round(self.user_weapon.true_raw*self.user_weapon.get_class_mod()))

        #Clear combo
        self.clear_all(None) #No event

        #Update damage_grid
        self.update_damage_grid()

    def convert_weapon(self,index):
        """
        Converts the self.user_weapon object to  a new weapon
        object based on its index from the drop down menu
        """

        if (self.weapon_list[index]=='Great Sword'): #GS
            #Update specific menu and checkboxes
            self.update_specific_choice()
            self.update_specific_checkboxes()

            return GreatSword(
               bloat_attack=self.user_weapon.true_raw,
               affinity=self.aff_int_ctrl.GetValue(),
               bloat_elem=self.elem_int_ctrl.GetValue(),
               elem_type=self.elem_list[self.elem_type_choice.GetSelection()].lower(),
               sharp_color=self.sharp_list[self.sharp_choice.GetSelection()].lower(),
               is_true_elem=self.elem_checkbox.IsChecked(),
               is_true_raw=True,
               buff_dict=copy.deepcopy(self.user_weapon.buff_dict)
            )

            

        if (self.weapon_list[index]=='Sword & Shield'): #SnS
            #Update specific menu and checkboxes
            self.update_specific_choice()
            self.update_specific_checkboxes()

            return SwordNShield(
               bloat_attack=self.user_weapon.true_raw,
               affinity=self.aff_int_ctrl.GetValue(),
               bloat_elem=self.elem_int_ctrl.GetValue(),
               elem_type=self.elem_list[self.elem_type_choice.GetSelection()].lower(),
               sharp_color=self.sharp_list[self.sharp_choice.GetSelection()].lower(),
               is_true_elem=self.elem_checkbox.IsChecked(),
               is_true_raw=True,
               buff_dict=copy.deepcopy(self.user_weapon.buff_dict)
            )

            

        if (self.weapon_list[index]=='Lance'): #Lance
            #Update specific menu and checkboxes
            self.update_specific_choice()
            self.update_specific_checkboxes()

            return Lance(
               bloat_attack=self.user_weapon.true_raw,
               affinity=self.aff_int_ctrl.GetValue(),
               bloat_elem=self.elem_int_ctrl.GetValue(),
               elem_type=self.elem_list[self.elem_type_choice.GetSelection()].lower(),
               sharp_color=self.sharp_list[self.sharp_choice.GetSelection()].lower(),
               is_true_elem=self.elem_checkbox.IsChecked(),
               is_true_raw=True,
               buff_dict=copy.deepcopy(self.user_weapon.buff_dict)
            )

            

        if (self.weapon_list[index]=='Hammer'): #Hammer
            #Update specific menu and checkboxes
            self.update_specific_choice()
            self.update_specific_checkboxes(self.specific_hammer_text)
            return Hammer(
               bloat_attack=self.user_weapon.true_raw,
               affinity=self.aff_int_ctrl.GetValue(),
               bloat_elem=self.elem_int_ctrl.GetValue(),
               elem_type=self.elem_list[self.elem_type_choice.GetSelection()].lower(),
               sharp_color=self.sharp_list[self.sharp_choice.GetSelection()].lower(),
               is_true_elem=self.elem_checkbox.IsChecked(),
               is_true_raw=True,
               power_charge=True,
               buff_dict=copy.deepcopy(self.user_weapon.buff_dict)
            )

            

        if (self.weapon_list[index]=='Switch Axe'): #SA
            #Update specific menu
            self.update_specific_choice(self.specific_sa_text,
                                        self.specific_sa_list)
            self.update_specific_checkboxes()

            return SwitchAxe(
               bloat_attack=self.user_weapon.true_raw,
               affinity=self.aff_int_ctrl.GetValue(),
               bloat_elem=self.elem_int_ctrl.GetValue(),
               elem_type=self.elem_list[self.elem_type_choice.GetSelection()].lower(),
               sharp_color=self.sharp_list[self.sharp_choice.GetSelection()].lower(),
               is_true_elem=self.elem_checkbox.IsChecked(),
               is_true_raw=True,
               sa_phial='power',
               sa_dragon=0,
               buff_dict=copy.deepcopy(self.user_weapon.buff_dict)
            )

        if (self.weapon_list[index]=='Charge Blade'): #CB
            #Update specific menu
            self.update_specific_choice(self.specific_cb_text1,
                                        self.specific_cb_list)
            self.update_specific_checkboxes(self.specific_cb_text2,
                                            self.specific_cb_text3)

            return ChargeBlade(
               bloat_attack=self.user_weapon.true_raw,
               affinity=self.aff_int_ctrl.GetValue(),
               bloat_elem=self.elem_int_ctrl.GetValue(),
               elem_type=self.elem_list[self.elem_type_choice.GetSelection()].lower(),
               sharp_color=self.sharp_list[self.sharp_choice.GetSelection()].lower(),
               is_true_elem=self.elem_checkbox.IsChecked(),
               is_true_raw=True,
               cb_phial='impact',
               cb_shield=True,
               cb_power=False,
               buff_dict=copy.deepcopy(self.user_weapon.buff_dict)
            )    

        if (self.weapon_list[index]=='Dual Blades'): #DB
            #Update specific menu
            self.update_specific_choice()
            self.update_specific_checkboxes()

            return DualBlades(
               bloat_attack=self.user_weapon.true_raw,
               affinity=self.aff_int_ctrl.GetValue(),
               bloat_elem=self.elem_int_ctrl.GetValue(),
               elem_type=self.elem_list[self.elem_type_choice.GetSelection()].lower(),
               sharp_color=self.sharp_list[self.sharp_choice.GetSelection()].lower(),
               is_true_elem=self.elem_checkbox.IsChecked(),
               is_true_raw=True,
               buff_dict=copy.deepcopy(self.user_weapon.buff_dict)
            )

            

        if (self.weapon_list[index]=='Long Sword'): #LS
            #Update specific menu
            self.update_specific_choice(self.specific_ls_text,
                                         self.specific_ls_list)
            self.update_specific_checkboxes()
            return LongSword(
               bloat_attack=self.user_weapon.true_raw,
               affinity=self.aff_int_ctrl.GetValue(),
               bloat_elem=self.elem_int_ctrl.GetValue(),
               elem_type=self.elem_list[self.elem_type_choice.GetSelection()].lower(),
               sharp_color=self.sharp_list[self.sharp_choice.GetSelection()].lower(),
               is_true_elem=self.elem_checkbox.IsChecked(),
               is_true_raw=True,
               ls_gauge='red',
               buff_dict=copy.deepcopy(self.user_weapon.buff_dict)
            )

            

        if (self.weapon_list[index]=='Insect Glaive'): #IG
            #Update specific menu
            self.update_specific_choice(self.specific_ig_text,
                                        self.specific_ig_list)
            self.update_specific_checkboxes()

            return InsectGlaive(
               bloat_attack=self.user_weapon.true_raw,
               affinity=self.aff_int_ctrl.GetValue(),
               bloat_elem=self.elem_int_ctrl.GetValue(),
               elem_type=self.elem_list[self.elem_type_choice.GetSelection()].lower(),
               sharp_color=self.sharp_list[self.sharp_choice.GetSelection()].lower(),
               is_true_elem=self.elem_checkbox.IsChecked(),
               is_true_raw=True,
               ig_extract='triple up',
               buff_dict=copy.deepcopy(self.user_weapon.buff_dict)
            )

    def convert_true_raw(self,event):
        """
        Converts attack value shown from bloated to
        true when the "True?" checkbox is ticked.
        """

        if self.raw_checkbox.IsChecked(): #Convert to true
            self.raw_int_ctrl.SetValue(int(self.user_weapon.true_raw))
        else: #Set Bloated value
            self.raw_int_ctrl.SetValue(int(self.user_weapon.true_raw*self.user_weapon.get_class_mod()))
    
    def convert_true_elem(self,event):
        """
        Converts attack value shown from bloated to
        true when the "True?" checkbox is ticked.
        """

        if self.elem_checkbox.IsChecked(): #Convert to true
            self.elem_int_ctrl.SetValue(int(self.user_weapon.true_elem))
        else: #Set Bloated value
            self.elem_int_ctrl.SetValue(int(self.user_weapon.true_elem*10))

    def sharp_select(self,event):
        """
        Updates the sharpness modifiers for a selected
        sharpness color
        """

        #Get the index from current selection
        index=self.sharp_choice.GetSelection()

        #Update sharpness modifiers
        self.user_weapon.update_sharpness(self.sharp_list[index].lower())
        #Backend uses lowercase names

        #Update damage_grid
        self.update_damage_grid()
    
    def elem_type_select(self,event):
        """
        Updates the elem_type (None,'fire','water', 'thunder',
        'ice' or 'dragon') of the current weapon
        """

        #Get index from the choice
        index=self.elem_type_choice.GetSelection()

        #Index 0 is no element
        if (index==0):
            self.user_weapon.elem_type=None
        else:
            self.user_weapon.elem_type=self.elem_list[index].lower()
            #lowercase names are used interally

        #Update damage_grid
        self.update_damage_grid()

    def specific_select(self,event):
        """
        Updates specific weapon choices for SA, CB, IG and LS
        """

        #Get index from the choice
        index=self.specific_choice.GetSelection()

        if (self.user_weapon.weapon_type=='sa'): #For SA
            self.user_weapon.update_phial(self.specific_sa_list[index].lower())
            #lowercase names are used interally
        
        elif (self.user_weapon.weapon_type=='cb'): #For CB
            self.user_weapon.update_phial(self.specific_cb_list[index].lower())
        
        elif (self.user_weapon.weapon_type=='ls'): #For LS
            self.user_weapon.set_ls_gauge(self.specific_ls_list[index].lower())
        
        elif (self.user_weapon.weapon_type=='ig'): #For IG
            self.user_weapon.extract_extracts(self.specific_ig_list[index].lower())
        
        #Update damage_grid
        self.update_damage_grid()

    def specific_check1(self,event):
        """
        Updates specific weapon choices for SA, CB and HH
        """

        #Get index from the choice
        index=self.specific_choice.GetSelection()

        if (self.user_weapon.weapon_type=='hammer'): #For Hammer
            self.user_weapon.set_power_charge(self.specific_checkbox1.IsChecked())
        
        elif (self.user_weapon.weapon_type=='cb'): #For CB
            self.user_weapon.update_shield(self.specific_checkbox1.IsChecked())
            #To do

        elif (self.user_weapon.weapon_type=='hh'): #For HH
            pass
            #To do

        #Update damage grid
        self.update_damage_grid()

    def specific_check2(self,event):
        """
        Updates Power Axe information for CB
        """

        #Get index from the choice
        index=self.specific_choice.GetSelection()

        self.user_weapon.update_power(self.specific_checkbox2.IsChecked())

        #Update damage grid
        self.update_damage_grid()
    
    def set_attack(self,event):
        """
        Sets the weapon attack value as the input value
        Will also update the final value with skills, etc once those are implemented
        """

        #Check if the given value is in bonds. Only has a minimum value
        if not self.raw_int_ctrl.IsInBounds(): #if it isn't, fix it
            self.raw_int_ctrl.SetValue(self.raw_int_ctrl.GetMin()) #Get the minium raw

        #Update true attack value on weapon
        self.user_weapon.update_attack(self.raw_int_ctrl.GetValue(),self.raw_checkbox.IsChecked())

        #Update damage_grid
        self.update_damage_grid()

    def set_element(self,event):
        """
        Sets the weapon element value as the input value
        Will also update the final value with skills, etc once those are implemented
        """

        #Check if the given value is in bonds. Only has a minimum value
        if not self.elem_int_ctrl.IsInBounds(): #if it isn't, fix it
            self.elem_int_ctrl.SetValue(self.elem_int_ctrl.GetMin()) #Get the minium raw

        #Update true element value on weapon
        self.user_weapon.update_element(self.elem_int_ctrl.GetValue(),self.elem_checkbox.IsChecked())

        #Update damage_grid
        self.update_damage_grid()

    def set_affinity(self,event):
        """
        Sets the weapon affinity value as the input value
        Will also update the final value with skills, etc once those are implemented
        """

        #Check if the given value is in bonds. Has min and max.
        if not self.aff_int_ctrl.IsInBounds(): #if it isn't in-bounds, fix it
            #If below the minimum value, set minimum
            if self.aff_int_ctrl.GetValue() < self.aff_int_ctrl.GetMin():
                self.aff_int_ctrl.SetValue(self.aff_int_ctrl.GetMin()) #Get the minium raw
            else: #OTherwise, set maximum
                self.aff_int_ctrl.SetValue(self.aff_int_ctrl.GetMax())
        #Update the affinity value on the weapon
        self.user_weapon.update_affinity(self.aff_int_ctrl.GetValue())
    
        #Update damage_grid
        self.update_damage_grid()

    def hitzone_select(self,event):
        """
        Sets the clicked hitzone as the selected hitzone.
        Works for clicking any HZV (raw or elemental) for a given hitzone
        ie checks for the ROW in the self.monster_grid!
        """
    
        #Get selected row
        if event:
            row=event.GetRow()
        else:
            row=0 #Default to 0
            self.monster_grid.SelectRow(row)

        #Check selected row against currently targeted hitzone
        #Only select another hitzone if they're different
        if (row != self.target_monster.target_hitzone or not event):
            #Reset the tenderized checkbox, if needed
            if self.hitzone_checkbox.IsChecked(): #If checked
                self.hitzone_checkbox.SetValue(False) #Uncheck
                self.toggle_tenderize(None)      #Toggle is_tenderized

            #Check for tenderize group 0, which cannot be tenderized.
            #Is group 0, disable Tenderize button. Otherwise, enable
            if self.monster_grid.GetCellValue(row,11)=='0':
                self.hitzone_checkbox.Disable()
            else:
                self.hitzone_checkbox.Enable()

            #Set cell values in self.hitzone_grid
            for i in range(2):
                self.hitzone_grid.SetCellValue(0,i,self.monster_grid.GetCellValue(row,i))
            
            #Refresh
            self.hitzone_grid.Refresh()

            #Set the targeted hitzone in the Monster object
            self.target_monster.set_target_hitzone(row) #Each row corresponds to a hitzone

        #Update damage_grid
        self.update_damage_grid()

    def toggle_rage(self,event):
        """
        Toggles rage status from the monster
        """

        self.target_monster.toggle_rage()

        #Update damage_grid
        self.update_damage_grid()

    def toggle_tenderize(self,event):
        """
        Toggles tenderize status from the selected hitzone
        Also updates the hitzone table with tenderized values
        """

        #self.target_monster.target_hitzone corresponds to a row in self.monster_grid
        row=self.target_monster.target_hitzone
        
        #Toggling tenderize status
        self.target_monster.get_hitzone(row).toggle_tenderize()

        #Tenderize group
        tender_group=(self.monster_grid.GetCellValue(row,11))
        
        #Check for tender_group !=0.
        #tender_group == 0 can't be tenderized!

        if tender_group=='0': #For group 0, uncheck and do nothing
            self.hitzone_checkbox.SetValue(False)
        
        else: #For other groups, tenderize
        #Toggle tenderized HZVs for all hitzones of the same
        
            for i in range(self.monster_grid.GetNumberRows()):
                if (self.monster_grid.GetCellValue(i,11)==tender_group):
                    
                    if self.target_monster.get_hitzone(row).is_tenderized: 
                        self.monster_grid.SetCellValue(i,2,str(self.target_monster.hitzones[i].raw_tenderized['cut']))
                        self.monster_grid.SetCellValue(i,3,str(self.target_monster.hitzones[i].raw_tenderized['impact']))
                        self.monster_grid.SetCellValue(i,4,str(self.target_monster.hitzones[i].raw_tenderized['shot']))
                    else:
                        self.monster_grid.SetCellValue(i,2,str(self.target_monster.hitzones[i].raw['cut']))
                        self.monster_grid.SetCellValue(i,3,str(self.target_monster.hitzones[i].raw['impact']))
                        self.monster_grid.SetCellValue(i,4,str(self.target_monster.hitzones[i].raw['shot']))

        #Update damage_grid
        self.update_damage_grid()

    def add_attack(self,event):
        """
        Adds the selected attack to the current
        weapon combo. Also displays the attack
        name in the damage_grid grid.
        """

        # try: #May get an error if there are too many rows
        #Get the index of the selection
        index=self.attack_choice.GetSelection()

        #Update combo
        self.user_weapon.append_combo(index)

        # #Write name to damage_grid
        # #Row index comes from the length of the combo list
        # row=len(self.user_weapon.attack_combo)-1
        # self.damage_grid.SetCellValue(row,0,self.user_weapon.attack_combo[row].name)

        #Update damage_grid
        self.update_damage_grid()

        # except: #Simply do not do anything in that case
        #     pass
    
    def update_damage_grid(self):
        """
        calc is a Damage_Number object

        calc_type must be set as 'normal', 'critical' or
        'average' to determine which damage to return
        """

        #Recalculate damage
        #self.calc_type is updated via the calculation_select
        #function, which is called when an option
        #from the drop-down menu is chosen.
        self.user_weapon.damage_calculation(self.target_monster,self.calc_type)

        #self.user_weapon.damage_calcualtion is a list of lists. 
        # Each item in it is a list of damage values in the 
        # form 
        # (attack object, raw dmg,elem dmg,fixed dmg,total dmg)

        #Also calculate total damage per column
        total_damage=['TOTAL DAMAGE',0,0,0]

        #Organized as raw total, elem total, fixed total and
        #"total total"
        max_rows=len(self.user_weapon.attack_combo)

        for i in range(max_rows):
            row_total=0
            for j in range(4):   
                if j>0: #Damage numbers
                    self.damage_grid.SetCellValue(i,j,str(self.user_weapon.attack_combo[i][j]))
                    total_damage[j]+=self.user_weapon.attack_combo[i][j]
                else: #Name
                    self.damage_grid.SetCellValue(i,j,self.user_weapon.attack_combo[i][j].name)
                             
        try:
            #Create final row of total damage
            for i in range(4):
                if i > 0: #damage numbers
                    self.damage_grid.SetCellValue(max_rows,i,str(total_damage[i]))
                else: #TOTAL DAMAGE label
                    self.damage_grid.SetCellValue(max_rows,i,'TOTAL DAMAGE: ')
        except: #If there is an error, simply don't display total damage.
            pass
            

        #Update EFR and EFE calculations. Update capped affinity.
        self.efr_int_ctrl.SetValue(round(self.user_weapon.get_efr()))
        self.efe_int_ctrl.SetValue(round(self.user_weapon.get_efe()))
        self.efa_int_ctrl.SetValue(round(100*(min(max(-1,self.user_weapon.aff_final),1))))
    
    def clear_all(self,event):
        """
        Clears all attacks from the current combo
        """

        #Clear the combo in the weapon object
        self.user_weapon.delete_combo()

        #Clear the damage_grid:
        self.damage_grid.ClearGrid()

        #Update damage_calc:
        self.update_damage_grid()
        
    def calculation_select(self,event):
        """
        Updates the calculation type ('average', 'normal' or 'crit')
        for a given choice in the drop-down menu
        """

        #Get the index from current selection
        index=self.damage_choice.GetSelection()

        #Update self.calc_type accordingly
        if index<2: #First two options
            self.calc_type=self.damage_options[index].lower() #backend uses lowercase names
            
        else: #third option
            self.calc_type='crit' #'crit' also encompasses Feeble hits
                                #backend has 'crit' option, not 'crit/feeble'

        #Update damage calculations accordingly
        self.update_damage_grid()

    def open_skill_window(self,event):
        """
        Opens new window for active skill and item buff
        selection
        """
        self.skill_window=BuffWindow(self.user_weapon,self.update_damage_grid)
        self.skill_window.Show()

    def save_combo(self,event):
        """
        Saves the current combo to a .cmb file
        """

        to_save=[] #empty list

        #This will save only the attack indexes.
        #Append the index of each attack in the current combo
        for attack in self.user_weapon.attack_combo:
            to_save.append(str(self.user_weapon.attack_list.index(attack[0].name)))

        #Convert to string
        to_save=','.join(to_save)
        
        #Get extension from weapon type
        ext=self.user_weapon.weapon_type

        #Pop up window to save
        with wx.FileDialog(self, "Save current combo", 
                           wildcard=ext+" files (*."+ext+")|*."+ext,
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                           defaultDir='.\datafiles\saved_combos') as dlg:

            if dlg.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            pathname = dlg.GetPath()
            try:
                with open(pathname, 'w') as file:
                    file.write(to_save)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    def load_combo(self,event):
        """
        Loads a previously saved combo from a .weapon_type file
        """

        #Get extension from weapon type
        ext=self.user_weapon.weapon_type
        with wx.FileDialog(self, "Open combo file", 
                           wildcard=ext+" files (*."+ext+")|*."+ext,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
                           defaultDir='.\datafiles\saved_combos') as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r') as file:
                    string_combo=list(csv.reader(file))[0] #Only 1 row
                    int_combo=[]
                    
                    for item in string_combo:
                        int_combo.append(int(item))

                    #Update attack combo
                    self.user_weapon.append_combo(int_combo)

                    #Update damage grid
                    self.update_damage_grid()

            except IOError:
                wx.LogError("Cannot open file '%s'." % newfile)

    def save_buffs(self,event):
        """
        Saves the currently selected buffs
        from skills, items, canteen, melody, etc
        """
        pass

    def load_buffs(self,event):
        """
        Loads the currently selected buffs
        from skills, items, canteen, melody, etc
        """
        pass

    def clear_selected_attacks(self,event):
        """
        Clears selected attacks from the
        current combo
        """

        #Get selection
        selection=self.damage_grid.GetSelectedRows()
        
        #Clear selection from combo
        self.user_weapon.delete_from_combo(selection)

        #Update damage grid
        self.damage_grid.ClearGrid()
        self.update_damage_grid()

    def OnMotion(self, event):
    # just trap this event and prevent it from percolating up the window hierarchy
        pass

class FrameWithForms(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(FrameWithForms, self).__init__(*args, **kwargs)
        notebook = wx.Notebook(self)
        form1 = MainWindow(notebook)
        form2 = MainWindow(notebook)
        form3 = MainWindow(notebook)
        notebook.AddPage(form1, 'Tab1')
        notebook.AddPage(form2, 'Tab2')
        notebook.AddPage(form3, 'Tab3')
        self.SetClientSize(notebook.GetBestSize()) 

class BuffWindow(wx.Frame):
    def __init__(self,weapon,update_function):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Skills and Items")

        self.SetBackgroundColour('white')

        #Pass weapon object to this window
        self.buff_weapon=weapon

        #Store function for updating damage grid
        self.update_grid=update_function

        self.createControls()
        # self.bindEvents()
        # self.doLayout()

    def createControls(self):
        
        """
        Encapsulate all kinds of buffs in dictionaries
        and place corresponding widgets.
        """

        #Main box is a gridbagsizer
        self.main_box=wx.BoxSizer(orient=wx.VERTICAL)
        self.top_box=wx.GridBagSizer(hgap=5,vgap=10)

        ######################################
        ##      SKILL LIST
        ######################################    
     
        #Empty dictionaries to start
        self.skill_labels={}
        self.skill_choices={}

        #Create a header label for these buffs
        self.skill_main=wx.StaticText(self, label="OFFENSIVE SKILLS")

        #Place it
        self.top_box.Add(self.skill_main,pos=(0,7),span=(1,2),flag=wx.ALIGN_CENTER)
        
        #Place the skill choice menus
        self.place_buffs(buff_dict=skill_dict,
                         label_dict=self.skill_labels,
                         choice_dict=self.skill_choices,
                         col_elem=5,
                         row_offset=1,
                         col_offset=0)

        #Disable skills not yet implemented        
        for todo in not_implemented_skills:
            self.skill_choices[todo].Disable()

        ######################################
        ##      ITEM
        ###################################### 

        #Empty dictionaries to start
        self.item_labels={}
        self.item_choices={}

        #Create a header label for these buffs
        self.item_main=wx.StaticText(self, label="ITEM BUFFS")

        #Place it
        self.top_box.Add(self.item_main,pos=(6,2),span=(1,3),flag=wx.ALIGN_CENTER)
        
        #Place the item choice menus
        self.place_buffs(buff_dict=item_dict,
                         label_dict=self.item_labels,
                         choice_dict=self.item_choices,
                         col_elem=3,
                         row_offset=7,
                         col_offset=0)

        ######################################
        ##      CANTEEN
        ###################################### 

        #First, create a dictionary for canteen buffs
        #Form: canteen_Name:(Skill_Function,[option1,option2,...])
      
        #Empty dictionaries to start
        self.canteen_labels={}
        self.canteen_choices={}

        #Create a header label for these buffs
        self.canteen_main=wx.StaticText(self, label="CANTEEN SKILLS              ")

        #Place it
        self.top_box.Add(self.canteen_main,pos=(6,8),span=(1,3),flag=wx.ALIGN_CENTER)
        
        #Place the canteen choice menus
        self.place_buffs(buff_dict=canteen_dict,
                         label_dict=self.canteen_labels,
                         choice_dict=self.canteen_choices,
                         col_elem=3,
                         row_offset=7,
                         col_offset=6)
    
        #Disable skills not yet implemented        
        for todo in not_implemented_canteen:
            self.canteen_choices[todo].Disable()

        ######################################
        ##      HUNTING HORN SONGS
        ###################################### 
        
        #Empty dictionaries to start
        self.song_labels={}
        self.song_choices={}

        #Create a header label for these buffs
        self.song_main=wx.StaticText(self, label="HUNTING HORN SONGS")

        #Place it
        self.top_box.Add(self.song_main,pos=(6,13),span=(1,2),flag=wx.ALIGN_CENTER)
        
        #Place the canteen choice menus
        self.place_buffs(buff_dict=song_dict,
                         label_dict=self.song_labels,
                         choice_dict=self.song_choices,
                         col_elem=2,
                         row_offset=7,
                         col_offset=12)

        #Finish window
        self.main_box.Add(self.top_box)
        self.SetSizerAndFit(self.main_box) 

    def add_buff(self,event):
        """
        Sends selected buffs to the buff_dict of the current
        user_weapon
        """
        #Get the choice object that called the event
        choice=event.GetEventObject()

        #Add appropriate buff. Current selection corresponds
        #to level
        self.buff_weapon.update_buff_dict(choice.BuffName,choice.GetSelection())

        #Update damage grid
        self.update_grid()                             

    def place_buffs(self,buff_dict,label_dict,choice_dict,col_elem,row_offset,col_offset):
        """
        Places the buff choice menus in the skills & itens window
        Inputs:
        buff_dict: dictionary where keys are strings with the
        buff's name, values are tuples in the form
        (Buff_function,Max_Buff_Level) or
        (Buff_function,[Buff_Option1,Buff_Option2,...])

        label_dict: empty dictionary where label buffs will be stored

        choice_dict: same, but for wx.Choice objects

        col_elem: how many elements will be per column

        row_offset, col_offset: offsets in the window
        """
        
        buffcount=1
        for name,skill_info in buff_dict.items():
            #Auxiliary variables for readability
            function=skill_info[0] #Function that represents the skill
            level=skill_info[1]    #Level of some kind, determines choics
            
            #Create label objects
            label_dict[name]=wx.StaticText(self,label=name+":")
            
            #Create choice. Two different kinds of choices
            if type(level)==int: #Skill levels
                choice_dict[name]=wx.Choice(self,choices=[str(i) for i in range(level+1)])        
            else: #List is already made
                choice_dict[name]=wx.Choice(self,choices=level)

            #Default selection to skill level stored in the
            #user_weapon object
            if (function in self.buff_weapon.buff_dict):
                choice_dict[name].SetSelection(self.buff_weapon.buff_dict[function])
            else:
                choice_dict[name].SetSelection(0)

            #Associate choice object to the respective skill
            choice_dict[name].BuffName=function

            #Bind to function to add buffs to user_weapon
            choice_dict[name].Bind(wx.EVT_CHOICE,self.add_buff)
            
            #Create an empty space label
            empty=wx.StaticText(self,label='            ')
            
            #Add to main_box sizer
            row=(buffcount - 1) % col_elem + row_offset 
            col=int((buffcount-1)/ col_elem)*3 + 1 + col_offset

            #If col==1, add empty space to the left
            if col==1:
                empty2=wx.StaticText(self,label='            ')
                self.top_box.Add(empty2,pos=(row,col-1))  
            self.top_box.Add(label_dict[name],pos=(row,col))
            self.top_box.Add(choice_dict[name],pos=(row,col+1),flag=wx.EXPAND)
            self.top_box.Add(empty,pos=(row,col+2))
            
            # empty.Hide()
            buffcount+=1
if __name__ == '__main__':                  
    app = wx.App(0)
    frame = FrameWithForms(None, title='Cissa Damage Calculator')
    frame.Show()
    app.MainLoop()