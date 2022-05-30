using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun;

 
public class AutoPlayerControllerCopy : MonoBehaviourPunCallbacks
{  
    GameObject mainCamera; 
    bool cursorLock = true;
    GameObject Target;
    int count = 0;
    float pastPosition;
    float gap;
    float positionX;
    private bool canShot = true;
 
    // Start is called before the first frame update
    private void Start()
    {
        if(AutoGameManager.cpuFlag == 0){
            mainCamera = Camera.main.gameObject;// Main Camera(Game Object) の取得
        }
        GameState.canShoot = true;
    }
 
    // Update is called once per frame
    private void Update()
    {
        if(photonView.IsMine){
            UpdateCursorLock();
            var players = PhotonNetwork.PlayerListOthers;

            if(players.Length >= 1){ //CPUが存在しているとき
                if(!Target){
                    Target = GameObject.FindWithTag("Observer");
                }
                else{
                    gap = Target.transform.position.x - pastPosition;
                    positionX = Target.transform.position.x;
                    if(canShot){
                        if(gap > 0){
                            // 実行遅延時間なしと仮定したとき（送受信遅延のみ）
                            // 0.405-0.63
                            // if(0.62 < positionX && positionX < 0.6245 && GameState.canShoot){

                            // RTT(送受信遅延 + 実行遅延)の時
                            // 1.45-2.0
                            if(1.765 < positionX && positionX < 1.865 && GameState.canShoot){
                                Shoot.instance.Shot();
                                BulletControllerCopy.instance.shoot();
                                canShot = false;
                                // Debug.Log(positionX);
                            }
                        }
                        else if(gap < 0){
                            // 実行遅延時間なしと仮定したとき（送受信遅延のみ）
                            // 3.6-3.9
                            // if(3.745 < positionX && positionX < 3.753 && GameState.canShoot){

                            // RTT(送受信遅延 + 実行遅延)の時
                            // 2.4-3.0
                            if(2.7 < positionX && positionX < 2.8 && GameState.canShoot){
                                Shoot.instance.Shot();
                                BulletControllerCopy.instance.shoot();
                                canShot = false;
                                // Debug.Log(positionX);
                            }
                        }
                    }
                    else{
                        if(positionX < 1.4 || 3.0 < positionX){
                            canShot = true;
                        }
                    }
                    
                    pastPosition = positionX;
                }
            }
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