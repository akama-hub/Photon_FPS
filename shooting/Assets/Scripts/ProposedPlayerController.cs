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
    private DateTime dt;

    private forudp.UDP commUDP = new forudp.UDP();
    [SerializeField] GameObject EstimatedPlayerPrefab;
    // [SerializeField] GameObject CPUPrefab;
    GameObject CPUPrefab;
    GameObject estimate;
    Vector3 CPURespawn = new Vector3(0f, -12, 10f);
    private int firstTime = 0;
 
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
        if(!photonView.IsMine){
            // Debug.Log("This player is not made by me");
            return;
        }

        if(firstTime == 0){
            var players = PhotonNetwork.PlayerListOthers;

            if(players.Length > 0){
                // Debug.Log("Finding");
                CPUPrefab = GameObject.FindGameObjectWithTag("Observer");
                if(CPUPrefab){
                    firstTime = 1;
                }
                else{
                    // Debug.Log("Retrying to find");
                }
            }
        }
        

        UpdateCursorLock();

        if(CPUPrefab){
            // Debug.Log("CPU is found");
            // nowTime = Time.time;
            dt = DateTime.Now;
            milSec = dt.Millisecond / 1000f;
            nowTime = (dt.Minute * 60) + dt.Second + milSec;
            // Debug.Log(milSec);

            pos_x  = CPUPrefab.transform.position.x;
            pos_y  = CPUPrefab.transform.position.y;
            pos_z  = CPUPrefab.transform.position.z;
            // Debug.Log(pastPosX);
            if(pastPosX == -100){
                Debug.Log("Initiate");
            }
            else{
                float deltaT = nowTime - pastTime;
                // Debug.Log(deltaT);

                float vel_x = (pos_x - pastPosX) / deltaT;
                float vel_y = (pos_y - pastPosY) / deltaT;
                float vel_z = (pos_z - pastPosZ) / deltaT;

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
                    if(0.62 < positionX && positionX < 0.65 && GameState.canShoot){
                        Shoot.instance.Shot();
                        // Debug.Log(estimate.transform.position.x);
                        BulletController.instance.MakeBullet();
                        GameState.canShoot = false;
                    }
                }
                else if(gap < 0){
                    if(3.745 < positionX && positionX < 3.753 && GameState.canShoot){
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
        else{
            // Debug.Log("CPU is not found");
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