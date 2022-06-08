using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun;
using System;
 
public class ProposedPlayerController : MonoBehaviourPunCallbacks
{ 
    GameObject mainCamera; 
    private bool cursorLock = true;
    private float pastPosition;
    private float gap;
    private float positionX;
    private float pastTime;
    private float nowTime = 0.1f;
    private float milSec;
    // 絶対にとらない値を初期値に与えて判定に使用
    private float pastPosX = -100, pastPosY, pastPosZ;
    private float pos_x, pos_y, pos_z;
    private float vel_x, vel_y, vel_z;
    private DateTime dt;

    private forudp.UDP commUDP = new forudp.UDP();
    [SerializeField] private GameObject EstimatedPlayerPrefab;
    private GameObject estimate;
    private Vector3 CPURespawn = new Vector3(0f, -12, 10f);
    private int firstTime = 0;

    private Vector3 RecievePosition;
    private Vector3 RecieveVelocity;
 
    // Start is called before the first frame update
    private void Start()
    {
        if(photonView.IsMine){
            mainCamera = Camera.main.gameObject;// Main Camera(Game Object) の取得

            GameState.canShoot = true;

            // commUDP.init(int型の送信用ポート番号, int型の送信先ポート番号, int型の受信用ポート番号);
            commUDP.init(50004, 50000, 50005);

            estimate = Instantiate(EstimatedPlayerPrefab, CPURespawn, Quaternion.identity) as GameObject;
        }
    }
 
    // Update is called once per frame
    private void Update()
    {
        UpdateCursorLock();

        if(photonView.IsMine){
            Debug.Log(RecievePosition.x);
            
            // nowTime = Time.time;
            dt = DateTime.Now;
            milSec = dt.Millisecond / 1000f;
            nowTime = (dt.Minute * 60) + dt.Second + milSec;
            // Debug.Log(milSec);

            pos_x  = RecievePosition.x;
            pos_y  = RecievePosition.y;
            pos_z  = RecievePosition.z;

            // Debug.Log(pastPosX);
            if(pastPosX == -100){
                Debug.Log("Initiate");
            }
            else{
                vel_x = RecieveVelocity.x;
                vel_y = RecieveVelocity.y;
                vel_z = RecieveVelocity.z;

                string position_x = pos_x.ToString("00.000000");
                string position_y = pos_y.ToString("00.000000");
                string position_z = pos_z.ToString("00.000000");
                // string time = nowTime.ToString("0000.0000");
                string time = nowTime.ToString("F3");
                
                // Debug.Log(nowTime);
                // Debug.Log(time);

                string velocity_x = vel_x.ToString("00.000000");
                string velocity_y = vel_y.ToString("00.000000");
                string velocity_z = vel_z.ToString("00.000000");
                // Debug.Log(Time.time);
                string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y + "vz" + velocity_z;
                // string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y;
                commUDP.send(data);
                // Debug.Log("send Data: " + data);
            }

            if(estimate){
                gap = estimate.transform.position.x - pastPosition;
                positionX = estimate.transform.position.x;
                // Debug.Log(gap);
                if(gap > 0){
                    if(1.7 < positionX && positionX < 1.8 && GameState.canShoot){
                        Shoot.instance.Shot();
                        // Debug.Log(estimate.transform.position.x);
                        BulletController.instance.MakeBullet();
                        GameState.canShoot = false;
                    }
                }
                else if(gap < 0){
                    if(2.2 < positionX && positionX < 2.3 && GameState.canShoot){
                        Shoot.instance.Shot();
                        // Debug.Log(estimate.transform.position.x);
                        BulletController.instance.MakeBullet();
                        GameState.canShoot = false;
                    }
                }
                pastPosition = positionX;
            }

            pastTime = nowTime;
            pastPosX = pos_x;
            pastPosY = pos_y;
            pastPosZ = pos_z;
        }

    }
 

    public void UpdateCursorLock(){
        if(Input.GetKeyDown(KeyCode.Escape)){
            cursorLock = false;
        }
        else if(Input.GetMouseButton(0) && !Input.GetKey(KeyCode.LeftShift)){
            cursorLock = true;
        }

        if(cursorLock){
            Cursor.lockState = CursorLockMode.Locked;
        }
        else if(!cursorLock){
            Cursor.lockState = CursorLockMode.None;
        }
    }
}