using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Photon.Pun; //Photonサーバーの情報を使用するため
 
public class GameManager : MonoBehaviourPunCallbacks //Photon viewやPunを使用する
{
    [SerializeField] GameObject playerPrefab; //Inspectorで紐づけ

    //プレイヤのリスポーン位置の設定
    Vector3 respawn = new Vector3(3,-12,-1);
 
    // Start is called before the first frame update
    void Start()
    {
        if(PhotonNetwork.IsConnected) //サーバーに接続していたら
        {
            Debug.Log("PUN connected");
            if(playerPrefab!=null) //生成するモノが紐づけられているか確認
            {
                PhotonNetwork.Instantiate(playerPrefab.name, respawn, Quaternion.identity); //y座標のみ0の下でプレハブを生成
            }
            else{
                Debug.Log("player prefab is Null");
            }
        }
        else{
            Debug.Log("PUN disconnected");
        }
    }

}