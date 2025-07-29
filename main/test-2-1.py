from core.base import BaseCanvas

class Test(BaseCanvas):

    def initialize(self, parent):
        print("Initializing program...")

    def update(self):
        pass

# instantiate this class and run the program
Test().run()
