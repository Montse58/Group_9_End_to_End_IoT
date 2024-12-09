import socket  # Import the socket module for network communication
from pymongo import MongoClient
from datetime import datetime, timedelta

# This is the connection to MongoDB and the collections:
client = MongoClient("mongodb+srv://montsealonso24:Montse24@cluster0.zzo67.mongodb.net/")
db = client['test']

device1_metadata_collection = db['device1_metadata']#metadata for IoT devices
device1_virtual_collection = db['device1_virtual']#virtual data from IoT devices

# This is the function for the binaryTree
class Node:
    def __init__(self, key, value=None):
        self.key = key#sorting key
        self.value = value  #associated data
        self.left = None #left child
        self.right = None

class BinaryTree:
    def __init__(self):
        self.root = None#initialize empty tree

    #insert a new node based on key for sorting
    def insert(self, key, value):
        if self.root is None:
            self.root = Node(key, value)
        else:
            self._insert(self.root, key, value)

    def _insert(self, current, key, value):
        if key < current.key:#navigate to the left subtree
            if current.left is None:
                current.left = Node(key, value)
            else:
                self._insert(current.left, key, value)
        else:  #navigate to the right subtree
            if current.right is None:
                current.right = Node(key, value)
            else:
                self._insert(current.right, key, value)

    #return nodes in sorted order
    def inorder(self):
        values = []
        self._inorder(self.root, values)
        return values

    #helper method - private
    def _inorder(self, current, values):
        if current is not None:
            self._inorder(current.left, values)
            values.append((current.key, current.value))
            self._inorder(current.right, values)

    #find the node with the max key
    def find_max(self):
        current = self.root
        while current and current.right is not None:
            current = current.right
        return current

# THIS IS THE FIRST QUERY FUNCTION:
def calc_moisture():
    fridge_data = device1_metadata_collection.find_one({"customAttributes.name": "Fridge"})
    if fridge_data:
        fridge_uid = fridge_data["assetUid"]#unique ID for fridge
    else:
        return "No data found"

    #calculates a timestamp representing 3 hours before the current time
    three_hours = datetime.now() - timedelta(hours=3)

    query = {
        "topic": "brokertodb",
        "payload.parent_asset_uid": fridge_uid,
        "time": {"$gte": three_hours}
    }
    #query database for recent data
    new_data = device1_virtual_collection.find(query)

    #sort moisture data using binary tree
    moisture_tree = BinaryTree()

    for record in new_data:
        #extract moisture values 
        moisture = record['payload'].get('Moisture Meter - Moisture Meter-Fridge')
        if moisture:
            moisture_tree.insert(float(moisture), None)

    #retrieve sorted moisture values
    moisture_values = [val[0] for val in moisture_tree.inorder()]
    if moisture_values:
        avg_moisture = sum(moisture_values) / len(moisture_values)#compute average
        response_units = f"{avg_moisture:.2f}% RH" #format results in RH%
        print(f"Average Moisture in the last 3 hours: {response_units}")
        return response_units
         
    else:
        print("No moisture data available in the last 3 hours.")
        return None

# THIS IS THE SECOND QUERY FUNCTION:
def avg_consumption():

    #fetches dishwasher metadata
    dishwasher_data = device1_metadata_collection.find_one({"customAttributes.name": "Smart Dishwasher"})
    if dishwasher_data:
        #unique ID for dishwasher
        dishwasher_uid = dishwasher_data["assetUid"]
    else:
        print("No dishwasher data found.")
        return None

    query = {
        "topic": "brokertodb",
        "payload.parent_asset_uid": dishwasher_uid
    }
    #query database for water consumption data
    new_data = device1_virtual_collection.find(query)

    #sort water data using binary tree
    water_consumption_tree = BinaryTree()
    for record in new_data:
        timestamp = int(record['payload']['timestamp'])#extracts timestamps
        #extract water consumption values
        water_consumption = record['payload'].get('Water Consumption Sensor')
        if water_consumption:
            water_consumption_tree.insert(timestamp, float(water_consumption))

    #retrieve sorted data
    sorted_data = water_consumption_tree.inorder()
    cycle_data = []
    current_cycle = []
    previous_timestamp = None

    for timestamp, water_consumption in sorted_data:
        if previous_timestamp is not None and (timestamp - previous_timestamp > 3600):
            cycle_data.append(current_cycle)#save current cycle
            current_cycle = []
        current_cycle.append(water_consumption)#add data to current cycle
        previous_timestamp = timestamp

    if current_cycle:
        cycle_data.append(current_cycle)#append last cycle

    #calculates averages for each cycle
    cycle_averages = [sum(cycle) / len(cycle) for cycle in cycle_data if cycle]
    if cycle_averages:
        overall_average = sum(cycle_averages) / len(cycle_averages)
        response_units = f"{overall_average:.2f} gallons"#format result in gallons
        print(f"Average Water Consumption per Cycle: {response_units}")
        return response_units
         
    else:
        print("No water consumption data available for cycles.")
        return None

# THIS IS THE THIRD QUERY FUNCTION:
def most_electricity():
    #metadata for fridge 1
    fridge1_data = device1_metadata_collection.find_one({"customAttributes.name": "Fridge"})
    #metadata for fridge 2
    fridge2_data = device1_metadata_collection.find_one({"customAttributes.name": "Second Fridge"})
    #metadata for dishwasher
    dishwasher_data = device1_metadata_collection.find_one({"customAttributes.name": "Smart Dishwasher"})

    if not fridge1_data or not fridge2_data or not dishwasher_data:
        return "One or more devices have missing metadata."

    devices = {
        "Fridge 1": fridge1_data["assetUid"],
        "Fridge 2": fridge2_data["assetUid"],
        "Dishwasher": dishwasher_data["assetUid"]
    }

    #sort electricity data using binary tree
    consumption_tree = BinaryTree()
    for device_name, uid in devices.items():
        query = {
            "topic": "brokertodb",
            "payload.parent_asset_uid": uid
        }
        #query database for electricity data
        records = device1_virtual_collection.find(query)

        total_electricity = sum(
            float(record['payload'].get("Ammeter(Dishwasher)" if device_name == "Dishwasher" else "Ammeter(Fridge)"))
            for record in records if record['payload'].get("Ammeter(Dishwasher)" if device_name == "Dishwasher" else "Ammeter(Fridge)")
        )
        #insert total consumption into tree
        consumption_tree.insert(total_electricity, device_name)

    #find device with max consumption
    max_node = consumption_tree.find_max()
    if max_node:
        response_units = f"{max_node.value} with {max_node.key:.2f} kWh"#format result
        print(f"The device with the most electricity consumption is {response_units}")
        return response_units
        
    else:
        return None, None

# THIS IS THE SERVER FUNCTION:
def TCP_server():
    try:
        serverIP = input("Enter the IP address of the server: >")#server IP input
        serverPort = int(input("Enter a port number for the server: >"))#server port input

        myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#create TCP socket
        myTCPSocket.bind(('0.0.0.0', serverPort))#bind to all interfaces
        myTCPSocket.listen(5)#listen for incoming connections
        print(f"Server is listening to {serverIP}:{serverPort}")

        incomingSocket, incomingAddress = myTCPSocket.accept()#accept a connection
        print(f"Connection {incomingAddress} was accepted.")

        while True:
            myData = str(incomingSocket.recv(250).decode())#receive data from client
            if not myData:
                print(f"Error. {incomingAddress} has disconnected.")
                break

            if int(myData) == 1:#query for moisture data
                print(f"Received message from client: >{myData}")
                moisture_data = calc_moisture()
                incomingSocket.send(bytearray(f"Moisture Data: {moisture_data}", encoding='utf-8'))

            elif int(myData) == 2:#query for water consumption data
                print(f"Received message from client: >{myData}")
                consumption_data = avg_consumption()
                incomingSocket.send(bytearray(f"Consumption Data: {consumption_data}", encoding='utf-8'))

            elif int(myData) == 3:#query for electricity consumtion
                print(f"Received message from client: >{myData}")
                device_name = most_electricity()
                incomingSocket.send(bytearray(f"Device: {device_name}", encoding='utf-8'))

            else:
                print(f"Received message from client: >{myData} - INVALID INPUT")#handle invalid input
                incomingSocket.send(bytearray("Invalid input. Please try again.", encoding='utf-8'))

    except Exception as e:
        print(f"Error: >{e}")

    finally:
        incomingSocket.close()

if __name__ == "__main__":
    TCP_server()#start server
