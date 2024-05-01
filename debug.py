from tkinter import *
from tkinter import ttk

import game

shoe_list=['0 Basic shoe lv1','1 Basic shoe lv1']
sock_list=['0 Basic sock lv1','1 Basic sock lv1']

def step():
    game.step()
    update()

def update_slist():
    global shoe_list, sock_list
    shoe_list = ['{} {} lv{}'.format(i,s.name,s.level) for i,s in enumerate(game.shoes)]
    sock_list = ['{} {} lv{}'.format(i,s.name,s.level) for i,s in enumerate(game.socks)]
    for i,m in enumerate(menus):
        m[0].destroy()
        m[0] = OptionMenu(root, menus_opti[i][0], *sock_list)
        m[0].pack()
        m[1].destroy()
        m[1] = OptionMenu(root, menus_opti[i][1], *shoe_list)
        m[1].pack()

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

def equip():
    for i,j in enumerate(menus_opti):
        game.equip(0, sock_list.index(j[0].get()), i)
        game.equip(1, shoe_list.index(j[1].get()), i)
    update_slist()

def buy_u5():
    if game.buy_upgrade_5():
        u[4].set("U5: BOUGHT")


def chg_not():
    game.change_notation()
    nota.set('Notation: ' + ['Scientific','Standard','Mixed scientific'][game.notation])
    update()

def fbuyf():
    if not game.buy_foot(): return
    fbuy.set("Feet: x" + fstr(game.feet) + " $"+ fstr(game.foot_price))
    menus.append([Label(text='h'),Label(text='h')])
    menus_opti.append([StringVar(),StringVar()])
    update_slist()
    update()

root = Tk()
root.title("Incremental Podometer Test")


money = StringVar()
u = [StringVar(), StringVar(), StringVar(), StringVar(), StringVar()]
u[4].set("U5: $"+fstr(game.money_upgrade_5_cost))

Label(textvariable = money).pack()
Button(text = "step", command = step).pack()
Button(text = "step x1000", command = megastep).pack()

Label().pack()

for i in range(4):
    Button(textvariable = u[i], command = buy(i)).pack()
Button(textvariable = u[4], command = buy_u5).pack()

Label().pack()

nota = StringVar()
nota.set("Notation: Mixed scientific")
Button(textvariable = nota, command = chg_not).pack()

Label().pack()

fbuy = StringVar()
fbuy.set("Feet: x" + fstr(game.feet) + " $"+ fstr(game.foot_price))
Button(textvariable = fbuy, command = fbuyf).pack()

Button(text = 'Equip shoes and socks set below', command = equip).pack()

Button(text='Save', command = game.save).pack()

menus = [[Label(text='h'),Label(text='h')],[Label(text='h'),Label(text='h')]]
menus_opti = [[StringVar(),StringVar(),],[StringVar(),StringVar(),]]

step()
update_slist()
root.mainloop()
