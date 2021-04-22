from .i10g import *
import FreeCAD as App
import FreeCADGui as Gui


class CreateAnimation():
    def GetResources(self):
        return {'Pixmap': f'{ICONPATH}/i10g.svg',
                'MenuText': 'Create animation',
                'ToolTip': 'Create animation'}

    def Activated(self):
        STATE['animation'] = Animation.getInstance()

    def IsActive(self):
        return (not STATE['animation']) and App.ActiveDocument and \
            App.ActiveDocument == STATE['doc']


class FirstStepCmd():
    def GetResources(self):
        return {
            'Pixmap': f'{ICONPATH}/first.svg',
            'MenuText': 'Jump to first step',
            'ToolTip': 'Jump to first step',
        }

    def Activated(self):
        a = STATE['animation']
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(a.obj.Group[0])

    def IsActive(self):
        return STATE['animation'] and STATE['step'] != 0 and not STATE['play']


class PrevStepCmd():
    def GetResources(self):
        return {
            'Pixmap': f'{ICONPATH}/prev.svg',
            'MenuText': 'Previous step',
            'ToolTip': 'Previous step',
        }

    def Activated(self):
        a = STATE['animation']
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(a.obj.Group[STATE['step'] - 1])

    def IsActive(self):
        return STATE['animation'] and STATE['step'] != 0 and not STATE['play']


class PlayCtrlCmd():
    def GetResources(self):
        return {
            'Pixmap': f'{ICONPATH}/play.svg',
            'MenuText': 'Play animation',
            'ToolTip': 'Play animation',
        }

    def Activated(self):
        STATE['animation'].play()

    def IsActive(self):
        return STATE['animation'] and not STATE['play']


class PauseCtrlCmd():
    def GetResources(self):
        return {
            'Pixmap': f'{ICONPATH}/pause.svg',
            'MenuText': 'Pause animation',
            'ToolTip': 'Pause animation',
        }

    def Activated(self):
        STATE['play'] = False

    def IsActive(self):
        return STATE['animation'] and STATE['play'] and not STATE['render']


class NextStepCmd():
    def GetResources(self):
        return {
            'Pixmap': f'{ICONPATH}/next.svg',
            'MenuText': 'Next step',
            'ToolTip': 'Next step',
        }

    def Activated(self):
        a = STATE['animation']
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(a.obj.Group[STATE['step'] + 1])

    def IsActive(self):
        return STATE['animation'] and STATE['step'] < STATE['#step'] and \
            not STATE['play']


class LastStepCmd():
    def GetResources(self):
        return {
            'Pixmap': f'{ICONPATH}/last.svg',
            'MenuText': 'Jump to last step',
            'ToolTip': 'Jump to last step',
        }

    def Activated(self):
        a = STATE['animation']
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(a.obj.Group[STATE['#step'] - 1])

    def IsActive(self):
        return STATE['animation'] and STATE['step'] < STATE['#step'] and \
            not STATE['play']


class AddStepCmd():
    def GetResources(self):
        return {
            'Pixmap': f'{ICONPATH}/add.svg',
            'MenuText': 'Add step',
            'ToolTip': 'Add step',
        }

    def Activated(self):
        a = STATE['animation']
        a.addStep()

    def IsActive(self):
        return STATE['animation'] and not STATE['play']


class CopyStepCmd():
    def GetResources(self):
        return {
            'Pixmap': f'{ICONPATH}/copy.svg',
            'MenuText': 'Copy step',
            'ToolTip': 'Copy step',
        }

    def Activated(self):
        a = STATE['animation']
        selection = Gui.Selection.getCompleteSelection()
        if selection[0] == STATE['animation'].obj.Group[-1]:
            a.addStep()
        else:
            a.addStep(before=STATE['step'] + 1)

    def IsActive(self):
        selection = Gui.Selection.getCompleteSelection()
        return STATE['animation'] and len(selection) == 1 and \
            selection[0] in STATE['animation'].obj.Group and not STATE['play']


class UpdateStepCmd():
    def GetResources(self):
        return {
            'Pixmap': f'{ICONPATH}/update.svg',
            'MenuText': 'Update step',
            'ToolTip': 'Update step',
        }

    def Activated(self):
        a = STATE['animation']
        obj = a.obj.Group[STATE['step']]
        a.steps[obj.Name].updateState(True)

    def IsActive(self):
        return STATE['animation'] and not STATE['play']


class RenderCmd():
    def GetResources(self):
        return {
            'Pixmap': f'{ICONPATH}/video.svg',
            'MenuText': 'Render Animation',
            'ToolTip': 'Export video file',
        }

    def Activated(self):
        STATE['animation'].video()

    def IsActive(self):
        return STATE['animation'] and (not STATE['play']) and \
            STATE['animation'].obj.getPropertyByName('FFmpeg') != ''


class RenderGIFCmd():
    def GetResources(self):
        return {
            'Pixmap': f'{ICONPATH}/gif.svg',
            'MenuText': 'Render Animation',
            'ToolTip': 'Export gif file',
        }

    def Activated(self):
        start = time.time()
        STATE['animation'].video()
        ffmpeg = STATE['animation'].obj.getPropertyByName('FFmpeg')
        video = STATE['animation'].obj.getPropertyByName('OutputFilename')
        res = STATE['animation'].obj.getPropertyByName('Resolution')
        params = f'{ffmpeg} -y -i {video} -vf palettegen /tmp/palette.png'
        p = subprocess.Popen(params.split(), stdin=None)
        p.wait()
        outfile = os.path.splitext(video)[0]
        params = f'{ffmpeg} -y -i {video} -i /tmp/palette.png '
        params += f'-filter_complex paletteuse {outfile}.gif'
        p = subprocess.Popen(params.split(), stdin=None)
        p.wait()
        dt = time.time() - start
        dt = '{:0>2.0f}:{:0>2.0f}'.format(dt//60, dt%60)
        print(f'Done in {dt}')

    def IsActive(self):
        return STATE['animation'] and (not STATE['play']) and \
            STATE['animation'].obj.getPropertyByName('FFmpeg') != ''


class RenderPNGCmd():
    def GetResources(self):
        return {
            'Pixmap': f'{ICONPATH}/png.svg',
            'MenuText': 'Render Frame',
            'ToolTip': 'Export png file',
        }

    def Activated(self):
        start = time.time()
        r = STATE['animation'].obj.getPropertyByName('Resolution')
        w, h = (int(c) for c in r.split('x'))
        bg = STATE['animation'].obj.getPropertyByName('Background')
        view = Gui.activeDocument().activeView()
        view.saveImage('frame.png', w, h, bg)
        dt = time.time() - start
        dt = '{:0>2.0f}:{:0>2.0f}'.format(dt//60, dt%60)
        print(f'Done in {dt}')

    def IsActive(self):
        return STATE['animation'] and (not STATE['play'])


class StopRenderCmd():
    def GetResources(self):
        return {
            'Pixmap': f'{ICONPATH}/abort.svg',
            'MenuText': 'Abort Render',
            'ToolTip': 'Cancel export',
        }

    def Activated(self):
        STATE['play'] = False

    def IsActive(self):
        return STATE['animation'] and STATE['play'] and STATE['render']


class CreateExampleCmd():
    def GetResources(self):
        return {
            'Pixmap': f'{ICONPATH}/animation.svg',
            'MenuText': 'Open Example',
            'ToolTip': 'Open example',
        }

    def Activated(self):
        doc = App.newDocument('AnimationExample')
        App.setActiveDocument(doc.Name)
        Gui.runCommand('CreateAnimation')

        # create part
        p0 = doc.addObject('App::Part', 'Part')
        box = doc.addObject('Part::Box', 'Box')
        p0.addObject(box)
        p0.Visibility = False

        # create links
        l0 = doc.addObject('App::Link', 'Link')
        l0.setLink(p0)
        l1 = doc.addObject('App::Link', 'Link')
        l1.setLink(p0)
        l2 = doc.addObject('App::Link', 'Link')
        l2.setLink(p0)

        # set step 0
        l1.Placement.Base.x = 10
        l2.Placement.Base.x = 20
        doc.recompute()
        Gui.ActiveDocument.ActiveView.viewTrimetric()
        Gui.SendMsgToActiveView('ViewFit')

        # update first step
        Gui.runCommand('UpdateStepCmd')

        # set step 1
        l0.Placement.Base.z = 10
        l0.Visibility = False

        l1.Placement.Base.z = 10
        l1.ViewObject.OverrideMaterial = True
        l1.ViewObject.ShapeMaterial = App.Material(DiffuseColor=(1, 0, 0))

        l2.Placement.Base.z = 10
        l2.Placement.Rotation.Angle = -numpy.pi/2
        # l2.Placement.Base.x += 20

        doc.recompute()
        Gui.SendMsgToActiveView('ViewFit')

        # add 2nd step
        Gui.runCommand('AddStepCmd')
        Gui.runCommand('FirstStepCmd')

    def IsActive(self):
        return not STATE['play']


cmds = [
    CreateAnimation,
    FirstStepCmd,
    PrevStepCmd,
    PlayCtrlCmd,
    PauseCtrlCmd,
    NextStepCmd,
    LastStepCmd,
    AddStepCmd,
    CopyStepCmd,
    UpdateStepCmd,
    RenderCmd,
    RenderGIFCmd,
    RenderPNGCmd,
    StopRenderCmd,
    CreateExampleCmd,
]
for cmd in cmds:
    Gui.addCommand(cmd.__name__, cmd())