#PyNAFF is imported from my local site
import os
import numpy as np
import ipywidgets as widgets
try:
    import PyNAFF
except:
    os.chdir("/eos/user/r/retaylor/.local/lib/python3.8/site-packages")
    import PyNAFF
    os.chdir('/eos/home-r/retaylor/SWAN_projects/sloexlab/sloexlab')

import base64
from tqdm.notebook import tqdm

from tools.VisualiserDashboard.TunePlot import TunePlotDash

def tune_scroll(Tracks, n_particles, t_step, Q_step, param='X'):
    ''' 
    x_pos is a np array of number of turns T
    t_step is the number of turns per step
    '''
    X_pos = Tracks[0]
    coord = {'X': 0, 'Xp':1, 'Y':2, 'Yp':3}
    N_turns = np.shape(X_pos)[2]
    Q = np.zeros((2, n_particles, int(N_turns/t_step)))
    for p in tqdm(range(n_particles)):
        x_pos = X_pos[coord[param], p, :]
        for t in range(int(N_turns/t_step)):
            Turn_no = t * t_step
            if Turn_no - Q_step > 0:
                x_step = x_pos[Turn_no - Q_step : Turn_no]
                Q[0,p,t] = PyNAFF.naff(x_step - np.mean(x_step), Q_step, 1, 0, False)[0][1]

            Q[1,p,t] = Turn_no
    return Q


def TuneDashboard(Tracks):
    '''
    '''
    
    '----- Inputs -----'
    WindowCalc = widgets.BoundedIntText(value=128, min=2**0, max=2**15, step=64, description='Window Calc')
    WindowStep = widgets.BoundedIntText(value=10,  min=1, max=2**15, step=1, description='Window Step')
    Coordinate = widgets.ToggleButtons(options=['X', 'Y'], value='X',  description = 'Coordinate', layout=widgets.Layout(width='auto'))
    nparticles = widgets.BoundedIntText(value=100  , min=0, max=1E10, step=100, description='Particle no.')

    Calculate = widgets.Button(description='Calculate')
    Download = widgets.Output() # Button(description='Download')
    PlotOutput = widgets.Output()
    Upload = widgets.FileUpload(description='Upload')
    Plot = widgets.Button(description='Plot')
    
    TuneOut = widgets.Output()
    
    TuneInputs = widgets.HBox([ widgets.VBox([WindowCalc, WindowStep, nparticles, Coordinate]), widgets.VBox([widgets.HBox([Calculate, Download]), Upload, PlotOutput])       ])
    
    TunePlotOut = widgets.Output()
    Tunes = []
    
    def TuneCalc(change):
        TuneOut.clear_output()
        with TuneOut:
            qx = tune_scroll(Tracks, nparticles.value, WindowStep.value, WindowCalc.value, Coordinate.value)
            Tunes.append(qx)
            filename = f'Tune_{Coordinate.value}_{WindowCalc.value}_T_{np.max(qx[1,:,:])}_P_{nparticles.value}.npy'
            
            QX = np.save(filename, qx)
            
            with open(filename, mode='rb') as file: # b is important -> binary
                QX_file = file.read()
           
                b64 = base64.b64encode(QX_file)
                payload = b64.decode()
                
                html_buttons = '''<html>
                            <head>
                            <meta name="viewport" content="width=device-width, initial-scale=1">
                            </head>
                            <body>
                            <a download="{filename}" href="data:text/csv;base64,{payload}" download>
                            <button class="p-Widget jupyter-widgets jupyter-button widget-button mod-warning">Download File</button>
                            </a>
                            </body>
                            </html>
                            '''
                html_button = html_buttons.format(payload=payload,filename=filename)
            with Download:
                Download.clear_output()
                display(widgets.HTML(html_button))
            with PlotOutput:
                PlotOutput.clear_output()
                display(Plot)
                
            Plot.on_click(TunePlotting)

    Calculate.on_click(TuneCalc)
    
    def TunePlotting(change):
        TunePlotOut.clear_output()
        with TunePlotOut:
            display(TunePlotDash(Tunes, Tracks))
    
    TuneDash = widgets.VBox([TuneInputs, TuneOut, TunePlotOut])
    return TuneDash