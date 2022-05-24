using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun; //Photonサーバーの情報を使用するため

public class AutoGameManager : MonoBehaviourPunCallbacks
{
    [SerializeField] GameObject playerPrefab; //Inspectorで紐づけ
    public GameObject Cpu;
    GameObject FPSCamera;
    private Vector3 CameraPosition;

    //プレイヤのリスポーン位置の設定
    Vector3 respawn = new Vector3(2.2f, -12, 3f);
    Vector3 CPURespawn = new Vector3(0f, -12, 10f);
    public static int cpuFlag = 0;
    // player が cpu として参加しているとき -> 1
    // それ以外 -> 0

    // Start is called before the first frame update
    void Start()
    {
        if(PhotonNetwork.IsConnected) //サーバーに接続していたら
        {
            Debug.Log("PUN connected");

            var players = PhotonNetwork.PlayerListOthers;
        
            if(players.Length > 0){
                cpuFlag = 1;
                Debug.Log("You are CPU!!");
                PhotonNetwork.Instantiate("Observer", CPURespawn, Quaternion.identity); //y座標のみ0の下でプレハブを生成
                Cpu = GameObject.FindWithTag("Observer");

                FPSCamera = Camera.main.gameObject; // Main Camera(Game Object) の取得

                CameraPosition = new Vector3 (Cpu.transform.position.x, Cpu.transform.position.y + 0.6f, Cpu.transform.position.z - 0.7f);
                FPSCamera.transform.parent = Cpu.transform;
                FPSCamera.transform.position = CameraPosition;
                FPSCamera.transform.rotation = Quaternion.Euler(0.0f, 180f, 0.0f);
            }

            else{
                if(playerPrefab!=null) //生成するモノが紐づけられているか確認
                {
                    PhotonNetwork.Instantiate(playerPrefab.name, respawn, Quaternion.identity); //y座標のみ0の下でプレハブを生成
                }
                else{
                    Debug.Log("player prefab is Null");
                }
            }
            
            
        }
        else{
            Debug.Log("PUN disconnected");
        }
    }

    void Update(){
        if(!Cpu && cpuFlag == 1){
            Cpu = GameObject.FindWithTag("Observer");
            if(Cpu){
                FPSCamera.transform.parent = Cpu.transform;
                FPSCamera.transform.position = CameraPosition;
                FPSCamera.transform.rotation = Quaternion.Euler(0.0f, 180f, 0.0f);
            }
        }
    }
}
