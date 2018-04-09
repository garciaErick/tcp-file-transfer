#!/bin/bash
pkill python

printf "Testing TCP with Normal Proxy\n"

printf "Starting TCP Server\n"
python server/tcpServer.py &
printf "Success\n\n"

printf "Starting TCP Proxy\n"
python proxy.py &
printf "Success\n\n"

sleep 1

printf "Starting TCP Client\n"
python client/tcpClient.py -n 2 -r 'PUT|testFileFromClient.txt GET|testFileFromServer.txt'
printf "Success\n\n"

printf "Done Testing TCP with Normal Proxy\n\n"

pkill python

printf "\nTesting TCP with Stammering Proxy\n"
printf "Starting TCP Server\n"
python server/tcpServer.py &
printf "Success\n\n"

printf "Starting TCP Proxy\n"
python stammerProxy.py &
printf "Success\n\n"

sleep 1

printf "Starting TCP Client\n"
python client/tcpClient.py -n 2 -r "PUT|testFileFromClient.txt GET|testFileFromServer.txt"
printf "Success\n\n"

printf "Done Testing TCP with Stammer Proxy\n\n"


pkill python