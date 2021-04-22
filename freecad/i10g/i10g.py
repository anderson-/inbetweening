import os
import re
import time
import copy
import numpy
import subprocess
import FreeCAD as App
import FreeCADGui as Gui
from freecad.i10g import ICONPATH


IGNORELIST = ['App::Origin', 'App::Line', 'App::Plane']

DEF_RES = [
    '320x240',
    '640x480',
    '800x600',
    '960x720',
    '1024x768',
    '1280x960',
    '1400x1050',
    '1440x1080',
    '1600x1200',
    '1920x1440',
    '2048x1536',
    '426x240',
    '640x360',
    '854x480',
    '1280x720',
    '1920x1080',
    '2560x1440',
    '3840x2160',
    '7680x4320',
    '15360x8640',
]

STATE = {
    'step': 0,
    'render': False,
    'play': False,
    'animation': None,
    'selObs': None,
    'docObs': None,
    'doc': None,
    'GUIFPS': 24,
}


def Doc():
    return App.ActiveDocument


def log(msg):
    App.Console.PrintLog(f'{msg}\n')


def print(msg):
    App.Console.PrintMessage(f'{msg}\n')


def warn(msg):
    App.Console.PrintWarning(f'{msg}\n')


def err(msg):
    App.Console.PrintError(f'{msg}\n')


def createObjState(obj):
    pos = str(obj.Placement.Matrix).split('Matrix')[1]
    pos = pos.translate({ord(c):'' for c in ' ()'})
    pos = [float(i) for i in pos.split(',')]
    assert len(pos) == 16, f'Failed parsing: {str(obj.Placement.Matrix)}'
    color = None
    material = None
    transparency = 0
    if obj.TypeId == 'App::Link':
        material = obj.ViewObject.OverrideMaterial
        color = list(obj.ViewObject.ShapeMaterial.DiffuseColor)[:3]
        transparency = obj.ViewObject.ShapeMaterial.Transparency
    return {
        'name': obj.Name,
        'pos': pos,
        'visible': obj.Visibility,
        'material': material,
        'color': color,
        'transparency': transparency,
    }


def newMaterial(color=None, transparency=None):
    m = App.Material(
        DiffuseColor=(tuple(color or (0.80, 0.80, 0.80))[:3]),
        AmbientColor=(0.20, 0.20, 0.20),
        SpecularColor=(0.00, 0.00, 0.00),
        EmissiveColor=(0.00, 0.00, 0.00),
        Shininess=(0.20),
        Transparency=(float(transparency or 0.00)),
    )
    return m


def interpolate(v1, v2, delta):
    return v1 + (v2 - v1)*delta


def interpolateMaterial(s1, s2, delta):
    r = interpolate(s1.DiffuseColor[0], s2.DiffuseColor[0], delta)
    g = interpolate(s1.DiffuseColor[1], s2.DiffuseColor[1], delta)
    b = interpolate(s1.DiffuseColor[2], s2.DiffuseColor[2], delta)
    t = interpolate(s1.Transparency, s2.Transparency, delta)
    return newMaterial((r, g, b), t)


def applyObjState(state):
    obj = Doc().getObject(state['name'])
    if not obj:
        return
    obj.Placement = state['pos'].copy()
    obj.Visibility = state['visible']
    if obj.TypeId == 'App::Link' and 'material' in state:
        if state['material']:
            obj.ViewObject.OverrideMaterial = True
            obj.ViewObject.ShapeMaterial = state['material']
        else:
            obj.ViewObject.OverrideMaterial = False
            obj.ViewObject.ShapeMaterial = newMaterial()


def animObjState(obj, s1, s2, delta):
    if not obj:
        return
    obj.Placement = s1['pos'].slerp(s2['pos'], delta)
    m1 = s1.get('material')
    m2 = s2.get('material')
    if s1['visible'] == False and not m1:
        m1 = newMaterial(None, 1)
    if s2['visible'] == False and not m2:
        m2 = newMaterial(None, 1)
    if obj.TypeId == 'App::Link':
        if m1 or m2:
            obj.Visibility = True
            obj.ViewObject.OverrideMaterial = True
            obj.ViewObject.ShapeMaterial = interpolateMaterial(
                m1 or newMaterial(),
                m2 or newMaterial(),
                delta
            )
        elif obj.ViewObject.OverrideMaterial:
            obj.ViewObject.OverrideMaterial = False
            obj.ViewObject.ShapeMaterial = newMaterial()


def getState():
    objs = Doc().findObjects()
    state = {}

    for obj in objs:
        if hasattr(obj, 'Placement') and obj.TypeId not in IGNORELIST:
            if obj.TypeId not in ['App::Link', 'App::Part']:
                warn(f'warning: found {obj.FullName} as {obj.TypeId}')
                continue
            state[obj.Name] = createObjState(obj)
    log(f'state: {state}')
    return state


def newProp(obj, name, type_, value, subsection='', tooltip='', default=None):
    if name in obj.PropertiesList:
        return False
    obj.addProperty(f'App::Property{type_}', name, subsection, tooltip)
    setattr(obj, name, value)
    return True


def getDeltas(frames, last=False):
    array = numpy.arange(0, 1, 1 / frames)
    if last:
        array = numpy.append(array, 1)
    return array


class VideoRenderer:

    def __init__(self, ffmpeg):
        self.ffmpeg = ffmpeg
        self.pipein, self.pipeout = (None, None)
        self.tmpfile = '/tmp/stream.png'
        self.start = 0

    def begin(self, name, w=300, h=300, bg='Current', framerate=24, more=''):
        self.filename = name
        self.w = w
        self.h = h
        self.bg = bg
        self.count = 0
        self.start = time.time()

        self.pipein, self.pipeout = os.pipe()
        pid = os.getpid()
        if os.path.exists(self.tmpfile):
            os.remove(self.tmpfile)
        os.symlink(f'/proc/{pid}/fd/{self.pipein}', self.tmpfile)

        params = f'{self.ffmpeg} -y -f image2pipe -framerate {framerate} -i '
        params += f'/proc/{pid}/fd/{self.pipeout} -vcodec png '
        params += more
        params += self.filename

        self.p = subprocess.Popen(params.split(), stdin=None)

    def addFrame(self, total):
        view = Gui.activeDocument().activeView()
        view.saveImage(self.tmpfile, self.w, self.h, self.bg)
        self.count += 1
        if self.count % 10 == 0:
            dt = time.time() - self.start
            left = (total * dt)/(self.count) - dt
            fmt = '{:0>2.0f}:{:0>2.0f}'.format(left//60, left%60)
            print(f'{fmt} remaining')
            Gui.updateGui()

    def end(self):
        os.close(self.pipein)
        os.close(self.pipeout)
        self.p.wait()
        os.remove(self.tmpfile)
        dt = time.time() - self.start
        fps = '{:.0f}'.format(self.count/dt)
        dt = '{:0>2.0f}:{:0>2.0f}'.format(dt//60, dt%60)
        print(f'Exported {self.count} frames in {dt} ({fps} fps)')


class Animation:

    @staticmethod
    def getObject():
        return Doc().getObject('Animation')

    @staticmethod
    def getInstance():
        return Animation(Animation.getObject())

    def __init__(self, obj=None):
        if not obj:
            obj = Doc().addObject('App::DocumentObjectGroupPython', 'Animation')
        self.obj = obj
        self.steps = {}
        for step in obj.Group:
            self.steps[step.Name] = Step(step, obj)
        if not obj.Group:
            self.addStep()
        obj.Proxy = self
        obj.ViewObject.Proxy = self
        # Properties
        newProp(obj, 'OutputFilename', 'File', 'video.mp4', 'Video')
        newProp(obj, 'FFmpeg', 'File', '', 'Video')
        if newProp(obj, 'Resolution', 'Enumeration', DEF_RES, 'Video'):
            obj.Resolution = '1280x720'
        newProp(obj, 'CustomResolution', 'String', '', 'Video')
        newProp(obj, 'Background', 'Enumeration', [
            'Current', 'Black', 'White', 'Transparent'
        ], 'Video')
        newProp(obj, 'FPS', 'Integer', 24, 'Video')

    def onChanged(self, fp, prop):
        pass

    def execute(self, fp):
        pass

    def getIcon(self):
        return f'{ICONPATH}/animation.svg'

    def addStep(self, before=None):
        if not before:
            id = 'Step{:0>3d}'.format(len(self.obj.Group))
            obj = Doc().addObject('App::DocumentObjectGroupPython', f'Step')
            obj.Label = id
            step = Step(obj, self.obj)
            self.steps[obj.Name] = step
            self.obj.addObject(obj)
            STATE['step'] = len(self.obj.Group) - 1
        else:
            tmp = Doc().addObject('App::DocumentObjectGroupPython', 'TMPGroup')
            for i in range(len(self.obj.Group) - before):
                obj = self.obj.removeObject(self.obj.Group[before])[0]
                obj.Label = f'_{obj.Label}'
                tmp.addObject(obj)
            self.addStep()
            id0 = len(self.obj.Group)
            for i in range(len(tmp.Group)):
                obj = tmp.removeObject(tmp.Group[0])[0]
                obj.Label = 'Step{:0>3d}'.format(id0 + i)
                self.obj.addObject(obj)
            Doc().removeObject(tmp.Name)

    def getTotalFrames(self):
        tf = 0
        fps = self.obj.getPropertyByName('FPS')
        for obj in self.obj.Group[:-1]:
            step = self.steps[obj.Name]
            tf += step.ds * fps
        return int(tf)

    def play(self):
        prev = None
        Gui.Selection.clearSelection()
        Gui.runCommand('Std_DrawStyle', 5)
        STATE['play'] = True
        guifps = STATE['GUIFPS']
        framecount = 0
        start = time.time()
        count = len(self.obj.Group)
        for i, obj in enumerate(self.obj.Group):
            STATE['step'] = i
            step = self.steps[obj.Name]
            if prev is None:
                prev = step
                continue
            prev.obj.ViewObject.signalChangeIcon()
            step.obj.ViewObject.signalChangeIcon()
            for delta in getDeltas(guifps, i == count - 1):
                step.anim(prev, delta)
                framecount += 1
                Gui.updateGui()
                time.sleep(0.01)
                if not STATE['play']:
                    break
            guifps = numpy.max((framecount / (time.time() - start), 3))
            prev = step
            if not STATE['play']:
                break
        STATE['GUIFPS'] = guifps
        print(f'{int(guifps)} fps')
        STATE['play'] = False
        Gui.runCommand('Std_DrawStyle', 6)
        Doc().recompute(None, True, True)

    def video(self):
        name = self.obj.getPropertyByName('OutputFilename')
        r = self.obj.getPropertyByName('CustomResolution')
        if not r:
            r = self.obj.getPropertyByName('Resolution')
        w, h = (int(c) for c in r.split('x'))
        bg = self.obj.getPropertyByName('Background')
        fps = self.obj.getPropertyByName('FPS')
        ffmpeg = self.obj.getPropertyByName('FFmpeg')
        if not ffmpeg:
            err(f'FFmpeg path not set!')
            return
        vr = VideoRenderer(ffmpeg)
        vr.begin(name, w, h, bg, fps)
        prev = None
        STATE['render'] = True
        STATE['play'] = True
        Gui.Selection.clearSelection()
        Gui.runCommand('Std_DrawStyle', 5)
        tf = self.getTotalFrames()
        count = len(self.obj.Group)
        for i, obj in enumerate(self.obj.Group):
            STATE['step'] = i
            step = self.steps[obj.Name]
            if prev is None:
                prev = step
                continue
            prev.obj.ViewObject.signalChangeIcon()
            step.obj.ViewObject.signalChangeIcon()
            frames = prev.ds * fps
            for delta in getDeltas(frames, i == count - 1):
                step.anim(prev, delta)
                Gui.updateGui()
                vr.addFrame(tf)
                if not STATE['play']:
                    break
            prev = step
            if not STATE['play']:
                break
        Gui.runCommand('Std_DrawStyle', 6)
        vr.end()
        STATE['play'] = False
        STATE['render'] = False
        Doc().recompute(None, True, True)

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None


class Step:
    def __init__(self, obj, animation):
        obj.Proxy = self
        obj.ViewObject.Proxy = self
        self.obj = obj
        self.name = self.obj.Name
        self.updateState()
        self.animation = animation
        STATE['#step'] = len(animation.Group)
        obj.ViewObject.signalChangeIcon()

    def onChanged(self, fp, prop):
        if prop == 'DurationInSeconds':
            self.ds = self.obj.getPropertyByName('DurationInSeconds')

    def execute(self, fp):
        pass

    def getIcon(self):
        if STATE['step'] == self.animation.Group.index(self.obj):
            return f'{ICONPATH}/selected_step.svg'
        return f'{ICONPATH}/step.svg'

    def updateState(self, force=False):
        if force:
            self.obj.removeProperty('DocState')
        # Properties
        newProp(self.obj, 'DurationInSeconds', 'Integer', 1, 'Animation')
        newProp(self.obj, 'DocState', 'PythonObject', getState())
        self.state = copy.deepcopy(self.obj.getPropertyByName('DocState'))
        self.ds = self.obj.getPropertyByName('DurationInSeconds')
        # Parse values
        for value in self.state.values():
            value['pos'] = App.Placement(App.Matrix(*value['pos']))
            if value['material']:
                value['material'] = newMaterial(
                    value['color'],
                    value['transparency']
                )
            value['obj'] = Doc().getObject(value['name'])

    def apply(self):
        for objState in self.state.values():
            applyObjState(objState)
        Doc().recompute(None, True, True)

    def anim(self, prev, delta):
        for name, objState in self.state.items():
            animObjState(objState['obj'], prev.state[name], objState, delta)

    def __getstate__(self):
        return None

    def __setstate__(self,state):
        return None


class DocumentObserver():
    def __init__(self):
        App.addDocumentObserver(self)

    def slotActivateDocument(self, doc):
        if doc != STATE['doc']:
            STATE['doc'] = doc
            if doc.getObject('Animation'):
                STATE['animation'] = Animation.getInstance()
            else:
                STATE['animation'] = None

    def slotDeletedDocument(self, doc):
        if STATE['doc'] == doc:
            STATE['doc'] = None
            STATE['animation'] = None


class SelectionObserver:
    def __init__(self):
        Gui.Selection.addObserver(self)

    def addSelection(self, doc, obj, sub, pos):
        a = STATE['animation']
        if obj in a.steps:
            oldSelectedObj = a.obj.Group[STATE['step']]
            selectedObj = a.steps[obj].obj
            STATE['step'] = a.obj.Group.index(selectedObj)
            oldSelectedObj.ViewObject.signalChangeIcon()
            selectedObj.ViewObject.signalChangeIcon()
            a.steps[obj].apply()
