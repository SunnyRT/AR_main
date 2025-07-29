class Mediator:

    def __init__(self):
        self.components = {}

    def add(self, component, componentName):
        """Subscribe a component with the mediator."""
        self.components[componentName] = component

    def remove(self, componentName):
        """Unsubscribe a component from the mediator."""
        del self.components[componentName]


    def notify(self, sender, event, data=None):
        """Receive notifications from components and coordinate actions,
            called by the sender component upon event / changes."""
        if sender == "component1" and event == "event1":
            self.handleEvent1(event, data)
        elif sender == "component2" and event == "event2":
            self.handleEvent2(event, data)


    def handleEvent1(self, event, data):
        """Handle event in colleague1 upon notified by component1."""
        colleague1 = self.components.get("colleague1")
        if colleague1:
            colleague1.doSomething(data)

    def handleEvent2(self, event, data):
        """Handle event in colleague1 upon notified by component1."""
        colleague2 = self.componentsget("colleague2")
        if colleague2:
            colleague2.doSomethingElse(data)