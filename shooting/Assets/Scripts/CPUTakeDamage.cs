using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Photon.Pun;
 
public class CPUTakeDamage : MonoBehaviourPunCallbacks
{
    int maxCPUHP = 100;
    public int CPUHP;
    public Slider HPBer;

    Vector3 respawn = new Vector3(0,-12f,14f);
    int damage = 10;

    [SerializeField] ParticleSystem bulletHitEffectPrefab;
 
 
    // Start is called before the first frame update
    void Start()
    {
        CPUHP = maxCPUHP; //HPの初期値を最大にする
        HPBer.value = CPUHP;
    }

    void OnTriggerEnter(Collider other){
        Debug.Log("Hit");
        if(other.CompareTag("Bullet")){
            Debug.Log("Take Damage");
            CPUHP -= damage;

            bulletHitEffectPrefab.Play();

            //ぶつかってきたオブジェクトを破壊する.
            Destroy(other.gameObject);
        }

        if(CPUHP <= 0f) //hpが0以下になったら・・・
        {
            CPUHP = 0;
            PhotonNetwork.Instantiate("CPU", respawn, Quaternion.identity); //y座標のみ0の下でプレハブを生成

            Destroy(this.gameObject, 0f);
        }

        HPBer.value = CPUHP;
        Debug.Log(HPBer.value);
    }
 
    [PunRPC]
    public void TakeDamage(int _damage) //Playerへの当たり判定から呼び出されるメソッド
    {
        CPUHP -= _damage;
 
        if(CPUHP <= 0f) //hpが0以下になったら・・・
        {
            CPUHP = 0;
            PhotonNetwork.Instantiate("CPU", respawn, Quaternion.identity); //y座標のみ0の下でプレハブを生成
            
            Destroy(this.gameObject, 0f);
        }

        HPBer.value = CPUHP;
        Debug.Log(HPBer.value);
    }
}