############################################################### 
			server.py 
###############################################################
> This file contains Server class
> The Server class is inherited from Process and it instantiate socket server
	
	*** Features ***
	- The server can listen & accept requests from clients
	- It can receive requests from connected clients
	- It can store key value pair received from client
	- It can provide value stored against a key to the connected client
	
	*** To store key value pair on server ***
	- It requires an active connection with server
	- send a message string containing key & value pair as: 
		+ STORE your_single_word_key = VALUE FOR THIS KEY
		+ Wait for server response
			- if server response is 1	-> key value pair has been stored
			- if server response is 0	-> server is failed to store key value pair

	- you can also store key on server using provided function:
		call store_key(key, value) function with provided key & value

	*** To get stored value from server ***
	- It requires an active connection with server
	- send a message string containing key as:
		+ GET your_single_word_key
		+ Server will return value against your key if it is stored
		+ Server will return ERROR if key is not stored at server at that time

	
> To run server.py individually: 
	- open command line terminal in the same folder
	- run python server.py


############################################################### 
			clientA.py 
###############################################################
> This file contains Client_A class
> The Client_A class is inherited from Process and it instantiates socket client
	
	*** Features ***
	- The client can connect with a scoket server hosted at specific address & port
	- It can send message strings to the socket server
	- It can receive response from socket server
	- It can send key value pair to server
	- On process start (in driver.py) it performs some specified tests 
		to store some key value pairs on the server and show the results in a log file.

> To run clientA.py individually:
	- open command line terminal in the same folder
	- run python clientA.py --key your_key_name --value value_against_key
	- The script will connect with socket server on local network and will store the provide key value pair on server
	
	- You can also run python clientA.py, in this case the script will prompt for input 
	

############################################################### 
			clientB.py 
###############################################################
> This file contains Client_B class
> The Client_B class is inherited from Process and it instantiates socket client
	
	*** Features ***
	- The client can connect with a scoket server hosted at specific address & port
	- It can send message strings to the socketserver
	- It can receive response from socket server
	- It can get value against a key from socket server
	- On process start (in driver.py) it performs some specified tests 
		to get values against some key's from server and show the results in a log file.

> To run clientB.py individually:
	- open command line terminal in the same folder
	- run python clientB.py --key your_key_name 
	- The script will connect with socket server on local network and will request the provided key from server
	
	- You can also run python clientB.py, in this case the script will prompt for input
	

############################################################### 
			driver.py 
###############################################################
> This file contais script to launch Server, Client_A and Client_B processes from server.py, clientA.py and clientB.py .

> To run driver.py:
	- open command line terminal in the same folder
	- run python driver.py 
	- The script will launches Server, Client_A and Client_B processes. 


############################################################### 
			utils.py 
############################################################### 
> This file contains some extra utilities used in this project

	*** Commands ***
		- This is a simple class to hold commands, commonly used by server and clients

	*** Logger   ***
		- Logger is being used to save loges of server and clients in a file for later analysis