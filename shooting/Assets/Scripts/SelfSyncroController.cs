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
    bool isBack = false;

    bool noX = false;
    bool noZ = true;

    private Rigidbody rigidbody;

    // private forudp.UDP commUDP = new forudp.UDP();

    // private DateTime dt;
    // private float nowTime;
    // private float milSec;

    private string motion = "ohuku";
    // private string motion = "curb";
    // private string motion = "zigzag";
    
    // Start is called before the first frame update
    void Start()
    {
        if(photonView.IsMine){
            Application.targetFrameRate = 30; // 30fpsに設定

            // commUDP.init(int型の送信用ポート番号, int型の送信先ポート番号, int型の受信用ポート番号);
            // commUDP.init(50032, 50030, 50031);

            rigidbody = this.GetComponent<Rigidbody> ();
        }
    }

    private void FixedUpdate(){
        if(photonView.IsMine){
            // ohuku-加速あり\
            if(motion == "ohuku"){
                if(isRight){
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
            }
            // curb moovment 加速あり
            else if(motion == "curb"){
                if(isRight){
                    // 2
                    if(isBack){
                        if(this.rigidbody.velocity.z <= 0){
                            z = 1/Mathf.Sqrt(2);
                        }
                        else if(this.rigidbody.velocity.z >= NonLinearSpeed){
                            z = NonLinearSpeed;
                        }
                        else{
                            x = this.rigidbody.velocity.x + NonLinearAccel;
                            z = this.rigidbody.velocity.z + NonLinearAccel;
                            if(x >= NonLinearSpeed){
                                x = NonLinearSpeed;
                            }
                            if(z >= NonLinearSpeed){
                                z = NonLinearSpeed;
                            }
                        }
                        if(transform.position.x >= 9 * Mathf.Sqrt(2) / 2){
                            isBack = true;
                            isRight = false;
                            noZ = false;
                            noX = true;
                        }
                    }
                    // 1
                    else if(noZ){
                        if(this.rigidbody.velocity.z < 0){
                            x = this.rigidbody.velocity.x + LinearAccel;
                            z = 0;
                            if(this.rigidbody.velocity.x >= LinearSpeed){
                                x = LinearSpeed;
                            }
                        }
                        else{
                            if(this.rigidbody.velocity.x == 0){
                                x = 1;
                            }
                            else{
                                x = this.rigidbody.velocity.x + LinearAccel;
                            }
                            z = 0;
                            if(x >= LinearSpeed){
                                x = LinearSpeed;
                            }
                        }
                        if(transform.position.x >= 9 * Mathf.Sqrt(2) - 9){
                            noZ = false;
                            isBack = true;
                        }
                    }
                    // 8
                    else{
                        if(this.rigidbody.velocity.x == 0){
                            x = 1/Mathf.Sqrt(2);
                            if(Mathf.Abs(z) >= NonLinearSpeed){
                                z = - NonLinearSpeed;
                            }
                        }
                        else{
                            x = this.rigidbody.velocity.x + NonLinearAccel;
                            z = this.rigidbody.velocity.z - NonLinearAccel;
                            if(x >= NonLinearSpeed){
                                x = NonLinearSpeed;
                            }
                            if(Mathf.Abs(z) >= NonLinearSpeed){
                                z = - NonLinearSpeed;
                            }
                        }
                        if(transform.position.x >= 0){
                            noZ = true;
                            noX = false;
                            isRight = true;
                        }
                    }
                }
                else if(noX){
                    //3
                    if(isBack){
                        if(this.rigidbody.velocity.x > 0){
                            x = 0;
                        }
                        z = this.rigidbody.velocity.z + LinearAccel;
                        if(z > LinearSpeed){
                            z = LinearSpeed;
                        }

                        if(transform.position.z >= 9 * Mathf.Sqrt(2) / 2 + 10){
                            isRight = false;
                            noX = false;
                            noZ = false;
                            isBack = true;
                        }
                    }
                    // 7
                    else{
                        if(this.rigidbody.velocity.x < 0){
                            x = 0;
                            z = this.rigidbody.velocity.z - LinearAccel;
                            if(Mathf.Abs(z) >= LinearSpeed){
                                z = 0-LinearSpeed;
                            }
                        }
                        else{
                            x = 0;
                            z = this.rigidbody.velocity.z - LinearAccel;
                            if(Mathf.Abs(z) >= LinearSpeed){
                                z = 0-LinearSpeed;
                            }
                        }
                        if(transform.position.z <= 19 - 9 * Mathf.Sqrt(2) / 2){
                            isRight = true;
                            isBack = false;
                            noX = false;
                            noZ = false;
                        }
                    }
                }
                else{
                    // 5
                    if(noZ){
                        if(this.rigidbody.velocity.z > 0){
                            z = 0;
                        }

                        x = this.rigidbody.velocity.x - LinearAccel;
                        if(Mathf.Abs(x) >= LinearSpeed){
                            x = 0-LinearSpeed;
                        }
                        
                        if(transform.position.x <= 0){
                            noX = false;
                            noZ = false;
                            isBack = false;
                            isRight = false;
                        }
                    }
                    // 4
                    else if(isBack){
                        if(this.rigidbody.velocity.x == 0){
                            x = 1/Mathf.Sqrt(2);
                            if(Mathf.Abs(z) >= NonLinearSpeed){
                                z = 0-NonLinearSpeed;
                            }
                        }
                        else{
                            x = this.rigidbody.velocity.x - NonLinearAccel;
                            z = this.rigidbody.velocity.z + NonLinearAccel;
                            if(Mathf.Abs(x) >= NonLinearSpeed){
                                x = 0-NonLinearSpeed;
                            }
                            if(z >= NonLinearSpeed){
                                z = NonLinearSpeed;
                            }
                        }
                        if(transform.position.x <= 9 * Mathf.Sqrt(2) - 9){
                            noX = false;
                            isRight = false;
                            noZ = true;
                            isBack = false;
                        }
                    }
                    // 6
                    else{
                        if(this.rigidbody.velocity.z == 0){
                            z = -1/Mathf.Sqrt(2);
                            if(Mathf.Abs(x) >= NonLinearSpeed){
                                x = 0-NonLinearSpeed;
                            }
                        }
                        else{
                            x = this.rigidbody.velocity.x - NonLinearAccel;
                            z = this.rigidbody.velocity.z - NonLinearAccel;
                            if(Mathf.Abs(x) >= NonLinearSpeed){
                                x = 0-NonLinearSpeed;
                            }
                            if(Mathf.Abs(z) >= NonLinearSpeed){
                                z = 0-NonLinearSpeed;
                            }
                        }
                        if(transform.position.x <= 9 * Mathf.Sqrt(2) / 2 - 9){
                            noZ = false;
                            noX = true;
                            isRight = false;
                            isBack = false;
                        }
                    }
                }
            }
            // zigzag 加速あり
            else if(motion == "zigzag"){
                // position = (2, 1, 8) aite
                // position = (10, 1, -8) zibunn
                if(isRight){
                    if(isBack){
                        if(this.rigidbody.velocity.x <= 0){
                            x = 1/Mathf.Sqrt(2);
                        }
                        else{
                            x = this.rigidbody.velocity.x + NonLinearAccel;
                            if(x >= NonLinearSpeed){
                                x = NonLinearSpeed;
                            }
                        }
                        if(this.rigidbody.velocity.z <= 0){
                            z = 1/Mathf.Sqrt(2);
                        }
                        else{
                            z = this.rigidbody.velocity.z + NonLinearAccel;
                            if(z >= NonLinearSpeed){
                                z = NonLinearSpeed;
                            }
                        }
                    }
                    else{
                        if(this.rigidbody.velocity.x <= 0){
                            x = 1/Mathf.Sqrt(2);
                        }
                        else{
                            x = this.rigidbody.velocity.x + NonLinearAccel;
                            if(x >= NonLinearSpeed){
                                x = NonLinearSpeed;
                            }   
                        }
                        if(this.rigidbody.velocity.z >= 0){
                            z = -1/Mathf.Sqrt(2);
                        }
                        else{
                            z = this.rigidbody.velocity.z - NonLinearAccel;
                            if(Mathf.Abs(z) >= NonLinearSpeed){
                                z = 0-NonLinearSpeed;
                            }
                        }
                    }

                    if(transform.position.x > 10){
                        isRight = false;
                    }
                    
                    if(transform.position.z > 14.5){
                        isBack = false;
                    }
                    else if(transform.position.z < 9.5){
                        isBack = true;
                    }
                }
                else{
                    if(isBack){
                        if(this.rigidbody.velocity.x >= 0){
                            x = -1/Mathf.Sqrt(2);
                        }
                        else{
                            x = this.rigidbody.velocity.x - NonLinearAccel;
                            if(Mathf.Abs(x) >= NonLinearSpeed){
                                x = 0-NonLinearSpeed;
                            } 
                        }
                        if(this.rigidbody.velocity.z <= 0){
                            z = 1/Mathf.Sqrt(2);
                        }
                        else{
                            z = this.rigidbody.velocity.z + NonLinearAccel;
                            if(z >= NonLinearSpeed){
                                z = NonLinearSpeed;
                            }
                        }
                    }
                    else{
                        if(this.rigidbody.velocity.x >= 0){
                            x = -1/Mathf.Sqrt(2);
                        }
                        else{
                            x = this.rigidbody.velocity.x - NonLinearAccel;
                            if(Mathf.Abs(x) >= NonLinearSpeed){
                                x = 0-NonLinearSpeed;
                            }
                        }
                        if(this.rigidbody.velocity.z >= 0){
                            z = -1/Mathf.Sqrt(2);
                        }
                        else{
                            z = this.rigidbody.velocity.z - NonLinearAccel;
                            if(Mathf.Abs(z) >= NonLinearSpeed){
                                z = 0-NonLinearSpeed;
                            }
                        }
                    }

                    if(transform.position.x < -5){
                        isRight = true;
                    }
                    if(transform.position.z > 14.5){
                        isBack = false;
                    }
                    else if(transform.position.z < 9.5){
                        isBack = true;
                    }
                }
            }
            
            this.rigidbody.velocity = new Vector3(x, 0, z);

            // dt = DateTime.Now;
            // milSec = dt.Millisecond / 1000f;
            // nowTime = (dt.Minute * 60) + dt.Second + milSec;

            // string position_x = transform.position.x.ToString("00.000000");
            // string position_y = transform.position.y.ToString("00.000000");
            // string position_z = transform.position.z.ToString("00.000000");
            // // string time = nowTime.ToString("0000.0000");
            // string time = nowTime.ToString("F3");

            // string velocity_x = rigidbody.velocity.x.ToString("00.000000");
            // string velocity_y = rigidbody.velocity.y.ToString("00.000000");
            // string velocity_z = rigidbody.velocity.z.ToString("00.000000");
            // // Debug.Log(Time.time);
            // string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y + "vz" + velocity_z;
            
            // commUDP.send(data);
        }
    }
}
