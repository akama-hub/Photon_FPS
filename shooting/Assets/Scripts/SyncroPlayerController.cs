using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun;
using System;
 
public class SyncroPlayerController : MonoBehaviourPunCallbacks
{ 
    GameObject mainCamera; 
    private bool cursorLock = true;
    private float pastPosition;
    private float gap;
    private float positionX;
    private bool canShot = true;

    // private float pastTime;
    // private float nowTime = 0.1f;
    // private float milSec;
    
    // // 絶対にとらない値を初期値に与えて判定に使用
    // private float pastPosX = -100, pastPosY, pastPosZ;
    // private float pos_x, pos_y, pos_z;
    // private DateTime dt;

    // private forudp.UDP commUDP = new forudp.UDP();

    private GameObject CPUPrefab;
    private int firstTime = 0;

    // Start is called before the first frame update
    private void Start()
    {
        if(photonView.IsMine){
            mainCamera = Camera.main.gameObject;// Main Camera(Game Object) の取得

            GameState.canShoot = true;

            // commUDP.init(int型の送信用ポート番号, int型の送信先ポート番号, int型の受信用ポート番号);
            // commUDP.init(50004, 50000, 50005);
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
            // // Debug.Log("CPU is found");
            // // nowTime = Time.time;
            // dt = DateTime.Now;
            // milSec = dt.Millisecond / 1000f;
            // nowTime = (dt.Minute * 60) + dt.Second + milSec;
            // // Debug.Log(milSec);

            // pos_x  = CPUPrefab.transform.position.x;
            // pos_y  = CPUPrefab.transform.position.y;
            // pos_z  = CPUPrefab.transform.position.z;
            // // Debug.Log(pastPosX);
            // if(pastPosX == -100){
            //     Debug.Log("Initiate");
            // }
            // else{
            //     // float deltaT = nowTime - pastTime;
            //     float deltaT = Time.deltaTime;
            //     // Debug.Log(deltaT);

            //     float vel_x = (pos_x - pastPosX) / deltaT;
            //     float vel_y = (pos_y - pastPosY) / deltaT;
            //     float vel_z = (pos_z - pastPosZ) / deltaT;

            //     string position_x = pos_x.ToString("00.000000");
            //     string position_y = pos_y.ToString("00.000000");
            //     string position_z = pos_z.ToString("00.000000");
            //     // string time = nowTime.ToString("0000.0000");
            //     string time = nowTime.ToString("F3");
                
            //     // Debug.Log(nowTime);
            //     // Debug.Log(time);

            //     string velocity_x = vel_x.ToString("00.000000");
            //     string velocity_y = vel_y.ToString("00.000000");
            //     string velocity_z = vel_z.ToString("00.000000");
            //     // Debug.Log(Time.time);
            //     string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y + "vz" + velocity_z;
            //     // string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y;
            //     commUDP.send(data);
            //     // Debug.Log("send Data: " + data);
            // }

            gap = CPUPrefab.transform.position.x - pastPosition;
            positionX = CPUPrefab.transform.position.x;
            // Debug.Log(gap);

            if(canShot){
                if(gap > 0){
                    // 実行遅延時間なしと仮定したとき（送受信遅延のみ）
                    // 0.405-0.63
                    // if(0.8 < positionX && positionX < 0.9&& GameState.canShoot){

                    // RTT(送受信遅延 + 実行遅延)の時
                    // 1.55-2.0
                    // if(1.765 < positionX && positionX < 1.865 && GameState.canShoot){
                        
                    if(0.8 < positionX && positionX < 0.9&& GameState.canShoot){
                        Shoot.instance.Shot();
                        BulletControllerCopy.instance.shoot();
                        canShot = false;
                    }
                }
                else if(gap < 0){
                    // 実行遅延時間なしと仮定したとき（送受信遅延のみ）
                    // 3.6-3.9
                    // if(3.5 < positionX && positionX < 3.6 && GameState.canShoot){
                        
                    // RTT(送受信遅延 + 実行遅延)の時
                    // 2.4-3.0
                    // if(2.7 < positionX && positionX < 2.8 && GameState.canShoot){
                    
                    if(3.5 < positionX && positionX < 3.6 && GameState.canShoot){
                        Shoot.instance.Shot();
                        BulletControllerCopy.instance.shoot();
                        canShot = false;
                    }
                }
            }
            else{
                if(positionX < -3 || 8 < positionX){
                    canShot = true;
                }
            }
            
            pastPosition = positionX;

            // pastTime = nowTime;
            // pastPosX = pos_x;
            // pastPosY = pos_y;
            // pastPosZ = pos_z;

        }
        else{
            Debug.Log("CPU is not found");
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