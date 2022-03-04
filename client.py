import pickle
import signal
import socket
import sys,os
import time
from threading import Thread,main_thread
import socket
from tkinter import *
from tkinter import font
from tkinter import ttk
import tkinter.messagebox
import tkinter as tk
from errRecieve import decodeData

ACK_REQ = 10000000
STOP_REQ = 20000000
fSizeInPkts: int
fname: str

is_windows = sys.platform.startswith('win')
serverPort = 50000
#serverIp = '10.100.102.12'
serverIp = socket.gethostname()


menu = "WELCOME!\n\nAt the left side box, you can type the following commands:\n" \
       "all : To send a public message\n" \
       "member's name : To send a private message to specific member (write the member's name)\n" \
       "quit : To quit the chat\n" \
       "online : To get a list of online members names\n" \
       "getfiles : To get the list of files that able to be downloaded\n" \
       "file : To download a file from the existing files"

FORMAT = "utf-8"

clientSoc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fileSoc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


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

    def connectToServer(self, soc: socket.socket, udp: socket.socket):
        # connecting to the server

        try:  # set connection and user name
            response = b''
            soc.connect((serverIp, serverPort))
            udp.bind((socket.gethostname(), soc.getsockname()[1]))
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
        self.connectToServer(clientSoc, fileSoc)
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, "Connected successfully" + "\n\n")
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
        self.Window.configure(width=900, height=730, bg='white')

        # the label with the client's name
        self.labelHead = Label(self.Window, bg="#17202A", fg="#EAECEE", text=self.name, font="Helvetica 13 bold", pady=5)
        self.labelHead.place(relwidth=1)

        self.line = Label(self.Window, width=450, bg="#ABB2B9")
        self.line.place(relwidth=1, rely=0.07, relheight=0.012)

        # the place where text appears
        self.textCons = Text(self.Window, width=20, height=2, bg="white", fg="black", font="Helvetica 14", padx=5, pady=5)
        self.textCons.place(relheight=0.745, relwidth=1, rely=0.08)

        self.labelBottom = Label(self.Window, bg="#ABB2B9", height=80)
        self.labelBottom.place(relwidth=1, rely=0.925)

        # the text above the smaller box
        self.labelDown = Label(self.Window, bg="pink", fg="black",
                               text="Commands: all/online/\nmember's name/quit/\ngetfiles/file",
                               font="Helvetica 10 bold", pady=6)
        self.labelDown.place(relwidth=0.4 ,rely=0.825 , relx=-0.05)

        # the text above the bigger box
        self.labelMsg = Label(self.Window, bg="#17202A", fg="#EAECEE",
                              text="Type message/file name\n"
                                   "(blank to online/quit/getfiles commands)",
                               font="Helvetica 13 bold", pady=6)
        self.labelMsg.place(relwidth=0.6, rely=0.85, relx=0.25)

        # the small box
        self.entryType = Entry(self.labelBottom, bg="#2C3E50", fg="#EAECEE", font="Helvetica 13")
        self.entryType.place(relwidth=0.26, relheight=0.03, rely=0.0, relx=0.011)
        self.entryType.focus()

        # the big box
        self.entryMsg = Entry(self.labelBottom, bg="#2C3E50", fg="#EAECEE", font="Helvetica 13")
        self.entryMsg.place(relwidth=0.5, relheight=0.03, rely=0.0, relx=0.3)
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
        self.sendMessage(clientSoc, fileSoc)

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

    def sendMessage(self, soc: socket.socket, fileSoc: socket.socket ):
        print(menu)
        while True:
            message = self.msg

            if message == "quit:":
                return

            if message[:4] == 'file':
                Thread(target=self.getFile, daemon=True, args=(fileSoc,)).start()

            try:
                soc.send(message.encode(FORMAT))
                break
            except Exception as e:
                print(f"Socket error {e}")
                sys.exit()

    def getFile(self, fileSoc: socket.socket):
        # get file name and the number of incoming packets
        # file names to text box
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, "Incoming file" + "\n\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
        print(fileSoc)
        print("Incoming file")

        filename, _ = fileSoc.recvfrom(128)
        # print to chat the file name
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, str(filename) + "\n\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
        print(filename)

        packetsNum, _ = fileSoc.recvfrom(128)
        packetsNum = int(packetsNum.decode())

        # print to chat the number of packets
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, "size in packets: " + str(packetsNum) + "\n\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
        print("size in packets: " + str(packetsNum))

        packets = [b''] * packetsNum  # list to save the received packets

        fileSoc.settimeout(1)  # close thread and socket if no data sent for 5 seconds
        f = open(filename.decode(), 'wb')
        Acks = []
        try:
            while True:

                # get packets from server
                pac, addr = fileSoc.recvfrom(2048)
                # check if the pac is part of the file or it is an ack request
                seqNo = int.from_bytes(pac[:4], byteorder='big')
                if seqNo == ACK_REQ:
                    # we send the ACK list to the server
                    fileSoc.sendto(pickle.dumps(Acks), addr)
                    continue

                if seqNo == STOP_REQ:
                    # create pop up window asking the user to resume the download
                    res = tkinter.messagebox.askyesno('file download', 'Would you like to continue downloading?')
                    print("hi")
                    if res is True:
                        fileSoc.sendto('yes'.encode(), addr)
                        print("sent")
                    if str.lower(res) == 'yes':
                        continue
                    else:
                        return
                # check if the packet was corrupted
                # if remainder = 0, the packet is ok
                # otherwise it's corrupted
                # remainder = decodeData(pac, '1001')
                # if remainder != 0:
                #     print(f"corrupted packet {seqNo}")
                #     continue
                # check if we got the package already

                if packets[seqNo] == b'':  # packet haven't buffered before - solves problem of duplicate packets
                    packets[seqNo] = pac[4:]

                    self.textCons.config(state=NORMAL)
                    self.textCons.insert(END, str(seqNo) + "\n\n")
                    self.textCons.config(state=DISABLED)
                    self.textCons.see(END)
                    print(seqNo)
                    Acks.append(seqNo)  # mark that we got this package

                if b'' not in packets:
                    self.textCons.config(state=NORMAL)
                    self.textCons.insert(END, "all packets received successfully" + "\n\n")
                    self.textCons.config(state=DISABLED)
                    self.textCons.see(END)
                    print("all packets received successfully")
                    # read the last ACK_REQ to clear the buffer
                    d, _ = fileSoc.recvfrom(128)
                    self.textCons.config(state=NORMAL)
                    self.textCons.insert(END, f"leftovers {d}" + "\n\n")
                    self.textCons.config(state=DISABLED)
                    self.textCons.see(END)
                    print(f"leftovers {d}")
                    break

            for pac in packets:
                f.write(pac)
            f.close()
            # flush remaining data
            fileSoc.settimeout(0.1)
        except socket.error:
            f.close()


if __name__ == '__main__':
    g = GUI()



