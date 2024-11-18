from factory.meshFactory import MeshFactory

class ProjectorMeshFactory(MeshFactory):
    def __init__(self, microscope, n, f, delta, color, alpha=0.5, mediator=None):
        super().__init__(mediator)
        self.ms = microscope
        self.n = n
        self.f = f
        self.delta = delta
        self.color = color
        self.alpha = alpha


    def update(self, mesh, del_n=None, del_f=None):
        # override parent class method
        if del_n is not None: # update n
            self.n += del_n
        if del_f is not None:
            self.f += del_f
        mesh = super().update(mesh)
        mesh.translate(0, 0, -self.n)
        return mesh