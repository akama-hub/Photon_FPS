using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun;
using System;

public class ObserverSync : MonoBehaviourPunCallbacks, IPunObservable
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
    // private bool isBack = false;

    // private bool noX = false;
    // private bool noZ = true;

    private DateTime dt;
    private float nowTime;
    private float milSec;

    private forudp.UDP commUDP = new forudp.UDP();

    private Rigidbody rigidbody;

    private Vector3 p1;
    private Vector3 p2;
    private float elapsedTime;
    
    private float InterpolationPeriod = 0.1f;

    // Start is called before the first frame update
    void Start()
    {
        if(photonView.IsMine){
            // commUDP.init(int型の送信用ポート番号, int型の送信先ポート番号, int型の受信用ポート番号);
            commUDP.init(50012, 50010, 50013);
            //UDP受信開始
            // commUDP.start_receive();
            rigidbody = this.GetComponent<Rigidbody> ();
        }

        p1 = transform.position;
        p2 = p1;
        elapsedTime = Time.deltaTime;
    }

    private void FixedUpdate(){
        if(photonView.IsMine){
            // 自身のネットワークオブジェクトは、毎フレームの移動量と経過時間を記録する
            p1 = p2;
            p2 = transform.position;
            elapsedTime = Time.deltaTime;

            // curb moovment
            // position = (6. 1. 12)
            // if(isRight){
            //     if(isBack){
            //         this.rigidbody.velocity = new Vector3(Mathf.Sqrt(18) * 1, 0, Mathf.Sqrt(18) * 1);
            //         if(transform.position.x >= 6 + 7/Mathf.Sqrt(2)){
            //             isBack = false;
            //             noZ = true;
            //         }
            //     }
            //     else if(noZ){
            //         this.rigidbody.velocity = new Vector3(6.0f * 1, 0, 0);
            //         if(transform.position.x >= 13 + 7/Mathf.Sqrt(2)){
            //             noZ = false;
            //             isBack = false;
            //         }
            //     }
            //     else{
            //         this.rigidbody.velocity = new Vector3(Mathf.Sqrt(18) * 1, 0, -Mathf.Sqrt(18) * 1);
            //         if(transform.position.x >= 13 + 14/Mathf.Sqrt(2)){
            //             noX = true;
            //             isRight = false;
            //         }
            //     }
            // }
            // else if(noX){
            //     if(isBack){
            //         this.rigidbody.velocity = new Vector3(0, 0, 6.0f * 1);
            //         if(transform.position.z >= 12){
            //             isRight = true;
            //             noX = false;
            //         }
            //     }
            //     else{
            //         this.rigidbody.velocity = new Vector3(0, 0, -6.0f * 1);
            //         if(transform.position.z <= 5){
            //             isRight = false;
            //             noX = false;
            //         }
            //     }
            // }
            // else{
            //     if(noZ){
            //         this.rigidbody.velocity = new Vector3(-6.0f * 1, 0, 0);
            //         if(transform.position.x <= 6 + 7/Mathf.Sqrt(2)){
            //             noZ = false;
            //             isBack = true;
            //         }
            //     }
                
            //     else if(isBack){
            //         this.rigidbody.velocity = new Vector3(-Mathf.Sqrt(18) * 1, 0, Mathf.Sqrt(18) * 1);
            //         if(transform.position.x <= 6){
            //             noX = true;
            //             isRight = false;
            //         }
            //     }
                
            //     else{
            //         this.rigidbody.velocity = new Vector3(-Mathf.Sqrt(18) * 1, 0, -Mathf.Sqrt(18) * 1);
            //         if(transform.position.x <= 12 + 9/Mathf.Sqrt(2)){
            //             noZ = true;
            //             isRight = false;
            //         }
            //     }
            // }

            // ohuku-加速なし
            // if(isRight){
            //     // ohuku movement
            //     // position = (3, 1, 8) 
            //     // position = (15, 1, -8) 
            //     // transform.position += new Vector3(x, 0, 0);
            //     this.rigidbody.velocity = new Vector3(6f * 1, 0, 0);
            //     if(transform.position.x > 27){
            //         isRight = false;
            //     } 
            // }
            // else{
            //     // transform.position -= new Vector3(x, 0, 0);
            //     this.rigidbody.velocity = new Vector3(-6f * 1, 0, 0);
            //     if(transform.position.x < 2){
            //         isRight = true;
            //     }
            // }

            // ohuku-加速あり\
            if(isRight){
                // position = (0, 1, 8) aite
                // position = (10, 1, -8) zibunn
                Debug.Log(this.rigidbody.velocity.x);
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

            // this.rigidbody.velocity = new Vector3(x, 0, z);

            // zigzag
            // if(isRight){
            //     // ohuku movement
            //     // position = (3, 1, 8) 
            //     // transform.position += new Vector3(x, 0, 0);
            //     if(isBack){
            //         this.rigidbody.velocity = new Vector3(Mathf.Sqrt(18) * 5, 0, Mathf.Sqrt(18) * 5);
            //     }
            //     else{
            //         this.rigidbody.velocity = new Vector3(Mathf.Sqrt(18) * 5, 0, -Mathf.Sqrt(18) * 5);
            //     }

            //     if(transform.position.x > 27){
            //         isRight = false;
            //     }
                
            //     if(transform.position.z > 12){
            //         isBack = false;
            //     }
            //     else if(transform.position.z < 7){
            //         isBack = true;
            //     }
            // }
            // else{
            //     // transform.position -= new Vector3(x, 0, 0);
            //     if(isBack){
            //         this.rigidbody.velocity = new Vector3(-Mathf.Sqrt(18) * 5, 0, Mathf.Sqrt(18) * 5);
            //     }
            //     else{
            //         this.rigidbody.velocity = new Vector3(-Mathf.Sqrt(18) * 5, 0, -Mathf.Sqrt(18) * 5);
            //     }

            //     if(transform.position.x < 2){
            //         isRight = true;
            //     }
            //     if(transform.position.z > 12){
            //         isBack = false;
            //     }
            //     else if(transform.position.z < 7){
            //         isBack = true;
            //     }
            // }

            // curb moovment 加速あり
                // position = (2, 1, 8) aite
                // position = (10, 1, -8) zibunn
            // if(isRight){
            //     if(isBack){
            //         if(this.rigidbody.velocity.x == 0){
            //             x = 1/Mathf.Sqrt(2);
            //             if(this.rigidbody.velocity.z == 0){
            //                 z = 1/Mathf.Sqrt(2);
            //             }
            //             if(this.rigidbody.velocity.z >= NonLinearSpeed){
            //                 z = NonLinearSpeed;
            //             }
            //         }
                    
            //         else{
            //             x = this.rigidbody.velocity.x + NonLinearAccel;
            //             z = this.rigidbody.velocity.z + NonLinearAccel;
            //             if(x >= NonLinearSpeed){
            //                 x = NonLinearSpeed;
            //             }
            //             if(z >= NonLinearSpeed){
            //                 z = NonLinearSpeed;
            //             }
            //         }
            //         if(transform.position.x >= 2 + 5/Mathf.Sqrt(2)){
            //             isBack = false;
            //             noZ = true;
            //         }
            //     }
            //     else if(noZ){
            //         if(this.rigidbody.velocity.z > 0){
            //             x = this.rigidbody.velocity.x + LinearAccel;
            //             z = 0;
            //             if(this.rigidbody.velocity.x >= LinearSpeed){
            //                 x = LinearSpeed;
            //             }
            //         }
            //         else{
            //             if(this.rigidbody.velocity.x == 0){
            //                 x = 1;
            //             }
            //             else{
            //                 x = this.rigidbody.velocity.x + LinearAccel;
            //             }
            //             z = 0;
            //             if(x >= LinearSpeed){
            //                 x = LinearSpeed;
            //             }
            //         }
            //         if(transform.position.x >= 7 + 5/Mathf.Sqrt(2)){
            //             noZ = false;
            //             isBack = false;
            //         }
            //     }
            //     else{
            //         if(this.rigidbody.velocity.z == 0){
            //             z = -1/Mathf.Sqrt(2);
            //             if(x >= NonLinearSpeed){
            //                 x = NonLinearSpeed;
            //             }
            //         }
            //         else{
            //             x = this.rigidbody.velocity.x + NonLinearAccel;
            //             z = this.rigidbody.velocity.z - NonLinearAccel;
            //             if(x >= NonLinearSpeed){
            //                 x = NonLinearSpeed;
            //             }
            //             if(Mathf.Abs(z) >= NonLinearSpeed){
            //                 z = 0-NonLinearSpeed;
            //             }
            //         }
            //         if(transform.position.x >= 7 + 10/Mathf.Sqrt(2)){
            //             noX = true;
            //             isRight = false;
            //         }
            //     }
            // }
            // else if(noX){
            //     if(isBack){
            //         if(this.rigidbody.velocity.x < 0){
            //             x = 0;
            //             z = this.rigidbody.velocity.z + LinearAccel;
            //             if(z >= LinearSpeed){
            //                 z = LinearSpeed;
            //             }
            //         }
            //         else{
            //             x = 0;
            //             z = this.rigidbody.velocity.z + LinearAccel;
            //             if(z >= LinearSpeed){
            //                 z = LinearSpeed;
            //             }
            //         }
            //         if(transform.position.z >= 8){
            //             isRight = true;
            //             noX = false;
            //         }
            //     }
            //     else{
            //         if(this.rigidbody.velocity.x > 0){
            //             x = 0;
            //             z = this.rigidbody.velocity.z - LinearAccel;
            //             if(Mathf.Abs(z) >= LinearSpeed){
            //                 z = 0-LinearSpeed;
            //             }
            //         }
            //         else{
            //             x = 0;
            //             z = this.rigidbody.velocity.z - LinearAccel;
            //             if(Mathf.Abs(z) >= LinearSpeed){
            //                 z = 0-LinearSpeed;
            //             }
            //         }
            //         if(transform.position.z <= 3){
            //             isRight = false;
            //             noX = false;
            //         }
            //     }
            // }
            // else{
            //     if(noZ){
            //         if(this.rigidbody.velocity.z < 0){
            //             x = this.rigidbody.velocity.x - LinearAccel;
            //             z = 0;
            //             if(Mathf.Abs(x) >= LinearSpeed){
            //                 x = 0-LinearSpeed;
            //             }
            //         }
            //         else{
            //             x = this.rigidbody.velocity.x - LinearAccel;
            //             z = 0;
            //             if(Mathf.Abs(x) >= LinearSpeed){
            //                 x = 0-LinearSpeed;
            //             }
            //         }
            //         if(transform.position.x <= 2 + 5/Mathf.Sqrt(2)){
            //             noZ = false;
            //             isBack = true;
            //         }
            //     }
                
            //     else if(isBack){
            //         if(this.rigidbody.velocity.z == 0){
            //             z = 1/Mathf.Sqrt(2);
            //             if(Mathf.Abs(x) >= NonLinearSpeed){
            //                 x = 0-NonLinearSpeed;
            //             }
            //         }
            //         else{
            //             x = this.rigidbody.velocity.x - NonLinearAccel;
            //             z = this.rigidbody.velocity.z + NonLinearAccel;
            //             if(Mathf.Abs(x) >= NonLinearSpeed){
            //                 x = 0-NonLinearSpeed;
            //             }
            //             if(z >= NonLinearSpeed){
            //                 z = NonLinearSpeed;
            //             }
            //         }
            //         if(transform.position.x <= 2){
            //             noX = true;
            //             isRight = false;
            //         }
            //     }
                
            //     else{
            //         if(this.rigidbody.velocity.x == 0){
            //             x = -1/Mathf.Sqrt(2);
            //             if(Mathf.Abs(z) >= NonLinearSpeed){
            //                 z = 0-NonLinearSpeed;
            //             }
            //         }
            //         else{
            //             x = this.rigidbody.velocity.x - NonLinearAccel;
            //             z = this.rigidbody.velocity.z - NonLinearAccel;
            //             if(Mathf.Abs(x) >= NonLinearSpeed){
            //                 x = 0-NonLinearSpeed;
            //             }
            //             if(Mathf.Abs(z) >= NonLinearSpeed){
            //                 z = 0-NonLinearSpeed;
            //             }
            //         }
            //         if(transform.position.x <= 7 + 5/Mathf.Sqrt(2)){
            //             noZ = true;
            //             isRight = false;
            //         }
            //     }
            // }

            // this.rigidbody.velocity = new Vector3(x, 0, z);

            // zigzag 加速あり
            // position = (2, 1, 8) aite
            // position = (10, 1, -8) zibunn
            // if(isRight){
            //     if(isBack){
            //         if(this.rigidbody.velocity.x <= 0){
            //             x = 1/Mathf.Sqrt(2);
            //         }
            //         else{
            //             x = this.rigidbody.velocity.x + NonLinearAccel;
            //             if(x >= NonLinearSpeed){
            //                 x = NonLinearSpeed;
            //             }
            //         }
            //         if(this.rigidbody.velocity.z <= 0){
            //             z = 1/Mathf.Sqrt(2);
            //         }
            //         else{
            //             z = this.rigidbody.velocity.z + NonLinearAccel;
            //             if(z >= NonLinearSpeed){
            //                 z = NonLinearSpeed;
            //             }
            //         }
            //     }
            //     else{
            //         if(this.rigidbody.velocity.x <= 0){
            //             x = 1/Mathf.Sqrt(2);
            //         }
            //         else{
            //             x = this.rigidbody.velocity.x + NonLinearAccel;
            //             if(x >= NonLinearSpeed){
            //                 x = NonLinearSpeed;
            //             }   
            //         }
            //         if(this.rigidbody.velocity.z >= 0){
            //             z = -1/Mathf.Sqrt(2);
            //         }
            //         else{
            //             z = this.rigidbody.velocity.z - NonLinearAccel;
            //             if(Mathf.Abs(z) >= NonLinearSpeed){
            //                 z = 0-NonLinearSpeed;
            //             }
            //         }
            //     }

            //     if(transform.position.x > 20){
            //         isRight = false;
            //     }
                
            //     if(transform.position.z > 12){
            //         isBack = false;
            //     }
            //     else if(transform.position.z < 8){
            //         isBack = true;
            //     }
            // }
            // else{
            //     // transform.position -= new Vector3(x, 0, 0);
            //     if(isBack){
            //         if(this.rigidbody.velocity.x >= 0){
            //             x = -1/Mathf.Sqrt(2);
            //         }
            //         else{
            //             x = this.rigidbody.velocity.x - NonLinearAccel;
            //             if(Mathf.Abs(x) >= NonLinearSpeed){
            //                 x = 0-NonLinearSpeed;
            //             } 
            //         }
            //         if(this.rigidbody.velocity.z <= 0){
            //             z = 1/Mathf.Sqrt(2);
            //         }
            //         else{
            //             z = this.rigidbody.velocity.z + NonLinearAccel;
            //             if(z >= NonLinearSpeed){
            //                 z = NonLinearSpeed;
            //             }
            //         }
            //     }
            //     else{
            //         if(this.rigidbody.velocity.x >= 0){
            //             x = -1/Mathf.Sqrt(2);
            //         }
            //         else{
            //             x = this.rigidbody.velocity.x - NonLinearAccel;
            //             if(Mathf.Abs(x) >= NonLinearSpeed){
            //                 x = 0-NonLinearSpeed;
            //             }
            //         }
            //         if(this.rigidbody.velocity.z >= 0){
            //             z = -1/Mathf.Sqrt(2);
            //         }
            //         else{
            //             z = this.rigidbody.velocity.z - NonLinearAccel;
            //             if(Mathf.Abs(z) >= NonLinearSpeed){
            //                 z = 0-NonLinearSpeed;
            //             }
            //         }
            //     }

            //     if(transform.position.x < 0){
            //         isRight = true;
            //     }
            //     if(transform.position.z > 12){
            //         isBack = false;
            //     }
            //     else if(transform.position.z < 8){
            //         isBack = true;
            //     }
            // }
            // Debug.Log(x);
            // Debug.Log(z);
            // Debug.Log(NonLinearSpeed);
            
            this.rigidbody.velocity = new Vector3(x, 0, z);

            dt = DateTime.Now;

            milSec = dt.Millisecond / 1000f;
            nowTime = (dt.Minute * 60) + dt.Second + milSec;

            string position_x = transform.position.x.ToString("00.000000");
            string position_y = transform.position.y.ToString("00.000000");
            string position_z = transform.position.z.ToString("00.000000");
            // string time = Time.time.ToString("0000.0000");
            string time = nowTime.ToString("F3");

            string velocity_x = rigidbody.velocity.x.ToString("00.000000");
            string velocity_y = rigidbody.velocity.y.ToString("00.000000");
            string velocity_z = rigidbody.velocity.z.ToString("00.000000");
            // Debug.Log(Time.time);
            string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y + "vz" + velocity_z;
            // string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y;
            commUDP.send(data);
            
            // Debug.Log(rigidbody.velocity.magnitude);
            // Debug.Log(rigidbody.velocity);
            // Debug.Log(commUDP.rcvMsg)
        }
        else{
            // 他プレイヤーのネットワークオブジェクトは、補間処理を行う
            elapsedTime += Time.deltaTime;
            // transform.position = Vector3.LerpUnclamped(p1, p2, elapsedTime / InterpolationPeriod);
            transform.position = Vector3.LerpUnclamped(p1, p2, elapsedTime);
        }
    }

    void IPunObservable.OnPhotonSerializeView(PhotonStream stream, PhotonMessageInfo info) {
        if (stream.IsWriting) {
            stream.SendNext(transform.position);
            // 毎フレームの移動量と経過時間から、秒速を求めて送信する
            stream.SendNext((p2 - p1) / elapsedTime);
            stream.SendNext(rigidbody.velocity);
        } else {
            var networkPosition = (Vector3)stream.ReceiveNext();
            var networkVelocity = (Vector3)stream.ReceiveNext();
            var lag = Mathf.Max(0f, unchecked(PhotonNetwork.ServerTimestamp - info.SentServerTimestamp) / 1000f);
            Debug.Log(lag);

            // 受信時の座標を、補間の開始座標にする
            p1 = transform.position;
            // 現在時刻における予測座標を、補間の終了座標にする
            p2 = networkPosition + networkVelocity * lag;
            // 経過時間をリセットする
            elapsedTime = 0f;
        }
    }
}
