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
    return '{:.2g}'.format(f)

def update():
    for i in range(4):
        u[i].set("U"+str(i)+": x"+fstr(game.money_upgrades[i])+ ", $"+fstr(game.money_upgrades_cost[i]) + ", *"+fstr(game.money_upgrades_mult[i]))
    money.set(fstr(game.money))

def buy(i):
    def w():
        game.buy_upgrade(i)
        update()
    return w

root = Tk()
root.title("Incremental Podometer Test")

money = StringVar()
u = [StringVar(), StringVar(), StringVar(), StringVar()]

Label(textvariable = money).pack()
Button(text = "step", command = step).pack()
Button(text = "step x1000", command = megastep).pack()

for i in range(4):
    Button(textvariable = u[i], command = buy(i)).pack()

update()
root.mainloop()
