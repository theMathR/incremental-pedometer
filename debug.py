from tkinter import *
from tkinter import ttk

import game

def step():
    game.step()
    update()

def megastep():
    for i in range(1000):step()
    update()

def fstr(f):
    if snot: return '{:.2g}'.format(f)
    return game.float_to_str(f)

print(game.float_to_str(1))
print(game.float_to_str(1e151))

def update():
    for i in range(4):
        u[i].set("U"+str(i+1)+": x"+fstr(game.money_upgrades[i])+ ", $"+fstr(game.money_upgrades_cost[i]) + ", *"+fstr(game.money_upgrades_mult[i]))
    money.set(fstr(game.money))

def buy(i):
    def w():
        game.buy_upgrade(i)
        update()
    return w

def buy_u5():
    if game.buy_upgrade_5():
        u[4].set("U5: BOUGHT")

snot = False

def scie_not():
    global snot
    snot = not snot
    snots.set('Display: ' + ('Scientific' if snot else 'Standard'))
    update()

root = Tk()
root.title("Incremental Podometer Test")


money = StringVar()
u = [StringVar(), StringVar(), StringVar(), StringVar(), StringVar()]
u[4].set("U5: $"+fstr(game.money_upgrade_5_cost))

Label(textvariable = money).pack()
Button(text = "step", command = step).pack()
Button(text = "step x1000", command = megastep).pack()

for i in range(4):
    Button(textvariable = u[i], command = buy(i)).pack()
Button(textvariable = u[4], command = buy_u5).pack()

snots = StringVar()
snots.set("Display: Standard")
Button(textvariable = snots, command = scie_not).pack()

update()
root.mainloop()
