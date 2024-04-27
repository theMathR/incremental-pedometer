# i'm bad at coding

money = 0.0

# The first upgrade is the amount of money/step
# The others autobuy the previous upgrade
# You can only have 1 upgrade 5 since it is only possible to afford 1 U4
money_upgrades = [1.0, 0.0, 0.0, 0.0]
money_upgrades_cost = [10.0, 1000.0, 1e5, 1e9]
money_upgrades_cost_increase = [1.0, 1e2, 1e4, 100.0] # Last one is a multiplier
money_upgrades_mult = [1.0, 1.0, 1.0, 1.0]
money_upgrade_5, money_upgrade_5_cost = False, 1e10

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
    
    money += money_upgrades[0] * money_upgrades_mult[0]
    for i in range(3):
        buy_upgrade(i, money_upgrades[i+1] * money_upgrades_mult[i+1])
    if money_upgrade_5: buy_upgrade_4()

def calculate_money_upgrade_cost(i,n):
    return money_upgrades_cost[i] * n + money_upgrades_cost_increase[i] * (n-1) if i != 3 \
        else money_upgrades_cost[i] * money_upgrades_cost_increase[i] # Note: for upgrade 4 we assume we only buy it one at a time (that should be true)

def buy_upgrade(i,n=1): # i is the upgrade index (less than 3), n is the number of upgrades to buy
    global money
    if i==3: return buy_upgrade_4()
    if i==4: return buy_upgrade_5()
    
    while money_upgrades_cost[i] * n > money:
        n -= 1
        if n == 0: return False
        
    cost = money_upgrades_cost[i] * n
    money -= cost
    money_upgrades[i] += n
    return True

def buy_upgrade_4():
    global money
    if money_upgrades_cost[3] > money: return False
    money -= money_upgrades_cost[3]
    money_upgrades_cost[3] *= money_upgrades_cost_increase[3]
    money_upgrades[3] += 1
    return True

def buy_upgrade_5():
    global money, money_upgrade_5
    if money_upgrade_5 or money_upgrade_5_cost > money: return False
    money -= money_upgrade_5_cost
    money_upgrade_5 = True
    return True
