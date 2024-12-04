import socket  # Import the socket module for network communication
from pymongo import MongoClient
from datetime import datetime, timedelta

#This is the connection to mongodb and the collections:
client = MongoClient("mongodb+srv://montsealonso24:Montse24@cluster0.zzo67.mongodb.net/")
db = client['test']

device1_metadata_collection = db['device1_metadata']
device1_virtual_collection = db['device1_virtual']

#This is the function for the binaryTree
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



#THIS IS THE FIRST QUERY FUNCTION:
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

#This is the second query:
def avg_consumption():
    # Fetch the dishwasher metadata
    dishwasher_data = device1_metadata_collection.find_one({"customAttributes.name": "Smart Dishwasher"})

    if dishwasher_data:
        dishwasher_uid = dishwasher_data["assetUid"]  # Extract unique identifier
    else:
        print("No dishwasher data found.")
        return None

    # Query to fetch all water consumption data for the dishwasher
    query = {
        "topic": "brokertodb",
        "payload.parent_asset_uid": dishwasher_uid
    }

    # Fetch data from MongoDB
    new_data = device1_virtual_collection.find(query)

    # Group water consumption data into cycles based on timestamps
    cycle_data = []
    previous_timestamp = None
    current_cycle = []

    for record in new_data:
        timestamp = int(record['payload']['timestamp'])  # Convert timestamp to integer
        water_consumption = record['payload'].get('Water Consumption Sensor')

        if water_consumption:
            water_consumption = float(water_consumption)

            # Determine if a new cycle has started (e.g., a large gap in timestamps)
            if previous_timestamp is not None and (timestamp - previous_timestamp > 3600):  # Assuming 1 hour separates cycles
                # Store the current cycle and start a new one
                cycle_data.append(current_cycle)
                current_cycle = []

            # Add water consumption to the current cycle
            current_cycle.append(water_consumption)
            previous_timestamp = timestamp

    # Add the last cycle if it has data
    if current_cycle:
        cycle_data.append(current_cycle)

    # Calculate the average water consumption per cycle
    cycle_averages = [sum(cycle) / len(cycle) for cycle in cycle_data if cycle]

    # Calculate the overall average across all cycles
    if cycle_averages:
        overall_average = sum(cycle_averages) / len(cycle_averages)
        print(f"Average Water Consumption per Cycle: {overall_average} liters")
        return overall_average
    else:
        print("No water consumption data available for cycles.")
        return None
#third query
def most_electricity():
    # Fetch metadata for all devices
    fridge1_data = device1_metadata_collection.find_one({"customAttributes.name": "Fridge"})
    fridge2_data = device1_metadata_collection.find_one({"customAttributes.name": "Second Fridge"})
    dishwasher_data = device1_metadata_collection.find_one({"customAttributes.name": "Smart Dishwasher"})

    # Extract unique identifiers
    if fridge1_data:
        fridge1_uid = fridge1_data["assetUid"]
    else:
        return "Fridge 1 data not found."

    if fridge2_data:
        fridge2_uid = fridge2_data["assetUid"]
    else:
        return "Fridge 2 data not found."

    if dishwasher_data:
        dishwasher_uid = dishwasher_data["assetUid"]
    else:
        return "Dishwasher data not found."

    # Query MongoDB for electricity consumption for each device
    devices = {
        "Fridge 1": fridge1_uid,
        "Fridge 2": fridge2_uid,
        "Dishwasher": dishwasher_uid
    }

    total_consumption = {}

    for device_name, uid in devices.items():
        query = {
            "topic": "brokertodb",
            "payload.parent_asset_uid": uid
        }
        records = device1_virtual_collection.find(query)

        # Calculate total consumption for the device
        total_electricity = 0.0
        for record in records:
            electricity = record['payload'].get("Ammeter(Dishwasher)" if device_name == "Dishwasher" else "Ammeter(Fridge)")
            if electricity:
                total_electricity += float(electricity)

        total_consumption[device_name] = total_electricity

    # Find the device with the highest consumption
    most_consumed_device = max(total_consumption, key=total_consumption.get)
    most_consumed_value = total_consumption[most_consumed_device]

    print(f"The device with the most electricity consumption is {most_consumed_device} with {most_consumed_value} kWh.")
    return most_consumed_device, most_consumed_value


#This is the Server Function:
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
                consumption_data = avg_consumption()
                incomingSocket.send(bytearray(f"Consumption Data: {consumption_data}", encoding='utf-8'))

            elif int(myData) == 3:
                print(f"Received message from client: >{myData}")
                device_name = most_electricity()
                incomingSocket.send(bytearray(f"Device: {device_name}", encoding='utf-8'))

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
