import matplotlib.pyplot as plt
import matplotlib
from matplotlib.colors import Normalize as Norm
import matplotlib.cm as cm
import numpy as np
from tqdm.notebook import tqdm
import ipywidgets as widgets


def PhaseSpaceInputs(trackdata):
    ''''''
    XPlot = widgets.Dropdown(options=['X', 'Xp', 'Y', 'Yp', 't', 'Pt'], value='X',  description = 'X-axis coord')
    YPlot = widgets.Dropdown(options=['X', 'Xp', 'Y', 'Yp', 't', 'Pt'], value='Xp', description = 'Y-axis coord')
    coord = {'X':0, 'Xp':1, 'Y':2, 'Yp':3, 't':4, 'Pt':5}

    TurnType = widgets.RadioButtons(options=['Single Turn', 'Cumulative Turns'], description='Plot Type')
    TurnDisplay = widgets.Output()
    TurnNo  = widgets.BoundedIntText(value=100, min=0, max=1E10, step=100, description='Turn Number')
    TurnMin = widgets.BoundedIntText(value=0  , min=0, max=1E10, step=100, description='Turn Min')
    TurnMax = widgets.BoundedIntText(value=100, min=0, max=1E10, step=100, description='Turn Max')
    TurnStep = widgets.BoundedIntText(value=10, min=1, max=1E10, step=10, description='Turn Step')

    Color = widgets.ColorPicker(description='Colour', value='blue')
    Gradient = widgets.Checkbox(value=False, description='Gradient Plot')
    Color1 = widgets.ColorPicker(description='Colour 1', value='lightgray')
    Color2 = widgets.ColorPicker(description='Colour 2', value='purple')

    Inputs = widgets.VBox([TurnType, XPlot, YPlot])
    with TurnDisplay:
        display(widgets.HBox([TurnNo, Color]))
    
    PlotButton = widgets.Button(description='Plot', icon='chart-scatter')
    AnimateButton = widgets.Button(description='Animate', icon='photo-video')
    
    err_out = widgets.Output()
    tqdm_out = widgets.Output()
    
    AnimateDisplay = widgets.Output()
    Animate = widgets.HBox([AnimateButton, AnimateDisplay])
    def animatebutton(change):
        AnimateDisplay.clear_output()
        Valid = widgets.Valid(value=False, description='')
        with AnimateDisplay:
            display(Valid)

    AnimateButton.on_click(animatebutton)            
    
    Buttons = widgets.VBox([PlotButton, Animate])
    
    def InputType(check):
        TurnDisplay.clear_output()
        global TurnInputs
        global ColorInputs
        if TurnType.value == 'Single Turn':
            with TurnDisplay:
                display(widgets.HBox([TurnNo, Color]))
        if TurnType.value == 'Cumulative Turns':
            XPlot.options = ['X', 'Xp', 'Y', 'Yp', 't', 'Pt', 'Turns']
            YPlot.options = ['X', 'Xp', 'Y', 'Yp', 't', 'Pt', 'Turns']
            XPlot.value = 'X'
            YPlot.value = 'Xp'
            with TurnDisplay:
                display(widgets.HBox([widgets.VBox([TurnMin, TurnMax, TurnStep]), widgets.VBox([Color, Gradient])]))
        if Gradient.value == True:
            TurnDisplay.clear_output()
            with TurnDisplay:
                display(widgets.HBox([widgets.VBox([TurnMin, TurnMax, TurnStep]), widgets.VBox([Gradient, Color1, Color2])]))
                
    TurnType.observe(InputType, 'value')
    Gradient.observe(InputType, 'value')
    
    phase_output = widgets.Output()
    with phase_output:
        figP, axP = plt.subplots(figsize=(8,7))
        figP.canvas.header_visible = False
        axP.set_xlabel(f'{XPlot.value} [m]')
        axP.set_ylabel(f'{YPlot.value}')
        
        def plotphase(change):
            data = trackdata[0]
            axP.clear()
            
            if XPlot.value == 'X' or XPlot.value == 'Y': 
                axP.set_xlabel(f'{XPlot.value} [m]')
            else:
                axP.set_xlabel(f'{XPlot.value}')
            if YPlot.value == 'X' or YPlot.value == 'Y':
                axP.set_ylabel(f'{YPlot.value} [m]')
            else:
                axP.set_ylabel(f'{YPlot.value}')  
            
            if TurnType.value == 'Single Turn':
                try:
                    axP.plot(data[coord[XPlot.value], :, TurnNo.value],
                             data[coord[YPlot.value] ,:, TurnNo.value], '.', color=Color.value)
                    err_out.clear_output()
                    
                except IndexError:
                    with err_out:
                        err_out.clear_output()
                        CRED = '\033[91m'
                        CEND = '\033[0m'
                        print(CRED + f"Error: {TurnNo.value} is out of range" + CEND)
                        
            if TurnType.value == 'Cumulative Turns':
                T_arr = np.arange(TurnMin.value, TurnMax.value, TurnStep.value)
                
                if Gradient.value == False:
                    if XPlot.value != "Turns" and YPlot.value != "Turns":
                        axP.plot(data[coord[XPlot.value], :, T_arr],
                                 data[coord[YPlot.value] ,:, T_arr],
                                 '.', color=Color.value)
                    if XPlot.value == "Turns":
                        for T in T_arr:
                            axP.plot(T*np.ones(np.shape(data)[1]), data[coord[YPlot.value], :, T],
                                    '.', color=Color.value)
                    if YPlot.value == "Turns":
                        for T in T_arr:
                            axP.plot(data[coord[XPlot.value], :, T], T*np.ones(np.shape(data)[1]),
                                    '.', color=Color.value)
                    
                    
                if Gradient.value == True:
                    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", [Color1.value, Color2.value])
                    NormT = Norm(TurnMin.value, TurnMax.value)
                    plt.colorbar(cm.ScalarMappable(norm=NormT, cmap=cmap))
                    if XPlot.value != "Turns" and YPlot.value != "Turns":
                        with tqdm_out:
                            tqdm_out.clear_output()
                            for T in tqdm(T_arr):
                                for p in range(np.shape(data)[1]):
                                    axP.plot(data[coord[XPlot.value],  p, T],
                                             data[coord[YPlot.value] , p, T],
                                             '.', color=cmap(NormT(T)))
                    if XPlot.value == "Turns":
                        with tqdm_out:
                            tqdm_out.clear_output()
                            for T in tqdm(T_arr):
                                for p in range(np.shape(data)[1]):
                                    axP.plot(T, data[coord[YPlot.value], p, T],
                                            '.', color=cmap(NormT(T)))
                    if YPlot.value == "Turns":
                        with tqdm_out:
                            tqdm_out.clear_output()
                            for T in tqdm(T_arr):
                                for p in range(np.shape(data)[1]):
                                    axP.plot(data[coord[XPlot.value], p, T], T,
                                            '.', color=cmap(NormT(T)))                               
                
        
        PlotButton.on_click(plotphase)
        
        plt.show()
        
    PhaseSpaceDash = widgets.VBox([widgets.HBox([Inputs, widgets.VBox([TurnDisplay, err_out]), Buttons]), tqdm_out, phase_output])
    
    return PhaseSpaceDash



    '''
    phase_output = widgets.Output()
    
    with output:
        figP, axP = plt.subplots(figsize=(11,8))
        dimensions, nparticles, nturns = np.shape(tracks)
        nturns = 40000
        cmap = cm.get_cmap("Purples")
        NormT = Norm(0, nturns)
        
        for T in tqdm(range(nturns)):
            for p in range(nparticles):
                axP.plot(tracks[0,p,T], tracks[1,p,T], '.', color=cmap(T/nturns))
        plt.colorbar(cm.ScalarMappable(norm=NormT, cmap=cmap))
   '''