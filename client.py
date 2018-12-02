from PodSixNet.Connection import ConnectionListener, connection
from turtle import Screen, Turtle

from common_classes import *

import time
import keyboard as keyb
import types


class Listener(ConnectionListener):

    def Network_error(self, data):
        print(f"{data['error'][0]} Error: {data['error'][1]}")
        connection.Close()

    def Network_connected(self, data):
        print("Connection established with " + str(connection.addr))
        return

    def Network_disconnected(self, data):
        global connected
        if connected:
            print("Connection lost.")
            connected = False
        return

    def Network_create(self, data): # format: "type" "id" "data"
        print(data)
        if not data['type'] in draw_table.keys():
            return
        thing = GameObject(data['id'])
        thing.__dict__ = data['data']

        thing.draw_func = types.MethodType(draw_table[data['type']], thing)
        game_objects.append(thing)


    def Network_update(self, data): # format: "id" "data"
        thing = get(data['id'])
        draw_func = thing.draw_func
        new_dict = data['data']
        thing.__dict__ = {**thing.__dict__, **new_dict} # merge two dicts, overwriting old
        thing.draw_func = draw_func

    def Network_delete(self, data): # format: "id"
        thing = get(data['id'])
        game_objects.pop(thing)
        thing.safe_delete()


# Menu and functions

def menu(): # Main menu function and decides which type of game to start based on player input
    print("WELCOME TO TURTLE NATIONS!")
    print("-" * 30)
    print("\n")
    print("For a singleplayer game, enter 1. For a multiplayer game, enter 2. Enter anything else to exit.")

    option = input("> ")
    #TODO: Better interface
    if option == '1':
        # init_single()
        # TODO: SINGLEPLAYER GAME
        raise SystemExit

    elif option == '2':
        init_mult()

    else:
        raise SystemExit # Exit the game

    return main_loop()


def get_connection_info(): # Get connection info from player, with sanity checks
    address = input("Enter address to connect to (leave blank for localhost): ")
    port = input("Enter port to connect to: ")

    try:
        port = int(port) # Make sure the port entered is an integer
    except:
        print("Error, invalid port entered.")
        return None, None

    return address, port

def check_connection():
    seconds = 0
    while seconds < TIME_OUT and not connection.isConnected:
        connection.Pump()
        Client.Pump()
        seconds += 1
        time.sleep(1)
    return connection.isConnected

def init_mult():
    global connected
    address, port = None, None

    while not port:
        address, port = get_connection_info()


    Client.Connect((address,port))
    if not check_connection():
        print("Connection timed out.")
        return menu()

    connected = True
    start_visualizer()
    return

# Engine functionss

def start_visualizer():
    global screen
    screen = Screen()
    screen.tracer(0,0)

def key_hook(event):
    key_buffer.append(event.name)

def send_updates():
    global key_buffer
    for event in key_buffer:
        Client.Send({ "action" : "event", "event" : event})

    key_buffer = []

def collect_updates():
    connection.Pump() # Refreshes connections
    Client.Pump() # Runs new events also CLEARS events that it can use

def new_pen(color):
    pen = Turtle("turtle")
    pen.color(color)
    pen.penup()

    return pen


def render_updates():
 #   screen.clearscreen()
    for object in game_objects:
        object.draw_func()

    screen.update()

def turtle_draw(self):
    if not hasattr(self, 'pen'):
        self.pen = new_pen(self.color)
    self.pen.goto(self.x, self.y)
    self.pen.setheading(self.heading)

def main_loop():
    while connected:
        collect_updates()
        send_updates()
        render_updates()
        time.sleep(1/FPS)

    return menu()




# Global variables
screen = None
key_buffer = []
keyb.hook(key_hook)
game_objects = []
TIME_OUT = 10

draw_table = {'Turtle' : turtle_draw}

connected = False

# Main body
Client = Listener()
menu()
#main_loop()
