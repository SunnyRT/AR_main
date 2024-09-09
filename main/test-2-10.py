from core.base import Base

# check input
class Test(Base):

    def initialize(self):
        print("Initializing program...")

    def update(self):

        # # debug printing
        # if len(self.input.keysDownList) > 0:
        #     print("Keys down: ", self.input.keysDownList)

        # if len(self.input.keysPressedList) > 0:
        #     print("Keys pressed: ", self.input.keysPressedList)

        # if len(self.input.keysUpList) > 0:
        #     print("Keys up: ", self.input.keysUpList)

        # if self.input.mouseDelta != (0,0):
        #     print("Mouse delta: ", self.input.mouseDelta)

        # if self.input.mouseScroll != 0:
        #     print("Mouse scroll: ", self.input.mouseScroll)
        
        # typical usage
        if self.input.isKeyDown("space"):
            print("The 'space' bar was just pressed down.")
        
        if self.input.isKeyPressed("right"):
            print("The 'right' key is currently being pressed.")
        


# instantiate this class and run the program
Test().run()