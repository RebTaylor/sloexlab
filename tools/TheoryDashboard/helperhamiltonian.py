#Functions written by P. Arrutia

import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np
import os

def get_p3rtilde(twiss_df, nu):
    """
    Sextupole Component
    This function computes p3rtilde from the Wiedemann convention of sextupole str.

    Arguments:
      - twiss_df: twiss pandas dataframe
    Returns:
      - (totVStr, totVPhase): normalized strength and phase location of the virtual sextupole.
                              N.B. All the active sextupoles are used for the computations, also the
                              chromatic ones.
    """
    dfRStr = twiss_df.copy()
    lsTotDf = dfRStr[ dfRStr["k2l"] != 0 ].copy()
    
    strongest_sexts = lsTotDf.k2l.abs().sort_values(ascending=False).head(10).index
    #print(twiss_df.loc[strongest_sexts][['k2l', 'betx', 's', 'mux', 'l']])
    
    factor = np.sqrt(2)/(24*np.pi*np.sqrt(nu))
    normTotSeStr = factor*np.array(np.array(lsTotDf["k2l"])*np.array(lsTotDf["betx"].pow(3/2)) )
    totSePhases = 2*np.pi*np.array(lsTotDf["mux"])

    totSeSinSum = np.sum( normTotSeStr*np.sin(3*totSePhases) )
    totSeCosSum = np.sum( normTotSeStr*np.cos(3*totSePhases) )

    totVStr = np.sqrt( np.power(totSeSinSum,2) + np.power(totSeCosSum,2) )
    totVPhase = np.arctan2((totSeSinSum ),( totSeCosSum ))/3

    return totVStr, totVPhase    

def get_p40tilde(twiss_df, nu):
    """
    This function computes the p40tilde from the wiedemann convention for octupole str.

    Arguments:
      - twiss_df: twiss pandas dataframe
      - nu : tune
    Returns:
      - totVStr: normalized strength of the virtual octupole.
    """
    
    dfRStr = twiss_df.copy()
    lsTotDf = dfRStr[ dfRStr["k3l"] != 0 ].copy()

    strongest_octs = lsTotDf.k3l.abs().sort_values(ascending=False).head(10).index
    #print(twiss_df.loc[strongest_octs][['k3l', 'betx', 's', 'mux', 'l']])
    
    factor = 1/(32*nu*np.pi)
    normTotOcStr = factor*np.array(np.array(lsTotDf["k3l"])*np.array(lsTotDf["betx"].pow(2)) )
    totVStr = np.sum(normTotOcStr)

    return totVStr

def j_to_w(j, phi, nu):
    w = np.sqrt(2*j/nu)*np.cos(phi)
    wdot = np.sqrt(2*nu*j)*np.sin(phi)
    return w, wdot

def phi1_to_phi(j, phi1, hh, nu, dnu, mux):
    return phi1 + (nu-dnu)/nu * mux, hh+(nu-dnu)*j

def w_to_x(w, wdot, nu, alpha, beta, output):
    np.seterr(divide='raise')  # To Catch warnings instead of raises
    
    x = np.sqrt(beta)*w
    try:
        xp = wdot/(nu*np.sqrt(beta)) - alpha*w/np.sqrt(beta)
        return x, xp
    except FloatingPointError:
        with output:
            print('Error: Division by zero')
        xp = np.empty(np.shape(x))
        xp[:] = np.nan
        return x, xp

def hamiltonian(w, wdot, nu, dnu, p40tilde, p3rtilde):
    term1 = dnu*nu/2 * (w**2 + wdot**2/nu**2)
    term2 = p40tilde*(nu/2 * (w**2 + wdot**2/nu**2))**2
    term3 = p3rtilde*nu**(3/2)/2**(3/2) * (w**3 - 3*w*wdot**2/nu**2)
    return term1 + term2 + term3

def hamiltonian_radial(r, phi, delta, omega, n, phi0=0):
    return delta*r + omega*r**2 + r**(n/2)*np.cos(n*phi + phi0)

def get_delta_omega(dnu, p40tilde, pnrtilde, j0, n):
    delta = dnu/(pnrtilde*j0**(n/2-1))
    omega = p40tilde/(pnrtilde*j0**(n/2-2))
    return delta, omega


def readtfs(filename, usecols=None, index_col=0, check_lossbug=True):
    '''Reads twiss file into pandas df.'''
    header = {}
    nskip = 0
    closeit = False
    try:
        datafile = open(filename, 'r')
        closeit = True
    except TypeError:
        datafile = filename

    for line in datafile:
        nskip += 1
        if line.startswith('@'):
            entry = line.strip().split()
            header[entry[1]] = eval(' '.join(entry[3:]))
        elif line.startswith('*'):
            colnames = line.strip().split()[1:]
            break

    if closeit:
        datafile.close()

    table = pd.read_csv(filename, delim_whitespace = True,
                        skipinitialspace = True,
                        names = colnames, usecols = usecols,
                        index_col = index_col)

    if check_lossbug:
        try:
            table['ELEMENT'] = table['ELEMENT'].apply(lambda x: str(x).split()[0])
        except KeyError:
            pass
        try:
            for location in table['ELEMENT'].unique():
                if not location.replace(".","").replace("_","").replace('$','').isalnum():
                    print("WARNING: some loss locations in "+filename+
                          " don't reduce to alphanumeric values. For example "+location)
                    break
                if location=="nan":
                    print("WARNING: some loss locations in "+filename+" are 'nan'.")
                    break
        except KeyError:
            pass
        
    table = table.drop(index='$')
    cols = table.columns[1:]
    table = table.drop('N1', 1)
    table.columns = cols
    for col in table.columns[1:]:
        table[col] = pd.to_numeric(table[col],errors = 'coerce')
    table.columns= table.columns.str.strip().str.lower()
    return header, table

def HamiltonianContour(tdf, nu, nu_res, ele, Rmin, Rmax, ncount, output, title=''):   
    import matplotlib.cm as cm
    cmap = cm.get_cmap("coolwarm")
    # Compute contours
    dnu = nu - nu_res
    npoints = ncount
    j0 = 0.0002

    try:
        beta = tdf.loc[ele]['betx']
        alpha = tdf.loc[ele]['alfx']
        mux_seh = 2*np.pi*tdf.loc[ele]['mux']
        output.clear_output()
    except KeyError:
        with output:
            output.clear_output()
            CRED = '\033[91m'
            CEND = '\033[0m'
            print(CRED + f'ERROR : Element {ele} not found in lattice.' + CEND)
        return([0, 0], [0, 0], [[0, 0], [0, 0]]) #Empty contour plot
    
    p3rtilde, mux_sext = get_p3rtilde(tdf, nu)
    p40tilde = get_p40tilde(tdf, nu)

    mux = -(mux_seh - mux_sext)

    #r = np.linspace(0, 4, npoints)
    r = 10**np.linspace(Rmin, Rmax, int(npoints))
    phi = np.linspace(-np.pi, np.pi, int(npoints))
    rr, phiphi = np.meshgrid(r, phi)

    factor = 1.2
    delta, omega = get_delta_omega(dnu, factor*p40tilde, p3rtilde, j0, n=3)
    hh = hamiltonian_radial(rr, phiphi, delta, omega, 3)

    jj = rr*j0
    phiphi, hh = phi1_to_phi(jj, phiphi, hh, nu, dnu, mux)
    ww, wdotwdot = j_to_w(jj, phiphi, nu)

    xx, xpxp = w_to_x(ww, wdotwdot, nu, alpha, beta, output)

    # Get contours in increasing order (the stable region is a valley)
    flat_h = hh.flatten()
    sorted_h = np.unique(np.sort(flat_h))
    size = sorted_h.shape[0]
    step = int(size/50)
    
    return(xx, xpxp, hh)

