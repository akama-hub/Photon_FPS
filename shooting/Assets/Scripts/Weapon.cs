using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Weapon : MonoBehaviour
{
    void Start(){

    }

    void Update(){

    }
    public void CanShoot(){
        GameState.canShoot = true;
    }
}
