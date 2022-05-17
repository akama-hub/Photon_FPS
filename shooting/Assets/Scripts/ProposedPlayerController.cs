using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun;

 
public class ProposedPlayerController : MonoBehaviourPunCallbacks
{ 
    GameObject mainCamera; 
    bool cursorLock = true;
    GameObject Target;
    int count = 0;
    float pastPosition;
    float gap;
    float positionX;

    private forudp.UDP commUDP = new forudp.UDP();
    [SerializeField] GameObject CPUPrefab;
    [SerializeField] Rigidbody _rigidbody;

 
    // Start is called before the first frame update
    private void Start()
    {
        if(AutoGameManager.cpuFlag == 0){
            mainCamera = Camera.main.gameObject;// Main Camera(Game Object) の取得
        }
        GameState.canShoot = true;

        commUDP.init(50002, 50000, 50001);
        //UDP受信開始
        commUDP.start_receive();
    }
 
    // Update is called once per frame
    private void Update()
    {
        if(!photonView.IsMine){
            // Debug.Log("This player is not made by me");
            return;
        }   

        UpdateCursorLock();

        string position_x = CPUPrefab.transform.position.x.ToString("00.000000");
        string position_y = CPUPrefab.transform.position.y.ToString("00.000000");
        string position_z = CPUPrefab.transform.position.z.ToString("00.000000");
        string time = Time.time.ToString("0000.0000");
        string velocity_x = _rigidbody.velocity.x.ToString("00.000000");
        string velocity_y = _rigidbody.velocity.y.ToString("00.000000");
        // string velocity_z = rigidbody.velocity.z.ToString("00.000000");
        // Debug.Log(Time.time);
        // string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y + "vz" + velocity_z;
        string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y;
        commUDP.send(data);

        var players = PhotonNetwork.PlayerListOthers;

        if(players.Length >= 1){ //CPUが存在しているとき
            if(!Target){
                Target = GameObject.FindWithTag("Estimate");
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