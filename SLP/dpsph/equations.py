###########################################################################
# IMPORTS
###########################################################################

# PyPSH Equations Import
from pysph.sph.equation import Equation, Group

# Miscellaneous Import
from textwrap import dedent
from compyle.api import declare

# Math import
from math import sqrt, pow

################################################################################
# Delta_Plus - SPH Sceheme: Supplementary equations, and Particle Shifting 
# Technique
################################################################################

class RenormalizationTensor2D_DPSPH(Equation):
    r""" *Renormaliztion Tensor as defined by the Delta_plus SPH scheme for the 
        2D case*

        ..math::
            \mathbb{L}_{i}=\bigg[\sum_j\mathbf{r_{ji}}\otimes\nabla_i W_{ij}V_j\bigg]^{-1}

        ..math::
            \lambda_i=\text{min}\big(\text{eigenvalue}(\mathbb{L}_i^{-1})\big)

        References:
        -----------
        .. [Sun2017] Sun, P. N., et al. “The δ p l u s -SPH Model: Simple
        Procedures for a Further Improvement of the SPH Scheme.” Computer 
        Methods in Applied Mechanics and Engineering, vol. 315, Mar. 2017, pp. 
        25–49. DOI.org (Crossref), doi:10.1016/j.cma.2016.10.028.

        .. [Marrone2010] Marrone, S., et al. “Fast Free-Surface Detection and Level-
        Set Function Definition in SPH Solvers.” Journal of Computational Physics, 
        vol. 229, no. 10, May 2010, pp. 3652–63. DOI.org (Crossref), 
        doi:10.1016/j.jcp.2010.01.019.

        Parameters:
        -----------
        dim : integer
            Number of dimensions
    """
    def __init__(self, dest, sources, dim):
        r"""
        Parameters:
        -----------
        dim : integer
            Number of dimensions
        """
        if dim != 2:
            raise ValueError("RenormalizationTensor2D_DPSPH - Dimension must be 2!")
        else:
            self.dim = dim

        super(RenormalizationTensor2D_DPSPH, self).__init__(dest, sources)
        
    def initialize(self, d_idx, d_L00, d_L01, d_L10, d_L11, d_lmda):

        d_L00[d_idx] = 0.0
        d_L01[d_idx] = 0.0
        d_L10[d_idx] = 0.0
        d_L11[d_idx] = 0.0

        d_lmda[d_idx] = 0.0 # Initialize \lambda

    def loop(
        self, d_idx, s_idx, XIJ, DWIJ, s_m, s_rho, d_L00, d_L01, d_L10, d_L11
    ):
        r"""
            Computes the renormalization tensor
            
            Paramaters:
            -----------
            d_Lxx : DoubleArray
                Components of the renormalized tensor
        """

        rhoj = s_rho[s_idx]
        mj = s_m[s_idx]
        Vj = mj/rhoj

        # Tensor product
        ### (-1) multiplied because XJI = -1.0*XIJ
        a00 = -1.0*XIJ[0]*DWIJ[0]
        a01 = -1.0*XIJ[0]*DWIJ[1]
        a10 = -1.0*XIJ[1]*DWIJ[0]
        a11 = -1.0*XIJ[1]*DWIJ[1]

        # Sum Renormalization tensor
        d_L00[d_idx] += a00*Vj
        d_L01[d_idx] += a01*Vj
        d_L10[d_idx] += a10*Vj
        d_L11[d_idx] += a11*Vj

    def post_loop(
        self, d_idx, d_L00, d_L01, d_L10, d_L11, d_lmda, EPS
    ):

        # Store Tensor values
        L00 = d_L00[d_idx]
        L01 = d_L01[d_idx]
        L10 = d_L10[d_idx]
        L11 = d_L11[d_idx]

        # Calculate determinant
        Det = L00*L11 - L01*L10
        Det = Det + EPS # Correction if determinant zero

        # Quadratic equation to calculate eigen value
        quad_b = L00 + L11

        tmp1 = quad_b*quad_b - 4*Det

        if tmp1 < 0:
            d_lmda[d_idx] = 1.0
        else:
            tmp = sqrt(tmp1)
            lmda1 = (quad_b + tmp)/2.0
            lmda2 = (quad_b - tmp)/2.0

            # Store lambda with the smaller eigenvalue
            if lmda1 <= lmda2:
                d_lmda[d_idx] = lmda1
            else:
                d_lmda[d_idx] = lmda2

        # Store the inverse of the tensor
        d_L00[d_idx] = L11/Det 
        d_L01[d_idx] = -1.0*L01/Det 
        d_L10[d_idx] = -1.0*L10/Det 
        d_L11[d_idx] = L00/Det   

class AverageSpacing(Equation):
    r"""*Average particle spacing in the neighbourhood of the :math:`i^{th}` 
        particle*

        ..math::
            \Delta p_i = \frac{1}{N_i}\sum_j |\mathbf{r}_{ij}|

        where, :math:`N_i = ` number of neighbours of the :math:`i^{th}` particle

        References:
        -----------
        .. [Monaghan2000] Monaghan, J. J. “SPH without a Tensile Instability.” 
        Journal of Computational Physics, vol. 159, no. 2, Apr. 2000, pp. 
        290–311. DOI.org (Crossref), doi:10.1006/jcph.2000.6439.

        Parameters:
        -----------
        dim : integer
            Number of dimensions
    """
    def __init__(self, dest, sources, dim):
        r"""
        Parameters:
        -----------
        dim : integer
            Number of dimensions
        """
        self.dim = dim
        super(AverageSpacing, self).__init__(dest, sources)

    def initialize(self, d_idx, d_delta_p):
        d_delta_p[d_idx] = 0.0

    def loop_all(
        self, d_idx, d_delta_p, d_x, d_y, d_z, s_x, s_y, s_z, NBRS, N_NBRS
    ):
        i = declare('int')
        s_idx = declare('long')
        xij = declare('matrix(3)')
        rij = 0.0
        sum = 0.0

        for i in range(N_NBRS):
            s_idx = NBRS[i]
            xij[0] = d_x[d_idx] - s_x[s_idx]
            xij[1] = d_y[d_idx] - s_y[s_idx]
            xij[2] = d_z[d_idx] - s_z[s_idx]
            rij = sqrt(xij[0]*xij[0] + xij[1]*xij[1] + xij[2]*xij[2])
            
            sum += rij
    
        d_delta_p[d_idx] += sum/N_NBRS

class RDGC_DPSPH(Equation):
    r"""*The renormalized density gradient correction (RDGC) term  defined by 
        the Delta_plus SPH scheme*

        ..math::
            \langle\nabla\rho\rangle_i^L=\sum_j(\rho_j-\rho_i)\mathbb{L}_{i}.
            \nabla_i W_{ij}V_j

        References:
        -----------
        .. [Marrone2011] Marrone, S., et al. “δ-SPH Model for Simulating Violent
        Impact Flows.” Computer Methods in Applied Mechanics and 
        Engineering, vol. 200, no. 13–16, Mar. 2011, pp. 1526–42. DOI.org 
        (Crossref), doi:10.1016/j.cma.2010.12.016.

        Parameters:
        -----------
        dim : integer
            Number of dimensions
    """

    def __init__(self, dest, sources, dim):
        r"""
        Parameters:
        -----------
        dim : integer
            Number of dimensions
        """
        if dim != 2:
            raise ValueError("RDGC_DPSPH - Dimension must be 2!")
        else:
            self.dim = dim

        super(RDGC_DPSPH, self).__init__(dest, sources)

    def initialize(self, d_idx, d_grad_rho1, d_grad_rho2):
        d_grad_rho1[d_idx] = 0.0
        d_grad_rho2[d_idx] = 0.0

    def loop(
        self, d_idx, s_idx, d_grad_rho1, d_grad_rho2, d_rho, s_rho, d_L00, d_L01, 
        d_L10, d_L11, DWIJ, s_m
    ):

        rhoi = d_rho[d_idx]
        rhoj = s_rho[s_idx]

        Vj = s_m[s_idx]/rhoj

        rhoji = rhoj - rhoi

        tmp1 = d_L00[d_idx]*DWIJ[0] + d_L01[d_idx]*DWIJ[1]
        tmp2 = d_L10[d_idx]*DWIJ[0] + d_L11[d_idx]*DWIJ[1]

        d_grad_rho1[d_idx] += rhoji*tmp1*Vj
        d_grad_rho2[d_idx] += rhoji*tmp2*Vj

class ParticleShiftingTechnique(Equation):
    r"""*Particle-Shifting Technique employed in
        Delta_plus SPH scheme*

        ..math::
            \mathbf{r_i}^\ast=\mathbf{r_i}+\delta\mathbf{\hat{r_i}}
        
        where, 

        ..math::
            \delta\mathbf{\hat{r_i}}=\begin{cases}
                0  & ,\lambda_i\in[0,0.4) \\
                (\mathbb{I}-\mathbf{n_i}\otimes\mathbf{n_i})\delta\mathbf{r_i} 
                & ,\lambda_i\in[0.4, 0.75] \\
                \delta\mathbf{r_i} & ,\lambda_i\in(0.75,1]
            \end{cases}

        ..math::
            \delta\mathbf{r_i}=\frac{-\Delta t c_o(2h)^2}{h_i}.\sum_j\bigg[1+R
            \bigg(\frac{W_{ij}}{W(\Delta p)}\bigg)^n\bigg]\nabla_i W_{ij}\bigg(
            \frac{m_j}{\rho_i+\rho_j}\bigg)

        ..math::
            \mathbf{n_i}=\frac{\langle\nabla\lambda_i\rangle}{|\langle\nabla
            \lambda_i\rangle|}

        ..math::
            \langle\nabla\lambda_i\rangle=\sum_j(\lambda_j-\lambda_i)\otimes
            \mathbb{L}_i\nabla_i W_{ij}V_j

        ..math::
            \lambda_i=\text{min}\big(\text{eigenvalue}(\mathbb{L_i^{-1}})\big)

        ..math::
            \mathbb{L_i}=\bigg[\sum_j\mathbf{r_{ji}}\otimes\nabla_i W_{ij}V_j
            \bigg]^{-1}


        References:
        -----------
        .. [Sun2017] Sun, P. N., et al. “The δ p l u s -SPH Model: Simple
        Procedures for a Further Improvement of the SPH Scheme.” Computer 
        Methods in Applied Mechanics and Engineering, vol. 315, Mar. 2017, pp. 
        25–49. DOI.org (Crossref), doi:10.1016/j.cma.2016.10.028.

        .. [Sun2019] Sun, P. N., et al. “A Consistent Approach to Particle 
        Shifting in the δ - Plus -SPH Model.” Computer Methods in Applied 
        Mechanics and Engineering, vol. 348, May 2019, pp. 912–34. DOI.org 
        (Crossref), doi:10.1016/j.cma.2019.01.045.

        .. [Monaghan2000] Monaghan, J. J. “SPH without a Tensile Instability.” 
        Journal of Computational Physics, vol. 159, no. 2, Apr. 2000, pp. 
        290–311. DOI.org (Crossref), doi:10.1006/jcph.2000.6439.
        
        Parameters:
        -----------
        H : float
            Kernel smoothing length (:math:`h`)

        dim : integer
            Number of dimensions

        cfl : float, default = 0.75
            CFL value

        Uc0 : float. default = 15.0
            :math:`\frac{U}{c_o}` value of the system

        R_coeff : float, default = 0.2
            Artificial pressure coefficient

        n_exp : float, default = 4
            Artificial pressure exponent

        Rh : float, default = 0.075
            Maximum :math:`\frac{|\delta r_i|}{h}` value allowed during Particle
            shifting 
            (Note: :math:`\delta r_i = 0` if :math:`\frac{|\delta r_i|}{h}>R_h`)
    """
    def __init__(
        self, dest, sources, H, dim, cfl=0.5, Uc0=15.0, R_coeff=0.2, n_exp=4.0,
        Rh=0.115
    ):
        r'''
            Parameters:
            -----------
            H : float
                Kernel smoothing length (:math:`h`)

            dim : integer
                Number of dimensions

            cfl : float, default = 0.5
                CFL value

            Uc0 : float. default = 15.0
                :math:`\frac{U}{c_o}` value of the system

            R_coeff : float, default = 0.2
                Artificial pressure coefficient

            n_exp : float, default = 4
                Artificial pressure exponent

            Rh : float, default = 0.075
                Maximum :math:`\frac{|\delta r_i|}{h}` value allowed during Particle
                shifting 
                (Note: :math:`\delta r_i = 0` if :math:`\frac{|\delta r_i|}{h}>R_h`)
        '''       
        if dim != 2:
            raise ValueError("ParticleShiftingTechnique - Dimension must be 2!")
        else:
            self.dim = dim

        self.R_coeff = R_coeff
        self.n_exp = n_exp
        self.H = H
        self.cfl = cfl
        self.Uc0 = Uc0
        self.Rh = Rh

        self.CONST = (-self.cfl/self.Uc0)*4.0*H*H

        super(ParticleShiftingTechnique, self).__init__(dest, sources)

    def initialize(self, d_idx, d_DX, d_DY, d_DRh):
        d_DX[d_idx] = 0.0
        d_DY[d_idx] = 0.0
        d_DRh[d_idx] = 0.0

    def loop_all(
        self, d_idx, d_x, d_y, d_z, s_x, s_y, s_z, d_rho, s_rho, s_m, d_delta_p, 
        d_DX, d_DY, d_DRh, d_lmda, s_lmda, SPH_KERNEL, NBRS, N_NBRS, d_L00, 
        d_L01, d_L10, d_L11
    ):
        i = declare('int')
        s_idx = declare('long')
        xij = declare('matrix(3)')
        dwij = declare('matrix(3)')
        ni = declare('matrix(2)')
        rij = 0.0
        sum1 = 0.0
        sum2 = 0.0
        fac = 0.0
        x = 0.0
        y = 0.0
        rh = 0.0
        sum_nx = 0.0
        sum_ny = 0.0

        rhoi = d_rho[d_idx]
        lmdai = d_lmda[d_idx]
        L00 = d_L00[d_idx]
        L01 = d_L01[d_idx]
        L10 = d_L10[d_idx]
        L11 = d_L11[d_idx]

        if lmdai > 0.4:
            ##################
            # Case - 2 & 3
            ##################

            # Calculate W(\delta p) value
            delta_p = d_delta_p[d_idx]
            w_delta_p = SPH_KERNEL.kernel(xij, delta_p, self.H)

            for i in range(N_NBRS):
                s_idx = NBRS[i]

                rhoj = s_rho[s_idx]
                mj = s_m[s_idx]
                Vj = mj/rhoj

                xij[0] = d_x[d_idx] - s_x[s_idx]
                xij[1] = d_y[d_idx] - s_y[s_idx]
                xij[2] = d_z[d_idx] - s_z[s_idx]
                rij = sqrt(xij[0]*xij[0] + xij[1]*xij[1] + xij[2]*xij[2])

                # Calculate Kernel values
                wij = SPH_KERNEL.kernel(xij, rij, self.H)
                SPH_KERNEL.gradient(xij, rij, self.H, dwij)

                ################################################################
                # Calculate \delta r_i
                ################################################################

                # Calcuate fij
                fij = self.R_coeff * pow( (wij/w_delta_p), self.n_exp )

                # Calcuate multiplicative factor
                fac = (1.0 + fij)*( mj/(rhoi+rhoj) )

                # Sum \delta r_i
                sum1 += fac*dwij[0]
                sum2 += fac*dwij[1]

                ################################################################
                # Calculate n_i
                ################################################################
                lmdaj = s_lmda[s_idx]
                
                # Calcuate multiplicative factor
                fac = (lmdai - lmdaj)*Vj

                # Sum n_i
                sum_nx += (L00*dwij[0] + L01*dwij[1])*fac
                sum_ny += (L01*dwij[0] + L11*dwij[1])*fac

            # (x,y) components of \delta r_i
            x = sum1*self.CONST
            y = sum2*self.CONST
            
            if lmdai <= 0.75:
                ##################
                # Case - 2
                ##################

                ni_norm = sqrt(sum_nx*sum_nx + sum_ny*sum_ny)
                
                ni[0] = sum_nx/ni_norm
                ni[1] = sum_ny/ni_norm

                # I - n_i \otimes n_i
                M00 = 1.0 - ni[0]*ni[0]
                M11 = 1.0 - ni[1]*ni[1]
                M01 = -ni[0]*ni[1]
                M10 = M01

                # Modified (x_new, y_new) values
                x_new = M00*x + M01*y
                y_new = M10*x + M11*y

                rh = sqrt(x_new*x_new + y_new*y_new)/self.H
                if rh > self.Rh:
                    # Check Rh condition
                    d_DX[d_idx] += 0.0
                    d_DY[d_idx] += 0.0
                    d_DRh[d_idx] += 0.0
                else:
                    d_DX[d_idx] += x_new
                    d_DY[d_idx] += y_new
                    d_DRh[d_idx] += rh

            else:
                ##################
                # Case - 3
                ##################
                rh = sqrt(x*x + y*y)/self.H
                if rh > self.Rh:
                    # Check Rh condition
                    d_DX[d_idx] += 0.0
                    d_DY[d_idx] += 0.0
                    d_DRh[d_idx] += 0.0
                else:
                    d_DX[d_idx] += x
                    d_DY[d_idx] += y
                    d_DRh[d_idx] += rh

        else:
            ##################
            # Case - 1
            ##################

            d_DX[d_idx] += 0.0
            d_DY[d_idx] += 0.0
            d_DRh[d_idx] += 0.0