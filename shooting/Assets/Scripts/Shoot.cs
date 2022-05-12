using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
// using Photon.Pun;
 
public class Shoot : MonoBehaviour
{
    // [SerializeField] Camera fpsCamera;
    Camera fpsCamera;
    public Animator animator; //アニメーション用

    // 所持弾薬、最高所持弾薬、マガジン内弾数、最高マガジン内弾数
    int ammunition = 100, maxAmmunition = 2000, ammoClip = 100, maxAmmoClip = 100;

    public Text ammoText;

    public static Shoot instance;
    public void Awake(){
        if(instance == null)
        {
            instance = this;
        }
    }

    void Start(){
        fpsCamera = Camera.main; // Main Camera(Camera) の取得
        ammoText.text = "Ammo " + ammoClip + " / " + ammunition;
    }
 
    // Update is called once per frame
    void Update()
    {
        // Debug.Log(GameState.canShoot);
        if(Input.GetMouseButtonDown(0) && GameState.canShoot) //左クリックした場合
        {
            Shot();            
        }

        if(Input.GetKeyDown(KeyCode.R)){
            int amountNeed = maxAmmoClip - ammoClip;
            int ammoAvailable  = amountNeed < ammunition ? amountNeed : ammunition;

            if(amountNeed != 0 && ammunition != 0){
                animator.SetTrigger("Reload");
            }
            
            ammunition -= ammoAvailable;
            ammoClip += ammoAvailable;
            ammoText.text = "Ammo " + ammoClip + " / " + ammunition;
        }
    }

    public void Shot(){
        if(ammoClip > 0){
            animator.SetTrigger("Fire");
            GameState.canShoot = false;

//             RaycastHit _hit; //Rayが衝突した情報を宣言
//             Ray ray = fpsCamera.ViewportPointToRay(new Vector3(0.5f, 0.5f)); //カメラから画面中心に向けて飛ばすRayを定義

//             // float distance = 100; // 飛ばす&表示するRayの長さ
//             // float duration = 10;   // 表示期間（秒）
//             // Debug.DrawRay(ray.origin, ray.direction * distance, Color.red, duration, false);
//             // Debug.Log("Draw Ray");

//             if(Physics.Raycast(ray, out _hit,100)) //Rayが何かオブジェクトに衝突した場合
//             {
//                 // Debug.DrawRay(ray.origin, ray.direction * distance, Color.red, duration, false);
//                 Debug.Log(_hit.collider.gameObject.name); //衝突したオブジェクトの名前を出力

//                 if(_hit.collider.gameObject.CompareTag("Player") &&!_hit.collider.gameObject.GetComponent<PhotonView>().IsMine) 
// 　　　　　　　　　　//衝突したオブジェクトにPlayerタグ付けがあり、なおかつそれが自分のプレイヤーでない場合
//                 {
//                     _hit.collider.gameObject.GetComponent<PhotonView>().RPC("TakeDamage", RpcTarget.AllBuffered, 10); 
//                     //RPCを介して、相手オブジェクトのメソッドを呼ぶ（10fというfloat値を渡す）
//                     Debug.Log("Hit");
//                 }

//                 if(_hit.collider.gameObject.CompareTag("CPU") ) 
// 　　　　　　　　　　//衝突したオブジェクトにCPUタグ付けがある場合
//                 {
//                     _hit.collider.gameObject.GetComponent<PhotonView>().RPC("TakeDamage", RpcTarget.AllBuffered, 10); 
//                     //RPCを介して、相手オブジェクトのメソッドを呼ぶ（10fというfloat値を渡す）
//                     Debug.Log("Hit");
//                 }
//             }
            ammoClip --;
            ammoText.text = "Ammo " + ammoClip + " / " + ammunition;
        }
        else if(ammoClip <= 0){
            Debug.Log("Out of Ammo");
        }
    }
}