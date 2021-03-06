import numpy as np
import ipywidgets as widgets
import matplotlib.pyplot as plt

from tools.helpers import *

from ipywidgets import interactive, interact

def Steinbach(S, QX, Q_r, dpp, dQX, ex, Np):
    '''
    Inputs
    -------
        S   : Sextupole strength
        QX  : Particle horizontal tune
        Q_r : Resonance horizontal tune
        dQX : Beam chromaticity
        dpp : Beam momentum spread
        ex  : Beam momentum [m]
        Np  : Number of particles
        
    Calculates slope of resonance region with S.
    Generates gaussian distribution of Np particles using EX, with uniform momentum spread DPP.
    Calculates amplitude and tune of each particle with respect to resonance.
    
    Returns
    -------
        QX + DPP*dQX  : particle tune range
        An            : particle amplitude
        Q_res+Q_range : range slope is plotted over
        A_stopb       : amplitude of stop-band region
    '''
    Q_range = np.linspace(-0.5, +0.5, 5000)                        # Tune range to plot line
    A_stopb = (48 * np.pi * 3**0.5)**0.5 * np.abs(Q_range / S )  # Amplitude due to virtual sextupole
    
    # Ensures particle distribution does not regenerate each time a parameter changes
    np.random.seed(1)
    
    DPP = np.random.uniform(-dpp, dpp, Np)                       # Beam momentum spread
    EX = np.random.normal(0, ex, Np)                             # Beam Emittance
    An = (abs(EX)/np.pi)**0.5                                    # Converts emittance to amplitude

    return([QX + DPP*dQX, An, Q_r+Q_range, A_stopb ])

def Steinbach_Output(st_in, st_out, spiral_in, hardt_in):
    '''
    Inputs
    -------
        st_in     : List of Steinbach inputs       - S, QX, QX_r, DPP, DQX, ex, Np
        spiral_in : List of Spiral Step inputs     - S, ES, phi, spir, kick
        hardt_in  : List of Hardt condition inputs - hardt_chroma, S, QX, DX, DXp, alf, mues, muxr
        
    Inputs from TheoryDashboard()
    Plots Steinbach diagram using Steinbach()
    Includes calculation functions which observe when parameters are being updated
    Defines variables which affect the plotting of the steinbach
 
    Returns
    -------
        SteinbachOut : widget output showing plot
    '''
    # Unpacking widgets from listed inputs
    S, QX, QX_r, DPP, DQX, ex, Np = st_in
    S, ES, phi, spir, kick = spiral_in
    hardt_chroma, S, QX, DX, DXp, alf, mues, muxr = hardt_in
    
    # Defining output widget
    with st_out:
        figS, axS = plt.subplots(figsize=(10,5))
        figS.canvas.header_visible = False
        plt.show()
        
    # callback functions
    def updateSteinbach(change):
        '''
        Inputs
        -------
            st_in : list of widget changes
            
        If st_in values change, redraws Steinbach line & updates plot
        '''
        particle_Q, particle_E, SLine, ALine = Steinbach(S.value, QX.value, QX_r.value, DPP.value, DQX.value, ex.value, Np.value) 
        with st_out:
            particles.set_xdata(particle_Q), particles.set_ydata(particle_E)
            sline.set_xdata(SLine), sline.set_ydata(ALine)
            axS.set_xlim(xmin.value, xmax.value)
            axS.set_ylim(ymin.value, ymax.value)
            axS.set_title(f"{steinbach_title.value}")
            figS.canvas.draw_idle()
    
    # Plots initial default steinbach
    particle_Q, particle_E, SLine, ALine = Steinbach(S.value,QX.value,QX_r.value,DPP.value,DQX.value,ex.value,Np.value)
    with st_out:
        particles, = axS.plot(particle_Q, particle_E, 'o')
        sline, = axS.plot(SLine, ALine)

        axS.set_ylabel('$A_n$ [$\sqrt{m}$]')
        axS.set_xlabel(r'$Q_x$')
        axS.set_title("Tune and amplitude of beam distribution compared to resonance")
        axS.set_xlim(QX_r.value-0.003, QX_r.value+0.01)
        axS.set_ylim(0, 0.005)
    
     
    def updateSpiralStep(change):
        '''
        Inputs
        -------
            spiral_in : list of widget changes
            
        If spiral_in values change, updates value of Spiral Step and Spiral Kick
        '''
        dR = 3/4 * S.value / np.cos(rad(phi.value)) * ES.value**2
        dRp = 3/4 * S.value * np.tan(rad(phi.value)) / np.cos(rad(phi.value)) * ES.value**2
        spir.value = round(dR, 3)
        kick.value = round(dRp, 4) 
        
    def HardtCondition(*args):
        '''
        Inputs
        -------
            hardt_in : list of widget changes
            
        If hardt_in values change AND Calculate Hardt Condition is ticked, updates chromaticity
        '''
        if hardt_chroma.value == True:
            dmu = 360 - ((mues.value - muxr.value) / QX.value * 360)
            dqx_hardt = (-S.value / (4 * np.pi)) * (DX.value * np.cos(rad(alf.value) - rad(dmu)) + DXp.value * np.sin(rad(alf.value) - rad(dmu)))
            DQX.value = dqx_hardt
            DQX.disabled = True
        if hardt_chroma.value == False:
            DQX.disabled = False
      
    # List of widgets to observe with functions
    [params.observe(updateSteinbach, 'value') for params in st_in]           #Observing changes in Steinbach baseline parameters
    [spiral.observe(updateSpiralStep, 'value') for spiral in spiral_in]    #Observing changes in spiral step baseline parameters
    [hardt.observe(HardtCondition, 'value') for hardt in hardt_in]              #Observing changes in Hardt baseline parameters
    
       
    # matplotlib plotting settings
    steinbach_title = widgets.Text(value='Tune and amplitude of beam distribution compared to resonance', description='Title', layout=widgets.Layout(width='auto'))
    xmin = widgets.FloatText(value=1.66, description=r'X$_{min}$', step=0.01, layout=widgets.Layout(width='190px'))
    xmax = widgets.FloatText(value=1.68, description=r'X$_{max}$', step=0.01, layout=widgets.Layout(width='200px'))
    ymin = widgets.FloatText(value=0, description=r'Y$_{min}$', step=0.001, layout=widgets.Layout(width='190px'))
    ymax = widgets.FloatText(value=0.005, description=r'Y$_{max}$', step=0.001, layout=widgets.Layout(width='200px'))
    
    axes = [steinbach_title, xmin, xmax, ymin, ymax]
    
    Axes = widgets.VBox([steinbach_title, widgets.HBox([xmin, xmax]), widgets.HBox([ymin, ymax])])
    [axis.observe(updateSteinbach, 'value') for axis in axes]
    
    return Axes