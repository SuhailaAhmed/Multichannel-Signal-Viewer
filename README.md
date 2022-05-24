# Multichannel-Signal-Viewer

Monitor the vital signals like ECG, EMG in any ICU room with signal viewing options using Python, Qt.

![demo](demo.gif)

## Features

* The user can browse his PC to open any signal file. Each group will need to provide samples from three different
medical signals (e.g. ECG, EMG, EEG,...etc). Each signal type should have an example for normal signal and
abnormal signal.

* Application contain one main graph. When the user opens a signal file, it should show up on your
graph in the cine mode (i.e. a running signal through time, similar to the one you see in the ICU monitors). Do
NOT open a signal in a static mode.

* The use can manipulate the running signals through UI elements that provide the below function:

    * Change color

    * Add a label/title for each signal

    * Show/hide

    * Control/customize the cine speed

    * Zoom in/out

    * Pause/play

    * Scroll/Pan the signal is any direction (left, top, right, bottom). Scroll is through sliders, and pan is
    through the mouse movements.

    During these manipulations, you need to take care of the boundary conditions! Intuitively, no scroll/pan should
    be allowed before your signal starts or after it ends or above its maximum values or below its minimum values.
    No user expects to see an empty graph coz he scrolled the signal too much to the top for example. Note:
    Ofcourse, all manipulations will be applied on all the opened signals (viewed or hidden).

* For each opened signal, the user can visualize the signal spectrogram (search for the term and how to generate
it) image somewhere beside the main graph (not as a popup window!). Please, show your design skills to
produce a nice-looking combination between the graph, the spectrogram, and the UI elements.

    * The user can control/customize the relative size of the signal graph and the spectrogram image via
    dragging a splitter or any other convenient method (Do NOT pop up a window that asks the user about
    the relative size!!!).

    * The UI can display several signals but only one spectrogram (for one of the displayed signals). The user
    should control which spectrogram to display via a combobox or menuitem that shows the labels/titles of
    the signals. When the user select the label/title of the signal s/he wants, the spectrogram should be
    updated accordingly.

    * The color palette that is used in the spectrogram through a combo-box/
    drop-menu that has 5 different
    palettes to use from. You can use some standard palettes from your library. You do not need to create
    your own palettes.

    * The user can control the level of details shown in spectrogram by changing the range (i.e. min and max
    values) of the pixels intensity that are displayed. The use can control this through two sliders: one for
    the min value and one for the max. Each slider should go from min and max values of the pixel
    intensities of the spectrogram. Please, check the function imcontrast in Matlab to understand this
    feature before implementing it in your program.

* Exporting & Reporting: For the sake of reporting, the user can export the current status of the graph,
spectrogram along with some data statistics on the displayed signals to a pdf file. You need to generate the pdf
contents via the code. i.e. Do NOT take a snapshot image and convert it to a pdf file!

    * Data statistics can be mean, std, duration, min and max values for each signal. These numbers should show up in a nice table in the pdf file. The table can have the signals in different rows and the values in different columns.
