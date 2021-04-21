from .i10g import *
import FreeCAD as App
import FreeCADGui as Gui


class ReloadWorkbench():
    def GetResources(self):
        return {'Pixmap': f'{ICONPATH}/reload.svg',
                'MenuText': 'Reload workbench',
                'ToolTip': 'Reload workbench'}

    def Activated(self):
        App.Console.PrintLog(f'Reloading macro. Command {id(self)}\n')
        Gui.activateWorkbench('StartWorkbench')
        try:
            Gui.Selection.removeObserver(STATE['selObs'])
            App.removeDocumentObserver(STATE['docObs'])
        except:
            pass
        try:
            Gui.removeWorkbench('Inbetweening')
        except:
            pass
        import importlib
        import freecad.i10g
        importlib.reload(freecad.i10g.reload)
        importlib.reload(freecad.i10g.i10g)
        importlib.reload(freecad.i10g.commands)
        importlib.reload(freecad.i10g.init_gui)
        Gui.activateWorkbench('Inbetweening')
        if App.ActiveDocument:
            App.setActiveDocument(App.ActiveDocument.Name)

    def IsActive(self):
        return True

Gui.addCommand('ReloadWorkbench', ReloadWorkbench())