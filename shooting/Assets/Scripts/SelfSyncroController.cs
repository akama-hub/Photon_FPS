using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun;
using System;

public class SelfSyncroController : MonoBehaviourPunCallbacks
{
    float x = 0;
    float z = 0;

    //スピード調整用
    static float LinearAccel = 1f;
    float NonLinearAccel = Mathf.Sqrt(Mathf.Pow(LinearAccel, 2) / 2);

    // private static float LinearSpeed = 12f;
    static float LinearSpeed = 5f;
    private float NonLinearSpeed = Mathf.Sqrt(Mathf.Pow(LinearSpeed, 2) / 2);

    private bool isRight = true;
    private Rigidbody rigidbody;

    private forudp.UDP commUDP = new forudp.UDP();

    private DateTime dt;
    private float nowTime;
    private float milSec;
    
    // Start is called before the first frame update
    void Start()
    {
        if(photonView.IsMine){
            // commUDP.init(int型の送信用ポート番号, int型の送信先ポート番号, int型の受信用ポート番号);
            commUDP.init(50032, 50030, 50031);

            rigidbody = this.GetComponent<Rigidbody> ();
        }
    }

    private void FixedUpdate(){
        if(photonView.IsMine){
            // ohuku-加速あり\
            if(isRight){
                // position = (0, 1, 8) aite
                // position = (10, 1, -8) zibunn
                // Debug.Log(this.rigidbody.velocity.x);
                if(this.rigidbody.velocity.x < 0.7){
                    x = 1;
                    z = 0;
                }
                else{
                    x = this.rigidbody.velocity.x + LinearAccel; 
                    if(x >= LinearSpeed){
                        x = LinearSpeed;
                        z = 0;
                    }
                }

                // if(transform.position.x > 17){
                if(transform.position.x > 10){
                    isRight = false;
                } 
            }
            else{
                if(this.rigidbody.velocity.x > -0.7){
                    x = -1;
                    z = 0;
                }
                else{
                    x = this.rigidbody.velocity.x - LinearAccel; 
                    if(Mathf.Abs(x) >= LinearSpeed){
                        x = 0-LinearSpeed;
                    }
                }

                // if(transform.position.x < -12){
                if(transform.position.x < -5){
                    isRight = true;
                }
            }
            
            this.rigidbody.velocity = new Vector3(x, 0, z);

            dt = DateTime.Now;
            milSec = dt.Millisecond / 1000f;
            nowTime = (dt.Minute * 60) + dt.Second + milSec;

            string position_x = transform.position.x.ToString("00.000000");
            string position_y = transform.position.y.ToString("00.000000");
            string position_z = transform.position.z.ToString("00.000000");
            // string time = nowTime.ToString("0000.0000");
            string time = nowTime.ToString("F3");

            string velocity_x = rigidbody.velocity.x.ToString("00.000000");
            string velocity_y = rigidbody.velocity.y.ToString("00.000000");
            string velocity_z = rigidbody.velocity.z.ToString("00.000000");
            // Debug.Log(Time.time);
            string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y + "vz" + velocity_z;
            
            commUDP.send(data);
        }
    }
}
