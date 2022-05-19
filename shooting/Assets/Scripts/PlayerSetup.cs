using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Photon.Pun;
 
public class PlayerSetup : MonoBehaviourPunCallbacks
{
    
    // [SerializeField] public GameObject FPSCamera;
    GameObject FPSCamera; 
    // [SerializeField] public GameObject SubCamera;
    // [SerializeField] Text playerNameText;
    [SerializeField] public GameObject Player;
    // [SerializeField] public GameObject Weapon;

    [SerializeField] public GameObject PlayerUI;

    [SerializeField] public GameObject MakeBullet;
    private Vector3 CameraPosition;
    // private Vector3 SubCameraPosition;

    void Start(){
        FPSCamera = Camera.main.gameObject; // Main Camera(Game Object) の取得
        if(photonView.IsMine) //このオブジェクトが自分がPhotonを介して生成したものならば
        {
            // Debug.Log(Player.transform.position);
            // CameraPosition = new Vector3 (Player.transform.position.x, Player.transform.position.y + 0.6f, Player.transform.position.z + 0.2f);
            FPSCamera.transform.parent = Player.transform;
            // FPSCamera.transform.position = CameraPosition;
            FPSCamera.transform.position = Player.transform.position;
            FPSCamera.transform.rotation = Quaternion.Euler(3, 0, 0);

            MakeBullet.transform.position = new Vector3 (FPSCamera.transform.position.x, FPSCamera.transform.position.y - 0.15f, FPSCamera.transform.position.z + 0.7f);
            MakeBullet.transform.parent = FPSCamera.transform;
            // Debug.Log(MakeBullet.transform.position);
            // MakeBullet.transform.position = new Vector3(0.0f, 0f, 0f);
            MakeBullet.transform.rotation = FPSCamera.transform.rotation * Quaternion.Euler(-3,0,0);
            // SubCameraPosition = new Vector3 (Weapon.transform.position.x + 0f, Weapon.transform.position.y - 0.03f, Weapon.transform.position.z + 0.03f);
            // SubCamera.transform.parent = Weapon.transform;
            // SubCamera.transform.position = SubCameraPosition;
        }
        else{
            PlayerUI.SetActive(false);
        }
        
    }

 
    // Start is called before the first frame update
    // void Awake()
    // {
    //     if(photonView.IsMine) //このオブジェクトが自分がPhotonを介して生成したものならば
    //     {
    //         Debug.Log("This player is made by me");
    //         // Debug.Log(photonView.Owner.NickName);
    //         // transform.GetComponent<PlayerController>().enabled = true; //PlayerController.csを有効にする
    //         // SubCamera.GetComponent<Camera>().enabled = true;
    //         // FPSCamera.GetComponent<Camera>().enabled = true; //FPSCameraのCameraコンポーネントを有効にする
    //         // FPSCamera.SetActive(true);
    //         // SubCamera.SetActive(true);
    //         FPSCamera.transform.parent = Player.transform;
    //         FPSCamera.transform.position = Player.transform.position;
    //         Debug.Log(SubCamera.GetComponent<Camera>().enabled);
    //     }
    //     else{
    //         Debug.Log("This player is not made by me");
    //         // Debug.Log(photonView.Owner.NickName);
    //         transform.GetComponent<PlayerController>().enabled = false;
    //         // FPSCamera.GetComponent<Camera>().enabled = false;
    //         // SubCamera.GetComponent<Camera>().enabled = false;
    //         // FPSCamera.SetActive(false);
    //         // SubCamera.SetActive(false);
    //         // PlayerUI.SetActive(false);
    //         Debug.Log(SubCamera.GetComponent<Camera>().enabled);
    //     }
        
    //     // if(playerNameText!=null) //Textオブジェクトが空でなければ
    //     // {
    //     //     Debug.Log(photonView.Owner.NickName);
    //     //     playerNameText.text = photonView.Owner.NickName; //ログインした名前を代入
    //     // }
    // }
}