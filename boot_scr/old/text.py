# a sample graphical user interface using python-gtk

import pygtk
import gtk
import pango

# independent function to add new text to the end of a gtk.TextView object:
def addtext(TV,text):
    buffer = TV.get_buffer()
    iter = buffer.get_iter_at_mark(buffer.get_insert())
    buffer.insert(iter,text)   # use "\n" for newlines
# addtext      

# Main class for the GUI:
class gui2:
    # The init function will set up the graphical layout of the gui:
    def __init__(self,x,y):  # init with x,y position of window
        self.width, self.height = 350,400
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)  # create window object
        self.window.set_title("gui2 window")
        # self.window.resize(self.width,self.height)  # best leave alone

        # The principal verticle "box" containing gui elements
        self.mainbox = gtk.VBox(False,5) # 5 pixels between boxes
        self.window.add(self.mainbox)    # add box container to window

        # Create GUI elements:
        self.button1 = gtk.Button("OK")       # create button objects
        self.button2 = gtk.Button("Cancel")
        self.text1 = gtk.Entry(32)      # text entry field with max length
        self.check1 = gtk.CheckButton("Always trust contents from Microsoft")
        self.check1.set_active(False)  # initially unchecked
        self.check2 = gtk.CheckButton("Always trust contents from Prof. Liang")
        self.check2.set_active(True)  # initially checked
        self.label1 = gtk.Label("A TextView Widget:                          ")
        self.label2 = gtk.Label("A Textarea widget:                          ")
        
        # A multi-line text area must be first added to a scrollwindow:
        sw = gtk.ScrolledWindow()
        self.textarea = gtk.TextView()
        sw.add(self.textarea)
        sw.set_size_request(400,150)  # can use on any "widget"
        self.textarea.set_editable(False)  # won't use this area for input

        # box to hold two buttons side by side
        box1 = gtk.HBox(False, 30)    # a horizontal "box" of widgets
        # pack buttons into box (from the start)
        box1.pack_start(self.button1,True,True,5)  # ok button
        box1.pack_start(self.button2,True,True,5)  # cancel button


        ###### Create a menu bar with "file" and "help" menus
        self.menubar = gtk.MenuBar()

        # Create separate menus
        self.fmenu = gtk.Menu()
        self.hmenu = gtk.Menu()

        #Menu items:
        self.saveitem = gtk.MenuItem("Save")
        self.quititem = gtk.MenuItem("Quit")
        self.infoitem = gtk.MenuItem("About")

        # Add menu items to menus:
        self.fmenu.append(self.saveitem)
        self.fmenu.append(self.quititem)
        self.hmenu.append(self.infoitem)

        # Add menus to menu bar:
        # But this also involves labeling the menus on the menubar:
        filelabel = gtk.MenuItem("File")
        helplabel = gtk.MenuItem("Help")
        filelabel.set_submenu(self.fmenu)
        helplabel.set_submenu(self.hmenu)
        self.menubar.append(filelabel)
        self.menubar.append(helplabel)
        # note that filelabel is a local var - this is ok, since it
        # won't be referred to outside of init
        #########  # finally done with menus

        # "Pack" gui elements into the main container "box":
        self.mainbox.pack_start(self.menubar,True,True,5) # menu bar
        self.mainbox.pack_start(self.label1,True,True,5)  # label
        self.mainbox.pack_start(sw,True,True,5)           # textview scroll
        self.mainbox.pack_start(self.label2,True,True,5)       # label
        self.mainbox.pack_start(self.text1, True,True,5)       # entry
        self.mainbox.pack_start(box1,True,True,5)              # buttons
        self.mainbox.pack_start(self.check1,True,True,0)       # check button
        self.mainbox.pack_start(self.check2,True,True,0)       # check button

        # connect events with "callback" functions:
        self.button1.connect("clicked",self.handlerb1)
        self.button2.connect("clicked",self.handlerb2)
        self.check1.connect("toggled",self.checkhandler) 
        self.check2.connect("toggled",self.checkhandler) # note same handler
        self.text1.connect("activate",self.inputhandler)
        # Connect menu items with callback event handlers
        self.saveitem.connect("activate",self.menuhandler,"save") # note param
        self.quititem.connect("activate",self.menuhandler,"quit")
        self.infoitem.connect("activate",self.menuhandler,"info")

        # The following lines determine behavior upon window closing:
        # self.window.connect("destroy", lambda w: self.window.destroy())
        self.window.connect("destroy", lambda w: gtk.main_quit())

        # set some extra attributes
        self.text1.modify_font(pango.FontDescription("Sans 12")) #set font
        self.text1.grab_focus() # set curor to this widget

        ####################### Show and move main window #############
        self.window.show_all()  # displays window and all components
        self.window.move(x,y)   # moves window to screen coordinates
                                # move must be called after show_all
    # init  - end of contructor


    # event handler for the "OK" button:
    def handlerb1(self,widget): # first 2 params are required
        self.text1.set_text("No, it's not OK")
    # handlerb1

    def handlerb2(self,widget): # handler for the "cancel" button
        self.text1.set_text("Too late to cancel")
        # self.text1.get_text() will return text found in entry
    # handlerb2

    def checkhandler(self,widget):  # handler for the checkboxes
        state = widget.get_active()
        if widget==self.check1 and state==True:
            addtext(self.textarea,"Ha ha ha ha ha ha ha ha ha ha ...\n")
        if widget==self.check2 and state==False:
            addtext(self.textarea,"I'm hurt.\n")
    # checkhandler

    def inputhandler(self,widget):
        s = self.text1.get_text()
        addtext(self.textarea,"'"+s+"' right back to you!\n")
        self.text1.set_text("")  # clear what user typed
    # inputhandler
        
    def menuhandler(self,widget,source):  # handler for menu
        if source=="save":
            response = "You've done nothing worth saving.\n"
        if source=="quit":
            response = "Why would you want to quit such a nice program?\n"
        if source == "info":
            response = "This is a gui program, can't you tell!\n"
        addtext(self.textarea,response)
    #menuhandler

# gui2 class


# create instances of gui2 class
#mygui = gui2(0,0)
yourgui = gui2(405,405)

# The following line starts the gtk "event loop"
gtk.main()

