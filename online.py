import wifi
import socketpool

def host():
    wifi.radio.start_ap('test')
    pool = socketpool.SocketPool(wifi.radio)
    with pool.socket() as s:
        s.bind(('test', 4130))
        s.listen(5)

def connect():
    wifi.radio.connect('test')
    pool = socketpool.SocketPool(wifi.radio)
    with pool.socket() as s:
        s.connect(('test', 4130))
