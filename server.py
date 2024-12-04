import socket  # Import the socket module for network communication
from pymongo import MongoClient
from datetime import datetime, timedelta

class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None

    # Insert a key into the binary tree
    def insert(self, key):
        if self.root is None:
            self.root = Node(key)
        else:
            self._insert(self.root, key)

    def _insert(self, current, key):
        if key < current.key:
            if current.left is None:
                current.left = Node(key)
            else:
                self._insert(current.left, key)
        else:  # Allow duplicates on the right for simplicity
            if current.right is None:
                current.right = Node(key)
            else:
                self._insert(current.right, key)

    # Inorder traversal to get sorted moisture values
    def inorder(self):
        values = []
        self._inorder(self.root, values)
        return values

    def _inorder(self, current, values):
        if current is not None:
            self._inorder(current.left, values)
            values.append(current.key)
            self._inorder(current.right, values)

client = MongoClient("mongodb+srv://montsealonso24:Montse24@cluster0.zzo67.mongodb.net/")
db = client['test']

device1_metadata_collection = db['device1_metadata']
device1_virtual_collection = db['device1_virtual']

def calc_moisture():
    fridge_data = device1_metadata_collection.find_one({"customAttributes.name": "Fridge"})

    if fridge_data:
        fridge_uid = fridge_data["assetUid"]  # Fixed dictionary access
    else:
        return "No data found"

    three_hours = datetime.now() - timedelta(hours=3)

    query = {
        "topic": "brokertodb",
        "payload.parent_asset_uid": fridge_uid,
        "time": {"$gte": three_hours}
    }

    new_data = device1_virtual_collection.find(query)

    # Initialize binary tree to store moisture values
    moisture_tree = BinaryTree()

    for record in new_data:
        moisture = record['payload'].get('Moisture Meter - Moisture Meter-Fridge')

        if moisture:
            # Convert to float and insert into the tree
            moisture_tree.insert(float(moisture))

    # Retrieve all moisture values in sorted order
    moisture_values = moisture_tree.inorder()

    # Calculate the average moisture if there are values
    if moisture_values:
        avg_moisture = sum(moisture_values) / len(moisture_values)
        print(f"Average Moisture in the last 3 hours: {avg_moisture}")
        return avg_moisture
    else:
        print("No moisture data available in the last 3 hours.")
        return None

def TCP_server():
    try:
        # Get users server IP and port
        serverIP = input("Enter the IP address of the server: >")
        serverPort = int(input("Enter a port number for the server: >"))
        
        # Creates a TCP socket
        myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Binds socket to all interfaces on the specified port via 0.0.0.0
        myTCPSocket.bind(('0.0.0.0', serverPort)) 
        
        myTCPSocket.listen(5)  # Listen for incoming connections for a max of 5 queued connections
        print(f"Server is listening to {serverIP}:{serverPort}")
        
        # Accept a new connection from client and confirm that the server is listening
        incomingSocket, incomingAddress = myTCPSocket.accept()
        print(f"Connection {incomingAddress} was accepted.")

        while True:
            # Receive data from client and decode it
            myData = str(incomingSocket.recv(250).decode())  # Receive data from client

            # Check if received data is empty and client disconnected
            if not myData:
                print(f"Error. {incomingAddress} has disconnected.")
                break

            # Process the User's input from the client here:
            if int(myData) == 1:
                print(f"Received message from client: >{myData}")
                moisture_data = calc_moisture()
                incomingSocket.send(bytearray(f"Moisture Data: {moisture_data}", encoding='utf-8'))

            elif int(myData) == 2:
                print(f"Received message from client: >{myData}")

            elif int(myData) == 3:
                print(f"Received message from client: >{myData}")

            else:
                print(f"Received message from client: >{myData} - INVALID INPUT")
                incomingSocket.send(bytearray("Invalid input. Please try again.", encoding='utf-8'))

    except Exception as e:
        print(f"Error: >{e}")

    # Closes the socket
    finally:
        incomingSocket.close()

if __name__ == "__main__":
    TCP_server()
