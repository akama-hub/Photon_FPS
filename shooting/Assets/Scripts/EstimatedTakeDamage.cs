using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Photon.Pun;
 
public class EstimatedTakeDamage : MonoBehaviour
{
    int maxCPUHP = 100;
    public int CPUHP;
    public Slider selfHPBer;
    int damage = 10;

    [SerializeField] ParticleSystem bulletHitEffectPrefab;

    [SerializeField] public GameObject CPUUI;
 
 
    // Start is called before the first frame update
    void Start()
    {
        CPUHP = maxCPUHP; //HPの初期値を最大にする
    }

    void OnTriggerEnter(Collider other){
        Debug.Log("Hit");
        if(other.CompareTag("Bullet")){
            Debug.Log("Take Damage");
            CPUHP -= damage;

            bulletHitEffectPrefab.Play();
        }

        if(CPUHP <= 0f) //hpが0以下になったら・・・
        {
            CPUHP = 0;
            Destroy(this.gameObject, 0f);
        }

        selfHPBer.value = CPUHP;
    }
 
    [PunRPC]
    public void TakeDamage(int _damage) //Playerへの当たり判定から呼び出されるメソッド
    {
        CPUHP -= _damage;
 
        if(CPUHP <= 0f) //hpが0以下になったら・・・
        {
            CPUHP = 0;
            Destroy(this.gameObject, 0f);
        }
    }
}