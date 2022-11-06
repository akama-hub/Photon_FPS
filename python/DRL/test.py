import sys #引数を得るために使用

# playerSelect=str(sys.argv[1])
# print( "REPLY[" + playerSelect + "]:" + "Hello,CS." )
cnt = 0
rcv_message = f"case {cnt}, "
for i in range(len(sys.argv)):
    # print(i)
    # print(str(sys.argv[i]))
    rcv_message += str(sys.argv[i]) + ", "

cnt += 1

print(rcv_message)
