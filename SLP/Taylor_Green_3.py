###########################################################################
# IMPORTS
###########################################################################

# PySPH base imports
from pysph.base.kernels import QuinticSpline
from pysph.base.nnps import DomainManager

# PySPH solver imports
from pysph.solver.application import Application
from pysph.solver.solver import Solver

# PySPH sph imports
from pysph.sph.equation import Equation, Group
from pysph.sph.integrator import Integrator, IntegratorStep

# Numpy import
import numpy as np
import os
pi = np.pi

# Include path
import sys
sys.path.insert(1, '/home/prajwal/Desktop/Winter_Project/SLP-Smoothed-Particle-Hydrodynamics')

# Import Delta_Plus - SPH Equations
from SLP.dpsph.governing_equations import (
    EOS_DPSPH, ContinuityEquation_RDGC_DPSPH, MomentumEquation_DPSPH,
    ContinuityEquation_DPSPH
)
from SLP.dpsph.equations import (
    RenormalizationTensor2D_DPSPH, RDGC_DPSPH, AverageSpacing, 
    ParticleShiftingTechnique
)
from SLP.dpsph.utils import get_particle_array_dpsph

################################################################################
# CODE
################################################################################

# Exact Solution - Taylor Green Vortex
def exact_solution(U, b, t, x, y):
    factor = U * np.exp(b*t)

    u = -np.cos(2*pi*x) * np.sin(2*pi*y)
    v = np.sin(2*pi*x) * np.cos(2*pi*y)
    p = -0.25 * (np.cos(4*pi*x) + np.cos(4*pi*y))

    return factor * u, factor * v, factor * factor * p


# Integrator - Code
class EulerIntegrator_DPSPH(Integrator):
    def one_timestep(self, t, dt):
        self.compute_accelerations()
        self.stage1()
        self.update_domain()
        self.do_post_stage(dt, 1)

        self.stage2()
        self.update_domain()
        self.do_post_stage(dt, 2)


class EulerStep_DPSPH(IntegratorStep):
    """Fast but inaccurate integrator. Use this for testing"""
    def stage1(self, d_idx, d_u, d_v, d_w, d_au, d_av, d_aw, d_x, d_y,
                  d_z, d_rho, d_arho, dt):
        d_u[d_idx] += dt*d_au[d_idx]
        d_v[d_idx] += dt*d_av[d_idx]
        d_w[d_idx] += dt*d_aw[d_idx]

        d_x[d_idx] += dt*d_u[d_idx]
        d_y[d_idx] += dt*d_v[d_idx]
        d_z[d_idx] += dt*d_w[d_idx]

        d_rho[d_idx] += dt*d_arho[d_idx]

    def stage2(self, d_idx, d_d_x, d_d_y, d_x, d_y, d_z):
        """
        Correction -  ParticleShiftingTechnique
        """
        d_x[d_idx] += d_d_x[d_idx]
        d_y[d_idx] += d_d_y[d_idx]

################################################################################
# Tayloy Green Vortex - Application
################################################################################
class Taylor_Green(Application):
    def initialize(self):
        '''
        Initialize simulation paramters
        '''

        # Simulation Parameters
        self.nx = 25
        self.re = 100.0
        self.U = 1.0
        self.L = 1.0
        self.rho0 = 1000.0

        self.c0 = 15.0
        self.hdx = 1.0

        # Calculate simulation parameters
        self.nu = self.L * self.U/self.re
        self.mu = self.nu * self.rho0
        self.dx = self.L/self.nx
        
        
        self.vol = self.dx * self.dx
        self.m0 = self.rho0 * self.vol        
        self.h0 = self.hdx * self.dx
        
        # Simulation time-step parameters
        dt_cfl = 0.25 * self.h0 / (self.c0 + self.U)
        dt_viscous = 0.125 * self.h0**2 / self.nu
        dt_force = 0.25 * 1.0

        self.dt = min(dt_cfl, dt_viscous, dt_force)
        self.tf = 2.0

        # Print parameters
        print('dx : ', self.dx)
        print('dt : ', self.dt)

    def create_particles(self):
        '''
        Set up particle arrays
        '''
        dx = self.dx
        L = self.L
        _x = np.arange(dx/2, L, dx)

        # Fluid
        x0, y0 = np.meshgrid(_x, _x)
        
        b = -8.0-pi*pi/self.re

        u0, v0, p0 = exact_solution(U=self.U, b=b, t=0, x=x0, y=y0)

        pa_fluid = get_particle_array_dpsph(
            name='fluid',x = x0, y=y0, u=u0, v=v0, p=p0, rho = self.rho0, 
            m=self.m0, h=self.h0
        )
        return [pa_fluid]

    def create_domain(self):
        '''
        Set-up periodic boundary
        '''
        L = self.L
        return DomainManager(
            xmin=0, xmax=L, ymin=0, ymax=L, 
            periodic_in_x=True, periodic_in_y=True
        )

    def create_solver(self):
        '''
        Define solver
        '''

        kernel = QuinticSpline(dim=2)
        
        integrator = EulerIntegrator(fluid = EulerStep())

        solver = Solver(
            kernel=kernel, dim=2, integrator=integrator, dt=self.dt, tf=self.tf, 
            pfreq=100
        )

        return solver

    def create_equations(self):
        '''
        Set-up governing equations
        '''
        equations = [
            Group(
                equations=[
                    EOS_DPSPH(
                        dest='fluid', sources=['fluid'],rho0=self.rho0,
                        c0= self.c0
                    )
                ], real=False       
            ),
    
            Group(
                equations=[
                    RenormalizationTensor2D_DPSPH(
                        dest='fluid', sources=['fluid'], dim=2
                    ),

                    RDGC_DPSPH(
                        dest='fluid', sources=['fluid'], dim=2
                    ),

                    AverageSpacing(
                        dest='fluid', sources=['fluid'], dim=2
                    ),

                    ContinuityEquation_RDGC_DPSPH(
                        dest='fluid', sources=['fluid'], delta=0.1, c0=self.c0, 
                        H=self.h0, dim=2
                    ),

                    MomentumEquation_DPSPH(
                        dest='fluid', sources=['fluid'], dim=2, mu=self.mu
                    ), 
                    ParticleShiftingTechnique(
                        dest='fluid', sources=['fluid'], 
                    )
                ], real=True
            )
        ]

        return equations

    ###### Post processing
    def _get_post_process_props(self, array):
        """
        Return x, y, u, v, m
        """
        x, y, u, v, m = array.get('x', 'y', 'u', 'v', 'm')
        
        return x, y, u, v, m

    def post_process(self, info_fname):

        info = self.read_info(info_fname)
        if len(self.output_files) == 0:
            return

        from pysph.solver.utils import iter_output
        decay_rate = -8.0 * pi**2 / self.re

        files = self.output_files
        t, ke, ke_ex, decay, linf, l1 = [], [], [], [], [], []
        for sd, array in iter_output(files, 'fluid'):
            _t = sd['t']
            t.append(_t)
            x, y, u, v, m = self._get_post_process_props(array)
            u_e, v_e, p_e = exact_solution(self.U, decay_rate, _t, x, y)
            vmag2 = u**2 + v**2
            vmag = np.sqrt(vmag2)
            ke.append(0.5 * np.sum(m * vmag2))
            vmag2_e = u_e**2 + v_e**2
            vmag_e = np.sqrt(vmag2_e)
            ke_ex.append(0.5 * np.sum(m * vmag2_e))

            vmag_max = vmag.max()
            decay.append(vmag_max)
            theoretical_max = self.U * np.exp(decay_rate * _t)
            linf.append(abs((vmag_max - theoretical_max) / theoretical_max))

            l1_err = np.average(np.abs(vmag - vmag_e))
            avg_vmag_e = np.average(np.abs(vmag_e))
            # scale the error by the maximum velocity.
            l1.append(l1_err / avg_vmag_e)


        t, ke, ke_ex, decay, l1, linf = list(map(
            np.asarray, (t, ke, ke_ex, decay, l1, linf))
        )
        decay_ex = self.U * np.exp(decay_rate * t)
        fname = os.path.join(self.output_dir, 'results.npz')
        np.savez(
            fname, t=t, ke=ke, ke_ex=ke_ex, decay=decay, linf=linf, l1=l1, 
            decay_ex=decay_ex
        )

        import matplotlib
        matplotlib.use('Agg')

        from matplotlib import pyplot as plt
        plt.clf()
        plt.semilogy(t, decay_ex, label="exact")
        plt.semilogy(t, decay, label="computed")
        plt.xlabel('t')
        plt.ylabel('max velocity')
        plt.legend()
        fig = os.path.join(self.output_dir, "decay_dpsph_3.png")
        plt.savefig(fig, dpi=300)

        plt.clf()
        plt.plot(t, linf)
        plt.xlabel('t')
        plt.ylabel(r'$L_\infty$ error')
        fig = os.path.join(self.output_dir, "linf_error_dpsph_3.png")
        plt.savefig(fig, dpi=300)

        plt.clf()
        plt.plot(t, l1, label="error")
        plt.xlabel('t')
        plt.ylabel(r'$L_1$ error')
        fig = os.path.join(self.output_dir, "l1_error_dpsph_3.png")
        plt.savefig(fig, dpi=300)

################################################################################
# Main Code
################################################################################
if __name__ == '__main__':
    app = Taylor_Green()
    app.run()
    app.post_process(app.info_filename)