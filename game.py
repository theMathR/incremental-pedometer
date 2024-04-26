import math

money = 0.0
money_upgrades = [1.0, 0.0, 0.0, 0.0]
money_upgrades_times_bought = [0, 0, 0, 0]
money_upgrades_cost = [10.0, 1000.0, 1e5, 1e9]
money_upgrades_cost_mult = [100.0, 1e4, 1e6, 1e8]
money_upgrades_mult = [1.0, 1.0, 1.0, 1.0]
money_upgrades_base_mult = [1.0, 1.0, 1.0, 1.0]

def step():
    global money, money_upgrades_mult
    
    money_upgrades_mult = money_upgrades_base_mult[:]
    
    # TODO: Shoe bonuses
    
    money += money_upgrades[0] * money_upgrades_mult[0]
    for i in range(3):
        money_upgrades[i] += money_upgrades[i+1] * money_upgrades_mult[i+1]

def buy_upgrade(i):
    global money
    cost = money_upgrades_cost[i]
    if money < cost: return
    money -= cost
    money_upgrades[i] += 1
    money_upgrades_times_bought[i] += 1
    if money_upgrades_times_bought[i] % 10 == 0:
        money_upgrades_base_mult[i] *= 1.1
        money_upgrades_cost[i] *= money_upgrades_cost_mult[i]

