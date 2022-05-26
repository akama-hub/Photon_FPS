using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun;

public class BulletController : MonoBehaviourPunCallbacks
{
    // public GameObject bulletPrefab;
    public float shotSpeed;
    [SerializeField] ParticleSystem muzzleFlashParticle = null;

    public static BulletController instance;
    public void Awake(){
        if(instance == null)
        {
            instance = this;
        }
    }

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if(photonView.IsMine){
            // if(Input.GetMouseButtonDown(0) && GameState.canShoot){
            if(Input.GetMouseButtonDown(0)){
                MakeBullet();
                // Debug.Log("make bullet");
                // MakeRay();
            }   
        }
        
    }

    public void MakeBullet(){
        Vector3 respawn = new Vector3(transform.position.x, transform.position.y+0.05f, transform.position.z);
        // GameObject bullet = (GameObject)Instantiate(bulletPrefab, respawn, Quaternion.Euler(90, transform.parent.eulerAngles.y, 0));
        GameObject bullet = PhotonNetwork.Instantiate("Bullet", respawn, Quaternion.Euler(90, transform.parent.eulerAngles.y, 0));

        muzzleFlashParticle.Play();
        
        Rigidbody bulletRb = bullet.GetComponent<Rigidbody>();
        bulletRb.AddForce(transform.forward * shotSpeed);

        //射撃されてから1秒後に銃弾のオブジェクトを破壊する.
        // Destroy(bullet, 0.8f);
    }

    public void MakeRay(){
        RaycastHit _hit; //Rayが衝突した情報を宣言
        // Ray ray = fpsCamera.ViewportPointToRay(new Vector3(0.5f, 0.5f)); //カメラから画面中心に向けて飛ばすRayを定義
        float distance = 100; // 飛ばす&表示するRayの長さ
        float duration = 10;   // 表示期間（秒）
        if(Physics.Raycast(transform.position, -transform.forward, out _hit, 100)) //Rayが何かオブジェクトに衝突した場合
        {
            Debug.DrawRay(transform.position, -transform.forward * distance, Color.red, duration, false);
            Debug.Log(_hit.collider.gameObject.name); //衝突したオブジェクトの名前を出力

            if(_hit.collider.gameObject.CompareTag("Player") &&!_hit.collider.gameObject.GetComponent<PhotonView>().IsMine) 
　　　　　　　　　　//衝突したオブジェクトにPlayerタグ付けがあり、なおかつそれが自分のプレイヤーでない場合
            {
                _hit.collider.gameObject.GetComponent<PhotonView>().RPC("TakeDamage", RpcTarget.AllBuffered, 10); 
                //RPCを介して、相手オブジェクトのメソッドを呼ぶ（10fというfloat値を渡す）
                Debug.Log("Hit");
            }

            if(_hit.collider.gameObject.CompareTag("CPU") ) 
　　　　　　　　　　//衝突したオブジェクトにCPUタグ付けがある場合
            {
                _hit.collider.gameObject.GetComponent<PhotonView>().RPC("TakeDamage", RpcTarget.AllBuffered, 10); 
                //RPCを介して、相手オブジェクトのメソッドを呼ぶ（10fというfloat値を渡す）
                Debug.Log("Hit");
            }

//             if(_hit.collider.gameObject.CompareTag("Player") &&!_hit.collider.gameObject.GetComponent<PhotonView>().IsMine) 
// 　　　　　　　　　　//衝突したオブジェクトにPlayerタグ付けがあり、なおかつそれが自分のプレイヤーでない場合
//             {
//                 _hit.collider.gameObject.GetComponent<PhotonView>().RPC("TakeDamage", RpcTarget.AllBuffered, 10); 
//                 //RPCを介して、相手オブジェクトのメソッドを呼ぶ（10fというfloat値を渡す）
//                 Debug.Log("Hit");
//             }

//             if(_hit.collider.gameObject.CompareTag("CPU") ) 
// 　　　　　　　　　　//衝突したオブジェクトにCPUタグ付けがある場合
//             {
//                 _hit.collider.gameObject.GetComponent<PhotonView>().RPC("TakeDamage", RpcTarget.AllBuffered, 10); 
//                 //RPCを介して、相手オブジェクトのメソッドを呼ぶ（10fというfloat値を渡す）
//                 Debug.Log("Hit");
//             }
        }
    
    }
}
