using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Photon.Pun;
 
public class TakingDamage : MonoBehaviourPunCallbacks
{
    int maxPlayerHP = 100;
    public int PlayerHP;
    public Slider HPBer;

    [SerializeField] GameObject playerPrefab; //Inspectorで紐づけ
    [SerializeField] ParticleSystem bulletHitEffectPrefab;
    [SerializeField] int damage = 10;
 
 
    // Start is called before the first frame update
    void Start()
    {
        PlayerHP = maxPlayerHP; //HPの初期値を最大にする
        HPBer.value = PlayerHP;
    }

    void OnTriggerEnter(Collider other){
        Debug.Log("Hit");
        if(other.CompareTag("Bullet")){
            Debug.Log("Take Damage");
            PlayerHP -= damage;

            bulletHitEffectPrefab.Play();

            //ぶつかってきたオブジェクトを破壊する.
            Destroy(other.gameObject);
        }

        if(PlayerHP <= 0f) //hpが0以下になったら・・・
        {
            PlayerHP = 0;
            Destroy(this.gameObject, 0f);
            HPBer.value = PlayerHP;
            Debug.Log(HPBer.value);
            PhotonNetwork.LoadLevel("GameOver");
        }

        HPBer.value = PlayerHP;
        Debug.Log(HPBer.value);
    }
 
    [PunRPC]
    public void TakeDamage(int _damage) //Playerへの当たり判定から呼び出されるメソッド
    {
        PlayerHP -= _damage;
 
        if(PlayerHP <= 0f) //hpが0以下になったら・・・
        {
            PlayerHP = 0;
            GameState.GameOver = true;
            Destroy(playerPrefab, 0f);
            PhotonNetwork.LoadLevel("GameOver");
        }

        HPBer.value = PlayerHP;
        Debug.Log(HPBer.value);
    }
}