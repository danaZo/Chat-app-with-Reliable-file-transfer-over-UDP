import signal
import socket
import sys,os
import threading
from threading import Thread,main_thread
import socket
from tkinter import *
from tkinter import font
from tkinter import ttk

is_windows = sys.platform.startswith('win')
serverPort = 50000
serverIp = socket.gethostname()
menu = "WELCOME!\nAt the left side box, you can type the following commands:\n" \
       "all : To send a public message\n" \
       "member's name : To send a private message to specific member (write the member's name)\n" \
       "quit : To quit the chat\n" \
       "online : To get a list of online members names"
FORMAT = "utf-8"
clientSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)





"""
In this class we have the chat GUI from the client's side
Since only the clients will interact the server side does not have a GUI
"""
class GUI:

    def __init__(self):

        self.Window = Tk()
        self.Window.withdraw()

        self.login = Toplevel()
        self.login.title("Login")
        self.login.resizable(width=False, height=False)
        self.login.configure(width=400, height=300)

        self.pls = Label(self.login, text="Please Enter Your Name", justify=CENTER, font="Helvetica 14 bold")
        self.pls.place(relheight=0.15, relx=0.2, rely=0.07)

        # The label "Name: "
        self.labelName = Label(self.login, text="Name: ", font="Helvetica 12")
        self.labelName.place(relheight=0.2, relx=0.1, rely=0.2)

        self.entryName = Entry(self.login, font="Helvetica 14")
        self.entryName.place(relwidth=0.4, relheight=0.12,  relx=0.35, rely=0.2)
        self.entryName.focus()

        # Construct a Continue Button widget with the parent MASTER.
        self.go = Button(self.login, text="CONTINUE", font="Helvetica 14 bold",
                         command=lambda: self.go_ahead(self.entryName.get()))
        self.go.place(relx=0.4, rely=0.55)

        # Call the mainloop of Tk.
        self.Window.mainloop()

    def connectToServer(self, soc: socket.socket):
        # connecting to the server

        try:  # set connection and user name
            response = b''
            soc.connect((serverIp, serverPort))
            while response.decode() != "NAME_OK":
                print(response.decode())
                name = self.name
                soc.send(name.encode(FORMAT))
                response = soc.recv(128)


        except Exception as e:
            print(f"Connection failed due to: {e}")
            quit()

    def go_ahead(self, name):
        # Destroy this and all descendants widgets.
        self.login.destroy()
        self.layout(name)
        # initialize a daemon thread to listen for incoming messages
        self.connectToServer(clientSoc)
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END,"Connected successfully" + "\n\n")
        self.textCons.insert(END, menu + "\n\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
        Thread(target=self.getMessages, daemon=True, args=(clientSoc,)).start()

# The main layout of the chat
    def layout(self, name):
        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("ChatRoom")
        self.Window.resizable(width=True, height=True)
        self.Window.configure(width=900, height=550, bg="#17202A")

        self.labelHead = Label(self.Window, bg="#17202A", fg="#EAECEE", text=self.name, font="Helvetica 13 bold", pady=5)
        self.labelHead.place(relwidth=1)

        self.line = Label(self.Window, width=450, bg="#ABB2B9")
        self.line.place(relwidth=1, rely=0.07, relheight=0.012)

        self.textCons = Text(self.Window, width=20, height=2, bg="#17202A", fg="#EAECEE", font="Helvetica 14", padx=5, pady=5)
        self.textCons.place(relheight=0.745, relwidth=1, rely=0.08)

        self.labelBottom = Label(self.Window, bg="#ABB2B9", height=80)
        self.labelBottom.place(relwidth=1, rely=0.925)

        self.labelDown = Label(self.Window, bg="#17202A", fg="#EAECEE", text="Type: all/online/\nmember's name/quit",
                               font="Helvetica 13 bold", pady=6)
        self.labelDown.place(relwidth=0.4 ,rely=0.825 , relx=-0.05)

        self.labelMsg = Label(self.Window, bg="#17202A", fg="#EAECEE", text="Type message (blank to online/quit commands)",
                               font="Helvetica 13 bold", pady=6)
        self.labelMsg.place(relwidth=0.6, rely=0.85, relx=0.25)

        self.entryType = Entry(self.labelBottom, bg="#2C3E50", fg="#EAECEE", font="Helvetica 13")
        self.entryType.place(relwidth=0.26, relheight=0.03, rely=0.0, relx=0.011)
        self.entryType.focus()

        self.entryMsg = Entry(self.labelBottom, bg="#2C3E50", fg="#EAECEE", font="Helvetica 13")
        self.entryMsg.place(relwidth=0.74, relheight=0.03, rely=0.0, relx=0.3)
        self.entryMsg.focus()

        # create a Send Button
        self.buttonMsg = Button(self.labelBottom, text="Send", font="Helvetica 10 bold", width=20, bg="#ABB2B9",
                                command=lambda: self.sendButton(self.entryType.get()+':'+self.entryMsg.get()))
        self.buttonMsg.place(relx=0.77, rely=0.0, relheight=0.03, relwidth=0.22)

        self.textCons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        # place the scroll bar into the gui window
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.config(command=self.textCons.yview)
        self.textCons.config(state=DISABLED)

    # function to basically start sending messages
    def sendButton(self, msg):
        self.textCons.config(state=DISABLED)
        self.msg = msg
        self.entryMsg.delete(0, END)
        self.entryType.delete(0, END)
        self.sendMessage(clientSoc)


    def getMessages(self, soc: socket.socket):
        while True:
            try:
                message = soc.recv(2048).decode(FORMAT)
                if len(message) == 0:
                    self.textCons.config(state=NORMAL)
                    self.textCons.insert(END, "msg len is 0 ~ check why it happened" + "\n\n")
                    self.textCons.config(state=DISABLED)
                    self.textCons.see(END)
                    print("msg len is 0 ~ check why it happened")
                    sys.exit()
                # if the messages from the server is NAME send the client's name
                if message == 'NAME':
                    soc.send(self.name.encode(FORMAT))

                # insert messages to text box
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, message + "\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)
                print(message)
            except Exception as e:
                # an error will be printed on the command line or console if there's an error
                print(f"socket error{e}")
                soc.close()
                sys.exit()

    def sendMessage(self, soc: socket.socket):
        print(menu)
        while True:
            message = self.msg

            if message == "quit:":
                return

            try:
                soc.send(message.encode(FORMAT))
                break
            except Exception as e:
                print(f"Socket error {e}")
                sys.exit()


if __name__ == '__main__':
    g = GUI()

    #print("Connected successfully")

    # initialize a daemon thread to listen for incoming messages
    #Thread(target=getMessages, daemon=True, args=(clientSoc,)).start()

    # send messages when user want to
    #sendMessage(clientSoc)


