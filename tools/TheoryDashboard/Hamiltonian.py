import numpy as np
import ipywidgets as widgets
import matplotlib.pyplot as plt

from tools.TheoryDashboard.helperhamiltonian import *

import io
import warnings
        
def Hamiltonian_Output(tdf, QX, QX_r, ES, ele_pos, Hamilton_err):
    '''
    Inputs
    -------
        tdf             : Twiss dataframe uploader widget
        QX              : Horizontal tune widget
        QX_r            : Resonant tune widget
        ES              : Electrostatic septa widget
        ele_pos         : Element where hamilton is measured
        Hamiltonian_err : Error output widget
        
    Uses functions in tools.Ham_tools to calculate the Hamiltonian from a Twiss Dataframe file.
    Plots as a matplotlib contour plot.
    
    Returns
    -------
        Hamilton_out  : widget output showing contour plot of Hamiltonian
    '''
    # Defining output, containing figure and axis
    Hamilton_out = widgets.Output()
    with Hamilton_out:
        figH, axH = plt.subplots(figsize=(9,8))
        figH.canvas.header_visible = False
        plt.show()
        
    def HamiltonPlot(change):
        '''
        Inputs
        -------
            tdf             : Twiss dataframe uploader widget
            QX              : Horizontal tune widget
            QX_r            : Resonant tune widget
            ES              : Electrostatic septa widget
            ele_pos         : Element where hamilton is measured
            
        If input values change, redraws Hamiltonian & updates plot
        
        Output
        ------
           HamiltonOut     : dashboard including widget output and axes inputs
        '''
        import matplotlib.cm as cm
        
        if tdf.data != []:                                       #If non-empty Twiss dataframe uploader
            tdf_bytes = io.BytesIO( tdf.data[0] )                # Converts uploaded file into binary
            TDF = io.TextIOWrapper(tdf_bytes, encoding='utf-8')  # Unwraps binary values
            header, twiss_df = readtfs(TDF)                      # Extracts header information and dataframe.

            axH.clear()                                          #Removes previous plot to avoid overlapping contours
            xx, xpxp, hh = HamiltonianContour(twiss_df, QX.value, QX_r.value, ele_pos.value, rmin.value, rmax.value, ncount.value, Hamilton_err)

            with warnings.catch_warnings():                      # Ignores errors of empty contour lines
                warnings.simplefilter("ignore")
                axH.contour(xx, xpxp, hh, 500, colors=[cm.get_cmap("coolwarm")(0)], linestyles='solid')

            axH.axvline(ES.value, color='black')                 # Draws on position of aperture limit
            axH.set_xlabel('x [m]')
            axH.set_ylabel('px')
            axH.set_xlim(xmin.value, xmax.value)
            axH.set_ylim(ymin.value, ymax.value)
            axH.set_title(f'{title.value} - Qx={QX.value}')

            figH.canvas.draw()
            
    # If either of these change, update Hamiltonian Plot
    tdf.observe(HamiltonPlot, 'data')
    QX.observe(HamiltonPlot, 'value')
    QX_r.observe(HamiltonPlot, 'value')
    ES.observe(HamiltonPlot, 'value')
    ele_pos.observe(HamiltonPlot, 'value')
    
    
    # matplotlib plotting settings
    title = widgets.Text(value='Hamiltonian', description='Title', layout=widgets.Layout(width='auto'))
    xmin = widgets.FloatText(value=-0.06,  description=r'X$_{min}$', step=0.01, layout=widgets.Layout(width='200px'))
    xmax = widgets.FloatText(value= 0.06,  description=r'X$_{max}$', step=0.01, layout=widgets.Layout(width='200px'))
    ymin = widgets.FloatText(value=-0.004, description=r'Y$_{min}$', step=0.001, layout=widgets.Layout(width='200px'))
    ymax = widgets.FloatText(value= 0.004, description=r'Y$_{max}$', step=0.001, layout=widgets.Layout(width='200px'))
    
    rmin = widgets.FloatText(value= -10, description=r'R$_{min}$ 10^', step=1, layout=widgets.Layout(width='200px'))
    rmax = widgets.FloatText(value= 0.5, description=r'R$_{max}$ 10^', step=1, layout=widgets.Layout(width='200px'))
    ncount = widgets.BoundedIntText(value=500, description=r'N$_{counts}$', step=100, min=1, max=10000, layout=widgets.Layout(width='auto'))
    
    spacer1 = widgets.HTML("  ", layout=widgets.Layout(height='100px'))
    spacer2 = widgets.HTML("  ", layout=widgets.Layout(height='20px'))
    
    axes = [title, xmin, xmax, ymin, ymax]
    contour_vals = [rmin, rmax, ncount]
    
    Axes = widgets.VBox([spacer1, title, widgets.HBox([xmin, xmax]), widgets.HBox([ymin, ymax]), spacer2, widgets.HBox([rmin, rmax]), ncount])
    [axis.observe(HamiltonPlot, 'value') for axis in axes]
    [cont.observe(HamiltonPlot, 'value') for cont in contour_vals]
    
    HamiltonOut = widgets.HBox([Hamilton_out, Axes])
    return HamiltonOut