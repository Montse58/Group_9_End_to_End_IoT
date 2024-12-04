import socket #import the socket module for network communication

def TCP_client ():
    try:
        #get users server IP and port
        serverIP = input("Enter the IP address of the server: >")
        serverPort = int(input("Enter a port number for the server: >"))

        #create TCP socket and connect to server
        myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        myTCPSocket.connect((serverIP, serverPort))
        print(f"Connected to server {serverIP}:{serverPort}")
        
        #main loop for sending messages
        while True:
            
            #Gets message input from user
            userMessage = input("Enter message to server (or type 'exit' to quit): >")

            #exits program if user enters 'exit'
            if userMessage.lower() == 'exit':
                print("Closing connection....")
                print("Connection closed successfully.")
                break #exits loop and closes connection

            #sends users message to server
            myTCPSocket.send(bytearray(str(userMessage), encoding='utf-8'))
            
            #recieves and prints the servers response
            serverResponse = myTCPSocket.recv(2500) #recieve up to 2500 bytes of data from the server
            #prints servers response, decoded from bytes to string
            print(f"Servers response                                : >{serverResponse.decode('utf-8')}")

    #handles invalid IP address or port
    except (ValueError, socket.gaierror):
        print("Error. Invalid IP address or port number.")

    #handles connection error
    except socket.error as e:
        print(f"Error. Couldn't connect to server: >{e}")

    #handles other errors
    except Exception as e:
        print(f"An error has occured: >{e}")

    #closes socket connection
    finally:
        myTCPSocket.close()

if __name__ == "__main__":
    TCP_client()
