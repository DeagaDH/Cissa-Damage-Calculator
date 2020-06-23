#Defines skills and other buffs
#All skills take 2 inputs: the desired level and
#a weapon object to apply the skill to.

#Also has dictionaries with correspondence between
#strings and skill functions, along with max levels
#or option choices (ie Might Seed/Pill, rather than levels)
#used in the front end choice menu

#############################################################
####           SKILLS & SET BONUSES
#############################################################

def Airborne(level, weapon):
    """
    Models the Artillery Skill
    """

    #2DO
    pass

def Agitator(level, weapon):
    """
    Stores the Agitator skill, if present
    
    It'll be activated during damage calculation
    via weapon.Agitator_Activate if the target monster
    is enraged
    """

    #Check for invalid levels
    level=max(min(level,7),0)

def Agitator_Activate(level, weapon):
    """
    Activates the Agitator skill
    """

    #Do its effect
    #Raw part
    weapon.true_raw_final+=4*level #4 per level

    #Affinity part depends heavily on level
    #Store affinity cases as a dictionary
    #Levels are keys, affinity gain is value
    aff_dict={1: 0.05, 2: 0.07, 3: 0.07, 4:0.10,
                5: 0.10, 6: 0.15, 7: 0.20}

    #apply affinity buff
    weapon.aff_final+=aff_dict[level]

def Artillery(level, weapon):
    """
    Stores the Artillery skill, if present

    Skill is activated during damage calculation,
    if required, via Artillery_Activate
    """

    #Check for invalid levels
    level=max(min(level,5),0)

def Artillery_Activate(level):
    """
    Activates the Artillery skill.

    This will RETURN the multiplier, due to how
    CB Impact Phials behave weirdly with attack
    scaling
    """

    return 1+0.1*level

def Attack_Boost(level, weapon):
    """
    Defines the Attack boost skill
    """

    #Check for invalid levels
    level=max(min(level,7),0)
    
    #Do its effect
    weapon.flat_raw_mod+=3*level #3 true raw per level

    if level >= 4:
        weapon.flat_aff_mod+=0.05 #Add 5% affinity on higher levels.

def Coalescence(level, weapon):
    """
    Defines the Coalescence skill

    Apply after Element Up skills.
    """

    #Check for invalid levels
    level=max(min(level,3),0)

    #Apply raw effect
    weapon.flat_raw_mod+=9+3*level

    #Apply elemental effect
    #Only valid if the weapon has element
    if (weapon.elem_type!=None and weapon.true_elem>0):
        weapon.flat_elem_mod+=3*level

def Critical_Boost(level, weapon):
    """
    Defines the Critical Boost skill
    """

    #Check for invalid levels
    level=max(min(level,3),0)

    #Apply the buff
    weapon.crit_mod_raw=1.25+0.05*level

def Critical_Eye(level, weapon):
    """
    Defines the Critical Eye skill
    """

    #Check for invalid levels
    level=max(min(level,7),0)
    
    #Do its effect
    if level < 7:
        weapon.flat_aff_mod+=0.05*level #5% affinity per level if level <7

    else:
        weapon.flat_aff_mod+=0.40 #Add 40% affinity on level 7

def Critical_Element(level,weapon,crit_elem_file='datafiles\\weapon\\crit_elem.csv'):
    """
    Models the Critical Element and 
    True Critical Element skills.
    CE is lv1, TCE is lv2.
    """

    #Check for invalid levels
    level=max(min(level,2),0)

    #(True) Critical Element mods in a dictionary in the format
    #dict={'weapon_type':(CE mod, TCE mod)}
    ce_dict={'gs':(1.50,1.70),
             'sns':(1.35,1.55),
             'db':(1.35,1.55),
             'ls':(1.35,1.55),
             'hammer':(1.50,1.70),
             'hh':(1.50,1.70),
             'lance':(1.35,1.55),
             'gl':(1.35,1.55),
             'sa':(1.35,1.55),
             'cb':(1.35,1.55),
             'ig':(1.35,1.55),
             'bow':(1.35,1.55),
             'hbg':(1.50,1.70),
             'lbg':(1.25,1.40)
    }

    #Apply effect
    weapon.crit_mod_elem=ce_dict[weapon.weapon_type][level-1]

def Dragonvein_Awakening(level, weapon):
    """
    Models the (True) Dragonvein Awakening set bonuses.
    3p version is level 1, 5p is level 2

    Also increases elemental cap.
    """

    #Check for invalid levels
    level=max(min(level,2),0)

    #Apply buffs
    weapon.flat_aff_mod+=0.2*level

    #Only valid if the weapon has element
    if (weapon.elem_type!=None and weapon.true_elem>0):
        weapon.flat_elem_mod+=1+7*level
        weapon.elem_cap+=1+7*level

def Elemental_Attack(level, weapon):

    """
    Encompasses all <Element> Attack-type skills.
    They all work exactly the same.
    """

    #Check for invalid levels
    level=max(min(level,6),0)

    #Only valid if the weapon has element
    if (weapon.elem_type!=None and weapon.true_elem>0):
        #Define flat boost
        if level <=2:  
            flat=2*level  #+3 for lv1, +6 for lv2
        else:
            flat=10 #For levels 3+

        #Define multiplier:
        mult={1: 1, 2:1, 3:1, 4:1.05, 5:1.1, 6:1.2}

        #Apply skill.
        weapon.flat_elem_mod+=flat
        weapon.mult_elem_mod*=mult[level]

def Elemental_Acceleration(level, weapon):
    """
    Models the (True) Dragonvein Awakening set bonuses.
    2p version is level 1, 5p is level 2
    """

    #Check for invalid levels
    level=max(min(level,2),0)

    #Only valid if the weapon has element
    if (weapon.elem_type!=None and weapon.true_elem>0):
        #Apply buffs
        weapon.flat_elem_mod+=-3+9*level

def Fortify(level, weapon):
    """
    Defines the Fortify skill

    Levels emulate carts (ie lv2 for 2 carts)
    """

    #Check for invalid levels
    level=max(min(level,2),0)
    
    #Apply buff
    weapon.mult_raw_mod*=1+(0.1*level)

def Frostcraft(level, weapon):
    """
    Models the Frostcraft skill

    Each level corresponds to a level in
    FC's gauge.
    """

    #Check for invalid levels
    level=max(min(level,3),0)

    pass

def Heroics(level, weapon):
    """
    Defines the Heroics skill.

    Levels 1 to 7 are the skill's usual levels.
    Level 8 models Felyne Heroics kitchen skill
    """
    
    #Check for invalid levels
    level=max(min(level,8),0)

    #Define buffs
    raw_dict={1:1, 2:1.05, 3:1.05, 4:1.10, 
                5:1.15, 6:1.25, 7:1.40, 8:1.35}

    #Apply buff
    weapon.mult_raw_mod*=raw_dict[level]

def Latent_Power(level, weapon):
    """
    Defines the Latent Power skill
    """

    #Check for invalid levels
    level=max(min(level,7),0)

    #Apply affinity effect
    if level <=5:
        weapon.flat_aff_mod+=0.1*level
    else:
        weapon.flat_aff_mod+=0.1*(level-1)

def Maximum_Might(level, weapon):
    """
    Models the Maximum Might skill
    """

    #Check for invalid levels
    level=max(min(level,4),0)
    #Level 4 gives the same boost as level 5, they are
    #equivalent from the point of view of damage calculation

    #Apply affinity effect
    weapon.flat_aff_mod+=0.1*level

def Non_Elemental_Boost(level, weapon):
    """
    Defines the NEB skill
    """

    #Check for invalid levels
    level=max(min(level,1),0)
    
    #Apply buff
    if (weapon.elem_type==None or weapon.true_elem==0):
        weapon.mult_raw_mod*=1.05

def NormalPierce_Shots(level, weapon):
    """
    Models all the Normal Shot
    and Pierce Shot skills.

    WILL BOOST ALL SHOTS IN THE DAMAGE
    GRID!!
    """
    #Check for invalid levels
    level=max(min(level,2),0)

    pass

def Offensive_Guard(level, weapon):
    """
    Models the Offensive Guard skill
    """

    #Check for invalid levels
    level=max(min(level,3),0)
    
    #Apply buff
    if (weapon.elem_type==None or weapon.elem_value==0):
        weapon.mult_raw_mod*=(1+0.05*level)

def Peak_Performance(level, weapon):
    """
    Defines the Peak Performance skill
    """

    #Check for invalid levels
    level=max(min(level,3),0)

    #Apply effect
    if level < 3: #5 per level on levels 1 and 2
        weapon.flat_raw_mod+=5*level
    else: #20 on level 3
        weapon.flat_raw_mod+=20 

def Punishing_Draw(level, weapon):
    """
    Models the Punishing Draw set bonus
    """

    #Check for invalid levels
    level=max(min(level,1),0)

    #Apply raw effect
    weapon.flat_raw_mod+=5

def Resentment(level, weapon):
    """
    Defines the Resentment skill
    """

    #Check for invalid levels
    level=max(min(level,5),0)

    #Apply effect
    weapon.flat_raw_mod+=5*level

def Special_Ammo_Boost(level, weapon):
    """
    Models the Artillery Skill
    """
    #Check for invalid levels
    level=max(min(level,2),0)
    #2DO
    pass

def SpreadPower_Shots(level, weapon):
    """
    Models all the Normal Shot
    and Pierce Shot skills.

    WILL BOOST ALL SHOTS IN THE DAMAGE
    GRID!!
    """
    #Check for invalid levels
    level=max(min(level,2),0)

    pass

def Weakness_Exploit(level, weapon):
    """
    Simply checks to see if the Weakness Exploit skill is 
    active.

    If it is, it'll be activated during damage
    calculation by the Weakness_Exploit_Activate function.
    """

    #Check for invalid levels
    level=max(min(level,3),0)

def Weakness_Exploit_Activate(level, weapon, hzv, is_tenderized):
    """
    Models the Weakness Exploit skill.
    Also requires a hitzone value (hzv) to check
    for the activation criteria. Also needs
    to know if the hitzone is tenderized.

    Call during DAMAGE CALCULATION
    """

    #Check for invalid levels
    level=max(min(level,3),0)
    
    #Check for hitzone value
    if (hzv>=45):
        #Check for tenderizing
        if is_tenderized:
            aff_dict={1:0.15, 2:0.3, 3:0.5}

        else: #Not tenderized
            aff_dict={1:0.10, 2:0.15, 3:0.30}
            
        weapon.aff_final+=aff_dict[level]

#############################################################
####        ITEMS
#############################################################

def Demondrug(level, weapon):
    """
    Includes both Demondrug and Mega Demondrug
    Demondrug is modelled as level 1,
    Mega as level 2
    """

    #Check for invalid levels
    level=max(min(level,2),0)

    #Apply raw effect
    weapon.flat_raw_mod+=3+2*level

def Demon_Powder(level, weapon):
    """
    Models the Demon Powder item
    """
    
    #Check for invalid levels
    level=max(min(level,1),0)

    #Apply raw effect
    weapon.flat_raw_mod+=10

def Evasion_Mantle(level, weapon):
    """
    Models the Evasion Mantle
    """

    #Check for invalid levels
    level=max(min(level,1),0)
    
    #Apply buff
    if (weapon.elem_type==None or weapon.elem_value==0):
        weapon.mult_raw_mod*=1.3

def Might_Seed(level, weapon):
    """
    Includes both Might Seed and Might Pill,
    as they cannot stack. Models Seed as level 1,
    Pill as level 2.
    """

    #Check for invalid levels
    level=max(min(level,2),0)

    #Apply raw effect
    weapon.flat_raw_mod+=15*level-5

def Powercharm(level, weapon):
    """
    Includes both Powercharm and Powertalon
    Models charm as level 1, talon as level 2,
    both as level 3.
    """

    #Check for invalid levels
    level=max(min(level,3),0)

    #Apply raw effect
    if level < 3: #Covers just Charm and just talon
        weapon.flat_raw_mod+=3+3*level
    else: #Covers both at once
        weapon.flat_raw_mod+=9+6

def Powercone(level, weapon):
    """
    Models the Powercone pickup
    """
    
    #Check for invalid levels
    level=max(min(level,1),0)

    #Apply raw effect
    weapon.flat_raw_mod+=5

#############################################################
####        CANTEEN
#############################################################

def CanteenAttack(level, weapon):
    """
    Attack Boost from canteen food.
    Models (S), (M) and (L) as levels
    1,2,3, respectively
    """

    #Check for invalid levels
    level=max(min(level,3),0)

    #Apply raw effect
    weapon.flat_raw_mod+=5*level

def Felyne_Bombardier(level, weapon):
    """
    Stores the Felyne Bombardier Kitchen Skill

    It is later activated during damage calculation
    via the Felyne_Bombardier_Activate function.
    """

    #Check for invalid levels
    level=max(min(level,1),0)

def Felyne_Bombardier_Activate(level):
    """
    Activates the Felyne Bombardier skill.

    This will RETURN the multiplier, due to how
    CB Impact Phials behave weirdly with attack
    scaling
    """

    return 1.15

def Felyne_Booster(level, weapon):
    """
    Models the Felyne Booster Canteen Skill
    """

    #Check for invalid levels
    level=max(min(level,1),0)

    #Apply raw effect
    weapon.flat_raw_mod+=9

def Felyne_Temper(level, weapon):
    """
    Models the Felyne Temper Kitchen Skill
    """

    #2DO
    pass

def Felyne_Sharpshooter(level, weapon):
    """
    Models the Felyne Sharpshooter Kitchen Skill
    """

    #2DO
    pass

#############################################################
####        HH MELODIES
#############################################################

def Melodies_Attack(level, weapon):
    """
    Encompasses all HH melody combinations for
    raw attacks. Levels are modeled as:

    1 Attack Up (S)
    2 Attack Up (L)
    3 Attack Up (XL)
    """

    #Check for invalid levels
    level=max(min(level,3),0)
    
    #Apply effect
    weapon.mult_raw_mod*=(1.05+0.05*level)

def Melodies_Elemental(level, weapon):
    """
    Encompasses all HH melody combinations for elemental attacks

    'levels' are organized as follows:
    1 Element Attack Boost (EAB) (S)
    2 EAB (L)
    3 Element Effectiviness Up (EEU)
    4 EEU+EAB (S)
    5 EEU+EAB (L)
    """

    #Check for invalid levels
    level=max(min(level,2),0)

    #Define buffs
    elem_dict={1: 1.08, 2:1.10, 3:1.05, 4:1.16, 5:1.20}

    #Apply
    weapon.mult_elem_mod*=elem_dict[level]

#############################################################
####        DICTIONARIES
#############################################################

skill_dict={'Airborne':(Airborne,['No','Yes']),
            'Agitator':(Agitator,7),
            'Artillery':(Artillery,5),
            'Attack Boost':(Attack_Boost,7),
            'Coalescence':(Coalescence,3),
            'Critical Boost':(Critical_Boost,3),
            'Critical Eye':(Critical_Eye,7),
            '(True) Crit. Elem. ':(Critical_Element,['None','CE','TCE']),
            '(True) D. Awaken. ':(Dragonvein_Awakening,['None','DVA','TDVA']),
            'Elemental Attack':(Elemental_Attack,6),
            '(True) Elem. Accel. ':(Elemental_Acceleration,['None','EA','TEA']),
            'Fortify':(Fortify,2),
            'Frostcraft':(Frostcraft,3),
            '(Felyne) Heroics':(Heroics,['0','1','2','3','4','5','6','7','Felyne']),
            'Latent Power':(Latent_Power,7),
            'Maximum Might':(Maximum_Might,5),
            'Non-Elemental Boost':(Non_Elemental_Boost,1),
            'Normal/Pierce Shots':(NormalPierce_Shots,2),
            'Offensive Guard':(Offensive_Guard,3),
            'Peak Performance':(Peak_Performance,3),
            'Punishing Draw':(Punishing_Draw,['No','Yes']),
            'Resentment':(Resentment,5),
            'Special Ammo Boost':(Special_Ammo_Boost,5),
            'Spread/Power Shots':(SpreadPower_Shots,2),
            'Weakness Exploit':(Weakness_Exploit,3)}

item_dict= {'Demondrug':(Demondrug,['No','Demondrug','Mega']),
            'Demon Power':(Demon_Powder,['No','Yes']),
            'Evasion Mantle':(Evasion_Mantle,['No','Yes']),
            'Might Seed/Pill':(Might_Seed,['None','Seed','Pill']),
            'Powercharm/talon':(Powercharm,['None','Charm','Talon','Both']),
            'Powercone':(Powercone,['No','Yes'])}

canteen_dict= { 'Canteen Atk Up':(CanteenAttack,['None','(S)','(M)','(L)']),
                'Felyne Bombardier':(Felyne_Bombardier,['No','Yes']),
                'Felyne Booster':(Felyne_Booster,['No','Yes']),
                'Felyne Temper':(Felyne_Temper,['No','Yes']),
                'Felyne Sharpshooter':(Felyne_Sharpshooter,['No','Yes'])}

song_dict= {'Attack Up':(Melodies_Attack,['None','(S)','(L)','(XL)']),
            'Elem. Atk and Effect.':(Melodies_Elemental,['None','EAB (S)','EAB (L)','EEU','EAB(S)+EEU','EAB(L)+EEU'])}


#############################################################
####        NOT YET IMPLEMENTED
#############################################################

not_implemented_skills=['Airborne','Frostcraft',
                        'Normal/Pierce Shots','Special Ammo Boost',
                        'Spread/Power Shots']
                        
not_implemented_canteen=['Felyne Temper',
                         'Felyne Sharpshooter']