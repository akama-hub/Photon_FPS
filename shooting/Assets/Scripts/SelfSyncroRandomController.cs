using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun;
using System;
using Random = System.Random;

public class SelfSyncroRandomController : MonoBehaviourPunCallbacks
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

    private static Random random = new Random(System.Environment.TickCount);
    private double[] normrand = new double[2]; 
    
    // Start is called before the first frame update
    void Start()
    {
        if(photonView.IsMine){
            // commUDP.init(int型の送信用ポート番号, int型の送信先ポート番号, int型の受信用ポート番号);
            commUDP.init(50032, 50030, 50031);

            rigidbody = this.GetComponent<Rigidbody> ();
            normrand = getNormalDistribution(normrand);
        }
    }

    private void FixedUpdate(){
        if(photonView.IsMine){
            // ohuku-加速あり\
            if(isRight){
                // -12 < position < 12
                if(rigidbody.velocity.x < 0.7){
                    x = 1;
                    z = 0;
                }
                else{
                    x = rigidbody.velocity.x + LinearAccel; 
                    if(x >= LinearSpeed){
                        x = LinearSpeed;
                        z = 0;
                    }
                }

                if(transform.position.x > normrand[0]){
                    isRight = false;
                } 
            }
            else{
                if(rigidbody.velocity.x > -0.7){
                    x = -1;
                    z = 0;
                }
                else{
                    x = rigidbody.velocity.x - LinearAccel; 
                    if(Mathf.Abs(x) >= LinearSpeed){
                        x = 0-LinearSpeed;
                    }
                }

                if(transform.position.x < normrand[1]){
                    isRight = true;
                    normrand = getNormalDistribution(normrand);
                }
            }
            
            rigidbody.velocity = new Vector3(x, 0, z);

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

    private double[] getNormalDistribution(double[] normrand, double mu = 0.0, double sigma = 1.0){
        double rand = 0.0;
        while ((rand = random.NextDouble()) == 0.0) ;
        double rand2 = random.NextDouble();
        normrand[0] = Math.Sqrt(-2.0 * Math.Log(rand)) * Math.Cos(2.0 * Math.PI * rand2);
        normrand[0] = normrand[0] * sigma + mu;
        normrand[1] = Math.Sqrt(-2.0 * Math.Log(rand)) * Math.Sin(2.0 * Math.PI * rand2);
        normrand[1] = normrand[1] * sigma + mu;

        // sigma = 1.0 の時
        if(normrand[0] >= 0){
            if(normrand[1] >= 0){
                normrand[0] = 12 - normrand[0] * 4;
                normrand[1] = (-1) * (12 - normrand[1] * 4);
            }
            else{
                normrand[0] = 12 - normrand[0] * 4;
                normrand[1] = -12 - normrand[1] * 4;
            }
        }
        else{
            if(normrand[1] >= 0){
                normrand[0] = 12 + normrand[0] * 4;
                normrand[1] = (-1) * (12 - normrand[1] * 4);
            }
            else{
                normrand[0] = 12 + normrand[0] * 4;
                normrand[1] = -12 - normrand[1] * 4;
            }
        }
        return normrand;
    }
}
