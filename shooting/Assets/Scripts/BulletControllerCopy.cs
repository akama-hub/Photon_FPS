using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun;

// public class BulletController : MonoBehaviourPunCallbacks
public class BulletControllerCopy : MonoBehaviourPunCallbacks
{
    // public GameObject bulletPrefab;
    public float shotSpeed;
    [SerializeField] ParticleSystem muzzleFlashParticle = null;

    [SerializeField] public GameObject Bullet;

    int count = 0;

    public static BulletControllerCopy instance;

    private GameObject CPUPrefab;
    private int firstTime = 0;

    private forudp.UDP commUDPisMine = new forudp.UDP();
    private forudp.UDP commUDPnotMine = new forudp.UDP();

    private int shoot_count = 0;
    private string senddata = "";

    public void Awake(){
        if(instance == null)
        {
            instance = this;
        }
    }

    // Start is called before the first frame update
    void Start()
    {

        if(photonView.IsMine){
            // commUDP.init(int型の送信用ポート番号, int型の送信先ポート番号, int型の受信用ポート番号);
            commUDPisMine.init(50052, 50050, 50051);
        }
        else{
            // commUDP.init(int型の送信用ポート番号, int型の送信先ポート番号, int型の受信用ポート番号);
            commUDPnotMine.init(50042, 50040, 50041);
        }
        
    }

    // Update is called once per frame
    void Update()
    {
        if(photonView.IsMine){
            // if(Input.GetMouseButtonDown(0) && GameState.canShoot){
            if(Input.GetMouseButtonDown(0)){
                photonView.RPC("MakeBullet", RpcTarget.All);
                // photonView.RPC("MakeBullet", RpcTarget.AllViaServer);
                // MakeBullet();
                // Debug.Log("make bullet");
                // MakeRay();
            }

            if(firstTime == 0){
                var players = PhotonNetwork.PlayerListOthers;

                if(players.Length > 0){
                    // Debug.Log("Finding");
                    CPUPrefab = GameObject.FindGameObjectWithTag("Observer");
                    if(CPUPrefab){
                        firstTime = 1;
                    }
                    else{
                        // Debug.Log("Retrying to find");
                    }
                }
            }   
        }
        else
        {
            if(firstTime == 0){
                var players = PhotonNetwork.PlayerListOthers;

                if(players.Length > 0){
                    // Debug.Log("Finding");
                    CPUPrefab = GameObject.FindGameObjectWithTag("Observer");
                    if(CPUPrefab){
                        firstTime = 1;
                    }
                    else{
                        // Debug.Log("Retrying to find");
                    }
                }
            }  
        }
    }

    public void shoot(){
        photonView.RPC("MakeBullet", RpcTarget.All);
        // photonView.RPC("MakeBullet", RpcTarget.AllViaServer);
    }

    [PunRPC]
    private void MakeBullet(PhotonMessageInfo info){
        Vector3 respawn = new Vector3(transform.position.x, transform.position.y+0.05f, transform.position.z);
        GameObject bullet = Instantiate(Bullet, respawn, Quaternion.Euler(90, transform.parent.eulerAngles.y, 0)) as GameObject;

        if(Async.instance != null)
        {
            // PhotonMessageInfoから、RPCを送信した時刻を取得する
            int timestamp = info.SentServerTimestamp;
            Async.instance.GetRpcLag(timestamp);
        }

        if(photonView.IsMine)
        {
            senddata = shoot_count.ToString("000") + "," + CPUPrefab.transform.position.x.ToString("F6") + "," + CPUPrefab.transform.position.y.ToString("F6") + "," + CPUPrefab.transform.position.z.ToString("F6");
            commUDPisMine.send(senddata);
            shoot_count += 1;
        }
        else
        {
            senddata = shoot_count.ToString("000") + "," + CPUPrefab.transform.position.x.ToString("F6") + "," + CPUPrefab.transform.position.y.ToString("F6") + "," + CPUPrefab.transform.position.z.ToString("F6");
            commUDPnotMine.send(senddata);
            shoot_count += 1;
        }

        muzzleFlashParticle.Play();
        
        Rigidbody bulletRb = bullet.GetComponent<Rigidbody>();
        bulletRb.AddForce(transform.forward * shotSpeed);

        //射撃されてから1秒後に銃弾のオブジェクトを破壊する.
        // Destroy(bullet, 0.8f);
    }
}
