###########################################################################
# IMPORTS
###########################################################################

# PySPH sph imports
from pysph.sph.integrator import Integrator, IntegratorStep
from math import sqrt, pow

################################################################################
# Delta_Plus - SPH Sceheme: Integrator
################################################################################
class EulerStep(IntegratorStep):
    def stage1(self, d_idx, d_u, d_v, d_au, d_av, d_x, d_y, d_ax, d_ay, dt):
        d_u[d_idx] += dt*d_au[d_idx]
        d_v[d_idx] += dt*d_av[d_idx]

        d_x[d_idx] += dt*d_ax[d_idx]
        d_y[d_idx] += dt*d_ay[d_idx]

class EulerIntegrator_DPSPH(Integrator):
    def one_timestep(self, t, dt):
        # Evaluate Stage1
        self.compute_accelerations(0)
        self.stage1()
        self.update_domain()
        self.do_post_stage(dt, 1)

        # Evaluate Stage2 - PST Correction
        self.compute_accelerations(1, update_nnps=True)
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

    def stage2(self, d_idx, d_DX, d_DY, d_x, d_y):
        r"""
            Particle Shifting Technique correction
        """
        d_x[d_idx] += d_DX[d_idx]
        d_y[d_idx] += d_DY[d_idx]


class DPSPHStep(IntegratorStep):
    """Standard Predictor Corrector integrator for the $\Delta^+$ formulation

    In the predictor step, the particles are advanced to `t + dt/2`. The 
    particles are then advanced with the new force computed at this position.

    This integrator can be used in PEC mode.


    """
    def initialize(self, d_idx, d_x0, d_y0, d_z0, d_x, d_y, d_z,
                   d_u0, d_v0, d_w0, d_u, d_v, d_w, d_rho0, d_rho):
        d_x0[d_idx] = d_x[d_idx]
        d_y0[d_idx] = d_y[d_idx]
        d_z0[d_idx] = d_z[d_idx]

        d_u0[d_idx] = d_u[d_idx]
        d_v0[d_idx] = d_v[d_idx]
        d_w0[d_idx] = d_w[d_idx]

        d_rho0[d_idx] = d_rho[d_idx]

    def stage1(self, d_idx, d_x0, d_y0, d_z0, d_x, d_y, d_z,
                   d_u0, d_v0, d_w0, d_u, d_v, d_w, d_rho0, d_rho, d_au, d_av,
                   d_aw, d_ax, d_ay, d_az, d_arho, dt):
        dtb2 = 0.5*dt
        d_u[d_idx] = d_u0[d_idx] + dtb2*d_au[d_idx]
        d_v[d_idx] = d_v0[d_idx] + dtb2*d_av[d_idx]
        d_w[d_idx] = d_w0[d_idx] + dtb2*d_aw[d_idx]

        d_x[d_idx] = d_x0[d_idx] + dtb2 * d_ax[d_idx]
        d_y[d_idx] = d_y0[d_idx] + dtb2 * d_ay[d_idx]
        d_z[d_idx] = d_z0[d_idx] + dtb2 * d_az[d_idx]

        # Update densities and smoothing lengths from the accelerations
        d_rho[d_idx] = d_rho0[d_idx] + dtb2 * d_arho[d_idx]

    def stage2(self, d_idx, d_x0, d_y0, d_z0, d_x, d_y, d_z, d_DX, d_DY, d_DZ,
                   d_u0, d_v0, d_w0, d_u, d_v, d_w, d_rho0, d_rho, d_au, d_av,
                   d_aw, d_ax, d_ay, d_az, d_arho, d_vmag, d_vmag2, dt):

        d_u[d_idx] = d_u0[d_idx] + dt*d_au[d_idx]
        d_v[d_idx] = d_v0[d_idx] + dt*d_av[d_idx]
        d_w[d_idx] = d_w0[d_idx] + dt*d_aw[d_idx]

        d_x[d_idx] = d_x0[d_idx] + dt * d_ax[d_idx]
        d_y[d_idx] = d_y0[d_idx] + dt * d_ay[d_idx]
        d_z[d_idx] = d_z0[d_idx] + dt * d_az[d_idx]

        # Update densities and smoothing lengths from the accelerations
        d_rho[d_idx] = d_rho0[d_idx] + dt * d_arho[d_idx]

        # magnitude of velocity squared
        d_vmag2[d_idx] = (d_u[d_idx]*d_u[d_idx] + d_v[d_idx]*d_v[d_idx] +
                          d_w[d_idx]*d_w[d_idx])

        d_vmag[d_idx] = sqrt(d_vmag2[d_idx])

        # PST Corrections
        d_x[d_idx] += d_DX[d_idx]
        d_y[d_idx] += d_DY[d_idx]
        d_z[d_idx] += d_DZ[d_idx]


class TransportVelocityStep_DPSPH(IntegratorStep):
    def initialize(self, d_idx, d_rho, d_rho0):
        pass
        d_rho0[d_idx] = d_rho[d_idx]

    def stage1(
        self, d_idx, d_u, d_v, d_w, d_au, d_av, d_aw, d_uhat, d_auhat, d_vhat,
        d_avhat, d_what, d_awhat, d_x, d_y, d_z, dt, d_rho, d_arho, d_rho0
    ):
        dtb2 = 0.5*dt

        # velocity update eqn (14)
        d_u[d_idx] += dtb2*d_au[d_idx]
        d_v[d_idx] += dtb2*d_av[d_idx]
        d_w[d_idx] += dtb2*d_aw[d_idx]

        # advection velocity update eqn (15)
        d_uhat[d_idx] = d_u[d_idx] + dtb2*d_auhat[d_idx]
        d_vhat[d_idx] = d_v[d_idx] + dtb2*d_avhat[d_idx]
        d_what[d_idx] = d_w[d_idx] + dtb2*d_awhat[d_idx]

        # position update eqn (16)
        d_x[d_idx] += dt*d_uhat[d_idx]
        d_y[d_idx] += dt*d_vhat[d_idx]
        d_z[d_idx] += dt*d_what[d_idx]

        d_rho[d_idx] += dtb2 * d_arho[d_idx]

    def stage2(
        self, d_idx, d_u, d_v, d_w, d_au, d_av, d_aw, d_vmag, d_vmag2, dt, 
        d_rho, d_arho, d_rho0, d_x, d_y, d_z, d_DX, d_DY, d_DZ,
    ):
        dtb2 = 0.5*dt

        # corrector update eqn (17)
        d_u[d_idx] += dtb2*d_au[d_idx]
        d_v[d_idx] += dtb2*d_av[d_idx]
        d_w[d_idx] += dtb2*d_aw[d_idx]

        # Update Density
        #d_rho[d_idx] = d_rho0[d_idx] + dt*d_arho[d_idx]
        d_rho[d_idx] = d_rho0[d_idx] + dt * d_arho[d_idx]

        # magnitude of velocity squared
        d_vmag2[d_idx] = d_u[d_idx]*d_u[d_idx] + d_v[d_idx]*d_v[d_idx] + d_w[d_idx]*d_w[d_idx]

        d_vmag[d_idx] = sqrt( d_vmag2[d_idx] )
        
        # PST Correction
        d_x[d_idx] += d_DX[d_idx]
        d_y[d_idx] += d_DY[d_idx]
        d_z[d_idx] += d_DZ[d_idx]

################################################################################
# Delta_Plus - SPH Sceheme: Runge Kutta (4th Order) Integrator
################################################################################

class RK4Integrator(Integrator):
    def one_timestep(self, t, dt):
        #Initialise `y_{n}` properties
        self.stage0()

        #Store computed `k_1` properties, and subsequently calculate `Y_2`
        self.compute_accelerations(update_nnps=True)
        self.stage1()
        self.update_domain()

        #Store computed `k_2` properties, and subsequently calculate `Y_3`
        self.compute_accelerations(update_nnps=True)
        self.stage2()
        self.update_domain()

        #Store computed `k_3` properties, and subsequently calculate `Y_4`
        self.compute_accelerations(update_nnps=True)
        self.stage3()
        self.update_domain()

        #Store computed `k_4` properties, and subsequently calculate `y_{n+1}`
        self.compute_accelerations(update_nnps=True)
        self.stage4()
        self.update_domain()

        self.compute_accelerations(index=1, update_nnps=True)
        self.stage5()
        self.update_domain()

class RK4Step(IntegratorStep):
    def stage0(
        self, d_idx, d_x, d_y, d_u, d_v, d_rho,
        d_x0, d_y0, d_u0, d_v0, d_rho0,
    ):
        #Initialise `y_{n}` properties
        d_x0[d_idx] = d_x[d_idx]
        d_y0[d_idx] = d_y[d_idx]
        d_u0[d_idx] = d_u[d_idx]
        d_v0[d_idx] = d_v[d_idx]
        d_rho0[d_idx] = d_rho[d_idx]

        #print('0', d_x[d_idx], d_y[d_idx], d_u[d_idx], d_v[d_idx], d_rho[d_idx])

    def stage1(
        self, d_idx, d_x, d_y, d_u, d_v, d_rho,
        d_x0, d_y0, d_u0, d_v0, d_rho0,
        d_ax, d_ay, d_au, d_av, d_arho,
        d_xstar, d_ystar, d_ustar, d_vstar, d_rhostar,
        dt,
    ):
        dtby2 = dt*0.5
        
        #Store computed `k_1` properties
        d_xstar[d_idx] = d_ax[d_idx]
        d_ystar[d_idx] = d_ay[d_idx]
        d_ustar[d_idx] = d_au[d_idx]
        d_vstar[d_idx] = d_av[d_idx]
        d_rhostar[d_idx] = d_arho[d_idx]
        
        #Calculate `Y_2`
        d_x[d_idx] = d_x0[d_idx] + d_ax[d_idx]*dtby2
        d_y[d_idx] = d_y0[d_idx] + d_ay[d_idx]*dtby2
        d_u[d_idx] = d_u0[d_idx] + d_au[d_idx]*dtby2
        d_v[d_idx] = d_v0[d_idx] + d_av[d_idx]*dtby2
        d_rho[d_idx] = d_rho0[d_idx] + d_arho[d_idx]*dtby2

    def stage2(
        self, d_idx, d_x, d_y, d_u, d_v, d_rho,
        d_x0, d_y0, d_u0, d_v0, d_rho0,
        d_ax, d_ay, d_au, d_av, d_arho,
        d_xstar, d_ystar, d_ustar, d_vstar, d_rhostar,
        dt,
    ):
        dtby2 = dt*0.5
        
        #Store computed `k_2` properties
        d_xstar[d_idx] += 2.0*d_ax[d_idx]
        d_ystar[d_idx] += 2.0*d_ay[d_idx]
        d_ustar[d_idx] += 2.0*d_au[d_idx]
        d_vstar[d_idx] += 2.0*d_av[d_idx]
        d_rhostar[d_idx] += 2.0*d_arho[d_idx]
        
        #Calculate `Y_3`
        d_x[d_idx] = d_x0[d_idx] + d_ax[d_idx]*dtby2
        d_y[d_idx] = d_y0[d_idx] + d_ay[d_idx]*dtby2
        d_u[d_idx] = d_u0[d_idx] + d_au[d_idx]*dtby2
        d_v[d_idx] = d_v0[d_idx] + d_av[d_idx]*dtby2
        d_rho[d_idx] = d_rho0[d_idx] + d_arho[d_idx]*dtby2

    def stage3(
        self, d_idx, d_x, d_y, d_u, d_v, d_rho,
        d_x0, d_y0, d_u0, d_v0, d_rho0,
        d_ax, d_ay, d_au, d_av, d_arho,
        d_xstar, d_ystar, d_ustar, d_vstar, d_rhostar,
        dt,
    ):
        #Store computed `k_3` properties
        d_xstar[d_idx] += 2.0*d_ax[d_idx]
        d_ystar[d_idx] += 2.0*d_ay[d_idx]
        d_ustar[d_idx] += 2.0*d_au[d_idx]
        d_vstar[d_idx] += 2.0*d_av[d_idx]
        d_rhostar[d_idx] += 2.0*d_arho[d_idx]
        
        #Calculate `Y_4`
        d_x[d_idx] = d_x0[d_idx] + d_ax[d_idx]*dt
        d_y[d_idx] = d_y0[d_idx] + d_ay[d_idx]*dt
        d_u[d_idx] = d_u0[d_idx] + d_au[d_idx]*dt
        d_v[d_idx] = d_v0[d_idx] + d_av[d_idx]*dt
        d_rho[d_idx] = d_rho0[d_idx] + d_arho[d_idx]*dt

    def stage4(
        self, d_idx, d_x, d_y, d_u, d_v, d_rho,
        d_x0, d_y0, d_u0, d_v0, d_rho0,
        d_ax, d_ay, d_au, d_av, d_arho,
        d_xstar, d_ystar, d_ustar, d_vstar, d_rhostar,
        d_vmag2, d_vmag, dt,
    ):
        dtby6 = dt/6.0
        #Store computed `k_4` properties
        d_xstar[d_idx] += d_ax[d_idx]
        d_ystar[d_idx] += d_ay[d_idx]
        d_ustar[d_idx] += d_au[d_idx]
        d_vstar[d_idx] += d_av[d_idx]
        d_rhostar[d_idx] += d_arho[d_idx]
        
        #Calculate `y_{n+1}`
        d_x[d_idx] = d_x0[d_idx] + d_xstar[d_idx]*dtby6
        d_y[d_idx] = d_y0[d_idx] + d_ystar[d_idx]*dtby6
        d_u[d_idx] = d_u0[d_idx] + d_ustar[d_idx]*dtby6
        d_v[d_idx] = d_v0[d_idx] + d_vstar[d_idx]*dtby6
        d_rho[d_idx] = d_rho0[d_idx] + d_rhostar[d_idx]*dtby6

        # magnitude of velocity squared
        d_vmag2[d_idx] = (d_u[d_idx]*d_u[d_idx] + d_v[d_idx]*d_v[d_idx])

        d_vmag[d_idx] = sqrt(d_vmag2[d_idx])

    def stage5(
        self, d_idx, d_x, d_y,
        d_DX, d_DY,
    ):

        # PST Corrections
        d_x[d_idx] += d_DX[d_idx]
        d_y[d_idx] += d_DY[d_idx]