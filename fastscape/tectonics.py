import numpy as np
import xsimlab as xs

from .boundaries import ClosedBoundaryFaces
from .main_drivers import SurfaceTopography


@xs.process
class BlockUplift(object):
    """Vertical block uplift as external forcing."""

    rate = xs.variable(dims=[(), ('y', 'x')], description='uplift rate')
    active_nodes = xs.foreign(ClosedBoundaryFaces, 'active_nodes', intent='in')

    uplift = xs.variable(dims=[(), ('y', 'x')], intent='out',
                         group='elevation_up',
                         description='tectonic (vertical) uplift')

    def initialize(self):
        self.uplift = np.zeros_like(self.active_nodes, dtype='d')

    def run_step(self, dt):
        self.uplift = self.u_rate * dt
        self.uplift[~self.active_nodes] = 0.


@xs.process
class ApplyTectonicUplift(object):
    """Apply tectonic uplift on surface topography.

    The main purpose of this process is to compute erosion processes
    based on a surface elevation that has been already uplifted.

    It addresses some issues especially when erosion processes are
    computed using an implicit numerical scheme.

    """
    elevation = xs.foreign(SurfaceTopography, 'elevation')
    uplift = xs.foreign(BlockUplift, 'uplift')

    elevation_uplifted = xs.variable(dims=('y', 'x'), intent='out')

    def run_step(self, dt):
        self.elevation_uplifted = self.elevation + self.uplift
