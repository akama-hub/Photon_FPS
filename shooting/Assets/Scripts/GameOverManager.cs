using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun;

public class GameOverManager : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        Cursor.lockState = CursorLockMode.None;   
    }

    // Update is called once per frame
    void Update()
    {
       
    }

    public void Retry(){
        PhotonNetwork.LoadLevel("LauncherScene");
        Debug.Log("Retry the match");
    }

    public void Title(){
        PhotonNetwork.LoadLevel("LauncherScene");
        Debug.Log("Connecting the lobby");
    }
}
