using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun;
 
public class ProposedPlayerController : MonoBehaviourPunCallbacks
{ 
    GameObject mainCamera; 
    bool cursorLock = true;
    int count = 0;
    float pastPosition;
    float gap;
    float positionX;

    private forudp.UDP commUDP = new forudp.UDP();
    [SerializeField] GameObject EstimatedPlayerPrefab;
    // [SerializeField] GameObject CPUPrefab;
    GameObject CPUPrefab;
    GameObject estimate;
    Rigidbody _rigidbody;
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
                // Debug.Log(CPUPrefab.name);
                _rigidbody = CPUPrefab.GetComponent<Rigidbody>();
                firstTime = 1;
            }
        }
        

        UpdateCursorLock();

        if(CPUPrefab){
            Debug.Log("CPU is found");
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
            // Debug.Log("send Data: " + data);

            if(estimate){
                gap = estimate.transform.position.x - pastPosition;
                positionX = estimate.transform.position.x;
                Debug.Log(gap);
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