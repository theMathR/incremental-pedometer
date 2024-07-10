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
    def __init__(self, level=1, previous_owners=['00000','00000','00000']):
        self.level = level
        self.previous_owners = previous_owners

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
    def description(self): return "Multiplies money/step by {:.3f}".format(math.log(self.level,100000)+1)
    
    def apply_effect(self, multiplier=1):
        effects[0] *= (math.log(self.level,100000)+1)*multiplier

class EnergyShoe(Shoe):
    i=2
    @property
    def name(self): return f"Energy shoe LV{self.level}"
    
    @property
    def description(self): return "Makes you lose energy slower by /{:.3f}".format(math.log(self.level,500)+1)
    
    def apply_effect(self, multiplier=1):
        effects[1] /= (math.log(self.level,500)+1)*multiplier

class OrpheusShoe(Shoe):
    i=4
    @property
    def name(self): return f"Orpheus shoe LV{self.level}"
    
    @property
    def description(self): return "Makes sacrifice summon more Orpheuses"
    
    def apply_effect(self, multiplier=1):
        effects[2] = 1

class FoodShoe(Shoe):
    i=5
    @property
    def name(self): return f"Food shoe LV{self.level}"
    
    @property
    def description(self): return "Makes food prices lower by -{:.0f}".format(min(20,self.level)*10)
    
    def apply_effect(self, multiplier=1):
        effects[3] += min(20,self.level)*10*math.sqrt(self.multiplier)
        effects[3] = min(effects[3],400)


class UpgradeShoe(Shoe):
    i=13
    @property
    def name(self): return f"Upgrade shoe LV{self.level}"
    
    @property
    def description(self): return "Makes money upgrade prices lower by -{:.0f}".format(min(20,self.level)*10)
    
    def apply_effect(self, multiplier=1):
        effects[9] += min(20,self.level)*10*math.sqrt(self.multiplier)
        effects[9] = min(effects[3],400)

class MoneyShoe(Shoe):
    i=7
    @property
    def name(self): return f"Money shoe LV{self.level}"
    
    @property
    def description(self): return "Makes money upgrades stronger by x{:.0f}".format(math.pow(self.level + 1, 1/4) * 1.5)
    
    def apply_effect(self, multiplier=1):
        effects[4] *= self.multiplier * math.pow(self.level + 1, 1/4) * 1.5

class RobotShoe(Shoe):
    i=8
    @property
    def name(self): return f"Robot shoe LV{self.level}"
    
    @property
    def description(self): return "Autobuyers prices raise slower by /{:.0f}".format(1+math.log(self.multiplier * (self.level + 1), 100))
    
    def apply_effect(self, multiplier=1):
        effects[5] += math.log(self.multiplier * (self.level + 1), 100)


class TrainingShoe(Shoe):
    i=9
    @property
    def name(self): return f"Training shoe LV{self.level}"
    
    @property
    def description(self): return "Makes the debuffs in Training mode smaller"
    
    def apply_effect(self, multiplier=1):
        effects[8] += math.log(self.multiplier * (self.level + 1), 100)


class PowerShoe(Shoe):
    i=10
    @property
    def name(self): return f"Power shoe LV{self.level}"
    
    @property
    def description(self): return "Multiplies money by a small value every step depending on level"
    
    def apply_effect(self, multiplier=1):
        effects[7] += self.level * self.multiplier


class DoubleShoe(Shoe):
    i=11
    @property
    def name(self): return f"Double shoe LV{self.level}"
    
    @property
    def description(self): return "Makes a step give money twice once level 5 is reached"
    
    def apply_effect(self, multiplier=1):
        effects[6] = 0 if self.level >= 5 else 1

class BasicSock(Sock):
    i=1
    @property
    def name(self): return f"Basic sock LV{self.level}"
    
    @property
    def description(self): return "Boost shoe depending only on level (x{:.3f})".format(self.boost)
    
    @property
    def boost(self):
        return 1+math.log(self.level,1000)

class TeamworkSock(Sock):
    i=3
    @property
    def name(self): return f"Teamwork sock LV{self.level}"
    
    @property
    def description(self): return "Does nothing until level 10 where it boosts shoe by x5"
    
    @property
    def boost(self):
        return 5 if self.level >= 10 else 1

class ExperienceSock(Sock):
    i=6
    @property
    def name(self): return f"Experience sock LV{self.level}"
    
    @property
    def description(self): return "Boost shoe depending on total step count (x{:.3f})".format(self.boost)
    
    @property
    def boost(self):
        return math.log(total_steps*math.sqrt(self.level),1e8)+1

class GoldenSock(Sock):
    i=12
    @property
    def name(self): return f"Golden sock LV{self.level}"
    
    @property
    def description(self): return "Boost shoe depending on money (x{:.3f})".format(self.boost)
    
    @property
    def boost(self):
        return math.log(math.sqrt(money*math.sqrt(self.level)),1e10)+1

ALL = [
    BasicShoe,
    BasicSock,
    EnergyShoe,
    TeamworkSock,
    OrpheusShoe,
    FoodShoe,
    ExperienceSock,
    MoneyShoe,
    RobotShoe,
    TrainingShoe,
    PowerShoe,
    DoubleShoe,
    GoldenSock,
    UpgradeShoe,
]

effects = [1]*10

with open('save.json','r') as save_file:
    
    muscles=money_upgrades=money_gained=energy_orpheus=0.0
    money_upgrades_autobuyers=cereal_bar_autobuyers=apple_autobuyers=0.0
    money_upgrades_autobuyer_price,cereal_bar_autobuyer_price,apple_autobuyer_price=1000.0,1000.0,100000.0
    money_upgrades_autobuyers_on = True
    sacrifice_price=123456789.0
    energy = energy_orpheus = 100.0
    training_mode_unlocked = False
    training_mode = False
    cereal_bar_price = 500
    apple_price = 1000
    nb_orpheus=10
    
    save = json.load(save_file)

    steps = save['steps']
    total_steps = save['total_steps']

    money = save['money']

    name = save['name']
    
    item_price = 500
    
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
    shoes = [ALL[s['type']](s['level'], s['previous_owners']) for s in save['shoes']]
    socks = [ALL[s['type']](s['level'], s['previous_owners']) for s in save['socks']]
    
    items_bought = save['items_bought']
    bears = save['bears']
    
    # Theme
    theme_index = save['theme']

def step():
    global money, energy, energy_orpheus, steps, total_steps, money_gained, effects
        
    # Count steps
    steps += 1
    total_steps += 1
    
    # Shoe effects
    effects = [1]*len(effects)
    for i in range(feet):
        if shoes_equipped[i] and socks_equipped[i]:
            shoes[shoes_equipped[i]].apply_effect(socks[socks_equipped[i]].boost)
    
    # Get money
    money_gained = (1+money_upgrades * effects[4] * (energy/100)**(1/4)) * (1 + nb_orpheus * (energy_orpheus/100)**(1/8))
    print(effects)
    print(money_gained)
    money += money_gained * effects[0]
    money *= 1+effects[7]/5e4
    energy -= ((1+money_upgrades/200)/5) * (1.5/effects[8] if training_mode else 1) * effects[1]
    if energy < 0: energy = 0
    if nb_orpheus:
        energy_orpheus -= (1+money_upgrades/200)/10
        if energy_orpheus < 0: energy_orpheus = 0
    
    # Use autobuyers
    if money_upgrades_autobuyers_on: buy_money_upgrade(n=money_upgrades_autobuyers)
    buy_cereal_bar(n=min(cereal_bar_autobuyers, int(100+muscles - energy)/(10 if training_mode else 20)))
    buy_apple(n=min(apple_autobuyers, (100-energy_orpheus)*nb_orpheus/20))
    
    if effects[6] == 0:
        step()
        steps -= 1
        total_steps -= 1

def unlock_training_mode():
    global money, training_mode_unlocked
    if money < 5000: return False
    money -= 5000
    training_mode_unlocked = True
    return True
    
def buy_money_upgrade(n=1):
    global money, money_upgrades
    money_upgrades_price = 100+money_upgrades*150-effects[9]+1
    for i in range(n):
        if money<money_upgrades_price: return False
        money -= money_upgrades_price
        money_upgrades += 1
        money_upgrades_price = 100+money_upgrades*150-effects[9]+1
    return True
        

def buy_cereal_bar(n=1):
    global money, energy
    for i in range(n):
        if money < cereal_bar_price - effects[3] + 1: return False
        money -= cereal_bar_price - effects[3] + 1
        energy = min(energy+(10+max(5,10*(effects[8]-1)) if training_mode else 20), 100+int(muscles))
    return True

def buy_apple(n=1):
    global money, energy_orpheus
    for i in range(n):
        if money < apple_price - effects[3] + 1: return False
        money -= apple_price - effects[3] + 1
        energy_orpheus = min(100, energy_orpheus+20/nb_orpheus)
    return True

def buy_money_upgrades_autobuyer():
    global money, money_upgrades_autobuyers, money_upgrades_autobuyer_price
    if money < money_upgrades_autobuyer_price: return False
    money -= money_upgrades_autobuyer_price
    money_upgrades_autobuyer_price += 1000/effects[5]
    money_upgrades_autobuyers+=1
    return True

def buy_cereal_bar_autobuyer():
    global money, cereal_bar_autobuyers, cereal_bar_autobuyer_price
    if money < cereal_bar_autobuyer_price: return False
    money -= cereal_bar_autobuyer_price
    cereal_bar_autobuyer_price += 1000/effects[5]
    cereal_bar_autobuyers+=1
    return True

def buy_apple_autobuyer():
    global money, apple_autobuyers, apple_autobuyer_price
    if money < apple_autobuyer_price: return False
    money -= apple_autobuyer_price
    apple_autobuyer_price += 1000/effects[5]
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
    nb_orpheus *= 2 + effects[2]
    sacrifice_price += 1234565789
    if nb_orpheus == 0: nb_orpheus = 1 + effects[2]
    return True

def money_to_muscles():
    return int(math.log(money+1, 10))

def toggle_training():
    global training_mode, money, money_saved, muscles
    if not training_mode:
        money_saved = money
        money = 0
        training_mode = True
    else:
        x = money_to_muscles()
        if muscles < x: muscles = x
        money = money_saved
        training_mode = False
    return True

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
    
    if random.randint(1,16)==16:
        bears+=1
        return True
    
    item = random.choice(ALL)()
    (shoes if isinstance(item, Shoe) else socks).append(item)
    return item


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

#def remove_item(sock_or_shoe, inv_index):
#    if sock_or_shoe == SOCK:
#        if inv_index in socks_equipped: return False
#        socks.pop(inv_index)
#        for i,s in enumerate(socks_equipped):
#            if s > inv_index:
#                socks_equipped[i]-=1
#    else:
#        if inv_index in shoes_equipped: return False
#        shoes.pop(inv_index)
#        for i,s in enumerate(shoes_equipped):
#            if s > inv_index:
#                shoes_equipped[i]-=1
#    return True

def change_notation():
    global notation
    notation = (notation+1)%3

def change_theme(l):
    global theme_index
    theme_index = (theme_index+1)%l

def reset_steps():
    global steps
    steps = 0

def trade(sock_or_shoe, index, new_item):
    (shoes if sock_or_shoe==SHOE else socks)[index] = new_item
    if not name in new_item.previous_owners:
        new_item.previous_owners.pop(0)
        new_item.level += 1
    else:
        new_item.previous_owners.remove(name)
    new_item.previous_owners.append(name)

def item_to_bytes(item):
    l = [item.i, item.level]
    for o in item.previous_owners:
        l += list(map(ord, o))
    return bytearray(l)

def bytes_to_item(bytes):
    item = ALL[int(bytes[0])]()
    item.level = int(bytes[1])
    item.previous_owners = [
        ''.join(map(chr,bytes[2:7])),
        ''.join(map(chr,bytes[7:12])),
        ''.join(map(chr,bytes[12:17])),
    ]
    return item

def save():
    save = {
        'steps': steps,
        'total_steps': total_steps,
        'money': money,
        'feet': feet,
        'shoes_equipped': shoes_equipped,
        'socks_equipped': socks_equipped,
        'notation': notation,
        'shoes': [
            {
                'type': s.i,
                'level': s.level,
                'prevous_owners': s.prevous_owners,
            }
        for s in shoes],
        'socks': [
            {
                'type': s.i,
                'level': s.level,
                'prevous_owners': s.prevous_owners,
            }
        for s in socks],
        'bears': bears,
        'items_bought': items_bought,
        'theme': theme_index,
        'name': name
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

