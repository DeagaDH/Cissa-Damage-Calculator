class Attack:
    """
    This class stores data for generic attacks. Input is
    an attribute list organized as
    attributes=[name,damage_type,mv,elemod]
    Where each one of those is defined below:

    name: the attack's name
    damage_type: 'cut', 'impact' or 'shot' for damage type
    MV: the motion value of the attack
    EleMod: the elemental mod, typically==1 but not always
    """

    def __init__(self,attributes):
        #Basic attributes
        self.name=str(attributes[0])
        self.damage_type=str(attributes[1])
        self.mv=int(attributes[2])
        self.elemod=float(attributes[3])

        #Special attributes. May be modified by subclasses
        #for specific weapons
        self.true_raw_mult=1.0 #Multiplier for true raw. Used by some subclasses.
        self.true_elem_mult=1.0 #Multiplier for true element. Used by some subclasses
        self.green_sharp=False #Flag for attacks calculated at green sharpness
    
class DualBladesAttack(Attack):
    """
    Sub-class specific for Dual Blade attacks due to unique 
    raw modifiers. Input is an attribute list organized as
    attributes=[name,damage_type,mv,elemod,raw_mult]
    """

    def __init__(self,attributes):
        #Initialize parent class
        Attack.__init__(self,attributes)

        #Check for true raw multipliers
        #Can happen on Heavenly Blade Dance after many hits
        self.true_raw_mult*=float(attributes[4])

class LongSwordAttack(Attack):
    """
    Sub-class specific for Long Sword attacks due to unique 
    raw modifiers for attacks that do NOT use the
    Spirit Gauge buff. Input is an attribute list organized as
    attributes=[name,damage_type,mv,elemod,
                applies_gauge_buff,ls_color]

    applies_gauge_buff: True/False for using the Spirit Gauge buff

    ls_color: numerical value for the current spirit gauge color
              ie 1.05 for white, 1.1 for yellow or 1.2 for red
    """

    def __init__(self,attributes):
        #Initialize parent class
        Attack.__init__(self,attributes)

        #Store attributes to variables for readability
        applies_gauge_buff=bool(int(attributes[4]))
        ls_color=float(attributes[5])

        #Check for attacks that do NOT use the Spirit
        #Gauge Buff. Applies for Iai Slashes
        if not applies_gauge_buff:
            self.true_raw_mult=1/ls_color #Cancel out the color buff

class SwitchAxeAttack(Attack):
    
    """
    Sub-class specific for switch axe attacks due to unique 
    modifiers. Input is an attribute list organized as
    attributes=[name,damage_type,mv,elemod,raw_mult,
    elem_mult, is_sword, green_sharp,sa_phial]

    Specific attributes defined below:
    raw_mult: raw multiplier applied by attack
    elem_mult: element multiplier applied by attack
    is_sword: Is Sword attack? True/False
    green_sharp: Forces Green sharpness? True/False
    sa_phial: SA phial type.
    """

    def __init__(self,attributes):
        #Initialize parent class
        Attack.__init__(self,attributes)

        #Apply attributes to self.true_raw_mult, 
        # self_true_elem mult and self_green_sharp
        self.true_raw_mult=float(attributes[4])
        self.true_elem_mult=float(attributes[5])
        self.green_sharp=bool(int(attributes[7]))
        
        #Other attributes are conditions to check for sword
        #mode and apply Phial boost, if applicable.
        #Store them in new variables for readability
        is_sword=bool(int(attributes[6])) #Is Sword attack?
        sa_phial=str(attributes[8])

        #Apply more buffs if needed (check for sword)
        if (sa_phial=='power' and is_sword):
            self.true_raw_mult*=1.17 #Can't happen simultaneously to the Wild Swings multiplier
        elif (sa_phial=='elemental' and is_sword):
            self.true_elem_mult*=1.45

class ChargeBladeAttack(Attack):
    
    """
    Sub-class specific for Charge Blade attacks due to unique 
    modifiers. Input is an attribute list organized as
    attributes=[name,damage_type,mv,elemod,is_axe,
    is_phial, PA raw, PA elem,cb_phial,cb_shield,cb_power]

    Specific attributes defined below:
    is_axe: is axe attack?
    is__special_phial: is it a special phial attack?
                       SAED phials, shield thrust phials and
                       charged sword phials are unnaffected by 
                       shield charge
    PA raw: extra MV on Impac Phial CB with Power Axe
    PA elem: extra elemod on Elem Phial CB with Power axe
    cb_phial: Impact/Elemental
    cb_shield: Charged?
    cb_power: Activated?
    sharp_raw: raw sharpness modifier
    elem_raw: elem sharpness modifier

    Sharpness modifiers are used to cancel themselves
    out of phial attacks
    """

    def __init__(self,attributes):
        #Initialize parent class
        Attack.__init__(self,attributes)

        #Read variables from attributes list
        is_axe=bool(int(attributes[4]))
        self.is_phial=(self.damage_type=='HZI') #Only Phials have HZI damage type
        is_special_phial=bool(int(attributes[5]))
        pa_raw=int(attributes[6])
        pa_elem=float(attributes[7])
        cb_phial=attributes[8]
        cb_shield=attributes[9]
        cb_power=attributes[10]
        sharp_raw=attributes[11]
        sharp_elem=attributes[12]

        #Check for axe attack with charged shield
        if is_axe and cb_shield:
            self.true_raw_mult=1.10
       
        #Check for phial attacks
        if self.is_phial:
            if cb_phial=='impact':
                self.elemod=0 #No elemental damage
                if cb_shield and not is_special_phial:
                    self.true_raw_mult*=1.20 #extra damage for charged shield
            
            else: #Elemental phials
                self.mv=0 #No raw damage
                self.true_elem_mult=1/sharp_elem #Cancel sharp mod
                if cb_shield and not is_special_phial:
                    self.true_elem_mult*=1.30

        #Check for power axe attacks
        if cb_phial=='impact' and cb_power:
            self.mv+=pa_raw
        elif cb_phial=='element' and cb_power:
            self.elemod+=pa_elem