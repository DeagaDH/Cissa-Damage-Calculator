from weapon_class import *

class Blademaster(Weapon):
    """
    Sub-class from Weapon for Blademaster weapons.
    Do not use directly; instead, create an object for a specific weapon type.
    In addition to information stored in the Weapon class, also 
    stores information on element value and type (fire, etc) and sharpness.

    elem_type must be None, 'fire, 'water', 'thunder',
    'ice' or 'dragon'

    sharp_color must be 'red', 'orange', 'yellow', 'green', 'blue',
    'white' or 'purple'
    """

    def __init__(self,bloat_attack=300,affinity=0,bloat_elem=0,buff_dict={},
                 elem_type=None,sharp_color='white',is_true_raw=True,is_true_elem=True):
        #Initialize parent class
        Weapon.__init__(self,bloat_attack,affinity,is_true_raw,buff_dict)
        
        #Store true element and element type
        
        #Check for true element value
        if is_true_elem:
            self.true_elem=bloat_elem
        else:
            self.true_elem=bloat_elem/10
        self.true_elem_final=self.true_elem #May be updated with elem buffs from skills, etc
        self.elem_type=elem_type

        #Store the sharpness values:
        self.update_sharpness(sharp_color)

    def update_element(self, elem_value, is_true=False):
        """
        Updates the stored true_elem value for
        a given new attack value.
        Optional argument "is_true" for instances when true_raw
        is given directly.

        NEED TO IMPLEMENT ELEMENT BOOSTING SKILLS!
        """

        if is_true:  #If true, directly update
            self.true_elem=elem_value
        else: #Else, divide by 10
            self.true_elem=elem_value/10
        
        #Update the final value (after buffs)
        self.true_elem_final=self.true_elem #2DO

    def update_sharpness(self, sharp_color):
        """
        Update the two sharpness modifier (raw and element)
        for a given new sharpness color
        """

        sharp_mods=self.sharpness_modifier(sharp_color) #sharpness_modifier returns a tuple in the form (sharp_raw,sharp_elem)
        self.sharp_raw=float(sharp_mods[0])   #Save values separately for readability and ease of use
        self.sharp_elem=float(sharp_mods[1])

        #Also update the current attack_combo to take this into account
        self.update_combo()
        
    def sharpness_modifier(self,color,sharp_mod_file='datafiles\\weapon\\sharpcolors.csv'):
        """
        Returns the raw and elemental sharpness modifiers for a given sharpness color. Checks values on sharpcolors.csv
        The returned object is a tuple in the form (raw_sharp_modifier,elem_sharp_modifier)
        The should be organized as:
        COLOR,RAW SHARP MOD,ELEM SHARP MOD
        on each line
        """

        with open(sharp_mod_file,'r') as file:
            sharp_source=csv.reader(file) #Open the file as a csv

            for row in sharp_source: #Check all rows for the sharpness color
                if (row[0]==color): #First value is the sharpness color
                    return row[1:]     #Return the rest of the line as the sharp mods

class GreatSword(Blademaster):
    """
    Class specific to GreatSword weapons.
    Sub-class of Blademaster, which is a sub-class of Weapon

    Does not hold much extra information, only specific GS
    class_mod, attacks and crit_mod_elem (when implemented)
    """

    def __init__(self,bloat_attack=300,affinity=0,bloat_elem=0,elem_type=None,
                 sharp_color='white',is_true_elem=True,is_true_raw=True,buff_dict={}):
        #Initialize parent class
        Blademaster.__init__(self,bloat_attack,affinity,bloat_elem,buff_dict,
                             elem_type,sharp_color,is_true_raw,is_true_elem)

        #Store GS weapon type
        self.weapon_type='gs'

        #Correct bloat attack to true value if needed
        if not is_true_raw:
            self.true_raw=self.true_raw/self.get_class_mod()
                        
        #Update crit mod for elements (when CE and TCE are implemented!)
        self.crit_mod_elem=1.0

        #Update self.attack_list with GS attacks.
        self.set_attack_list()

class LongSword(Blademaster):
    """
    Class specific to Long Sword weapons.
    Sub-class of Blademaster, which is a sub-class of Weapon

    Holds extra information on class mod, LS's attacks and LS's 
    spirit gauge. Also uses Special LongSwordAttack objects due to special
    properties on said attacks.
    """

    def __init__(self,bloat_attack=300,affinity=0,bloat_elem=0,elem_type=None,
                 sharp_color='white',is_true_elem=True,is_true_raw=True,buff_dict={},ls_gauge='red'):
        #Initialize parent class
        Blademaster.__init__(self,bloat_attack,affinity,bloat_elem,buff_dict,
                             elem_type,sharp_color,is_true_raw,is_true_elem)
        #Store Hammer weapon type
        self.weapon_type='ls'

        #Correct bloat attack to true value if needed
        if not is_true_raw:
            self.true_raw=self.true_raw/self.get_class_mod()

        #Update crit mod for elements (when CE and TCE are implemented!)
        self.crit_mod_elem=1.0

        #Update self.attack_list with Hammer attacks.
        self.set_attack_list()

        #Set LS's gauge colors as a weapon_raw_mod.
        self.set_ls_gauge(ls_gauge)

        #Store specific attack class for this weapon
        self.attack_class=LongSwordAttack

    def set_ls_gauge(self,ls_gauge='red',file_path='datafiles\\weapon\\'):
        """
        Sets the Spirit Gauge Buff from LS's Spirit Gauge.
        """

        #Extract the extract buff
        with open(file_path+"ls_colors.csv",'r') as file:
            ls_source=csv.reader(file) #Open the file as a csv

            for row in ls_source: #Check all rows for the sharpness color
                if (row[0]==ls_gauge): #First value is the sharpness color
                    self.weapon_raw_mod = float(row[1])     #Return the rest of the line as the sharp mods

        #Apply it to the weapon
        self.apply_weapon_buffs()            

        #Also update the current attack_combo to take this into account
        self.update_combo()

    def add_extra(self,attribute_list):
        """
        Adds extra parameters to the given attribute_list and returns it.
        Overrides base Weapon class function to add Spirit Gauge buff
        value, stored in self.weapon_raw_mod
        """
        #Append to attribute list
        attribute_list.append(self.weapon_raw_mod)

        # Return it
        return attribute_list

class SwordNShield(Blademaster):
    """
    Class specific to SwordNShield weapons.
    Sub-class of Blademaster, which is a sub-class of Weapon

    Does not hold much extra information, only specific SnS
    class_mod, attacks and crit_mod_elem (when implemented)
    """

    def __init__(self,bloat_attack=300,affinity=0,bloat_elem=0,elem_type=None,
                 sharp_color='white',is_true_elem=True,is_true_raw=True,buff_dict={}):
        #Initialize parent class
        Blademaster.__init__(self,bloat_attack,affinity,bloat_elem,buff_dict,
                             elem_type,sharp_color,is_true_raw,is_true_elem)

        #Store SnS weapon type
        self.weapon_type='sns'

        #Correct bloat attack to true value if needed
        if not is_true_raw:
            self.true_raw=self.true_raw/self.get_class_mod()

        #Update crit mod for elements (when CE and TCE are implemented!)
        self.crit_mod_elem=1.0

        #Update self.attack_list with SnS attacks.
        self.set_attack_list()    

class DualBlades(Blademaster):
    """
    Class specific to Dual Blades weapons.
    Sub-class of Blademaster, which is a sub-class of Weapon

    In addition to specific DB class mod and attacks, hits class
    also uses a special DualBladesAttack class for its special properties.
    """

    def __init__(self,bloat_attack=300,affinity=0,bloat_elem=0,elem_type=None,
                 sharp_color='white',is_true_elem=True,is_true_raw=True,buff_dict={}):
        #Initialize parent class
        Blademaster.__init__(self,bloat_attack,affinity,bloat_elem,buff_dict,
                             elem_type,sharp_color,is_true_raw,is_true_elem)
        #Store Lance weapon type
        self.weapon_type='db'

        #Correct bloat attack to true value if needed
        if not is_true_raw:
            self.true_raw=self.true_raw/self.get_class_mod()

        #Update crit mod for elements (when CE and TCE are implemented!)
        self.crit_mod_elem=1.0

        #Update self.attack_list with Lance attacks.
        self.set_attack_list()

        #Store specific attack class for this weapon
        self.attack_class=DualBladesAttack

class Lance(Blademaster):
    """
    Class specific to Lance weapons.
    Sub-class of Blademaster, which is a sub-class of Weapon

    Does not hold much extra information, only specific Lance
    class_mod, attacks and crit_mod_elem (when implemented)
    """

    def __init__(self,bloat_attack=300,affinity=0,bloat_elem=0,elem_type=None,
                 sharp_color='white',is_true_elem=True,is_true_raw=True,buff_dict={}):
        #Initialize parent class
        Blademaster.__init__(self,bloat_attack,affinity,bloat_elem,buff_dict,
                             elem_type,sharp_color,is_true_raw,is_true_elem)
        #Store Lance weapon type
        self.weapon_type='lance'

        #Correct bloat attack to true value if needed
        if not is_true_raw:
            self.true_raw=self.true_raw/self.get_class_mod()

        #Update crit mod for elements (when CE and TCE are implemented!)
        self.crit_mod_elem=1.0

        #Update self.attack_list with Lance attacks.
        self.set_attack_list()

class Hammer(Blademaster):
    """
    Class specific to Hammer weapons.
    Sub-class of Blademaster, which is a sub-class of Weapon

    Does not hold much extra information, only specific Hammer
    class_mod and attacks
    """

    def __init__(self,bloat_attack=300,affinity=0,bloat_elem=0,elem_type=None,
                 sharp_color='white',is_true_elem=True,is_true_raw=True,
                 power_charge=True,buff_dict={}):
        #Initialize parent class
        Blademaster.__init__(self,bloat_attack,affinity,bloat_elem,buff_dict,
                             elem_type,sharp_color,is_true_raw,is_true_elem)
        #Store Hammer weapon type
        self.weapon_type='hammer'

        #Correct bloat attack to true value if needed
        if not is_true_raw:
            self.true_raw=self.true_raw/self.get_class_mod()

        #Update crit mod for elements (when CE and TCE are implemented!)
        self.crit_mod_elem=1.0

        #Update self.attack_list with Hammer attacks.
        self.set_attack_list()

        #Set Power Charge's buff
        self.set_power_charge(power_charge)

    def set_power_charge(self,is_power_charge):
        """
        Set the Power Charge buff for Hammer
        in self.weapon_raw_buff
        """

        if is_power_charge:
            self.weapon_raw_buff=1.07
        else:
            self.weapon_raw_buff=1.00

        #Apply it to the weapon
        self.apply_weapon_buffs()

class InsectGlaive(Blademaster):
    """
    Class specific to Insect Glaive weapons.
    Sub-class of Blademaster, which is a sub-class of Weapon

    Holds extra information on class mod, IG attacks and extracts
    """

    def __init__(self,bloat_attack=300,affinity=0,bloat_elem=0,elem_type=None,
                 sharp_color='white',is_true_elem=True,is_true_raw=True,ig_extract='triple up',buff_dict={}):
        #Initialize parent class
        Blademaster.__init__(self,bloat_attack,affinity,bloat_elem,buff_dict,
                             elem_type,sharp_color,is_true_raw,is_true_elem)
        #Store Hammer weapon type
        self.weapon_type='ig'

        #Correct bloat attack to true value if needed
        if not is_true_raw:
            self.true_raw=self.true_raw/self.get_class_mod()

        #Update crit mod for elements (when CE and TCE are implemented!)
        self.crit_mod_elem=1.0

        #Update self.attack_list with Hammer attacks.
        self.set_attack_list()

        #Set IG's extracts as a weapon_raw_mod.
        self.extract_extracts(ig_extract)

    def extract_extracts(self,ig_extract,ig_mod_file='datafiles\\weapon\\ig_extracts.csv'):
        """
        Extracts the buff relative to IG extracts from a file
        and sets as self.weapon_raw_mod.

        Yeah, I'm funny.
        """

        #Extract the extract buff
        with open(ig_mod_file,'r') as file:
            ig_source=csv.reader(file) #Open the file as a csv

            for row in ig_source: #Check all rows for the extract
                if (row[0]==ig_extract): #First value is the buff
                    self.weapon_raw_mod = 1.10

        #Apply it to the weapon
        self.apply_weapon_buffs()

class SwitchAxe(Blademaster):
    """
    Class specific to Switch Axe weapons.
    Sub-class of Blademaster, which is a sub-class of Weapon

    In addition to regular Blademaster information, also holds
    information on the SA class mod, phial type and, if required,
    Dragon element value from phial.
    """

    def __init__(self,bloat_attack=300,affinity=0,bloat_elem=0,elem_type=None,
                 sharp_color='white',is_true_elem=True,is_true_raw=True,
                 sa_phial='power',sa_dragon=0,buff_dict={}):
        #Initialize parent class
        Blademaster.__init__(self,bloat_attack,affinity,bloat_elem,buff_dict,
                             elem_type,sharp_color,is_true_raw,is_true_elem)
        #Store Switch Axe weapon type
        self.weapon_type='sa'

        #Correct bloat attack to true value if needed
        if not is_true_raw:
            self.true_raw=self.true_raw/self.get_class_mod()

        #Update crit mod for elements (when CE and TCE are implemented!)
        self.crit_mod_elem=1.0

        #Update self.attack_list with Switch Axe attacks.
        self.set_attack_list()    

        #Store phial type
        self.sa_phial=sa_phial

        #Dragon value from Dragon Phials. Implement later.
        self.sa_dragon=sa_dragon

        #Store specific attack class for this weapon
        self.attack_class=SwitchAxeAttack

    def update_phial(self,new_phial,file_path='datafiles\\weapon\\attacks\\'):
        """
        Update phial type to new_phial
        """
        
        #Change phial type
        self.sa_phial=new_phial

        #Also update the current attack_combo to take this into account
        self.update_combo()

        #When the main program calls this function, it'll also update the damage grid
        #That also re-runs the damage calculation, so no need to run it here.                   

    def add_extra(self,attribute_list):
        """
        Adds extra parameters to the given attribute_list and returns it.
        Overrides base Weapon class function to add sa_phials
        """
        #Append to attribute_list
        attribute_list.append(self.sa_phial)

        #Return it
        return attribute_list

class ChargeBlade(Blademaster):
    """
    Class specific to Switch Axe weapons.
    Sub-class of Blademaster, which is a sub-class of Weapon

    In addition to regular Blademaster information, also holds
    information on the CB class mod, phial type, shield charge
    and power axe (or savage axe) status
    """

    def __init__(self,bloat_attack=300,affinity=0,bloat_elem=0,elem_type=None,
                 sharp_color='white',is_true_elem=True,is_true_raw=True,
                 cb_phial='impact',cb_shield=True,cb_power=False,buff_dict={}):
        #Initialize parent class
        Blademaster.__init__(self,bloat_attack,affinity,bloat_elem,buff_dict,
                             elem_type,sharp_color,is_true_raw,is_true_elem)
        #Store Switch Axe weapon type
        self.weapon_type='cb'

        #Correct bloat attack to true value if needed
        if not is_true_raw:
            self.true_raw=self.true_raw/self.get_class_mod()

        #Update crit mod for elements (when CE and TCE are implemented!)
        self.crit_mod_elem=1.0

        #Update self.attack_list with Switch Axe attacks.
        self.set_attack_list()    

        #Store phial type, shield charge and power axe status
        self.cb_phial=cb_phial
        self.cb_shield=cb_shield
        self.cb_power=cb_power

        #Store specific attack class for this weapon
        self.attack_class=ChargeBladeAttack

    def update_phial(self,new_phial,file_path='datafiles\\weapon\\attacks\\'):
        """
        Update phial type to new_phial
        """
        
        #Change phial type
        self.cb_phial=new_phial

        #Also update the current attack_combo to take this into account
        self.update_combo()

        #When the main program calls this function, it'll also update the damage grid
        #That also re-runs the damage calculation, so no need to run it here.                   
    
    def update_shield(self,new_shield,file_path='datafiles\\weapon\\attacks\\'):
        """
        Update Shield Charge status (True/False) to new_shield
        """
        
        #Change phial type
        self.cb_shield=new_shield

        #Also update the current attack_combo to take this into account
        self.update_combo()

        #When the main program calls this function, it'll also update the damage grid
        #That also re-runs the damage calculation, so no need to run it here. 

    def update_power(self,new_power,file_path='datafiles\\weapon\\attacks\\'):
        """
        Update Power Axe status (True/False) to new_shield
        """
        
        #Change phial type
        self.cb_power=new_power

        #Also update the current attack_combo to take this into account
        self.update_combo()

        #When the main program calls this function, it'll also update the damage grid
        #That also re-runs the damage calculation, so no need to run it here. 

    def add_extra(self,attribute_list):
        """
        Adds extra parameters to the given attribute_list and returns it.
        Overrides base Weapon class function to add sa_phials
        """
        #Append to attribute_list
        attribute_list.extend([self.cb_phial,self.cb_shield,self.cb_power,self.sharp_raw,self.sharp_elem])

        #Return it
        return attribute_list

    def damage_calculation(self,target_monster,calc_type='average'):
        """
        CB gets its own damage_calculation function due to the weird
        interaction between Impact Phials and Attack boosting skills.
        Couldn't quite figure out how to implement this in the general
        damage_calculation function due to generic Attacks not having
        the Phial attribute. Inputs are the same as the generic function:

        target_monster: a Monster object
                        target hitzone data is extracted from it.

        Three different 'calc types' are possible:
        
        normal: returns que regular non-critical damage
        
        crit: returns the critical hit damage, or feeble hit damage if Affinity < 0

        average: average between 'normal' and 'crit' damage, pondered by Affinity.
                    for negative affinity, ponder by absolute (ie positive) value.
                    Negative affinity is treated as a different crit mod.
        """

        #Apply relevant buffs
        self.apply_buffs()

        #Extract data from the monster
        #Also applies Agitator if required and enraged
        temp_mon=self.get_monster_data(target_monster)
        raw_HZ=temp_mon[0]
        elem_HZ=temp_mon[1]
        rage_mod=temp_mon[2]

        #Iterate through attack_combo to obtain all damage values
        for attack in self.attack_combo:
            #Check for Phial attacks
            if attack[0].is_phial: #Phial
                if self.cb_phial=='impact': #Impact
                    #Adjust raw value used for phial
                    phial_raw=self.true_raw+(self.true_raw_final-self.true_raw)/2 #Apply only half the boost from attack skills
                    
                    #Apply Artillery and Felyne Bombardier if needed
                    if Artillery in self.buff_dict:
                        phial_raw*=Artillery_Activate(self.buff_dict[Artillery])
                    if Felyne_Bombardier in self.buff_dict:
                        phial_raw*=Felyne_Bombardier_Activate(self.buff_dict[Felyne_Bombardier])

                    #Calculate damage.
                    attack[1]=self.impact_phial_number(attack[0],phial_raw,rage_mod)
                    attack[2]=0 #No elemental damage
                    attack[3]=attack[1]

                else: #Elemental
                    #No need to adjust any Elemental stats.
                    #however, crit_mod_elem is set to 1 as phials never crit

                    attack[1]=0 #No Raw damage
                    attack[2]=self.elem_number(attack[0],elem_HZ,1,rage_mod) #Use 1 as crit_mod as it never crits
                    attack[3]=attack[2]

            else: #All other attacks are calculated normally
                
                self.generic_calculation(attack,raw_HZ,elem_HZ,rage_mod,calc_type) 

    def impact_phial_number(self,attack,phial_raw,rage_mod):
        """
        Calculates Impact Phial damage. Inputs are:

        attack: an Attack object with information on the Attack being used.
                So far only checks for MV and damage type, but may carry additional
                information later.

        phial_raw: attack value used for the impact phial
                   Since Attack boosts scale only up to 50% with Impact Phials,
                   this will be different from the weapon's true raw if any
                   attack boost is used. Also considers Artillery and F. Bombardier.

        rage_mod: the current rage mod for the target monster
        """

        #Get damage type and MV data from the attack object
        mv=attack.mv
       
        #Apply possible raw multipliers (ie shield charge) from attack
        calc_raw=phial_raw*attack.true_raw_mult
        
        #Calculate raw damage. Currently missing practically all situational modifiers.
        #Round later. For total damage, raw and fixed damage are rounded together!
        return round(calc_raw * (mv/100.0) * rage_mod)