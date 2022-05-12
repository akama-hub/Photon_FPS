using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun;

 
public class AutoPlayerController : MonoBehaviourPunCallbacks
{  
    GameObject mainCamera; 
    bool cursorLock = true;
    GameObject Target;
    int count = 0;
    float pastPosition;
    float gap;
    float positionX;
 
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
        if(!photonView.IsMine){
            // Debug.Log("This player is not made by me");
            return;
        }   

        UpdateCursorLock();
        var players = PhotonNetwork.PlayerListOthers;

        if(players.Length >= 1){ //CPUが存在しているとき
            if(!Target){
                Target = GameObject.FindWithTag("CPU");
            }
            else{
                gap = Target.transform.position.x - pastPosition;
                positionX = Target.transform.position.x;
                if(gap > 0){
                    if(0.62 < positionX && positionX < 0.65 && GameState.canShoot){
                        Shoot.instance.Shot();
                        Debug.Log(Target.transform.position.x);
                        BulletController.instance.MakeBullet();
                        GameState.canShoot = false;
                    }
                }
                else if(gap < 0){
                    if(3.745 < positionX && positionX < 3.753 && GameState.canShoot){
                        Shoot.instance.Shot();
                        Debug.Log(Target.transform.position.x);
                        BulletController.instance.MakeBullet();
                        GameState.canShoot = false;
                    }
                }
                pastPosition = positionX;
            }
        }
    }
 
    private void FixedUpdate()
    {
        if(!photonView.IsMine){
            // Debug.Log("This player is not made by me");
            return;
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