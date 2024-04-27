# i'm bad at coding
import math, random

money = 0.0

# The first upgrade is the amount of money/step
# The others autobuy the previous upgrade
# You can only have 1 upgrade 5 since it is only possible to afford 1 U4
money_upgrades = [0.0, 0.0, 0.0, 0.0]
money_upgrades_cost = [10.0, 1000.0, 1e5, 1e9]
money_upgrades_cost_increase = [1.0, 1e2, 1e4, 100.0] # Each upgrade bought adds a certain value to its cost (which quickly becomes negligible) except for U4 which is multiplied (exponantial price)
money_upgrades_mult = [1.0, 1.0, 1.0, 1.0] # Multipliers given by the shoes
money_upgrade_5, money_upgrade_5_cost = False, 1e10 # Separated because there can be only 1

class BasicShoe:
    def __init__(self, level=1):
        self.level = level
    
    @property
    def name(self): return "Basic shoe"
    
    @property
    def description(self): return "Multiplies money/step by {:.3f}".format(math.log(self.level,100)+1)
    
    def apply_effect(self, multiplier=1):
        money_upgrades_mult[0] *= (1+math.log(self.level,100))*multiplier

class BasicSock:
    def __init__(self, level=1):
        self.level = level
    
    @property
    def name(self): return "Basic shoe"
    
    @property
    def description(self): return "Boost shoe depending only on level (x{:.3f})".format(math.log(self.level,1000)+1)
    
    @property
    def boost(self):
        return 1+math.log(self.level,1000)

# Shoes and socks owned
shoes = [BasicShoe(10)]
socks = [BasicSock(12)]

feet = 1
# Contain index numbers to the shoes/socks in the previous lists
shoes_equipped = [0]
socks_equipped = [0]

# 0: Scientific
# 1: Standard
# 2: Mixed scientific (standard < 1e33)
notation = 2

# TODO: Elements, challenges

def step():
    global money, money_upgrades_mult
    
    # Apply shoe effects
    money_upgrades_mult = [1.0, 1.0, 1.0, 1.0] # Multipliers are reset to be recalculated
    for i in range(feet):
        shoe, sock = shoes[shoes_equipped[i]], socks[socks_equipped[i]]
        shoe.apply_effect(sock.boost)
    
    # Create money based on U1
    money += (1+money_upgrades[0]) * money_upgrades_mult[0]
    
    # Each upgrade except U1 autobuys the one before
    for i in range(3):
        buy_upgrade(i, money_upgrades[i+1] * money_upgrades_mult[i+1])
    if money_upgrade_5: buy_upgrade_4()

def buy_upgrade(i,n=1): # i is the upgrade index, n is the number of upgrades to buy
    global money
    if i==3: return buy_upgrade_4()
    if i==4: return buy_upgrade_5()
    
    # Check number of upgrades we can afford
    while money_upgrades_cost[i] * n > money:
        n -= 1
        if n == 0: return False
        
    # Buy!
    cost = money_upgrades_cost[i] * n
    money -= cost
    money_upgrades[i] += n
    return True

def buy_upgrade_4(): # Seperated because upgrade 4 works differently
    global money
    if money_upgrades_cost[3] > money: return False
    money -= money_upgrades_cost[3]
    money_upgrades_cost[3] *= money_upgrades_cost_increase[3]
    money_upgrades[3] += 1
    return True

def buy_upgrade_5(): # Same
    global money, money_upgrade_5
    if money_upgrade_5 or money_upgrade_5_cost > money: return False
    money -= money_upgrade_5_cost
    money_upgrade_5 = True
    return True

def change_notation():
    global notation
    notation = (notation+1)%3

# Convert float to str depending on the notation
BEGIN = ['M','B','T','Qa','Qi','Sx','Sp','Oc','No']
UNITS = ['', 'Un', 'Du', 'Tr','Qa','Qi','Sx','Sp','Oc','No']
DEC = ['','De','Vg','Tg','Qag','Qig','Sxg','Spg','Og','Ng']
CEN = ['','Ce','De','Te','Qae','Qie','Sxe','Spe','Oe','Ne']
def float_to_str(f):
    if f < 1e6: return '{:.1f}'.format(f)
    if notation == 0: return '{:.2g}'.format(f)
    N = math.floor(math.log10(f)/3)
    number_part = f / (1000**N)
    N-=1
    if f < 1e33: suffix = BEGIN[N-1]
    elif notation == 2: return '{:.2g}'.format(f)
    else: suffix = UNITS[N%10] + DEC[(N//10)%10] + CEN[N//100]
    return '{:.1f} {}'.format(number_part, suffix)
