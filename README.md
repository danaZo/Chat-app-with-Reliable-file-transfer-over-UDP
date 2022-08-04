# Chat-app-with-Reliable-file-transfer-over-UDP
## Networking Final Project
### Fast RUDP - safe file transfer over UDP
#### Fast vs TCP
The Tcp protocol take care for many things behind the scenes, providing a reliable data transfer between two hosts.
However, our “Fast” protocol is based on UDP, so it has to provide those functions Itself in the application level.

#### RDT Element
Here are the staple functions that our protocol should provide for it to be called RDT: 
-	Detection and correction of corrupted packets.
-	Loss recovery –make sure all the packets reaches the destination.
-	Latency –make sure retransmitted or delayed packets won’t create a mess.
-	In order delivery.
-	Congestion control. 

In this section we will review the solutions we implemented to tackle these problems.

#### Packet Loss Recovery:
Arguably the most important attribute of any RDT protocol. 
In the early days of the internet, networks tended to be unreliable, and packets got lost frequently. 
Even today lossy networks or full buffers can cause a packet to get thrown or lost.

One of the major drawbacks of Tcp is the big overhead it generates to ensure arrival of packets 
(all the ACKs make the network crowded and slow down things even more).

Our aim is to reduce the number of unnecessary packets to minimum, our protocol follows these steps:

- Sender side:
  -	open a connection between two hosts. 
  -	The sender parses the file and split it to 500 bytes packets – this step is done to avoid IP fragmentation.
    If we send a file that can’t fit into lower protocols it will be split to smaller packets,
    and since we don’t know the exact way it works, if one of these little packets get lost it will be hard to
    determine the exact data that was lost. Sending 500 bytes packets ensures that fragmentation won’t be a problem.
  -	Sending the number of packets to the client – the client allocates an array with size equal to the number of incoming
    packets, that way it can know if something missing.
  -	The sender appends Sequence number and CRC remainder to the packets (see diagram below) and send all the packets to
    the client. 
  -	After all the packets were sent, he sends ACK_REQ for the client, requesting to know which packets received correctly
    the response arrives in one message for all the packets – hence saves lots of redundant ACK’S that would be sent in
    other protocols. The server retransmit all the packets that got lost.
    
- Receiver side:
  -	The receiver gets the number of packets from the server and create an empty array with that size
  -	When getting an uncorrupted packet, the receiver checks if it has it already, if not he buffers it in the array and
    mark the packet number as ACK’ed.
  -	After getting an ACK_REQ, the Receiver sends a list of all the ack’ed packets to the sender.
  -	When the buffer array is full the receiver ends the connection and write the binary array to file with the same name
    as the requested file

The FAST-UDP packet header:
<p align="center">
<img width="675" alt="image" src="https://user-images.githubusercontent.com/93203695/182905524-215ddb29-e36e-41ce-b01b-4c7797140a90.png">
</a>
</p>
- seqNo – is a value between 0 to PACKETS_NUM – 1

#### Error Detection:
The Udp provide an error detection mechanism – checksum.
However, he can miss lot of errors, so we chose a more robust error detection algorithm – 
Cycle Redundancy Check – CRC we won’t explain how it works since it was taught on class.
Before sending a packet, we compute its remainder and append it to the packet.
When receiving a packet, the Receiver compute it again and compare the two values
If they don’t match, the packet discarded, and will be asked to be retransmitted again later.

#### Latency:
Lossy or slow Networks can cause a packet to be received more then once, in order to solve that,
we check the seqNo of each incoming packet, if we already have the packet buffered, we discard it.
In case that we got message that doesn’t belong to the current state of the connection we discard it as well
(example: open connection request, while it’s already open).

#### In Order Delivery:
This one is simple, since our protocol aim is file transfer, we just wait for all the data to arrive while buffering it
in the correct order(determined by the packet seq numbers) in our array, when we got all of it, we just write it from the
start to the end of the array.

#### Congestion Control:
Our protocol is already doing a good job, by reducing the number packets the moving around.
Regardless, we should control adjust our sending speed to the environment and to the Receiver.

For this mission we employed couple of well-known elements.
We created a sending window with a size of 10 bytes – meaning, we send 10 bytes and wait for the cumulative
acknowledgement message.
After creating the window we use the slow-start algorithm to enlarge it until we encounter the first congestion control
event or we reached the maximum window size (file size in our case)
In case of congestion control event, the window sized decreased, and it goes into Fast recovery mode

### State Diagram:
<p align="center"> 
<img src="https://user-images.githubusercontent.com/93203695/182906297-029c9310-17e0-4b3d-9365-0b6e68f603c2.png" >
</a>
</p>

### Usage
#### Graphical User Interface
- Step 1
  -	Open the terminal and run the server:
  
  <p align="center"> 
  <img src="https://user-images.githubusercontent.com/93203695/182894531-1524866d-9fb7-454b-a6a3-0359c8b66890.png" >
  </a>
  </p>
  
  - Choose the percentage of packet loss you would like it to be, 0 for normal state:
  
  <p align="center"> 
  <img src="https://user-images.githubusercontent.com/93203695/182894599-95a3e155-e70d-4d6b-a194-033fbd854807.png">
  </a>
  </p>
  
  - Choose the percentage of packet corruption you would like, 0 for normal state:
  
  <p align="center"> 
  <img src="https://user-images.githubusercontent.com/93203695/182894658-eb69d1fa-160d-43a8-819c-b91e771d8eb7.png">
  </a>
  </p>
  
  - If the message "Server is up and listening." Shows up in your terminal than you can move forward to the next step.

- Step 2
  - Open new terminal and run the client:
  
  <p align="center"> 
  <img src="https://user-images.githubusercontent.com/93203695/182894973-8e25cf2f-6b72-466e-8dd5-f4ee87ead488.png">
  </a>
  </p>

- Step 3
  - Now a login window will appear, enter your name in the box, and press continue.

- Step 4
  - Now you entered the chat window.
  - The commands entry box is the smaller one at the left side, and the bigger one is where you type your message, of the file name you wish to download:
  
  <p align="center"> 
  <img src="https://user-images.githubusercontent.com/93203695/182895389-99b33978-b3f8-4a38-9b63-a5e171bb67bf.png">
  </a>
  </p>
  
  -	If you want to see who's online, write online in the commands box, and nothing in the message box.
    Press the button send and the list of online members will appear in your chat window:
    
    <p align="center">
    <img src="https://user-images.githubusercontent.com/93203695/182895479-585eaa6c-d07d-4225-b468-ad13f0b9d2ff.png">
    </a>
    </p>
     
    <p align="center">
    <img src="https://user-images.githubusercontent.com/93203695/182895515-72e494a2-0a1e-4c06-8d01-f1592f557649.png">
    </a>
    </p>
  
  - If you want to send private message, write name of online member in the commands box, and the message in the message box. Press the button send and the message will be sent to this member:
    
    <p align="center">
    <img src="https://user-images.githubusercontent.com/93203695/182895600-f382a9e5-8670-4caf-ab4d-d5065d87f2b3.png">
    </a>
    </p>
    
    <p align="center">
    <img src="https://user-images.githubusercontent.com/93203695/182895628-59dc3b11-43f4-48a6-b230-179680cd5aee.png">
    </a>
    </p>
  
  -	If you want to send massage to everyone who's online, write all in the commands box, and the message in the message box. Press the button send and the message will be sent to all the members:
    
    <p align="center">
    <img src="https://user-images.githubusercontent.com/93203695/182895724-f86da22d-6a82-4692-a9e0-0e4dca2c4169.png">
    </a>
    </p>
    
    <p align="center">
    <img src="https://user-images.githubusercontent.com/93203695/182895769-910455e7-860e-4d7d-a560-533cf2659465.png">
    </a>
    </p>
    
    <p align="center">
    <img src="https://user-images.githubusercontent.com/93203695/182895805-13926492-4fb6-41b3-94aa-b35f034da032.png">
    </a>
    </p>
  
  -	If you want to see which files are available for download, write getfiles in the commands box, and nothing in the message box. Press the button send and the list of files will appear at your chat window:
    
    <p align="center">
    <img src="https://user-images.githubusercontent.com/93203695/182895867-ef6116cc-ecb9-44a9-9a6b-caf5cd8da1fb.png">
    </a>
    </p>
    
    <p align="center">
    <img src="https://user-images.githubusercontent.com/93203695/182895904-780b9485-5307-4193-a428-c70e6920b761.png">
    </a>
    </p>
  
  -	If you want to download a file, write file in the commands box, and the name of the file in the message box. Press the button send and the file will start downloading. At the middle of the downloading progress a pop-up message will appear and it will ask you if you wish to continue downloading:
    
    <p align="center">
    <img src="https://user-images.githubusercontent.com/93203695/182895979-ae80dee7-cbc2-410f-bfad-919e2d96f62c.png">
    </a>
    </p>
    
    <p align="center">
    <img src="https://user-images.githubusercontent.com/93203695/182896015-6486fc6d-7363-4877-bd0f-b9670facaea3.png">
    </a>
    </p>
    
    <p align="center">
    <img src="https://user-images.githubusercontent.com/93203695/182896047-0ee8cbed-01b7-44ae-bbfc-13ec27b82332.png">
    </a>
    </p>
  
  -	If you want to exit the chat you can press the red X button at the upper right side of the window.
  
### Wireshark
<p align="center">
<img src="https://user-images.githubusercontent.com/93203695/182902620-fff70e94-b493-4ffe-a06b-0654b7669dd2.png">
</a>
</p>

- On the picture above, 1,2 represents that the server sends the name of the file.
- All the packets below it are the sending process of the file (the file split to packets). 

<p align="center">
<img src="https://user-images.githubusercontent.com/93203695/182903353-cab3f44a-857c-409f-9c66-9124ffbb14f9.png">
</a>
</p>

- On the picture above, 3 represents req_Ack, server asks the client to send how many packets it received , 4 is the client's response – which packets it received.


