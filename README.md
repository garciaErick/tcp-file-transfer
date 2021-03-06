# TCP
A file transfer protocol and implement a client and server.  The server must be 
* single-threaded, 
* and accept multiple concurrent client connections.   

Recall that unlike UDP, which is a message-oriented protocol, TCP is stream-oriented.  

A practical implication of this difference is that the outputs of multiple writes may be concatenated and reads may only return a portion of the data already sent. 

## Client
A client can begin a PUT or GET request
* A *PUT* request will send a file from the /client/ to the /server/ directory
* A *GET* request will receive a file from the /server/ in the /clients/ directory

## Testing the application
On the root directory there is a sample script **tcpDemo.sh** you can just run it and you will run the application and testing it with both the proxy.py and the stammerProxy.py, or run the following commands:

* The following will run a sample run that tests the multi client capability as well as the PUT and the GET implemented through tcp: 

```sh
python server/tcpServer.py &
python proxy.py &
python client/tcpClient.py -n 2 -r 'PUT|testFileFromClient.txt GET|testFileFromServer.txt'
pkill python

python server/tcpServer.py &
python stammerProxy.py &
python client/tcpClient.py -n 2 -r 'PUT|testFileFromClient.txt GET|testFileFromServer.txt'
pkill python
```
