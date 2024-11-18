from factory.meshFactory import MeshFactory

class MatchMeshFactory(MeshFactory):
    def __init__(self, alpha=0.5, mediator=None):
        super().__init__(mediator)

    # FIXME:!
    def update(self, del_n=None):
        # override parent class method
        if del_n is not None:
            pass