current_id = 1
register = dict()
FPS = 60

def get_new_id(thing):
    global current_id
    ident = current_id
    current_id += 1

    register[ident] = thing
    return ident

def get(ident):
    return register[ident]

def isclass(thing): # Checks to see if something is a class or contains classes
    if hasattr(thing,'__dict__') or hasattr(thing,'__slots__'):
        return True
    else:
        try:
            for i in thing: # Attempt to iterate, if we can, go deeper
                if isclass(i): return True
        except:
           return False # Otherwise just quit

class GameObject: # Container for all data on a server to be passed to the client when an object is created, requested, or updated

    def __init__(self, parent, id = 0):
        if not id:
            self.id = get_new_id(self)

        else:
            self.id = id
            register[id] = self

        self.parent = parent
        self.tracked_vars = []
        self.update_buffer = None

    def safe_delete(self):
        del register[id]
        del self.parent
        del self

    def register(self, var):
        self.tracked_vars.append(var)

    def update(self): # Updates own tracked variables to reflect parent tracked variables
        for var in self.tracked_vars:
            if var in self.parent.__dict__.keys():
                if isclass(self.parent.__dict__[var]): # Ignore classes for safety purposes
                    continue
                self.__dict__[var] = self.parent.__dict__[var]

        if not self in self.update_buffer:
            self.update_buffer.append(self)