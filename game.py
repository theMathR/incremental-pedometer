# i'm bad at coding
import math, random, json

# TODO: Fix saving

def gauss(mu=0,sigma=1):
    while True:
        u = random.uniform(-1,1)
        v = random.uniform(-1,1)
        s = u**2 + v**2
        if s >= 1: continue
        return mu + sigma*math.sqrt(-2*math.log(s)/s)


class Item:
    def __init__(self, level=1, data=0, durability=int(750000+1000*gauss(mu=0,sigma=15))):
        self.level = level
        self.data = data
        self.durability = durability

class Shoe(Item): pass
class Sock(Item): pass

class Nothing:
    def apply_effect(self, multiplier=1): pass
    boost = 1

class BasicShoe(Shoe):
    i=0
    @property
    def name(self): return "Basic shoe"
    
    @property
    def description(self): return "Multiplies money/step by {:.3f}".format(math.log(self.level,100)+1)
    
    def apply_effect(self, multiplier=1):
        money_upgrades_mult[0] *= (1+math.log(self.level,100))*multiplier


class BasicSock(Sock):
    i=1
    @property
    def name(self): return "Basic sock"
    
    @property
    def description(self): return "Boost shoe depending only on level (x{:.3f})".format(math.log(self.level,1000)+1)
    
    @property
    def boost(self):
        return 1+math.log(self.level,1000)

ALL = [
    BasicShoe,
    BasicSock,
] 

TIERS = [
    [ # Tier 1
    BasicShoe,
    BasicSock,
    ],
    [ # Tier 2
    BasicShoe,
    BasicSock,
    ],
    [ # Tier 3
    BasicShoe,
    BasicSock,
    ],
    [ # Tier 4
    BasicShoe,
    BasicSock,
    ],
] 

with open('save.json','r') as save_file:
    save = json.load(save_file)

    steps = save['steps']
    total_steps = save['total_steps']

    money = save['money']

    # The first upgrade is the amount of money/step
    # The others autobuy the previous upgrade
    # You can only have 1 upgrade 5 since it is only possible to afford 1 U4
    money_upgrades = save['money_upgrades']
    money_upgrades_cost = save['money_upgrades_cost']
    money_upgrade_5 = save['money_upgrade_5'] # Separated because there can be only 1


    feet = save['feet']
    foot_price = save['foot_price']

    # Contain index numbers to the shoes/socks in the previous lists
    shoes_equipped = save['shoes_equipped']
    socks_equipped = save['socks_equipped']
    
    # 0: Scientific
    # 1: Standard
    # 2: Mixed scientific (standard < 1e33)
    notation = save['notation']
    
    # Shoes and socks owned
    shoes = [ALL[s['type']](s['level'], s['data']) for s in save['shoes']]
    socks = [ALL[s['type']](s['level'], s['data']) for s in save['socks']]
    
    item_price = save['item_price']
    bears = save['bears']
    
    # Theme
    theme_index = save['theme']

money_upgrade_5_cost = 1e10
money_upgrades_cost_increase = [1.0, 1e2, 1e4, 100.0] # Each upgrade bought adds a certain value to its cost (which quickly becomes negligible) except for U4 which is multiplied (exponential price)
foot_price_increase = 1.3
money_upgrades_mult = [1.,1.,1.,1.] # Multipliers given by the shoes

# TODO: Elements, challenges

def step():
    global money, money_upgrades_mult, steps, total_steps
    
    # Count steps
    steps += 1
    total_steps += 1
    
    # Apply shoe effects
    money_upgrades_mult = [1.0, 1.0, 1.0, 1.0] # Multipliers are reset to be recalculated
    for i in range(feet):
        shoe, sock = shoes[shoes_equipped[i]] if shoes_equipped[i] else Nothing(), socks[socks_equipped[i]] if socks_equipped[i] else Nothing()
        shoe.apply_effect(sock.boost)
    
    # Create money based on U1
    money += (1+money_upgrades[0]) * money_upgrades_mult[0]
    
    # Each upgrade except U1 autobuys the one before
    for i in range(3):
        buy_upgrade(i, money_upgrades[i+1] * money_upgrades_mult[i+1])
    if money_upgrade_5: buy_upgrade_4()
    
    # Update item durability
    update_durability(shoes,shoes_equipped)
    update_durability(socks,socks_equipped)

def update_durability(inventory, equipped):
    to_remove=[]
    for i,s in enumerate(equipped):
        inventory[s].durability-=1
        if inventory[s].durability == 0:
            to_remove.append(s)
    for r in to_remove:
        inventory.pop(r)
        for i,s in enumerate(equipped):
            if r == s:
                equipped[i]=False
            if s > r:
                equipped[i]-=1

def buy_upgrade(i,n=1): # i is the upgrade index, n is the number of upgrades to buyF
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

def buy_foot():
    global money, foot_price, feet
    if money < foot_price: return False
    money -= foot_price
    foot_price **= foot_price_increase
    feet += 1
    shoes.append(BasicShoe(1))
    socks.append(BasicSock(1))
    shoes_equipped.append(len(shoes)-1)
    socks_equipped.append(len(socks)-1)
    return True

item_price_multiplier = 1.05
def buy_item():
    global money, item_price, bears
    if money < item_price: return False
    money -= item_price
    item_price *= item_price_multiplier
    
    tier_rand = random.randint(1,16)
    if tier_rand <= 8:
        tier = TIERS[0]
    elif tier_rand <= 12:
        tier = TIERS[1]
    elif tier_rand <= 14:
        tier = TIERS[2]
    elif tier_rand <= 15:
        tier = TIERS[3]
    else:
        bears+=1
        return True
    
    item = random.choice(tier)()
    item.durability = 5
    if tier_rand==15:
        item.durability = math.inf
    if isinstance(item, Sock):
        socks.append(item)
    else:
        shoes.append(item)
    return True

SOCK = 0
SHOE = 1
def equip(sock_or_shoe, inv_index, foot_index):
    if sock_or_shoe == SOCK:
        if inv_index in socks_equipped: return False
        socks_equipped[foot_index] = inv_index
    else:
        if inv_index in shoes_equipped: return False
        shoes_equipped[foot_index] = inv_index
    return True

def change_notation():
    global notation
    notation = (notation+1)%3

def change_theme(l):
    global theme_index
    theme_index = (theme_index+1)%l

def reset_steps():
    global steps
    steps = 0

def save():
    save = {
        'steps': steps,
        'total_steps': total_steps,
        'money': money,
        'money_upgrades': money_upgrades,
        'money_upgrades_cost': money_upgrades_cost,
        'money_upgrade_5': money_upgrade_5,
        'feet': feet,
        'foot_price': foot_price,
        'shoes_equipped': shoes_equipped,
        'socks_equipped': socks_equipped,
        'notation': notation,
        'shoes': [
            {
                'type': s.i,
                'level': s.level,
                'data': s.data,
            }
        for s in shoes],
        'socks': [
            {
                'type': s.i,
                'level': s.level,
                'data': s.data,
            }
        for s in socks],
        'bears': bears,
        'item_price': item_price,
        'theme': theme,
    }
    with open('save.json', 'w') as save_file:
        json.dump(save, save_file)

# Convert float to str depending on the notation
BEGIN = ['M','B','T','Qa','Qi','Sx','Sp','Oc','No']
UNITS = ['', 'Un', 'Du', 'Tr','Qa','Qi','Sx','Sp','Oc','No']
DEC = ['','De','Vg','Tg','Qag','Qig','Sxg','Spg','Og','Ng']
CEN = ['','Ce'] # The maximum is 179.7 UnCe (1.79e308)
def float_to_str(f):
    if f < 1e6: return '{:.0f}'.format(f)
    if notation == 0: return '{:.2g}'.format(f)
    N = math.floor(math.log(f,10)/3)
    number_part = f / (1000**N)
    N-=1
    if f < 1e33: suffix = BEGIN[N-1]
    elif notation == 2: return '{:.2g}'.format(f)
    else: suffix = UNITS[N%10] + DEC[(N//10)%10] + CEN[N//100]
    return '{:.1f} {}'.format(number_part, suffix)

