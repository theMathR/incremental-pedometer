# i'm bad at coding
import math

money = 0.0

# The first upgrade is the amount of money/step
# The others autobuy the previous upgrade
# You can only have 1 upgrade 5 since it is only possible to afford 1 U4
money_upgrades = [0.0, 0.0, 0.0, 0.0]
money_upgrades_cost = [10.0, 1000.0, 1e5, 1e9]
money_upgrades_cost_increase = [1.0, 1e2, 1e4, 100.0] # Each upgrade bought adds a certain value to its cost (which quickly becomes negligible) except for U4 which is multiplied (exponantial price)
money_upgrades_mult = [1.0, 1.0, 1.0, 1.0] # Multipliers given by the shoes
money_upgrade_5, money_upgrade_5_cost = False, 1e10 # Separated because there can be only 1

# TODO: Buy feet, shoes, and socks
# TODO: Inventory
feet = 0
shoes_equipped = []
socks_equipped = []

# TODO: Shoes and socks effects
SHOES_FUNCTIONS = [

]

SOCKS_FUNCTIONS = [

]

# TODO: Elements, challenges

def step():
    global money, money_upgrades_mult
    
    # Apply shoe effects
    money_upgrades_mult = [1.0, 1.0, 1.0, 1.0] # Multipliers are reset to be recalculated
    for i in range(feet):
        shoe, sock = shoes_equipped[i], socks_equipped[i]
        SHOES_FUNCTIONS[shoe[0]](shoe[1], SOCKS_FUNCTIONS[sock[0]](sock[1]))
    
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

# Convert float to tandard notation
BEGIN = ['M','B','T','Qa','Qi','Sx','Sp','Oc','No']
UNITS = ['', 'Un', 'Du', 'Tr','Qa','Qi','Sx','Sp','Oc','No']
DEC = ['','De','Vg','Tg','Qag','Qig','Sxg','Spg','Og','Ng']
CEN = ['','Ce','De','Te','Qae','Qie','Sxe','Spe','Oe','Ne']
def float_to_str(f):
    if f < 1e6: return '{:.1f}'.format(f)
    N = math.floor(math.log10(f)/3)
    number_part = f / (1000**N)
    N-=1
    if f < 1e33: suffix = BEGIN[N-1]
    else:
        N_unit = N%10
        N_deci = (N//10)%10
        N_cent = N//100
        suffix = UNITS[N_unit] + DEC[N_deci] + CEN[N_cent]
    return '{:.1f} {}'.format(number_part, suffix)
