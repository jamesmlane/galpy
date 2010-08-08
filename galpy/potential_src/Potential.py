###############################################################################
#   Potential.py: top-level class for a full potential
#
#   Evaluate by calling the instance: Pot(R,z,phi)
#
#   API for Potentials:
#      function _evaluate(self,R,z,phi) returns Phi(R,z,phi)
#      function _Rforce(self,R,z,phi) return K_R
#      function _zforce(self,R,z,phi) return K_z
###############################################################################
import os, os.path
import cPickle as pickle
import numpy as nu
import galpy.util.bovy_plot as plot
from plotRotcurve import plotRotcurve
from plotEscapecurve import plotEscapecurve
class Potential:
    """Top-level class for a potential"""
    def __init__(self,amp=1.):
        """
        NAME:
           __init__
        PURPOSE:
        INPUT:
           amp - amplitude to be applied when evaluating the potential and its forces
        OUTPUT:
        HISTORY:
        """
        self._amp= amp
        self.dim= 3
        self.isRZ= True
        self.isNonAxi= False
        return None

    def __call__(self,*args):
        """
        NAME:
           __call__
        PURPOSE:
           evaluate the (R,z)
        INPUT:
           R - Cylindrical Galactocentric radius
           z - vertical height
           phi - azimuth (optional)
        OUTPUT:
           Phi(z;R)
        HISTORY:
           2010-04-16 - Written - Bovy (NYU)
        """
        try:
            return self._amp*self._evaluate(*args)
        except AttributeError:
            raise PotentialError("'_evaluate' function not implemented for this potential")

    def Rforce(self,*args):
        """
        NAME:
           Rforce
        PURPOSE:
           evaluate radial force K_R  (R,z)
        INPUT:
           R - Cylindrical Galactocentric radius
           z - vertical height
           phi - azimuth (optional)
        OUTPUT:
           K_R (R,z,phi)
        HISTORY:
           2010-04-16 - Written - Bovy (NYU)
        DOCTEST:
        """
        try:
            return self._amp*self._Rforce(*args)
        except AttributeError:
            raise PotentialError("'_Rforce' function not implemented for this potential")
        
    def zforce(self,*args):
        """
        NAME:
           zforce
        PURPOSE:
           evaluate the vertical force K_R  (R,z)
        INPUT:
           R - Cylindrical Galactocentric radius
           z - vertical height
           phi - azimuth (optional)
        OUTPUT:
           K_z (R,z,phi)
        HISTORY:
           2010-04-16 - Written - Bovy (NYU)
        DOCTEST:
        """
        try:
            return self._amp*self._zforce(*args)
        except AttributeError:
            raise PotentialError("'_zforce' function not implemented for this potential")

    def dens(self,*args):
        """
        NAME:
           dens
        PURPOSE:
           evaluate the density rho(R,z)
        INPUT:
           R - Cylindrical Galactocentric radius
           z - vertical height
           phi - azimuth (optional)
        OUTPUT:
           rho (R,z,phi)
        HISTORY:
           2010-08-08 - Written - Bovy (NYU)
        DOCTEST:
        """
        try:
            return self._amp*self._dens(*args)
        except AttributeError:
            raise PotentialError("'_dens' function not implemented for this potential")

    def normalize(self,norm):
        """
        NAME:
           normalize
        PURPOSE:
           normalize a potential in such a way that vc(R=1,z=0)=1., or a 
           fraction of this
        INPUT:
           norm - normalize such that Rforce(R=1,z=0) is such that it is
                  'norm' of the force necessary to make vc(R=1,z=0)=1
                  if True, norm=1
        OUTPUT:
        HISTORY:
           2010-07-10 - Written - Bovy (NYU)
        """
        self._amp*= norm/nu.fabs(self.Rforce(1.,0.))

    def phiforce(self,*args):
        """
        NAME:
           phiforce
        PURPOSE:
           evaluate the azimuthal force K_R  (R,z,phi)
        INPUT:
           R - Cylindrical Galactocentric radius
           z - vertical height
           phi - azimuth (rad)
        OUTPUT:
           K_phi (R,z,phi)
        HISTORY:
           2010-07-10 - Written - Bovy (NYU)
        """
        try:
            return self._amp*self._phiforce(*args)
        except AttributeError:
            return 0.

    def _phiforce(self,*args):
        """
        NAME:
           _phiforce
        PURPOSE:
           evaluate the azimuthal force K_R  (R,z,phi)
        INPUT:
           R - Cylindrical Galactocentric radius
           z - vertical height
           phi - azimuth (rad)
        OUTPUT:
           K_phi (R,z,phi)
        HISTORY:
           2010-07-10 - Written - Bovy (NYU)
        """
        return 0.

    def toPlanar(self):
        from planarPotential import RZToplanarPotential
        return RZToplanarPotential(self)

    def toVertical(self,R):
        from verticalPotential import RZToverticalPotential
        return RZToverticalPotential(self,R)

    def plot(self,rmin=0.,rmax=1.5,nrs=21,zmin=-0.5,zmax=0.5,nzs=21,
             ncontours=21,savefilename=None):
        """
        NAME:
           plot
        PURPOSE:
           plot the potential
        INPUT:
           rmin - minimum R
           rmax - maximum R
           nrs - grid in R
           zmin - minimum z
           zmax - maximum z
           nzs - grid in z
           ncontours - number of contours
           savefilename - save to or restore from this savefile (pickle)
        OUTPUT:
           plot to output device
        HISTORY:
           2010-07-09 - Written - Bovy (NYU)
        """
        if not savefilename == None and os.path.exists(savefilename):
            print "Restoring savefile "+savefilename+" ..."
            savefile= open(savefilename,'rb')
            potRz= pickle.load(savefile)
            Rs= pickle.load(savefile)
            zs= pickle.load(savefile)
            savefile.close()
        else:
            Rs= nu.linspace(rmin,rmax,nrs)
            zs= nu.linspace(zmin,zmax,nzs)
            potRz= nu.zeros((nrs,nzs))
            for ii in range(nrs):
                for jj in range(nzs):
                    potRz[ii,jj]= self._evaluate(Rs[ii],zs[jj])
            if not savefilename == None:
                print "Writing savefile "+savefilename+" ..."
                savefile= open(savefilename,'wb')
                pickle.dump(potRz,savefile)
                pickle.dump(Rs,savefile)
                pickle.dump(zs,savefile)
                savefile.close()
        return plot.bovy_dens2d(potRz.T,origin='lower',cmap='gist_gray',contours=True,
                                xlabel=r"$R/R_0$",ylabel=r"$z/R_0$",
                                xrange=[rmin,rmax],
                                yrange=[zmin,zmax],
                                aspect=.75*(rmax-rmin)/(zmax-zmin),
                                cntrls='-',
                                levels=nu.linspace(nu.nanmin(potRz),nu.nanmax(potRz),
                                                   ncontours))
        

    def plotRotcurve(self,*args,**kwargs):
        """
        NAME:
           plotRotcurve
        PURPOSE:
           plot the rotation curve for this potential (in the z=0 plane for
           non-spherical potentials)
        INPUT:
           Rrange - range
           grid - number of points to plot
           savefilename - save to or restore from this savefile (pickle)
           +bovy_plot(*args,**kwargs)
        OUTPUT:
           plot to output device
        HISTORY:
           2010-07-10 - Written - Bovy (NYU)
        """
        plotRotcurve(self.toPlanar(),*args,**kwargs)

    def plotEscapecurve(self,*args,**kwargs):
        """
        NAME:
           plotEscapecurve
        PURPOSE:
           plot the escape velocity  curve for this potential 
           (in the z=0 plane for non-spherical potentials)
        INPUT:
           Rrange - range
           grid - number of points to plot
           savefilename - save to or restore from this savefile (pickle)
           +bovy_plot(*args,**kwargs)
        OUTPUT:
           plot to output device
        HISTORY:
           2010-08-08 - Written - Bovy (NYU)
        """
        plotEscapecurve(self.toPlanar(),*args,**kwargs)

class PotentialError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def evaluatePotentials(*args):
    """
    NAME:
       evaluatePotentials
    PURPOSE:
       convenience function to evaluate a possible sum of potentials
    INPUT:
       R - cylindrical Galactocentric distance
       z - distance above the plane
       phi - azimuth
       Pot - potential or list of potentials
    OUTPUT:
       Phi(R,z)
    HISTORY:
       2010-04-16 - Written - Bovy (NYU)
    """
    hasphi= (len(args) == 4)
    if hasphi:
        R,z,phi,Pot= args
        args= (R,z,phi)
    else:
        R,z,Pot= args
        args= (R,z)
    if isinstance(Pot,list):
        sum= 0.
        for pot in Pot:
            sum+= pot(*args)
        return sum
    elif isinstance(Pot,Potential):
        return Pot(*args)
    else:
        raise PotentialError("Input to 'evaluatePotentials' is neither a Potential-instance or a list of such instances")

def evaluateDensities(*args):
    """
    NAME:
       evaluateDensities
    PURPOSE:
       convenience function to evaluate a possible sum of densities
    INPUT:
       R - cylindrical Galactocentric distance
       z - distance above the plane
       phi - azimuth
       Pot - potential or list of potentials
    OUTPUT:
       rho(R,z)
    HISTORY:
       2010-08-08 - Written - Bovy (NYU)
    """
    hasphi= (len(args) == 4)
    if hasphi:
        R,z,phi,Pot= args
        args= (R,z,phi)
    else:
        R,z,Pot= args
        args= (R,z)
    if isinstance(Pot,list):
        sum= 0.
        for pot in Pot:
            sum+= pot.dens(*args)
        return sum
    elif isinstance(Pot,Potential):
        return Pot.dens(*args)
    else:
        raise PotentialError("Input to 'evaluateDensities' is neither a Potential-instance or a list of such instances")

def evaluateRforces(*args):
    """
    NAME:
       evaluateRforce
    PURPOSE:
       convenience function to evaluate a possible sum of potentials
    INPUT:
       R - cylindrical Galactocentric distance
       z - distance above the plane
       phi - azimuth (optional)
       Pot - a potential or list of potentials
    OUTPUT:
       K_R(R,z,phi)
    HISTORY:
       2010-04-16 - Written - Bovy (NYU)
    """
    hasphi= (len(args) == 4)
    if hasphi:
        R,z,phi,Pot= args
        args= (R,z,phi)
    else:
        R,z,Pot= args
        args= (R,z)
    if isinstance(Pot,list):
        sum= 0.
        for pot in Pot:
            sum+= pot.Rforce(*args)
        return sum
    elif isinstance(Pot,Potential):
        return Pot.Rforce(*args)
    else:
        raise PotentialError("Input to 'evaluateRforces' is neither a Potential-instance or a list of such instances")

def evaluatephiforces(*args):
    """
    NAME:
       evaluateRforce
    PURPOSE:
       convenience function to evaluate a possible sum of potentials
    INPUT:
       R - cylindrical Galactocentric distance
       z - distance above the plane
       phi - azimuth (optional)
       Pot - a potential or list of potentials
    OUTPUT:
       K_R(R,z,phi)
    HISTORY:
       2010-04-16 - Written - Bovy (NYU)
    """
    hasphi= (len(args) == 4)
    if hasphi:
        R,z,phi,Pot= args
        args= (R,z,phi)
    else:
        R,z,Pot= args
        args= (R,z)
    if isinstance(Pot,list):
        sum= 0.
        for pot in Pot:
            sum+= pot.phiforce(*args)
        return sum
    elif isinstance(Pot,Potential):
        return Pot.phiforce(*args)
    else:
        raise PotentialError("Input to 'evaluatephiforces' is neither a Potential-instance or a list of such instances")

def evaluatezforces(*args):
    """
    NAME:
       evaluatezforces
    PURPOSE:
       convenience function to evaluate a possible sum of potentials
    INPUT:
       R - cylindrical Galactocentric distance
       z - distance above the plane
       phi - azimuth (optional)
       Pot - a potential or list of potentials
    OUTPUT:
       K_z(R,z)
    HISTORY:
       2010-04-16 - Written - Bovy (NYU)
    """
    hasphi= (len(args) == 4)
    if hasphi:
        R,z,phi,Pot= args
        args= (R,z,phi)
    else:
        R,z,Pot= args
        args= (R,z)
    if isinstance(Pot,list):
        sum= 0.
        for pot in Pot:
            sum+= pot.zforce(*args)
        return sum
    elif isinstance(Pot,Potential):
        return Pot.zforce(*args)
    else:
        raise PotentialError("Input to 'evaluatezforces' is neither a Potential-instance or a list of such instances")

def plotPotentials(Pot,rmin=0.,rmax=1.5,nrs=21,zmin=-0.5,zmax=0.5,nzs=21,
                   ncontours=21,savefilename=None):
        """
        NAME:
           plotPotentials
        PURPOSE:
           plot a set of potentials
        INPUT:
           Pot - Potential or list of Potential instances
           rmin - minimum R
           rmax - maximum R
           nrs - grid in R
           zmin - minimum z
           zmax - maximum z
           nzs - grid in z
           ncontours - number of contours
           savefilename - save to or restore from this savefile (pickle)
        OUTPUT:
           plot to output device
        HISTORY:
           2010-07-09 - Written - Bovy (NYU)
        """
        if not savefilename == None and os.path.exists(savefilename):
            print "Restoring savefile "+savefilename+" ..."
            savefile= open(savefilename,'rb')
            potRz= pickle.load(savefile)
            Rs= pickle.load(savefile)
            zs= pickle.load(savefile)
            savefile.close()
        else:
            Rs= nu.linspace(rmin,rmax,nrs)
            zs= nu.linspace(zmin,zmax,nzs)
            potRz= nu.zeros((nrs,nzs))
            for ii in range(nrs):
                for jj in range(nzs):
                    potRz[ii,jj]= evaluatePotentials(Rs[ii],zs[jj],Pot)
            if not savefilename == None:
                print "Writing savefile "+savefilename+" ..."
                savefile= open(savefilename,'wb')
                pickle.dump(potRz,savefile)
                pickle.dump(Rs,savefile)
                pickle.dump(zs,savefile)
                savefile.close()
        return plot.bovy_dens2d(potRz.T,origin='lower',cmap='gist_gray',contours=True,
                                xlabel=r"$R/R_0$",ylabel=r"$z/R_0$",
                                xrange=[rmin,rmax],
                                yrange=[zmin,zmax],
                                aspect=.75*(rmax-rmin)/(zmax-zmin),
                                cntrls='-',
                                levels=nu.linspace(nu.nanmin(potRz),nu.nanmax(potRz),
                                                   ncontours))
