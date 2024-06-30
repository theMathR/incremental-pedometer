import math, random, json

# Useful random function
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
    def name(self): return f"Basic shoe LV{self.level}"
    
    @property
    def description(self): return "Multiplies money/step by {:.3f}".format(math.log(self.level,100)+1)
    
    def apply_effect(self, multiplier=1):
        pass

class BasicSock(Sock):
    i=1
    power=False
    @property
    def name(self): return f"Basic sock LV{self.level}"
    
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
    
    muscles=money_upgrades=money_gained=nb_orpheus=training_mode=energy_orpheus=0.0
    money_upgrades_autobuyers=cereal_bar_autobuyers=apple_autobuyers=0.0
    money_upgrades_autobuyer_price,cereal_bar_autobuyer_price,apple_autobuyer_price=1000.0,1000.0,100000.0
    money_upgrades_autobuyers_on = True
    money_upgrade_price = 100.0
    sacrifice_price=123456789.0
    energy = energy_orpheus = 100.0
    training_mode_unlocked = False
    
    save = json.load(save_file)

    steps = save['steps']
    total_steps = save['total_steps']

    money = save['money']
    
    #money_step_upgrades = save['money_step_upgrades']
    
    #energy = save['energy']

    feet = save['feet']
    foot_price=1000.0

    # Contain index numbers to the shoes/socks in the previous lists
    shoes_equipped = save['shoes_equipped']
    socks_equipped = save['socks_equipped']
    
    # 0: Scientific
    # 1: Standard
    # 2: Mixed scientific (standard < 1e33)
    notation = save['notation']
    
    # Shoes and socks owned
    shoes = [ALL[s['type']](s['level'], s['data']) for s in save['shoes']] + [BasicShoe()]
    socks = [ALL[s['type']](s['level'], s['data']) for s in save['socks']]
    
    items_bought = save['items_bought']
    bears = save['bears']
    
    # Theme
    theme_index = save['theme']

def step():
    global money, energy, energy_orpheus, steps, total_steps, money_gained
    
    # TODO: Apply shoe effects
    
    # Count steps
    steps += 1
    total_steps += 1
    
    # Get money
    money_gained = (1+money_upgrades * (energy/100)**(1/4)) * (1 + nb_orpheus * (energy_orpheus/100)**(1/8))
    money += money_gained
    energy -= ((1+money_upgrades/200)/5) * (1.5 if training_mode else 1)
    if energy < 0: energy = 0
    if nb_orpheus:
        energy_orpheus -= (1+money_upgrades/200)/10
        if energy_orpheus < 0: energy_orpheus = 0
    
    # Use autobuyers
    if money_upgrades_autobuyers_on: buy_money_upgrade(n=money_upgrades_autobuyers)
    buy_cereal_bar(n=min(cereal_bar_autobuyers, int(100+muscles - energy)/(10 if training_mode else 20)))
    buy_apple(n=min(apple_autobuyers, (100-energy_orpheus)*nb_orpheus/20))
    
    # Update item durability
    update_durability(shoes,shoes_equipped)
    update_durability(socks,socks_equipped)

def unlock_training_mode():
    global money, training_mode_unlocked
    if money < 5000: return False
    money -= 5000
    training_mode_unlocked = True
    return True

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
                equipped[i]=None
            if s > r:
                equipped[i]-=1

def buy_money_upgrade(n=1):
    global money, money_upgrades, money_upgrades_price
    money_upgrades_price = 100+money_upgrades*150
    for i in range(n):
        if money<money_upgrades_price: return False
        money -= money_upgrades_price
        money_upgrades += 1
        money_upgrades_price = 100+money_upgrades*150
    return True
        

def buy_cereal_bar(n=1):
    global money, energy
    for i in range(n):
        if money < 500: return False
        money -= 500
        energy = min(energy+(10 if training_mode else 20), 100+int(muscles))
    return True

def buy_apple(n=1):
    global money, energy_orpheus
    for i in range(n):
        if money < 1000: return False
        money -= 1000
        energy_orpheus = min(100, energy_orpheus+20/nb_orpheus)
    return True

def buy_money_upgrades_autobuyer():
    global money, money_upgrades_autobuyers, money_upgrades_autobuyer_price
    if money < money_upgrades_autobuyer_price: return False
    money -= money_upgrades_autobuyer_price
    money_upgrades_autobuyer_price += 1000
    money_upgrades_autobuyers+=1
    return True

def buy_cereal_bar_autobuyer():
    global money, cereal_bar_autobuyers, cereal_bar_autobuyer_price
    if money < cereal_bar_autobuyer_price: return False
    money -= cereal_bar_autobuyer_price
    cereal_bar_autobuyer_price += 1000
    cereal_bar_autobuyers+=1
    return True

def buy_apple_autobuyer():
    global money, apple_autobuyers, apple_autobuyer_price
    if money < apple_autobuyer_price: return False
    money -= apple_autobuyer_price
    apple_autobuyer_price += 1000
    apple_autobuyers+=1
    return True

def toggle_money_upgrades_autobuyers():
    global money_upgrades_autobuyers_on
    money_upgrades_autobuyers_on = not money_upgrades_autobuyers_on
    return True

def sacrifice():
    global money, energy, money_upgrades, training_mode, muscles, feet, nb_orpheus, energy_orpheus, sacrifice_price
    if money<sacrifice_price: return False
    money = 0
    energy = 100
    money_upgrades = 0
    training_mode = False
    muscles = 0
    feet = 2
    training_mode_unlocked = False
    money_upgrades_autobuyers = cereal_bar_autobuyers = 0
    while len(shoes_equipped)>2:
        shoes_equipped.pop()
        socks.equipped.pop()
    energy_orpheus = 100
    nb_orpheus *= 2
    sacrifice_price += 1234565789
    if nb_orpheus == 0: nb_orpheus = 1
    return True

def money_to_muscles():
    return int(math.log10(money))

def toggle_training():
    global training_mode, money, money_saved, muscles
    if not training_mode:
        money_saved = money
        money = 0
        training_mode = True
    else:
        money = money_saved
        muscles = money_to_muscles()
        training_mode = False

def buy_foot():
    global money, foot_price, feet
    if money < foot_price: return False
    money -= foot_price
    foot_price **= 1.3
    feet += 1
    shoes.append(BasicShoe(1))
    socks.append(BasicSock(1))
    shoes_equipped.append(len(shoes)-1)
    socks_equipped.append(len(socks)-1)
    return True

def buy_item():
    global money, item_price, bears
    if money < item_price: return False
    money -= item_price
    item_price *= 1.05
    
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

def remove_item(sock_or_shoe, inv_index):
    if sock_or_shoe == SOCK:
        if inv_index in socks_equipped: return False
        socks.pop(inv_index)
        for i,s in enumerate(socks_equipped):
            if s > inv_index:
                socks_equipped[i]-=1
    else:
        if inv_index in shoes_equipped: return False
        shoes.pop(inv_index)
        for i,s in enumerate(shoes_equipped):
            if s > inv_index:
                shoes_equipped[i]-=1
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
        'bears': bears,
        'feet': feet,
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
        'items_bought': items_bought,
        'theme': theme_index,
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

