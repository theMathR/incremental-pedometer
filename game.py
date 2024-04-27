# i'm bad at coding

money = 0.0

# The first upgrade is the amount of money/step
# The others autobuy the previous upgrade
money_upgrades = [1.0, 0.0, 0.0, 0.0]
money_upgrades_cost = [10.0, 1000.0, 1e5, 1e9]
money_upgrades_cost_mult = [2.0, 4.0, 8.0, 16.0] # TODO: Balance cost increase
money_upgrades_mult = [1.0, 1.0, 1.0, 1.0]

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

def buy_upgrade(i,n=1): # i is the upgrade index, n is the number of upgrades to buy
    global money
    cost = money_upgrades_cost[i]
    mult = money_upgrades_cost_mult[i]
    while cost * mult ** (n-1) > money and n>0:
        n-=1
    if n==0:return
    total_cost = cost * mult ** (n-1)
    money -= total_cost
    money_upgrades[i] += n
    money_upgrades_cost[i] = total_cost * mult
    
