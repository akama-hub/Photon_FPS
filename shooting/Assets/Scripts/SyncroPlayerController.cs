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

    private GameObject CPUPrefab;
    private int firstTime = 0;

    // Start is called before the first frame update
    private void Start()
    {
        if(photonView.IsMine){
            Application.targetFrameRate = 30; // 30fpsに設定

            mainCamera = Camera.main.gameObject;// Main Camera(Game Object) の取得

            GameState.canShoot = true;
        }
    }
 
    // Update is called once per frame
    private void Update()
    {

        if(!photonView.IsMine){
            // Debug.Log("This player is not made by me");
            return;
        }

        // if(firstTime == 0){
        //     var players = PhotonNetwork.PlayerListOthers;

        //     if(players.Length > 0){
        //         // Debug.Log("Finding");
        //         CPUPrefab = GameObject.FindGameObjectWithTag("Observer");
        //         if(CPUPrefab){
        //             firstTime = 1;
        //         }
        //         else{
        //             // Debug.Log("Retrying to find");
        //         }
        //     }
        // }
        

        UpdateCursorLock();

        // if(CPUPrefab){
        //     gap = CPUPrefab.transform.position.x - pastPosition;
        //     positionX = CPUPrefab.transform.position.x;
        //     // Debug.Log(gap);

        //     if(canShot){
        //         // my bullet position x 2.265 
        //         if(gap > 0){
        //             if(1.815 < positionX && positionX < 1.915 && GameState.canShoot){
        //             // if(1.865 < positionX && positionX < 1.965 && GameState.canShoot){
        //                 Shoot.instance.Shot();
        //                 BulletControllerCopy.instance.shoot();
        //                 canShot = false;
        //             }
        //         }
        //         else if(gap < 0){
        //             if(2.615 < positionX && positionX < 2.715 && GameState.canShoot){
        //             // if(2.565 < positionX && positionX < 2.665 && GameState.canShoot){
        //                 Shoot.instance.Shot();
        //                 BulletControllerCopy.instance.shoot();
        //                 canShot = false;
        //             }
        //         }
        //     }
        //     else{
        //         if(positionX < -3 || 8 < positionX){
        //             canShot = true;
        //         }
        //     }
            
        //     pastPosition = positionX;
        // }
        // else{        }
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