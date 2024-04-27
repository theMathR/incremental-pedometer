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
    return game.float_to_str(f)

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


def chg_not():
    game.change_notation()
    nota.set('Notation: ' + ['Scientific','Standard','Mixed scientific'][game.notation])
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

nota = StringVar()
nota.set("Notation: Mixed scientific")
Button(textvariable = nota, command = chg_not).pack()

step()
root.mainloop()
