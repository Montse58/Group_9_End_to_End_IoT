import socket #import the socket module for network communication
from pymongo import MongoClient




client = MongoClient("mongodb+srv://montsealonso24:Montse24@cluster0.zzo67.mongodb.net/")
db = client['test']

device1_metadata_collection = db['device1_metadate']
device1_virutal_colection = db['device1_virtual']

def TCP_server():
    try:
        #get users server IP and port
        serverIP = input("Enter the IP address of the server: >")
        serverPort = int(input("Enter a port number for the server: >"))
        
        #creates a TCP socket
        myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        #binds socket to all interfaces on the specified port via 0.0.0.0
        myTCPSocket.bind(('0.0.0.0', serverPort)) 
        
        myTCPSocket.listen(5)#listen for incoming connections for a max of 5 queued connections
        print(f"Server is listening to {serverIP}:{serverPort}")
        
        #accept a new connection from client and confirm that the server is listening
        incomingSocket, incomingAddress = myTCPSocket.accept()
        print(f"Connection {incomingAddress} was accepted.")

        while True:
            #recieve data from client and decode it
            myData = str(incomingSocket.recv(250).decode()) #Recieve data from client

            #check if recieved data is empty and client disconnected
            if not myData:
                print(f"Error. {incomingAddress} has disconnected.")
                break

            #We are going to check the User's input from the client here:
            if int(myData) == 1:
                print(f"Recieved message from client: >{myData}")

            if int(myData) ==2:
                print(f"Recieved message from client: >{myData}")

            if int(myData) == 3:
                print(f"Recieved message from client: >{myData}")

            if int(myData) == 4:
                print(f"Recieved message from client: >{myData}")

            else:
                print(f"Recieved message from client: >{myData}"+"WRONGGG")


            

            someData = myData.upper() #converts the revieved data to uppercase
            incomingSocket.send(bytearray(str(someData), encoding='utf-8')) #Respond to client with data
            print(f"Message sent to client      : >{someData}")

    #handles exceptions
    except Exception as e:
        print(f"Error: >{e}")

    # closes the socket
    finally:
        incomingSocket.close()

if __name__ == "__main__":
    TCP_server()



#Here will be the first function 