import matplotlib.pyplot as plt
from matplotlib.colors import Normalize as Norm
import matplotlib.cm as cm
import numpy as np
from tqdm.notebook import tqdm
import ipywidgets as widgets


def PhaseSpaceInputs(trackdata):
    ''''''
    XPlot = widgets.Dropdown(options=['X', 'Xp', 'Y', 'Yp', 't', 'Pt', 'Turns'], value='X',  description = 'X-axis coord')
    YPlot = widgets.Dropdown(options=['X', 'Xp', 'Y', 'Yp', 't', 'Pt', 'Turns'], value='Xp', description = 'Y-axis coord')

    TurnType = widgets.RadioButtons(options=['Single Turn', 'Cumulative Turns'], description='Plot Type')
    TurnDisplay = widgets.Output()
    TurnNo  = widgets.BoundedIntText(value=100, min=0, max=1E10, step=100, description='Turn Number')
    TurnMin = widgets.BoundedIntText(value=0  , min=0, max=1E10, step=100, description='Turn Min')
    TurnMax = widgets.BoundedIntText(value=100, min=0, max=1E10, step=100, description='Turn Max')
    TurnStep = widgets.BoundedIntText(value=10, min=0, max=1E10, step=10, description='Turn Step')

    Color = widgets.ColorPicker(description='Colour', value='blue')
    Gradient = widgets.Checkbox(value=False, description='Gradient Plot')
    Color1 = widgets.ColorPicker(description='Colour 1', value='gray')
    Color2 = widgets.ColorPicker(description='Colour 2', value='purple')

    Inputs = widgets.VBox([XPlot, YPlot, TurnType])
    with TurnDisplay:
        display(widgets.HBox([TurnNo, Color]))
    
    PlotButton = widgets.Button(description='Plot', icon='fchart-scatter')
    AnimateButton = widgets.Button(description='Animate', icon='photo-video')
    
    Buttons = widgets.VBox([PlotButton, AnimateButton])
    
    def InputType(check):
        TurnDisplay.clear_output()
        global TurnInputs
        global ColorInputs
        if TurnType.value == 'Single Turn':
            with TurnDisplay:
                display(widgets.HBox([TurnNo, Color]))
        if TurnType.value == 'Cumulative Turns':
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
            if TurnType.value == 'Single Turn':
                axP.plot(data[0,:,TurnNo.value], data[1,:,TurnNo.value], '.', color=Color.value)
        
        PlotButton.on_click(plotphase)
        
        plt.show()
        
    def PlotType(check):
        if XPlot.value == 'X' or XPlot.value == 'Y':
            axP.set_xlabel(f'{XPlot.value} [m]')
        else:
            axP.set_xlabel(f'{XPlot.value}')
        if YPlot.value == 'X' or YPlot.value == 'Y':
            axP.set_ylabel(f'{YPlot.value} [m]')
        else:
            axP.set_ylabel(f'{YPlot.value}')    
    
    XPlot.observe(PlotType, 'value'), YPlot.observe(PlotType, 'value')
        
    PhaseSpaceDash = widgets.VBox([widgets.HBox([Inputs, TurnDisplay, Buttons]), phase_output])
    
    return PhaseSpaceDash

def PhaseSpacePlot(tracks):
    '====================== Phase-Space Inputs ============================'
    XPlot = widgets.Dropdown(options=['X', 'Xp', 'Y', 'Yp', 't', 'Pt', 'Turns'], value='X',  description = 'X-axis coord')
    YPlot = widgets.Dropdown(options=['X', 'Xp', 'Y', 'Yp', 't', 'Pt', 'Turns'], value='Xp', description = 'Y-axis coord')
    
    Type = widgets.RadioButtons(options=['Single Turn', 'Cumulative Turns'], description='Plot Type')
    
    phase_output = widgets.Output()
    with phase_output:
        print(tracks)
    return phase_output


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