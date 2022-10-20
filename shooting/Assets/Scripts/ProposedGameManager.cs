using UnityEngine;
using Photon.Pun; //Photonサーバーの情報を使用するため

public class ProposedGameManager : MonoBehaviour
{
    [SerializeField] GameObject playerPrefab; //Inspectorで紐づけ
    [SerializeField] GameObject EstimatedPlayerPrefab;
    GameObject Cpu;
    GameObject FPSCamera;
    private Vector3 CameraPosition;

    //プレイヤのリスポーン位置の設定
    Vector3 respawn = new Vector3(2.2f, -12, 3f);
    Vector3 CPURespawn = new Vector3(0f, -12, 10f);

    // Start is called before the first frame update
    void Start()
    {
        if(PhotonNetwork.IsConnected) //サーバーに接続していたら
        {
            Debug.Log("PUN connected");

            var players = PhotonNetwork.PlayerListOthers;
        
            if(players.Length > 0){
                Debug.Log("You are CPU!!");
                
                // GameObject Cpu = PhotonNetwork.Instantiate("SelfSyncroObserver", CPURespawn, Quaternion.identity) as GameObject;
                GameObject Cpu = PhotonNetwork.Instantiate("DRSyncroObserver", CPURespawn, Quaternion.identity) as GameObject;
                // GameObject Cpu = PhotonNetwork.Instantiate("MAADRSyncroObserver", CPURespawn, Quaternion.identity) as GameObject;
                // GameObject Cpu = PhotonNetwork.Instantiate("SelfSyncroRandomObserver", CPURespawn, Quaternion.identity) as GameObject;

                FPSCamera = Camera.main.gameObject; // Main Camera(Game Object) の取得

                CameraPosition = new Vector3 (Cpu.transform.position.x, Cpu.transform.position.y + 0.6f, Cpu.transform.position.z - 0.7f);
                FPSCamera.transform.parent = Cpu.transform;
                FPSCamera.transform.position = CameraPosition;
                FPSCamera.transform.rotation = Quaternion.Euler(0.0f, 180f, 0.0f);
            }

            else{
                if(playerPrefab!=null) //生成するモノが紐づけられているか確認
                {
                    PhotonNetwork.Instantiate("SyncroPlayer", respawn, Quaternion.identity);
                    // PhotonNetwork.Instantiate(playerPrefab.name, respawn, Quaternion.identity); //y座標のみ0の下でプレハブを生成
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

    // Update is called once per frame
    void Update()
    {
        //Spaceが押された時
        if (Input.GetKeyDown(KeyCode.Space))
        {
            EndGame();
        }

        // if(Cpu){
        //     FPSCamera.transform.parent = Cpu.transform;
        //     FPSCamera.transform.position = CameraPosition;
        //     FPSCamera.transform.rotation = Quaternion.Euler(0.0f, 180f, 0.0f);
        // }
    }

    //ゲーム終了
    private void EndGame()
    {
        #if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;//ゲームプレイ終了
        #else
            Application.Quit();//ゲームプレイ終了
        #endif
    }
}
