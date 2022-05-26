using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Photon.Pun;
 
public class CPUTakeDamageObserver : MonoBehaviourPunCallbacks
{
    int maxCPUHP = 100;
    public int CPUHP;
    public Slider HPBer;
    public Slider selfHPBer;
    [SerializeField] public Text Hptext;
    [SerializeField] public Text selfHptext;

    GameObject FPSCamera;
    private Vector3 CameraPosition;
    [SerializeField] GameObject CameraParent;

    Vector3 respawn = new Vector3(0,-12f,10f);
    private int damage = 1;
    private int HitCount = 0;

    [SerializeField] ParticleSystem bulletHitEffectPrefab;

    [SerializeField] public GameObject CPUUI;
 
 
    // Start is called before the first frame update
    void Start()
    {
        CPUHP = maxCPUHP; //HPの初期値を最大にする
        HPBer.value = CPUHP;
        Hptext.text = CPUHP.ToString();
        selfHptext.text = CPUHP.ToString();

        if(!photonView.IsMine){
            CPUUI.SetActive(false);
        }
    }

    void OnTriggerEnter(Collider other){
        Debug.Log("Hit");
        HitCount += 1;
        if(other.CompareTag("Bullet")){
            // Debug.Log("Take Damage");
            CPUHP -= damage;

            bulletHitEffectPrefab.Play();

            // DamageColor.instance.DamageImage();

            //ぶつかってきたオブジェクトを破壊する.
            Destroy(other.gameObject);
            Debug.Log("Destroy");
        }

        if(CPUHP <= 0f) //hpが0以下になったら・・・
        {
            CPUHP = 0;
            PhotonNetwork.Instantiate("CPUObserver", respawn, Quaternion.identity); //y座標のみ0の下でプレハブを生成
            FPSCamera = Camera.main.gameObject;  // Main Camera(Game Object) の取得
            if(FPSCamera.transform.parent == CameraParent){
                FPSCamera.transform.parent = null;
            }
            Destroy(this.gameObject, 0f);
        }

        HPBer.value = CPUHP;
        selfHPBer.value = CPUHP;
        Hptext.text = CPUHP.ToString();
        selfHptext.text = CPUHP.ToString();
        Debug.Log(HPBer.value);
    }
 
    [PunRPC]
    public void TakeDamage(int _damage) //Playerへの当たり判定から呼び出されるメソッド
    {
        CPUHP -= _damage;
 
        if(CPUHP <= 0f) //hpが0以下になったら・・・
        {
            CPUHP = 0;
            PhotonNetwork.Instantiate("CPUObserver", respawn, Quaternion.identity); //y座標のみ0の下でプレハブを生成
            FPSCamera = Camera.main.gameObject; // Main Camera(Game Object) の取得
            if(FPSCamera.transform.parent == CameraParent){
                FPSCamera.transform.parent = null;
            }
            Destroy(this.gameObject, 0f);
        }

        HPBer.value = CPUHP;
        Debug.Log(HPBer.value);
    }
}