from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

from common_classes import *

import time
from math import *

### Server Backend

class ClientChannel(Channel):

    def Network_event(self, data):
        events.append((data['event'], self))

    def Close(self):
        print("Disconnection: " + str(self.addr))

class MyServer(Server):
    channelClass = ClientChannel

    def Connected(self, channel, addr):
        print("New Connection: " + str(addr))
        handle_connection(channel)

# Object Helpers

def create_object(object, track_vars): # Creates an object with a data container tracking the specified vars
    object.object = GameObject(object)
    game_objects.append(object)

    for var in track_vars: object.object.register(var)
    object.object.update_buffer = update_list
    object.object.update()
    send_all_channels(object)
    return object

def send_object(obj, channel): # Sends an object to a channel, takes GameObject!
    safe_dict = {r: v for r, v in obj.object.__dict__.items() if not isclass(v)} # Removes classes to avoid encoding issues
    print(safe_dict)
    channel.Send({"action": "create", "type": type(obj).__name__, "id": obj.object.id, "data": safe_dict})

def send_all_objects(channel): # Sends all objects to a channel - generally used for new connections
    for object in game_objects:
        send_object(object, channel)

def send_all_channels(object): # Send an object to all channels - generally used for new objects
    for channel in server.channels:
        send_object(object, channel)

def update_object(obj): # Updates an object when update is called on that object
    safe_dict = {r: v for r, v in obj.__dict__.items() if not isclass(v)}  # Removes classes to avoid encoding  - TAKES GameObject!
    for channel in server.channels:
        channel.Send({"action": "update", "data" : safe_dict, "id" : obj.id})

def update_channels(obj, exclude): # Sends a created object to all other channels except the excluded one - TAKES ANY OBJECT! - used when only one client doesn't need to know something
    # TODO: A better solution than something snowflakey like this.
    for channel in server.channels:
        if channel == exclude:
            continue
        send_object(obj, channel)


# Main procs


def handle_connection(channel): # Called when a new client connects
    send_all_objects(channel) # By sending objects first and then creating the avatar, we don't have to snowflake in update_channels

    avatar = create_object(Turtle(), ['x', 'y', 'heading', 'color'])
    channel.avatar = avatar
    avatar.goto(0, 0)

def process_events():
    global events
    for event, channel in events:
        if event == "up":
            channel.avatar.forward(5)

        if event == "down":
            channel.avatar.forward(-5)

        if event == "left":
            channel.avatar.turn(5)

        if event == "right":
            channel.avatar.turn(-5)

    events = []

def process_updates():
    for update in update_list:
        update_object(update)

def main_loop():
    while True:
        server.Pump()
        process_events()
        process_updates()
        time.sleep(1/FPS)

### Server Frontend

class Turtle:
    def __init__(self, x = 0, y = 0, heading = 0, color = "black"):
        self.x = x
        self.y = y
        self.heading = heading
        self.color = color
        self.object = None

    def forward(self, amount):
        self.y += amount * sin(radians(self.heading))
        self.x += amount * cos(radians(self.heading))
        self.object.update()

    def turn(self, amount):
        self.heading += amount
        if self.heading >= 360:
            self.heading -= 359

        if self.heading < 0:
            self.heading += 360

        self.object.update()

    def goto(self, x, y):
        self.x = x
        self.y = y
        self.object.update()


# Global Variables
game_objects = []
events = []
update_list = []

# main
server = MyServer()
print("Server Started")
main_loop()

