import os
import tkinter as tk
from PIL import ImageTk, Image, UnidentifiedImageError
from generiekeFuncties.fileHandlingFunctions import veranderVanKant, markeerGecontroleerd
from generiekeFuncties.plaatjesFuncties import blur
from screeninfo import get_monitors



def rgb_naar_hex(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb

def sorteer(x, y):
    return min(x, y), max(x, y)

class MousePositionTracker(tk.Frame):
    """ Tkinter Canvas mouse position widget. """

    def __init__(self, canvas):
        self.canvas = canvas
        self.canv_width = self.canvas.cget('width')
        self.canv_height = self.canvas.cget('height')
        self.reset()

        # Create canvas cross-hair lines.
        xhair_opts = dict(dash=(3, 2), fill='white', state=tk.HIDDEN)
        self.lines = (self.canvas.create_line(0, 0, 0, self.canv_height, **xhair_opts),
                      self.canvas.create_line(0, 0, self.canv_width,  0, **xhair_opts))

    def cur_selection(self):
        return (self.start, self.end)

    def begin(self, event):
        self.hide()
        self.start = (event.x, event.y)  # Remember position (no drawing).

    def update(self, event):
        self.end = (event.x, event.y)
        self._update(event)
        self._command(self.start, (event.x, event.y))  # User callback.

    def _update(self, event):
        # Update cross-hair lines.
        self.canvas.coords(self.lines[0], event.x, 0, event.x, self.canv_height)
        self.canvas.coords(self.lines[1], 0, event.y, self.canv_width, event.y)
        self.show()

    def reset(self):
        self.start = self.end = None

    def hide(self):
        self.canvas.itemconfigure(self.lines[0], state=tk.HIDDEN)
        self.canvas.itemconfigure(self.lines[1], state=tk.HIDDEN)

    def show(self):
        self.canvas.itemconfigure(self.lines[0], state=tk.NORMAL)
        self.canvas.itemconfigure(self.lines[1], state=tk.NORMAL)

    def autodraw(self, command=lambda *args: None):
        """Setup automatic drawing; supports command option"""
        # self.reset()
        self._command = command
        self.canvas.bind("<Button-1>", self.begin)
        self.canvas.bind("<B1-Motion>", self.update)
        self.canvas.bind("<ButtonRelease-1>", self.quit)

    def quit(self, event):
        self.hide()  # Hide cross-hairs.
        #self.reset()


class SelectionObject:
    """ Widget to display a rectangular area on given canvas defined by two points
        representing its diagonal.
    """
    def __init__(self, canvas, select_opts):
        # Create attributes needed to display selection.
        self.canvas = canvas
        self.select_opts1 = select_opts
        self.width = self.canvas.cget('width')
        self.height = self.canvas.cget('height')

        # Options for areas outside rectanglar selection.
        select_opts1 = self.select_opts1.copy()  # Avoid modifying passed argument.
        select_opts1.update(state=tk.HIDDEN)  # Hide initially.
        # Separate options for area inside rectanglar selection.
        select_opts2 = dict(dash=(2, 2), fill='', outline='white', state=tk.HIDDEN)

        # Initial extrema of inner and outer rectangles.
        imin_x, imin_y,  imax_x, imax_y = 0, 0,  1, 1
        omin_x, omin_y,  omax_x, omax_y = 0, 0,  self.width, self.height

        self.rects = (
            # Area *outside* selection (inner) rectangle.
            self.canvas.create_rectangle(omin_x, omin_y,  omax_x, imin_y, **select_opts2),
            self.canvas.create_rectangle(omin_x, imin_y,  imin_x, imax_y, **select_opts2),
            self.canvas.create_rectangle(imax_x, imin_y,  omax_x, imax_y, **select_opts2),
            self.canvas.create_rectangle(omin_x, imax_y,  omax_x, omax_y, **select_opts2),
            # Inner rectangle.
            self.canvas.create_rectangle(imin_x, imin_y,  imax_x, imax_y, **select_opts1)
        )

    def update(self, start, end):
        # Current extrema of inner and outer rectangles.
        imin_x, imin_y,  imax_x, imax_y = self._get_coords(start, end)
        omin_x, omin_y,  omax_x, omax_y = 0, 0,  self.width, self.height

        # Update coords of all rectangles based on these extrema.
        self.canvas.coords(self.rects[0], omin_x, omin_y,  omax_x, imin_y),
        self.canvas.coords(self.rects[1], omin_x, imin_y,  imin_x, imax_y),
        self.canvas.coords(self.rects[2], imax_x, imin_y,  omax_x, imax_y),
        self.canvas.coords(self.rects[3], omin_x, imax_y,  omax_x, omax_y),
        self.canvas.coords(self.rects[4], imin_x, imin_y,  imax_x, imax_y),

        for rect in self.rects:  # Make sure all are now visible.
            self.canvas.itemconfigure(rect, state=tk.NORMAL)

    def _get_coords(self, start, end):
        """ Determine coords of a polygon defined by the start and
            end points one of the diagonals of a rectangular area.
        """
        return (min((start[0], end[0])), min((start[1], end[1])),
                max((start[0], end[0])), max((start[1], end[1])))

    def hide(self):
        for rect in self.rects:
            self.canvas.itemconfigure(rect, state=tk.HIDDEN)

class Viewer:
    # Default selection object options.
    SELECT_OPTS = dict(dash=(2, 2), stipple='gray25', fill='blue',
                          outline='')
    def __init__(self, imgList, titel, aanleidingTotVeranderen):
        if len(imgList)>0:
            self.index = 0
            self.changeList = []
            self.imageList = imgList
            self.root = tk.Tk()
            self.titel = titel
            monitors = get_monitors()
            for m in monitors:
                if m.y == 0:
                    print(str(m))
                    breedte = m.width - 100
                    hoogte = m.height - 40
            self.aanleidingTotVranderen = aanleidingTotVeranderen
            geometrie = str(breedte) + "x" + str(hoogte)
            self.breedte = breedte
            self.hoogte = hoogte
            self.root.geometry(geometrie)
            nietBtn = tk.Button(self.root, text="NIET (z)", command=self.niet)
            nietBtn.place(x=breedte, y=0)
            verwijderBtn = tk.Button(self.root, text="VERWIJDER (^)", command=self.verwijder)
            verwijderBtn.place(x=breedte, y=30)
            welBtn = tk.Button(self.root, text="WEL (x)", command=self.wel)
            welBtn.place(x=breedte, y=60)
            backBtn = tk.Button(self.root, text="TERUG (<)", command=self.undo)
            backBtn.place(x=breedte, y=90)
            verwerkenBtn = tk.Button(self.root, text="VERWERKEN", command=self.verwerken)
            verwerkenBtn.place(x=breedte, y=400)
            klaarBtn = tk.Button(self.root, text="KLAAR", command=self.klaar)
            klaarBtn.place(x=breedte, y=610)
            afbrekenBtn = tk.Button(self.root, text="AFBREKEN", command=self.afbreken)
            afbrekenBtn.place(x=breedte, y=640)
            self.root.bind("<Key>", self.key)
            # Create selection object to show current selection boundaries.
            try:
                self.canvas = tk.Canvas(self.root, width=self.breedte, height=self.hoogte,
                                borderwidth=0, highlightthickness=0)
                self.canvas.pack(expand=True, anchor=tk.W)
                self.toon_new_image()
            except UnidentifiedImageError as e:
                print("Image niet te openen: ", self.imageList[self.index], " - ", e)
 # Enable callbacks.
            self.root.mainloop()
        else:
            print("lijst is leeg")

    def verwerken(self):
        print("verwerken Lijst ", self.titel)
        for operatie, filePad in self.changeList:
            print(operatie, " ", filePad)
            if operatie == "verwijder":
                os.remove(filePad)
            elif operatie == self.aanleidingTotVranderen:
                print(veranderVanKant(filePad, operatie))
            else:  # onveranderd maar wel gecontroleerd
                print(markeerGecontroleerd(filePad, operatie))
        self.imageList = self.imageList[self.index:]
        self.index = 0
        self.changeList = []


    def klaar(self):
        self.verwerken()
        self.root.destroy()


    def blur(self):
        print(str(self.posn_tracker.cur_selection()))
        a, b = self.posn_tracker.cur_selection()
        x1, y1 = (int(i // self.vergroting) for i in a)
        x2, y2 = (int(i // self.vergroting) for i in b)
        x1, x2 = sorteer(x1, x2)
        y1, y2 = sorteer(y1, y2)
        # Nu moeten we de vertaling maken naar de coordinaten van de image die immers vergroot of verkleind is
        box = (x1, y1, x2, y2)
        self.im = blur(self.im, box)
        self.toon_image()
        image_path = self.imageList[self.index]
        self.im.save(image_path)


    def afbreken(self):
        self.root.destroy()


    def toon_new_image(self):
        if self.index < len(self.imageList):
            image_path = self.imageList[self.index]
            self.im = Image.open(image_path)
            self.toon_image()
            self.root.title(self.titel + str(self.im.size) +
                            " [" + str(self.index) + " van " + str(len(self.imageList)) + "]    " +
                            image_path)
        else:
            self.root.title(self.titel + "      Alle images verwerkt")
    def toon_image(self):
        self.vergroting = min(self.breedte / self.im.size[0], self.hoogte / self.im.size[1])
        nieuweGrootte = (int(self.im.size[0] * self.vergroting), int(self.im.size[1] * self.vergroting))
        im = self.im.resize(nieuweGrootte, Image.BICUBIC)
        stgImg = ImageTk.PhotoImage(im)
        self.root.stgImg = stgImg
        self.canvas.create_image(0, 0, image=stgImg, anchor=tk.NW)
        self.root.configure(bg=rgb_naar_hex(((100 + 10 * self.index % 3), 100 + 10 * ((self.index + 1) % 3), 100 + 10 * ((self.index + 2) % 3))))
        self.selection_obj = None
        self.selection_obj = SelectionObject(self.canvas, self.SELECT_OPTS)

        # Callback function to update it given two points of its diagonal.
        def on_drag(start, end, **kwarg):  # Must accept these arguments.
            self.selection_obj.update(start, end)

        # Create mouse position tracker that uses the function.
        self.posn_tracker = MousePositionTracker(self.canvas)
        self.posn_tracker.autodraw(command=on_drag)




    def nextImage(self):
        if self.index == len(self.imageList):
            print("Next had niet gemogen is ongedaan gemaakt.")
        else:
            self.index = self.index + 1
            self.toon_new_image()

    def niet(self):
        if self.index < len(self.imageList):
            self.changeList.append(("niet", self.imageList[self.index]))
            self.nextImage()

    def verwijder(self):
        if self.index < len(self.imageList):
            self.changeList.append(("verwijder", self.imageList[self.index]))
            self.nextImage()


    def wel(self):
        if self.index < len(self.imageList):
            self.changeList.append(("wel", self.imageList[self.index]))
            self.nextImage()


    def undo(self):
        if self.index>0:
            self.index = self.index - 1
            del self.changeList[-1]
        self.toon_new_image()


    def key(self, event):
        kp = repr(event.keysym)
        print(kp)  # repr(event.char))
        if (kp == '\'z\''):
            self.niet()
        if (kp == '\'Up\''):
            self.verwijder()
        if (kp == '\'x\''):
            self.wel()
        if (kp == '\'Left\''):
            self.undo()
        if (kp == '\'a\''):
            self.blur()
        if (kp == '\'Shift_R\''):
            self.root.wm_state('iconic')