import socket

if __name__ == '__main__' :
    M_SIZE = 1024
    host = '127.0.0.1' 
    # 自分を指定

    serv_port = 50001
    unity_port = 50002

    serv = (host, serv_port)
    unity_addr = (host, unity_port)
    cli_sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
    cli_sock.bind(serv)
    unity_sock = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)

    print("connecting")

    while True:
        try:

            cli_data, cli_addr = cli_sock.recvfrom(M_SIZE)

            unity_sock.sendto(cli_data, unity_addr)

        except KeyboardInterrupt:
            print ('\n . . .\n')
            cli_sock.close()
            unity_sock.close()