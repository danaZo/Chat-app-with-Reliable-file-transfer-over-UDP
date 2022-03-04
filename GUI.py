"""
In this class we have the chat GUI from the client's side
Since only the clients will interact the server side does not have a GUI
"""

import socket
import threading
from tkinter import *
from tkinter import font
from tkinter import ttk

import client
from server import *
from client import *


#serverPort = 50000
#serverIP = socket.gethostname()
#ADDRESS = (serverPort, serverIP)

# Create a new client socket and connect to the server
#client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#client.connect(ADDRESS)


class GUI:

    def __init__(self):

        # Toplevel widget of Tk which represents mostly the main window of an application.
        # It has an associated Tcl interpreter.
        # Return a new Toplevel widget on screen SCREENNAME. A new Tcl interpreter will be created.
        self.Window = Tk()

        # Withdraw this widget from the screen such that it is
        # unmapped and forgotten by the window manager. Re-draw it with wm_deiconify
        self.Window.withdraw()

        # login window
        # Construct a toplevel widget with the parent MASTER.
        # Valid resource names: background, bd, bg, borderwidth, class, colormap, container, cursor, height,
        # highlightbackground, highlightcolor, highlightthickness, menu, relief, screen, takefocus, use, visual, width.
        self.login = Toplevel()

        # Set the title of this widget.
        self.login.title("Login")

        # Instruct the window manager whether this width can be resized in WIDTH or HEIGHT.
        # Both values are boolean values.
        self.login.resizable(width=False, height=False)

        # Configure resources of a widget.
        # The values for resources are specified as keyword arguments.
        # To get an overview about the allowed keyword arguments call the method keys
        self.login.configure(width=400, height=300)

        # Construct a label widget with the parent MASTER.
        # Label "Please Enter Your Name"
        self.pls = Label(self.login, text="Please Enter Your Name", justify=CENTER, font="Helvetica 14 bold")

        # Place a widget in the parent widget.
        self.pls.place(relheight=0.15, relx=0.2, rely=0.07)

        # The label "Name: "
        self.labelName = Label(self.login, text="Name: ", font="Helvetica 12")
        self.labelName.place(relheight=0.2, relx=0.1, rely=0.2)

        # Construct an entry widget with the parent MASTER.
        self.entryName = Entry(self.login, font="Helvetica 14")
        self.entryName.place(relwidth=0.4, relheight=0.12,  relx=0.35, rely=0.2)

        # Direct input focus to this widget.
        self.entryName.focus()

        # connect to server

        # Construct a Continue Button widget with the parent MASTER.
        self.go = Button(self.login, text="CONTINUE", font="Helvetica 14 bold", command=lambda: self.go_ahead(self.entryName.get()))
        self.go.place(relx=0.4, rely=0.55)

        # Call the mainloop of Tk.
        self.Window.mainloop()

    def go_ahead(self, name):
        # Destroy this and all descendants widgets.
        self.login.destroy()
        self.layout(name)

        # the thread to receive messages
        rcv = threading.Thread(target=client.getMessages())
        rcv.start()

    # The main layout of the chat
    def layout(self, name):
        self.name = name

        # to show chat window
        self.Window.deiconify()
        self.Window.title("ChatRoom")
        self.Window.resizable(width=False, height=False)
        self.Window.configure(width=470, height=550, bg="#17202A")

        self.labelHead = Label(self.Window, bg="#17202A", fg="#EAECEE", text=self.name, font="Helvetica 13 bold", pady=5)
        self.labelHead.place(relwidth=1)

        self.line = Label(self.Window, width=450, bg="#ABB2B9")
        self.line.place(relwidth=1, rely=0.07, relheight=0.012)

        self.textCons = Text(self.Window, width=20, height=2, bg="#17202A", fg="#EAECEE", font="Helvetica 14", padx=5, pady=5)
        self.textCons.place(relheight=0.745, relwidth=1, rely=0.08)

        self.labelBottom = Label(self.Window, bg="#ABB2B9", height=80)
        self.labelBottom.place(relwidth=1, rely=0.825)

        self.entryMsg = Entry(self.labelBottom, bg="#2C3E50", fg="#EAECEE", font="Helvetica 13")
        self.entryMsg.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.entryMsg.focus()

        # create a Send Button
        self.buttonMsg = Button(self.labelBottom, text="Send", font="Helvetica 10 bold", width=20, bg="#ABB2B9", command=lambda: self.sendButton(self.entryMsg.get()))
        self.buttonMsg.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)

        self.textCons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        # place the scroll bar into the gui window
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.config(command=self.textCons.yview)
        self.textCons.config(state=DISABLED)

    # function to basically start the thread for sending messages
    def sendButton(self, msg):
        self.textCons.config(state=DISABLED)
        self.msg = msg
        self.entryMsg.delete(0, END)











