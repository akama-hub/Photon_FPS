using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun;

 
public class PlayerController : MonoBehaviourPunCallbacks
{
    float speed = 3f;
    [SerializeField]private float WalkSpeed;
    [SerializeField]private float RunSpeed;
    // [SerializeField] private Transform spine;
    float x, z;
 
    [SerializeField]private float lookSensitivity = 3f; //Inspectorで調整可    
    Quaternion cameraRot, characterRot;
 
    //視点角度制限
    float minX = -40f, maxX = 40f;
 
    // エイム時の切り替え用
    // public GameObject mainCamera;
    GameObject mainCamera; 
    // public GameObject subCamera;
    //マウス感度調整用
    float Xsensitivity = 2f;
    float Ysensitivity = 2f;
 
    private Rigidbody rigidbody;

    bool cursorLock = true;

    public Animator animator; //アニメーション用

    private Vector3 past_position;

 
    // Start is called before the first frame update
    private void Start()
    {
        mainCamera = Camera.main.gameObject;// Main Camera(Game Object) の取得
        //カメラ、キャラクタカメラ角度取得
        cameraRot = mainCamera.transform.localRotation;
        characterRot = transform.localRotation;

        rigidbody = GetComponent<Rigidbody>();

        GameState.canShoot = true;
    }
 
    // Update is called once per frame
    private void Update()
    {
        if(!photonView.IsMine){
            // Debug.Log("This player is not made by me");
            return;
        }

        //マウス角度取得
        float xRot = Input.GetAxis("Mouse X") * Ysensitivity;
        float yRot = Input.GetAxis("Mouse Y") * Xsensitivity;

        //軸に対してどう回転するか
        cameraRot *= Quaternion.Euler(-yRot, 0, 0);
        characterRot *= Quaternion.Euler(0, xRot, 0);
 
        cameraRot = ClampRotation(cameraRot);

        mainCamera.transform.localRotation = cameraRot;
        transform.localRotation = characterRot;

        UpdateCursorLock();

        if(Mathf.Abs(x)>0 || Mathf.Abs(z)>0){
            if(!animator.GetBool("Walk")){
                animator.SetBool("Walk", true);
                speed = WalkSpeed;
            }
        }
        else if(animator.GetBool("Walk")){
            animator.SetBool("Walk", false);
        }

        if(z>0 && Input.GetKey(KeyCode.LeftShift)){
            // GetKeyは押している間、GetKeyDownは押して下がった時
            if(!animator.GetBool("Run")){
                animator.SetBool("Run", true);
                speed = RunSpeed;
            }
        }
        else if(animator.GetBool("Run")){
            animator.SetBool("Run", false);
            speed = WalkSpeed;
        }

        // if(Input.GetMouseButton(1)){
        //     subCamera.SetActive(true);
        //     //カメラのコンポーネントのみをfalseにする
        //     mainCamera.GetComponent<Camera>().enabled = false;
        // }
        // else if(subCamera.activeSelf){
        //     subCamera.SetActive(false);
        //     //カメラのコンポーネントのみをfalseにする
        //     mainCamera.GetComponent<Camera>().enabled = true;
        // }
    }
 
    private void FixedUpdate()
    {
        if(!photonView.IsMine){
            // Debug.Log("This player is not made by me");
            return;
        }

        x = 0;
        z = 0;

        //キーボード入力の取得
        x = Input.GetAxisRaw("Horizontal") * speed;
        z = Input.GetAxisRaw("Vertical") * speed;

        // Debug.Log(x);
        // Debug.Log(z);

        // transform.position += new Vector3(x, 0, z);
        //正面への移動
        // transform.position += cam.transform.forward * z + cam.transform.right * x;  
        this.rigidbody.velocity = mainCamera.transform.forward * z + mainCamera.transform.right * x;
    }

    void LateUpdate()
    {
        //　ボーンをカメラの角度を向かせる
        // RotateBone();
    }

    // void RotateBone() {
    //     //　腰のボーンの角度をカメラの向きにする
    //     spine.rotation = Quaternion.Euler (spine.eulerAngles.x+mainCamera.transform.localEulerAngles.x, spine.eulerAngles.y, spine.eulerAngles.z);
    // }

    public void UpdateCursorLock(){
        if(Input.GetKeyDown(KeyCode.Escape)){
            cursorLock = false;
        }
        else if(Input.GetMouseButton(0)){
            cursorLock = true;
        }

        if(cursorLock){
            Cursor.lockState = CursorLockMode.Locked;
        }
        else if(!cursorLock){
            Cursor.lockState = CursorLockMode.None;
        }
    }

    public Quaternion ClampRotation(Quaternion q){
        // q = (x, y, z, w)
        // x, y, z はベクトル , wはスカラー
        q.x /= q.w;
        q.y /= q.w;
        q.z /= q.w;
        q.w = 1f;

        //角度を求める
        float angleX = Mathf.Atan(q.x) * Mathf.Rad2Deg * 2f;
        //丸める
        angleX = Mathf.Clamp(angleX, minX, maxX);

        q.x = Mathf.Tan(angleX * Mathf.Deg2Rad * 0.5f);

        return q;
    }

}