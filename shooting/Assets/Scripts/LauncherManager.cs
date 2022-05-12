using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Photon.Pun;
using Photon.Realtime;
 
public class LauncherManager : MonoBehaviourPunCallbacks
{
    public GameObject LoginPanel;
    public InputField playerNameInput;
 
    public GameObject ConnectingPanel;
    public GameObject LobbyPanel;
    public int PlayMode = 0;

 
    #region Unity Methods
 
    private void Start()
    {
        PhotonNetwork.AutomaticallySyncScene = true;
        LoginPanel.SetActive(true);
        ConnectingPanel.SetActive(false);
        LobbyPanel.SetActive(false);
    } 
    #endregion
 
    #region Public Methods
 
    public void ConnectToPhotonServer() //LoginButtonで呼ぶ
    {
        if(!PhotonNetwork.IsConnected) //サーバーに接続していたら
        {
            string playerName = playerNameInput.text;
            Debug.Log(playerName);
            if(!string.IsNullOrEmpty(playerName))
            {
                PhotonNetwork.LocalPlayer.NickName = playerName;
                PhotonNetwork.ConnectUsingSettings();
                ConnectingPanel.SetActive(true);
                LoginPanel.SetActive(false);
            }
            else{
                PhotonNetwork.LocalPlayer.NickName = "player1";
                PhotonNetwork.ConnectUsingSettings();
                ConnectingPanel.SetActive(true);
                LoginPanel.SetActive(false);
            }
        }
        else{}
    }
 
    public void JoinRandomRoom() //StartButtonで呼ぶ
    {
        PhotonNetwork.JoinRandomRoom(); 
    }

    public void ProposedPlay(){
        PlayMode = 3;
    }

    public void AutoPlay(){
        PlayMode = 2;
    }
    public void VSCPU(){
        PlayMode = 1;
    }

    public void VSPlayer(){
        PlayMode = 0;
    }
    
    #endregion
    
 
    #region Photon Callbacks
 
    public override void OnConnectedToMaster() //ログインしたら呼ばれる
    {
        //Debug.Log(PhotonNetwork.NickName+ "Connected to Photon server");
        LobbyPanel.SetActive(true);
        ConnectingPanel.SetActive(false);
 
    }
 
    public override void OnJoinRandomFailed(short returnCode, string message)
    {
        //Debug.Log(message);
        CreateAndJoinRoom(); //ルームがなければ自ら作って入る
    }
 
    public override void OnJoinedRoom() //ルームに入ったら呼ばれる
    {
        //Debug.Log(PhotonNetwork.NickName+ "joined to"+ PhotonNetwork.CurrentRoom.Name);
        if(PlayMode == 0){
            PhotonNetwork.LoadLevel("GameScene"); //シーンをロード
        }
        else if(PlayMode == 1){
            PhotonNetwork.LoadLevel("VsCpuGameScene"); //シーンをロード
        }
        else if(PlayMode == 2){
            PhotonNetwork.LoadLevel("AutoScene"); //シーンをロード
        }
        else if(PlayMode == 3){
            PhotonNetwork.LoadLevel("ProposedMethodScene"); //シーンをロード
        }
    }
 
    #endregion
 
    #region Private Methods
    void CreateAndJoinRoom()
    {
        //自動で作られるルームの設定
        string roomName = "Room" + Random.Range(0, 10000); //ルーム名
        RoomOptions roomOptions = new RoomOptions();
        roomOptions.IsOpen = true;
        roomOptions.IsVisible = true;
        roomOptions.MaxPlayers = 100;　//ルームの定員
        PhotonNetwork.CreateRoom(roomName,roomOptions);
    }
    #endregion
}