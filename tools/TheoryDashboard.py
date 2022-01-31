import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tools.helpers import *

from tools.Steinbach import *
from tools.Hamiltonian import *

def TheoryDashboard():
    '''
    Dashboard requesting inputs which affect calculations of Steinbach & Kobayashi-Hamiltonian diagrams
    Two outputs : from tools.Steinbach and tools.Hamiltonian
    '''

    style = {'description_width': 'initial'}
    
    '====================== Steinbach Inputs ============================'
    h1 = widgets.HTML("<h2>Baseline Parameters</h2>")
    S = widgets.FloatText(value=36.7168, description='S [m-1]', step=0.25)  # Virtual Sextupole Strength
    QX = widgets.FloatText(value=1.67, description='QX', step=0.001)        # Beam horizontal tune
    QX_r = widgets.FloatText(value=5/3, description='QX res', step=0.001)   # Resonance horizontal tune
    Np = widgets.IntText(value=100, description='Np', step=100)             # Number of particles
    ex = widgets.FloatText(value=1E-6, description='ex rms', step=1E-6)     # RMS Normalised emittance
    DQX = widgets.FloatText(value=-4, description='DQX', step=0.1)          # Chromaticity
    DPP = widgets.FloatText(value=1E-4, description='dpp', step=1E-4)       # Particle momentum spread

    Steinbach_inputs = [S, QX, QX_r, DPP, DQX, ex, Np]
    col_param = widgets.VBox([h1, widgets.VBox(Steinbach_inputs)])                          #Putting widgets into dashboard

    '====================== Spiral Step Inputs ============================'
    h2 = widgets.HTML("<h2>Spiral Step Parameters</h2>", layout=widgets.Layout(height='auto'))
    ES = widgets.FloatText(value=0.055, description='ES', step = 0.01)      # Electrostatic Septum position
    phi = widgets.FloatText(value=45, description='phi')                    # Orientation of separatrices
    spir = widgets.FloatText(description='Spiral Step', disabled=True)      # Maximum Spiral Step
    kick =  widgets.FloatText(description='Spiral Kick', disabled=True)     # Maximum Spiral Kick
    
    Spiral_Step = [S, ES, phi, spir, kick]                                  #Listing widgets which affect the spiral step
    col_spiral = widgets.VBox([h2, ES, phi, spir, kick])                    #Putting spiral step widgets into dashboard

    '====================== Hardt Condition Inputs ============================'
    h3 = widgets.HTML("<h2>Hardt Condition Parameters</h2>", layout=widgets.Layout(height='auto'))
    hardt_chroma = widgets.Checkbox(description='Calculate Hardt Condition Chromaticity', value=False, indent=True, style=style)
    DX = widgets.FloatText(value=3.54, description='Dx', step=0.1)          # Dispersion at ES
    DXp = widgets.FloatText(value=-0.6, description='Dxp', step=0.1)        # Dispersion ' at ES
    alf = widgets.FloatText(value=90, description='alpha (deg)', step=1)    # Orientation
    mues = widgets.FloatText(value=36.7, description='ES muX', step=1)      # Phase-Advance at ES
    muxr = widgets.FloatText(value=186.1, description='XR muX', step=1)     # Phase-Advance at virtual resonant sextupole
    
    Hardt = [hardt_chroma, S, QX, DX, DXp, alf, mues, muxr]                 #Listing all widgets which affect the Hardt condition
    col_hardt = widgets.VBox([h3, DX, DXp, alf, mues, muxr, hardt_chroma])          #Putting Hardt Condition widgets into the dashboard
    
    '====================== Hamiltonian Inputs ============================'
    h4 = widgets.HTML("<h2>Hamiltonian Parameters</h2>", layout=widgets.Layout(height='auto'))
    tdf = widgets.FileUpload(accept='.tfs', description='Twiss DataFrame', multiple=False, style=style, layout=widgets.Layout(width='auto'))
    ele_pos = widgets.Text(value='ES', description='Element',  disabled=False, layout=widgets.Layout(width='auto'))
    h_tdf = widgets.HTML("  Produce .tfs file from 'Tracking Code' tab")
    Hamilton_err = widgets.Output()
 
    col_ham = widgets.VBox([h4, ele_pos, tdf, h_tdf, Hamilton_err], layout=widgets.Layout(width='250px', align='center'))
    
    '====================== Ouputs of Processes ============================'
    SteinbachOut = Steinbach_Output(Steinbach_inputs, Spiral_Step, Hardt)
    HamiltonOut = Hamiltonian_Output(tdf, QX, QX_r, ES, ele_pos, Hamilton_err)
        
    outtab = widgets.Tab()                           #Makes a tab of Steinbach & Hamiltonian Outputs
    outtab.children = SteinbachOut, HamiltonOut
    outtab.set_title(0, "Steinbach"), outtab.set_title(1, "Hamiltonian")

    '====================== Display Dashboard ============================'
    Dashboard = widgets.VBox([widgets.HBox([col_param, col_spiral, col_hardt, col_ham]), outtab]) 
    return(Dashboard)
