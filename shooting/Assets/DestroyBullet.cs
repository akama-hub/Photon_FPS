using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DestroyTama : MonoBehaviour
{
    void Update(){
        // Debug.Log("Destroy Bullet");
        Destroy(this.gameObject, 0.8f);
    }

}
