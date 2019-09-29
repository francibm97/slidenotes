from slidenotes import app

def onlydebug(decorator):
    return decorator if app.debug == True else lambda x: x

def onlyproduction(decorator):
    return decorator if app.debug == False else lambda x: x

def debugVSproduction(debug_decorator, production_decorator):
    return debug_decorator if app.debug == True else production_decorator
