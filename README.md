# Inbetweening

![logo](https://github.com/anderson-/inbetweening/raw/main/img/logo.svg "i10g logo")

[![donate](https://img.shields.io/badge/Donate-PayPal-yellow)](https://www.paypal.com/donate?hosted_button_id=HNR23JTXANYSQ) [![Liberapay](http://img.shields.io/liberapay/patrons/anderson.svg?logo=liberapay)](https://liberapay.com/anderson/donate) ![GitHub Repo stars](https://img.shields.io/github/stars/anderson-/inbetweening?style=social) ![GitHub](https://img.shields.io/github/license/anderson-/inbetweening)

Inbetweening (*abbreviated as i10g*) is a WYSIWYG (What You See Is What You Get) animation workbench for FreeCAD. It enables you to save the current placement, visibility and color of an assembly, composed of [`App:::Link`](https://wiki.freecadweb.org/Std_LinkMake) objects, as an animation "step". The workbench interpolates between steps to create smooth transitions. It can be used to create exploded-view animations.

![GIF](https://github.com/anderson-/inbetweening/raw/main/img/file.gif "Output GIF")

*Example of a GIF exported using i10g*

> **If you find this workbench useful, please consider supporting my work on [Liberapay](https://liberapay.com/anderson/donate) or [PayPal](https://www.paypal.com/donate?hosted_button_id=HNR23JTXANYSQ). Starring and sharing also helps! Thanks!**

## Features

- Create transitions between different states of visibility, placement and color
- Preview animation in realtime
- Export images, videos and gifs

> Note: Object rotation is simplified to the shorter path

## Getting Started


### Prerequisites

- [FreeCAD 0.19](https://www.freecadweb.org/downloads.php)
- [FFmpeg 4.2.2](https://www.johnvansickle.com/ffmpeg/old-releases/)

> If you have problems with the exported video/GIF, please check your ffmpeg version. For me `4.3.2` (bundled with the flatpak build) and the latest `4.4` version produce artifacts in the outputed GIF or doesn't have support for the parameter `image2pipe`

*Tested on linux*

### Installing


#### Python pip

*Please check if the current python environment is the same used in your installation of FreeCAD*

```
python3 -m pip install i10g
```

or

```
python3 -m pip install https://github.com/anderson-/inbetweening/archive/refs/heads/main.zip
```

#### Linux

```
wget -qO- https://github.com/anderson-/inbetweening/archive/refs/heads/main.zip | busybox unzip -d ~/.FreeCAD/Mod -
```

## Usage

Before starting, I reccommend to backup your work, and consider creating an extra file for the main assembly, importing each part as an [`App::Link`](https://wiki.freecadweb.org/App_Link) by using the [`Std LinkMake`](https://wiki.freecadweb.org/Std_LinkMake) button.

### Toolbar Overview


![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/i10g.svg) Add an `Animation` folder object to the current document, the current scene is set as the first step of the animation

![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/animation.svg) Create an example document

![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/add.svg) Adds another step to the end of the current animation

> In the tree view ![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/selected_step.svg) represents the current selected step, the other steps should have the icon ![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/step.svg)


![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/copy.svg) Duplicate the current selected step

![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/update.svg) Updates the selected step to reflect the current scene

![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/first.svg)
![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/prev.svg)
![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/play.svg)
![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/pause.svg)
![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/next.svg)
![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/last.svg)

Controls the animation preview

![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/png.svg) Export the current view using parameters from `Animation` folder

![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/video.svg) Export video file using parameters from `Animation` folder

![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/gif.svg) Export GIF file using parameters from `Animation` folder

![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/abort.svg) Abort the export process

### Example

> This example can be created automagically using the ![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/animation.svg) button

1. Create a `Part::Box`, add it to a `App::Part`, and make it not visible
2. Create 3 [`App::Link`](https://wiki.freecadweb.org/App_Link), and position them side by side, this will be the first animation step

3. Select the i10g workbench and click ![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/i10g.svg) to add an `Animation` folder, it should already set the current scene as the first step

![step0](https://github.com/anderson-/inbetweening/raw/main/img/step0.png "1st Step")

*First step*

4. Move all the cubes, 10mm up
5. Set `Visibility = False` for the first one
6. For the second one:
    - Set `OverrideMaterial = True`
    - Change `ShapeMaterial` color to red
6. Rotate the third one by 90°

![step1](https://github.com/anderson-/inbetweening/raw/main/img/step1.png "2nd Step")

*Second step*

7. Click ![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/add.svg) to add a step

8. Click ![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/play.svg) to preview the animation

9. Select `Animation` folder in the tree, set `FFmpeg` path and set `Resolution` to `426x240`

10. Click ![](https://github.com/anderson-/inbetweening/raw/main/freecad/i10g/resources/gif.svg) to export a GIF file

![GIF](https://github.com/anderson-/inbetweening/raw/main/img/file.gif "Output GIF")

*Result*

**Example of a 4k/2160p (3840x2160) 60fps video export:** https://www.youtube.com/watch?v=RZUoOqqV1uE

### Development

To reload the workbench for easy development, use the folowing command in the python console:

```python
Gui.activateWorkbench('Inbetweening'); App.DEV=1; Gui.runCommand('ReloadWorkbench')
```

## Acknowledgments

Special thanks to Lorenz Lechner - [@looooo](https://github.com/looooo) for his work on the [workbench_starterkit
](https://github.com/FreeCAD/freecad.workbench_starterkit) and [freecad.gears](https://github.com/looooo/freecad.gears)

