import csv

#This script defines the different classes used in the calculator

class Hitzone:
    """
    This is a Hitzone class for damage calculation. Hitzones correspond to monster body parts (Head, Tail, etc)
    and have different values, known as Hitzone Values (HZV) used to calculate damage for different damage types.
    The different damage types are: Cut, Impact, Shot, Fire, Water, Thunder, Ice and Dragon.
    Hitzone also carries the STUN value (how much Stun status the hitzone takes from Stun attacks) and the TENDERIZE
    value. Hitzones in the same TENDERIZE group (ie hitzones all with a 1 in this column) are tenderized together.

    First input is a list hitzone_info organized as follows:
    [NAME, STATE, CUT, IMPACT, SHOT, FIRE, WATER, THUNDER, ICE, DRAGON, STUN, TENDERIZE]
    NAME is a string with the hitzone's name, 
    STATE is a complement to the name (different modes of the same body part for example)
    other entries are ints with their respective values

    Second input is the tender_mod for the monster this hitzone belongs to. The default value, used for most monsters,
    is 25. Some monsters may have a 30 or 20 instead.
    """
    type="Hitzone"
  
    def __init__(self,hitzone_info,tender_mod=25):
        #Hitzone's name
        self.name=hitzone_info[0]
        
        #Name complement. If there is a name complement in the hitzone_info tuple, use it
        if (hitzone_info[1]!="" and hitzone_info[1]!="0"):
            self.state=hitzone_info[1]
        else: #Else, set name2 as an empty string
            self.state=""

        #Hitzone's raw damage values
        self.raw={"cut":int(hitzone_info[2]), "impact":int(hitzone_info[3]), "shot": int(hitzone_info[4])}

        #Hitzones elemental damage values
        self.elem={"fire":int(hitzone_info[5]), "water":int(hitzone_info[6]), "thunder":int(hitzone_info[7]),"ice":int(hitzone_info[8]),"dragon":int(hitzone_info[9])}

        #Stun value
        self.stun=int(hitzone_info[10])

        #Store tenderize groups and also the raw HZVs after wounding
        if (hitzone_info[11]==""):
            self.tender_group=0 #Group 0 means a hitzone that can't be wounded
            self.raw_tenderized=self.raw #Can't be wounded
        else:
            self.tender_group=int(hitzone_info[11])
            self.raw_tenderized=self.apply_wound(tender_mod)

        #Is the hitzone tenderized? By default, False, can be set to True
        #Modified via the toggle_tenderize function
        self.is_tenderized=False

    def apply_wound(self,tender_mod):
        """
        Calculates the new HZVs from a wounded body part.
        HZV_dict: dictionary in the form
                  {'cut: HZV, 'impact': HZV, 'shot': HZV}
                  containing the three raw HZVs. All three will be updated.
        tender_mod: the tenderizing mod corresponding to the target monster.
                    This function assumes that +25 has already been added to it!
        """

        #Create an empty dictionary to receive the results
        new_HZV={}

        #Apply the wounding formula on each hitzone
        for damage_type in self.raw.keys():
            new_HZV[damage_type]=int(0.75*self.raw[damage_type])+tender_mod

        return new_HZV

    def toggle_tenderize(self):
        """
        This function sets the current hitzone as wounded, if possible.
        If already wounded, returns to a non-wounded state
        Note that hitzones that are part of tender_group=0 cannot be wounded
        """

        if (self.tender_group==0): #tender_group==0 can't be wounded, so always set is_tenderized to false
            self.is_tenderized = False
        else: #Otherwise, flip value of is_tenderied
            self.is_tenderized = not self.is_tenderized

        print("Hitzone tenderized?",self.is_tenderized)
    def set_tenderize(self,is_tenderized):
        """
        Sets the hitzone as tenderized (true) or
        not tenderized (False)
        """

        self.is_tenderized=is_tenderized

class Monster():
    """
    The monster class encapsulates all Hitzones that belong to a specific monster. Input is the monster's name. 
    This will by default get hitzone data from .\datafiles\monster\hitzones.csv
    and rage mod/tenderize value data from .\datafiles\monster\ragemods.csv
    """
    
    type="Monster"

    def __init__(self,monster_name,ragetender_file="datafiles\\monster\\ragemods.csv",hitzone_file="datafiles\\monster\\hitzones.csv"):
        #monster_name is a string containing the monster's name
        #hitzone_file is a csv file with hitzone data

        #Use the create_monster method to create or update the monster
        self.create_monster(monster_name,ragetender_file,hitzone_file)

    def create_monster(self,monster_name,ragetender_file="datafiles\\monster\\ragemods.csv",hitzone_file="datafiles\\monster\\hitzones.csv"):
        #Store the monster's name
        self.name=monster_name
        
        #Store the rage mod (multiplier for taken damage in rage mode) and tenderize mod (affects tenderizing hitzones)
        with open(ragetender_file,'r') as file:
            #Store data from file in the monster_mods variable
            monster_mods=csv.reader(file)

            #Search for the relevant monster in file
            for row in monster_mods:
                if row[0]==self.name:
                    self.tender_mod=25+int(row[1]) #This is already the final value used in the tenderize formula, 25 + monster_value
                    self.rage_mod=float(row[2])      #This is the rage_mod for damage as a multiplier, i.e rage_mod = 1.05 -> monster takes 5% more damage (1.05x)
        
        #Store current rage status. By default, set to False (ie unenraged), change with the toggle_rage() function
        self.is_enraged=False

        #Store all the monster hitzones in a list
        with open(hitzone_file,"r") as file:
            #Store data in the monster_hitzones variable
            monster_hitzones=csv.reader(file)

            #Insert the hitzones found in hitzone_file to hitzone_list
            #Each row in hitzone list should have the following format:
            #MONSTER NAME, HITZONE NAME, HITZONE NAME2, CUT, IMPACT, SHOT, FIRE, WATER, THUNDER, ICE, DRAGON, STUN, TENDERIZE
            #The TENDERIZE column groups hitzones that are tenderized together (ie separate Horns and Head that are tenderized
            #together should have the same number in the TENDERIZE column)
            self.hitzones=[row[1:] for row in monster_hitzones if row[0]==self.name]        
            #First entry from ROW is the monster's name, do not copy it to hitzones!
        
        #Convert each entry in self.hitzone_list from a list to a hitzone object
        self.hitzones=[Hitzone(HZ,self.tender_mod) for HZ in self.hitzones]
        
        #Set a hitzone as the target hitzone. 
        #Defined by its index in the self_hitzones list
        self.target_hitzone=0 #change via set_target
                            
    def get_hitzone(self,hz_name="",hz_state=""):
        """
        Retrieves the Hitzone data for the Hitzone specified by hz_name and hz_state
        hz_state refers to a specific hitzone state (ie Acidic Glavenus' tail can be "normal", Hvy Crystal or Sharpened)
        By default, that's an empty string, which defaults to a "normal" state
        Most hitzones will have hz_state as an empty string!

        Alternatively, if hz_name is an INTEGER n, this will return the n-th hitzone in self.hitzones.
        Remember that Python counts from zero. (ie the first hitzone is 0, the second is 1, etc)

        If hz_name is empty, PRINT (not return!) all hitzones. Used for debugging.
        """

        if (type(hz_name)==int):
            if (hz_name<=len(self.hitzones)): #If the index is in the list
                return self.hitzones[hz_name]
            else: #Default to the first hitzone to avoid errors
                return self.hitzones[0]
        
        else:
            #If not an empty string, return specified hitzone
            if (hz_name!=""):
                for item in self.hitzones:
                    if (item.name==hz_name and item.state==hz_state): #If the two naming entries are equal to the entries supplied to the function
                        return item #Return this hitzone

            else: #Otherwise, ie if an empty string, PRINT (not return) all hitzones. Used for debugging.
                for item in self.hitzones:
                    print(item.name+" "+item.state)
                    print(item.raw)
                    print(item.elem)
                    
    def set_target_hitzone(self,hz_name=0,hz_state=""):
        """
        Sets the hitzone defined by hz_name and hz_state as
        the current target.

        Alternatively, if hz_name is an INTEGER n, this will return the n-th hitzone in self.hitzones.
        Remember that Python counts from zero. (ie the first hitzone is 0, the second is 1, etc)

        If it's a string, get the indez in self.hitzones corresponding
        to it and set that.
        """

        #First, assume it's an int
        if (type(hz_name)==int):
            if (hz_name<=len(self.hitzones)): #If the index is in the list
                self.target_hitzone=hz_name
            else: #Default to the first hitzone to avoid errors
                self.target_hitzone=0

        #Otherwise, search for hz_name and hz_state strings
        for item in self.hitzones:
            if (item.name==hz_name and item.state==hz_state): #If the two naming entries are equal to the entries supplied to the function
                 self.target_hitzone=self.hitzones.idex(item)
  
    def toggle_rage(self):
        """
        Toggles the value of self.is_enraged
        """

        self.is_enraged = not self.is_enraged