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
                // PhotonView.RPC(nameof(MakeBullet), RpcTarget.All);
                photonView.RPC("MakeBullet", RpcTarget.AllBuffered);
                // MakeBullet();
                // Debug.Log("make bullet");
                // MakeRay();
            }   
        }
    }

    public void shoot(){
        photonView.RPC("MakeBullet", RpcTarget.All);
    }

    [PunRPC]
    private void MakeBullet(){
        Vector3 respawn = new Vector3(transform.position.x, transform.position.y+0.05f, transform.position.z);
        GameObject bullet = Instantiate(Bullet, respawn, Quaternion.Euler(90, transform.parent.eulerAngles.y, 0)) as GameObject;

        muzzleFlashParticle.Play();
        
        Rigidbody bulletRb = bullet.GetComponent<Rigidbody>();
        bulletRb.AddForce(transform.forward * shotSpeed);

        //射撃されてから1秒後に銃弾のオブジェクトを破壊する.
        // Destroy(bullet, 0.8f);
    }
}
