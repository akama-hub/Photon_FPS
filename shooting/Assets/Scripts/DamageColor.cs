using UnityEngine;
using UnityEngine.UI;

public class DamageColor : MonoBehaviour
{
    public Image img;

    public static DamageColor instance;
    public void Awake(){
        if(instance == null)
        {
            instance = this;
        }
    }

    // Start is called before the first frame update
    void Start()
    {
        // 透明にして見えなくする
        img.color = Color.clear;   
    }

    // Update is called once per frame
    void Update()
    {
        // 時間が経過するにつれて徐々に透明にする
        this.img.color = Color.Lerp(this.img.color, Color.clear, Time.deltaTime);
    }

    public virtual void DamageImage()
    {
        // *画面を赤塗りにする
        this.img.color = new Color(0.5f, 0f, 0f, 0.5f);
    }
}
