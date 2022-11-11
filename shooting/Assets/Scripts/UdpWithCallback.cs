/***
1. 最低限の準備
    ・メインプログラムの冒頭でインスタンス生成　private UDP commUDP = new UDP(); //commUDPのところは何でもよい
    ・その後，良いところで初期設定　commUDP.init(int型の送信用ポート番号, int型の送信先ポート番号, int型の受信用ポート番号);
２．すると下記の機能が使えるようになります．
    ・UDP送信　commUDP.send(string型のメッセージ)
    ・UDP受信開始　commUDP.startReceive()
    ・UDP受信停止  commUDP.stopReceive()
    ・UDP受信した文字列の取得　commmUDP.rcvMsg
    ・終了処理　commUDP.end()
****/
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System;
namespace forudpwithCB
{
    public class UdpWithCallback
    {   
        private UdpClient udpForSend; //送信用クライアント
        private string remoteHost = "localhost";//送信先のIPアドレス
        private int remotePort;//送信先のポート
        private UdpClient udpForReceive; //受信用クライアント
        public string rcvMsg = "ini";//受信メッセージ格納用
        private System.Threading.Thread rcvThread; //受信用スレッド
        public bool callback = false;
        public float rcvTime;
        public DateTime dt;
        public float milSec;

        // public static UDP instance;
        public UdpWithCallback()
        //コンストラクタ(初期化用、インストラクタを生成したときに最初に実行される)
        {
        }
        
        // public bool init(int port_snd, int port_to, int port_rcv, bool cb)
        //UDP設定（送受信用ポートを開きつつ受信用スレッドを生成）
        public bool init(int port_snd, int port_to, int port_rcv)
        {
            try
            {
                udpForSend = new UdpClient(port_snd);
                //送信用ポート
                remotePort = port_to;
                //送信先ポート
                udpForReceive = new UdpClient(port_rcv); 
                //受信用ポート
                rcvThread = new System.Threading.Thread(new System.Threading.ThreadStart(receive)); 
                //受信スレッド生成
                return true;
            }
            catch
            {
                return false;
            }
        }

        public void send(string sendMsg) 
        //文字列を送信用ポートから送信先ポートに送信
        {
            try
            {
                byte[] sendBytes = Encoding.ASCII.GetBytes(sendMsg);
                udpForSend.Send(sendBytes, sendBytes.Length, remoteHost, remotePort);
            }
            catch{ }
        }
        public void receive() 
        //受信スレッドで実行される関数
        {
            IPEndPoint remoteEP = null;
            //任意の送信元からのデータを受信
            while (true)
            {
                try
                {
                    byte[] rcvBytes = udpForReceive.Receive(ref remoteEP);
                    Interlocked.Exchange(ref rcvMsg, Encoding.ASCII.GetString(rcvBytes));

                    dt = DateTime.Now;
                    milSec = dt.Millisecond / 1000f;
                    rcvTime = (dt.Minute * 60) + dt.Second + milSec;
                    
                    callback = true;
                }
                catch { }
            }
        }
        
        public void start_receive()
        //受信スレッド開始
        {
            try
            {
                rcvThread.Start();
            }
            catch { }
        }
        public void stop_receive()
        //受信スレッドを停止
        {
            try
            {
                rcvThread.Interrupt();
            }
            catch { }
        }
        public void end()
        //送受信用ポートを閉じつつ受信用スレッドも廃止
        {
            try
            {
                udpForReceive.Close();
                udpForSend.Close();
                rcvThread.Abort();
            }
            catch { }
        }
    }
}