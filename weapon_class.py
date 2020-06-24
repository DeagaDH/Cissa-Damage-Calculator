# from monster_classes import * #Import all classes from monster_classes without requiring monster_classes.class
import csv #For reading CSV files for data
from monster_classes import *
from attack_classes import *
from skill_functions import * #Import skills, itens and canteen buffs

class Weapon:
    """
    Generic weapon class. Hold attributes and functions common to all weapon types.
    Do not use directly; instead, create an object for a specific weapon type.
    Each weapon will have its own sub-class.

    Necessary inputs for the generic weapon:

    bloat_attack: bloated attack value; corrected by each sub-class to true raw

    affinity: weapon's affinity value

    buff_dict: a dictionary containing all appliccable buffs. Entries are in the form
                buff_dict={BUFF 1: LEVEL, BUFF 2: LEVEL...} where BUFF
                can be due to a Skill, Item, HH Melody, etc

                Certain skills will be left outside the main list due to peculiar behavior.
                These will de applied separetely.

    Further information is supplied specifically to each subclass.

    Weapon has one subclass: Blademaster. Gunner to be implemented soon (tm)

    Blademaster then has 11 sub-classes, one for each BM weapon.
    """

    def __init__(self,bloat_attack=290,affinity=0,is_true_raw=True,
                 buff_dict={}):
        
        #Store the bloat_attack value
        if is_true_raw:
            self.true_raw=bloat_attack #If the value given is true
        else:
            self.true_raw=bloat_attack/self.get_class_mod()
        self.true_raw_final=self.true_raw #To be corrected via buffs later

        #Store affinity
        self.aff=affinity/100 #Store affinity as a decimal
        self.aff_final=self.aff #To be updated via skills later

        #Default elem_type and true_elem to None and 0
        self.elem_type=None
        self.true_elem=0

        #Store attack and elemental caps
        self.attack_cap=2.0*self.true_raw
        self.elem_cap=max(self.true_elem*1.6,self.true_elem+15)

        #Store default crit mods for the weapon
        self.crit_mod_raw=1.25
        self.crit_mod_elem=1.00
        
        #Create an empty list of attacks. Will be updated by subclasses, attack selection
        self.attack_list=[] #Must be overriden by sub-classes!

        #Have a list to store attack combos. Also stores damage from the attack once calculated
        #Format is [[Combo1],[Combo2],...], where each [Combo] list has
        #the format [Attack Object,Raw Damage, Elemental Damage, Fixed Damage]
        self.attack_combo=[]

        #Create variable for weapon_raw_mod.
        #This is used for raw mods that affect all moves from
        #some weapon, such as IG's extracts or LS's spirit gauge
        self.weapon_raw_mod=1

        #Default weapon_type to gs, change via sub-classes
        self.weapon_type='gs'

        #Placeholder sharpness modifiers
        #Set to avoid special cases for gunner weapon damage (no sharpness)
        #Will be modified on blademaster weapons
        self.sharp_raw=1
        self.sharp_elem=1

        #Specify attack class used by this weapon.
        #Set the default Attack class for generic weapons
        #May be overriden by subclasses
        self.attack_class=Attack
        
        #Store skill and item buffs
        self.buff_dict=buff_dict

    def get_class_mod(self,class_mod_file='datafiles\\weapon\\classmods.csv'):
        """
        Returns the class mod for a certain weapon. Checks values on classmods.csv. File should be organized as:
        WEAPON,CLASSMOD
        on each line

        Should be called only by the specific weapon sub-sub-class (ie GreatSword class, etc)
        """

        try:
            with open(class_mod_file,'r') as file:
                mod_source=csv.reader(file) #Open the file as a csv

                for row in mod_source: #Check all rows for the weapon type
                    if (row[0]==self.weapon_type): #First value is the type of weapon
                        return float(row[1]) #Second value is the desired mod
                        break #Leave loop after finding a match
        
        except: #Return 1 if an error occurs (ie calling with an invalid weapon type)
            return 1
    
    def update_attack(self, attack_value, is_true=False):
        """
        Updates the stored true attack values for
        a given new attack value.
        Optional argument "is_true" for instances when true_raw
        is given directly.

        self.class_mod() must be already by subclass!
        Should be fine if an object for a specific weapon is used
        (ie a GreatSword, etc object)
        NEED TO IMPLEMENT RAW BOOSTING SKILLS!
        """

        if is_true:  #If true, directly update
            self.true_raw=attack_value
        else: #Else, obtain the class mod and use it
            self.true_raw=attack_value/self.get_class_mod()

        #Update the final value (after buffs)
        self.true_raw_final=self.true_raw #2DO

    def update_affinity(self, aff_value):
        """
        Updates the stored affinity value for a given new value.
        
        NEED TO IMPLEMENT AFFINITY BOOSTING SKILLS!
        """

        #Check for aff_value > 100 or <-100
        if aff_value > 100:
            aff_value=100
        elif aff_value < -100:
            aff_value=-100

        #Now update the stored affinity values
        self.aff=aff_value/100 #Convert to decimal,
                               #ie 20% aff = 0.2 aff
        
        #Update the final value (after buffs)
        self.aff_final=self.aff #2DO

    def set_attack_list(self,file_path='datafiles\\weapon\\attacks\\'):
        """
        This function creates a list with the names of all the attacks of the weapon.
        
        IMPORTANT! All attack data is by default referred from the file
        .\\datafiles\\weapon\\attacks\\'weapon_type'.csv
        Where 'weapon_type' is given when creating this class.
        So, for a Switch Axe with weapon_type=='sa', the file required is:
        .\\datafiles\\weapon\\attacks\\sa.csv
        and so on

        Changing the file_path input allows for a different path, but the file must still be
        named 'weapon_type.csv'.

        For HBG and LBG (weapon_type=='hbg' or weapon_type=='lbg'), also take the ammo data
        from .\\datafiles\\weapon\\bg_ammo.csv
        """

        #Open the relevant file:
        with open(file_path+self.weapon_type+'.csv') as file:
            attack_source=csv.reader(file) #Store in this variable
            
            #Use the next function to skip the first row (header)
            next(attack_source)

            #Iterate through the remaining rows
            for row in attack_source: #Each row is an attack
                #The first item in each row is the attack name
                self.attack_list.append(row[0])

        return self.attack_list

    def append_combo(self,index_list,file_path='datafiles\\weapon\\attacks\\'):
        """
        Appends one attack to the current combo
        The combo is stored as a list of Attack objects.
        
        index is a list of ints corresponding to rows
        in the respective .csv file for weapon_type.

        attack_class is an Attack class to creat the Attack object
        Can be the generic Attack Class by default, or
        a specific Attack class for some weapons.

        extra_attribute will be sent as an argument to the
        attack_class, if there is one.

        file_path works similarly to the one in the 
        weapon_attack_names function above. See details
        there.

        FUNCTION MUST BE OVERLOADED BY SUBCLASSES WITH SPECIFIC ATTACK TYPES
        Use this only with: GreatSword, SwordNShield, Lance, Hammer and IG.
        Other weapons have specific Attack objects!
        """

        #Check for int rather than list
        if type(index_list)==int:
            index_list=[index_list] #Convert to list

        #Open file with attacks
        with open(file_path+self.weapon_type+'.csv') as file:
          
            attack_source=csv.reader(file) #Store in this variable
            attack_source=list(attack_source)
            

            for index in index_list: #Go through list
                #row index+1 will be used to generate the attack object
                #+1 to skip the header.
            
                #Check for extra attributes to define an attack_class
                #Currently done for: SA, LS
                attack_source[index+1]=self.add_extra(attack_source[index+1])

                #Append attack_class to the attack_combo
                self.attack_combo.append([
                    self.attack_class(attack_source[index+1]),
                            0,0,0]    #Raw, element and total damage               
                    )                   #They'll be updated in the damage_calc() function

    def update_combo(self,file_path='datafiles\\weapon\\attacks\\'):
        """
        Updates all entries of the current combo with
        the current attributes of the selected weapon.

        Used for some weapons where attack properties can vary
        based on weapon attributes 
        """

        with open(file_path+self.weapon_type+'.csv') as file:
          
            attack_source=csv.reader(file) #Store in this variable
            attack_source=list(attack_source)
        
            for i in range(len(self.attack_combo)):
                #Get attack index from self.attack_list
                index=self.attack_list.index(self.attack_combo[i][0].name)

                #Check for extra attributes to define an attack_class
                #Currently done for: SA, LS
                attack_source[index+1]=self.add_extra(attack_source[index+1])
               
                #Update
                self.attack_combo[i]=[self.attack_class(
                                        attack_source[index+1]),  
                                        0,0,0]       #Raw, element and total damage               
                                                       #They'll be updated in the damage_calc() function              

    def add_extra(self,attribute_list):
        """
        Adds extra parameters to the given attribute_list and returns it.
        In the general Weapon class, simply return the list as is

        May be overridden in specific classes that have specific attributes
        """

        return attribute_list

    def delete_from_combo(self,min_index,max_index):
        """
        Deletes entries from the current combo
        starting from min_dex up to max_index
        """

        del self.attack_combo[min_index:max_index+1]

    def delete_combo(self):
        """
        Deletes the current combo  entirely
        """

        self.attack_combo=[]

    def damage_calculation(self,target_monster,calc_type='average'):
        """
        Do the damage calculation with current weapon and a target_monster
        information

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
        #Also applies Agitator if required and enr
        temp_mon=self.get_monster_data(target_monster)
        raw_HZ=temp_mon[0]
        elem_HZ=temp_mon[1]
        is_tenderized=temp_mon[2]
        rage_mod=temp_mon[3]

        #Iterate through attack_combo to obtain all damage values
        for attack in self.attack_combo:
            
            self.generic_calculation(attack,raw_HZ,elem_HZ,is_tenderized,rage_mod,calc_type) 

    def get_monster_data(self,target_monster):
        """
        Extracts relevant information from the monster
        returns it as a tuple in the form
        (raw_HZ,elem_HZ,rage_mod)
        """

        #Get the hitzone object from the monster 
        calc_hitzone=target_monster.get_hitzone(target_monster.target_hitzone)
        
        #Extract the relevant information from the hitzone (raw and elemental value)
        #Check for a wound to get appropriate raw HZVs.
        if (calc_hitzone.is_tenderized):
            raw_HZ=calc_hitzone.raw_tenderized
        else:
            raw_HZ=calc_hitzone.raw
                            
        #Elemental hitzones are not affected by tenderizing.
        elem_HZ=calc_hitzone.elem 

        #Also store tenderized status
        is_tenderized=calc_hitzone.is_tenderized                         

        #Extract the rage_mod from the monster, depending on its enraged status
        if target_monster.is_enraged: #If enraged, get the rage_mod
                                      #and activate Agitator
            rage_mod=target_monster.rage_mod
            if Agitator in self.buff_dict: #Check for Agitator in skills
                Agitator_Activate(self.buff_dict[Agitator],self)
        else:
            rage_mod=1 #Otherwise, set to 1 to not affect damage.

        return (raw_HZ,elem_HZ,is_tenderized,rage_mod)

    def generic_calculation(self,attack,raw_HZ,elem_HZ,is_tenderized,rage_mod,calc_type):
        """
        Calculates raw and elemental damage for a generic weapon attack.
        Applies for most attacks, but there are some exceptions such
        as CB Impact Phials, which don't consider hitzones, etc
        """

        #Apply Weakness Exploit, if needed
        if Weakness_Exploit in self.buff_dict:
            Weakness_Exploit_Activate(self.buff_dict[Weakness_Exploit],self,
                                        raw_HZ[attack[0].damage_type], is_tenderized)
                                        
        #Limit affinity if needed
        self.aff_final=max(min(self.aff_final,1),-1)

        #Obtain Crit mods for raw and elemental damage.
        #Check for desired calc_type ('normal','crit' or 'average)
        if self.aff_final > 0:
            calc_crit_mod_raw=self.determine_crit_mod(self.crit_mod_raw,calc_type)
        else:
            calc_crit_mod_raw=self.determine_crit_mod(0.75,calc_type) #Feeble
        
        calc_crit_mod_elem=self.determine_crit_mod(self.crit_mod_elem,calc_type)

        #Raw damage or 'fixed' damage
        #Some fixed damage scale with attack (such as CB Phials)
        attack[1]=self.raw_number(attack[0],raw_HZ,calc_crit_mod_raw,rage_mod)    #Raw damage value
        
        #Elemental damage
        attack[2]=self.elem_number(attack[0],elem_HZ,calc_crit_mod_elem,rage_mod) #Elemental damage value
        
        #Total damage
        attack[3]=attack[1]+attack[2]
    
    def raw_number(self,attack,hitzone,crit_mod_raw,rage_mod):
        """
        Calculates the raw portion of damage. Inputs are:

        attack: an Attack object with information on the Attack being used.
                So far only checks for MV and damage type, but may carry additional
                information later.

        hitzone: a hitzone dictionary (obtained from a Hitzone object) that contains
                 the raw hitzone data from the monster. Formatted as
                 hitzone={'cut': cutting HZV, 'impact': impact HZV, 'shot': shot HZV}

        crit_mod_raw: raw crit mod for the current calculation

        rage_mod: the current rage mod for the target monster
        
        Still need to implement a ton of possible multipliers, but this is a first attempt
        """

        #Get damage type and MV data from the attack object
        mv=attack.mv
        damage_type=attack.damage_type

        #Get the corresponding hitzone value from the hitzone object
        hzv=hitzone[damage_type]
        # try:
        #     hzv=hitzone[damage_type]
        # except KeyError: #For attacks with undefined hitzone type, such as CB Phials
        #     hzv=100

        
        #Apply possible raw multipliers from attack
        calc_raw=self.true_raw_final*attack.true_raw_mult
        
        #Check for attacks that force green sharpness
        if attack.green_sharp: #If true, use green sharpness
            calc_sharp=1.05
        else:
            calc_sharp=self.sharp_raw
        
        #Calculate raw damage. Currently missing practically all situational modifiers.
        #Round later. For total damage, raw and fixed damage are rounded together!
        return round(calc_raw * (mv/100.0) * crit_mod_raw * rage_mod * (hzv/100.0) * calc_sharp)

    def elem_number(self,attack,hitzone,crit_mod_elem,rage_mod):
        """
        Calculates the elemental portion of damage. Inputs are:
        attack: an Attack object with information on the Attack being used.
                So far only checks for EleMod, but may carry additional
                information later.

        hitzone: a hitzone dictionary (obtained from a Hitzone object) that contains
                 the raw hitzone data from the monster. Formatted as
                 hitzone={'fire': fire HZV, 'water': impact HZV, 
                 'thunder': thunder HZV, 'ice': ice HZV, 'dragon': dragon HZV}

        crit_mod_elem: elemental crit mod for this calculation

        rage_mod: the current rage mod for the target monster

        Still need to implement a ton of possible multipliers, but this is a first attempt
        """
        
        try: #Should work if elem_type is set properly
               
            #Get EleMod data from the Attack object
            ele_mod=attack.elemod

            #Get the corresponding hitzone value from the hitzone object
            hzv=hitzone[self.elem_type]

            #Apply possible raw multipliers from attack
            calc_elem=self.true_elem_final*attack.true_elem_mult

            #Check for attacks that force green sharpness
            if attack.green_sharp: #If true, use green sharpness
                calc_sharp=1.00
            else:
                calc_sharp=self.sharp_elem

            #Calculate raw damage. Currently missing practically all situational modifiers.
            return round(round(calc_elem * crit_mod_elem) * ele_mod * rage_mod * (hzv/100.0) * calc_sharp)

        except KeyError: #For a None in weapon.elem_type, return 0
            return 0

    def determine_crit_mod(self,crit_mod,calc_type='average'):
        """
        Choose the appropriate crit_mod_raw for a given calc_type
        Elemental crit mod determined in determine_crit_mod_elem

        calc_type = 'normal' -> 1.0, not a critical hit

        calc_type = 'crit'  -> self.crit_mod_raw.
                               Value should be already updated to account for crit boost
                               or feeble hits (aff < 0)

        calc_type = 'average -> average of the two previous values, weighted by affinity.
        """

        if calc_type=='normal' or self.aff_final==0: #Not crit/feeble
            return 1

        elif calc_type=='crit': #Crit damage, also feeble hits for Affinity < 0
                                #The crit_mod argument should be already 0.75 for Aff < 0
            return crit_mod
        
        else: #Default to average damage
            crit_mod_aff=max(min(self.aff_final,1),-1)
            return abs(crit_mod_aff)*crit_mod+(1.0-abs(crit_mod_aff))*1 

    def update_buff_dict(self,buff_func,buff_level=1):
        """
        Adds a specific buff function at a given level
        to the bonus_raw dict. Setting
        buff_level=0 will remove buff_func from bonus_raw,
        if buff_func was already there.
        """
        
        #Check for level 0:
        if buff_level==0:
            if buff_func in self.buff_dict:#Check for key
                del self.buff_dict[buff_func] #Remove from dictionary
            
        else: #For level > 0
            self.buff_dict[buff_func]=buff_level #Add or update buff_func
                                            #at buff_level to buff_dict
        
    def apply_buffs(self):
        """
        Applies raw buffs stored in the weapon to the
        self.true_raw_final variable.

        Only applies some weapon buffs for now, need to
        implement skills/items
        """
        #Reset the final values for true raw, element and affinity
        self.true_raw_final=self.true_raw
        self.aff_final=self.aff
        self.true_elem_final=self.true_elem

        #Reset the multipliers
        self.flat_raw_mod=0
        self.mult_raw_mod=1
        self.flat_elem_mod=0
        self.mult_elem_mod=1
        self.flat_aff_mod=0

        #Reset crit mods
        self.crit_mod_raw=1.25
        self.crit_mod_elem=1

        #Reset Elem cap (in case Dragonvein raised it)
        self.elem_cap=max(self.true_elem*1.6,self.true_elem+15)

        #Pre-cap value: Multiply by all items in self.base_raw_mult
        for buff,level in self.buff_dict.items(): #buff has the form buff=(function,level)
            buff(level,self)

        #Apply multipliers
        self.true_raw_final=self.true_raw*self.mult_raw_mod+self.flat_raw_mod
        self.true_elem_final=self.true_elem*self.mult_elem_mod+self.flat_elem_mod
        self.aff_final=self.aff+self.flat_aff_mod
        
        #Apply damage cap
        self.true_raw_final=min(self.true_raw_final,self.attack_cap)
        self.true_elem_final=min(self.true_elem_final,self.elem_cap)
        
        #Post cap multipliers are all in the form of specific weapon mods
        self.apply_weapon_buffs()

    def apply_weapon_buffs(self):
        """
        Applies weapon-specific post-cap multipliers,
        such as LS's and IG's buffs
        """

        self.true_raw_final*=self.weapon_raw_mod

    def get_efr(self):
        """
        Calculates EFR. 

        Use only after a damage calculation to ensure all
        buffs are applied.
        """

        return self.true_raw_final * self.determine_crit_mod(self.crit_mod_raw) * self.sharp_raw

    def get_efe(self):
        """
        Calculates EFE. 

        Use only after a damage calculation to ensure all
        buffs are applied.
        """

        if self.elem_type==None:
            return 0
        else:
            return self.true_elem_final * self.determine_crit_mod(self.crit_mod_elem) * self.sharp_elem