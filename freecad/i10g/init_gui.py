import FreeCAD as App
import FreeCADGui as Gui
from freecad.i10g import ICONPATH


class Inbetweening(Gui.Workbench):
    MenuText = 'Inbetweening'
    ToolTip = 'Simple Animation Workbench'
    Icon = f'{ICONPATH}/i10g.svg'

    def GetClassName(self):
        return 'Gui::PythonWorkbench'

    def Initialize(self):
        App.Console.PrintLog(f'Initialize inbetweening workbench')
        import freecad.i10g.commands
        self.appendToolbar(f'TestTools', [
            'CreateAnimation', 'CreateExampleCmd',
        ])
        self.appendToolbar(f'Control', [
            'FirstStepCmd', 'PrevStepCmd', 'PlayCtrlCmd',
            'PauseCtrlCmd', 'NextStepCmd', 'LastStepCmd',
        ])
        self.appendToolbar(f'Tools', [
            'AddStepCmd', 'CopyStepCmd', 'UpdateStepCmd',
        ])
        self.appendToolbar(f'Render', [
            'RenderPNGCmd', 'RenderCmd', 'RenderGIFCmd', 'StopRenderCmd',
        ])
        import freecad.i10g.i10g as i10g
        i10g.STATE['selObs'] = i10g.SelectionObserver()
        i10g.STATE['docObs'] = i10g.DocumentObserver()

    def Activated(self):
        pass

    def Deactivated(self):
        pass


Gui.addWorkbench(Inbetweening())