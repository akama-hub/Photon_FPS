using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun;

public class GameState : MonoBehaviour
{
    public static bool canShoot;

    public static bool GameOver = false;
    
    public void Update(){
        if(!canShoot){
            Invoke("CanShoot", 1.5f);
        }
    }

    public void CanShoot(){
        canShoot = true;
    }
}
