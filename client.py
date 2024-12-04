import socket  # Import the socket module for network communication

def TCP_client():
    # Define valid queries
    valid_queries = [
        "What is the average moisture inside my kitchen fridge in the past three hours?",
        "What is the average water consumption per cycle in my smart dishwasher?",
        "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
    ]
    
    try:
        # Get user's server IP and port
        serverIP = input("Enter the IP address of the server: >")
        serverPort = int(input("Enter a port number for the server: >"))
        
        # Create TCP socket and connect to server
        myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        myTCPSocket.connect((serverIP, serverPort))
        print(f"Connected to server {serverIP}:{serverPort}")
        
        # Main loop for sending messages
        while True:
            # Display valid queries to the user
            print("\nValid queries:")
            for i, query in enumerate(valid_queries, 1):
                print(f"{i}. {query}")
            
            # Get message input from user
            userMessage = input("\nEnter the number of your query (or type 'exit' to quit): >")
            
            # Exit program if user enters 'exit'
            if userMessage.lower() == 'exit':
                print("Closing connection....")
                print("Connection closed successfully.")
                break  # Exits loop and closes connection
            
            # Handle numeric input
            if userMessage.isdigit():
                queryIndex = int(userMessage) - 1  # Convert to 0-based index
                if 0 <= queryIndex < len(valid_queries):
                    # Send the corresponding query to the server
                    myTCPSocket.send(bytearray(valid_queries[queryIndex], encoding='utf-8'))
                    
                    # Receive and print the server's response
                    serverResponse = myTCPSocket.recv(2500)  # Receive up to 2500 bytes of data from the server
                    print(f"Server's response: {serverResponse.decode('utf-8')}")
                else:
                    print("Invalid number. Please select a valid query number.")
            else:
                print("Invalid input. Please enter a number corresponding to a query or 'exit' to quit.")
    
    except (ValueError, socket.gaierror):
        print("Error. Invalid IP address or port number.")
    
    except socket.error as e:
        print(f"Error. Couldn't connect to server: {e}")
    
    except Exception as e:
        print(f"An error has occurred: {e}")
    
    finally:
        # Close socket connection
        myTCPSocket.close()

if __name__ == "__main__":
    TCP_client()
