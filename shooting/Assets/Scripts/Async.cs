// ----------------------------------------------------------------------------
// <copyright file="PhotonTransformView.cs" company="Exit Games GmbH">
//   PhotonNetwork Framework for Unity - Copyright (C) 2018 Exit Games GmbH
// </copyright>
// <summary>
//   Component to synchronize Transforms via PUN PhotonView.
// </summary>
// <author>developer@exitgames.com</author>
// ----------------------------------------------------------------------------

using UnityEngine;
using Photon.Pun;
using System;

[AddComponentMenu("Photon Networking/Photon Transform View")]
public class Async : MonoBehaviourPun, IPunObservable
{
    private float m_Distance;
    private float m_Angle;

    // private Vector3 m_Direction;
    // private Vector3 m_NetworkPosition;
    private Vector3 m_StoredPosition;
    private Vector3 m_StoredPosition1;
    private Vector3 m_StoredPosition2;

    private Quaternion m_NetworkRotation;

    public bool m_SynchronizePosition = true;
    public bool m_SynchronizeRotation = true;
    public bool m_SynchronizeScale = false;

    private forudp.UDP commUDPisMine = new forudp.UDP();
    private forudpwithCB.UdpWithCallback commUDPnotMine = new forudpwithCB.UdpWithCallback();

    // private bool callback = false;

    private DateTime dt;
    private float nowTime, lastTime;
    private float milSec;

    private float delayedTime;
    
    private Rigidbody rb;

    private float pos_x, pos_y, pos_z;
    private Vector3 delayedPosition;

    private Vector3 m_Vel;
    private Vector3 m_StoredVel;
    private Vector3 m_Accel;
    private Vector3 m_StoredAccel;

    private Vector3 pos;

    private float lag;

    [Tooltip("Indicates if localPosition and localRotation should be used. Scale ignores this setting, and always uses localScale to avoid issues with lossyScale.")]
    public bool m_UseLocal;

    bool m_firstTake = false;

    private float elapsedTime;
    private bool isPositionUpdate = false;

    private int action;
    private float change_second;
    private string data;

    private float distance;
    private Ray ray;
    private RaycastHit hit;

    private string position_x, position_y, position_z ,time, velocity_x, velocity_y ,velocity_z ,lagging ,targetDistance;

    private float sendTime, recieveTime, networkDelay;

    private int change_act, change_frame;
    private int preAct;

    private Vector3 firstVel, calcVel;

    private float RpcLag = 0f;
    private float rcvRpcLag = 0f;

    public static Async instance;
    private bool canShot;
    private float reachfiredtime = 0.001334f; //6.67(aite z 10 - zibun z 3.33) / 5000

    public void Awake()
    {
        Application.targetFrameRate = 30; // 30fpsに設定
        PhotonNetwork.SendRate = 60; // メッセージの送信頻度(回/s)
        PhotonNetwork.SerializationRate = 30; // OnPhotonSerializeView()を一秒間に何度呼ぶか

        m_StoredPosition = transform.localPosition;
        // m_NetworkPosition = Vector3.zero;

        m_NetworkRotation = Quaternion.identity;
        
        if(instance == null)
        {
            instance = this;
        }
    }

    void Start()
    {
        rb = this.GetComponent<Rigidbody>();

        if(photonView.IsMine){
            // commUDP.init(int型の送信用ポート番号, int型の送信先ポート番号, int型の受信用ポート番号);
            commUDPisMine.init(50023, 50020, 50024);
        }
        else{
            canShot = true;
            // commUDP.init(int型の送信用ポート番号, int型の送信先ポート番号, int型の受信用ポート番号);
            commUDPnotMine.init(50025, 50026, 50021);
            //UDP受信開始
            commUDPnotMine.start_receive();
        }
    }

    private void Reset()
    {
        // Only default to true with new instances. useLocal will remain false for old projects that are updating PUN.
        m_UseLocal = true;
    }

    void OnEnable()
    {
        m_firstTake = true;
    }

    public void GetRpcLag(int RpcExetime)
    {
        if(this.photonView.IsMine)
        {
            // 弾を発射した時刻から現在時刻までの経過時間を求める
            this.RpcLag = Mathf.Max(0f, unchecked(PhotonNetwork.ServerTimestamp - RpcExetime) / 1000f);
        }
        // else
        // {
        //     this.RpcLag = Mathf.Max(0f, unchecked(PhotonNetwork.ServerTimestamp - timestamp) / 1000f);
        // }
    }

    public void FixedUpdate()
    {
        var tr = transform;

        if (!this.photonView.IsMine)
        {
            dt = DateTime.Now;
            milSec = dt.Millisecond / 1000f;
            delayedTime = (dt.Minute * 60) + dt.Second + milSec;

            // this.networkDelay = delayedTime - this.sendTime;
            this.networkDelay = delayedTime - this.sendTime + this.rcvRpcLag/4;
            // this.networkDelay = delayedTime - this.sendTime + this.rcvRpcLag;
            // Debug.Log(this.networkDelay);
            // Debug.Log(this.rcvRpcLag);

            if(commUDPnotMine.callback)
            {
                string[] rcvData = commUDPnotMine.rcvMsg.Split(',');
                // Debug.Log(commUDP.rcvMsg);

                change_frame = int.Parse(rcvData[0]);
                change_act = int.Parse(rcvData[1]);

                if(this.m_Vel.x > 0)
                {
                    if(this.m_Vel.z == 0) preAct = 0;
                    else if(this.m_Vel.z > 0) preAct = 1;
                    else preAct = 7;
                }
                else if(this.m_Vel.x < 0)
                {
                    if(this.m_Vel.z == 0) preAct = 4;
                    else if(this.m_Vel.z > 0) preAct = 3;
                    else preAct = 5;
                }
                else
                {
                    if(this.m_Vel.z == 0) preAct = 8;
                    else if(this.m_Vel.z > 0) preAct = 2;
                    else preAct = 6;
                }

                if(change_frame / 30 >= this.networkDelay || preAct == change_act)
                {
                    // Debug.Log("DR");
                    if(this.isPositionUpdate)
                    {
                        pos = delayedPosition + this.m_Vel * this.networkDelay;
                        tr.position = Vector3.LerpUnclamped(delayedPosition, pos, 1); 
                        this.isPositionUpdate = false;
                    }
                    else
                    {
                        pos = tr.position + this.m_Vel * Time.deltaTime;
                        // Debug.Log(pos);
                        tr.position = Vector3.LerpUnclamped(tr.position, pos, 1); 
                        // Debug.Log(tr.position);
                    }   
                }
                else
                {
                    // Debug.Log("DRL");
                    // Debug.Log(change_frame);
                    // Debug.Log(preAct);
                    // Debug.Log(change_act);
                    if(change_act == 0)
                    {
                        Vector3 firstVel = new Vector3(0.8f, 0f, 0f);
                    }
                    else if(change_act == 4)
                    {
                        Vector3 firstVel = new Vector3(-0.8f, 0f, 0f);
                    }
                    else if(change_act == 2)
                    {
                        Vector3 firstVel = new Vector3(0f, 0f, 0.8f);
                    }
                    else if(change_act == 6)
                    {
                        Vector3 firstVel = new Vector3(0f, 0f, -0.8f);
                    }
                    else if(change_act == 1)
                    {
                        Vector3 firstVel = new Vector3(0.5657f, 0f, 0.5657f);
                    }
                    else if(change_act == 3)
                    {
                        Vector3 firstVel = new Vector3(-0.5657f, 0f, 0.5657f);
                    }
                    else if(change_act == 5)
                    {
                        Vector3 firstVel = new Vector3(-0.5657f, 0f, -0.5657f);
                    }
                    
                    else if(change_act == 7)
                    {
                        Vector3 firstVel = new Vector3(0.5657f, 0f, -0.5657f);
                    }
                    else if(change_act == 8)
                    {
                        Vector3 firstVel = new Vector3(0f, 0f, 0f);
                    }

                    if(this.isPositionUpdate)
                    {
                        pos = delayedPosition + this.m_Vel * change_frame / 30;

                        if(change_frame <= 5){
                            Vector3 calcVel = new Vector3(((firstVel.x + firstVel.x * change_frame) * change_frame / 2) / change_frame, 0, ((firstVel.z + firstVel.z * change_frame) * change_frame / 2) / change_frame);
                        }
                        else
                        {
                            Vector3 calcVel = new Vector3((firstVel.x + firstVel.x * change_frame) * change_frame / 2, 0, (firstVel.z + firstVel.z * change_frame) * change_frame / 2);
                            calcVel = (calcVel + firstVel*(change_frame - 6)) / change_frame;
                        }
                        if(calcVel.x > 4.8) calcVel.x = 4.8f;
                        else if(calcVel.x < -4.8) calcVel.x = -4.8f;

                        if(calcVel.z > 4.8) calcVel.z = 4.8f;
                        else if(calcVel.z < -4.8) calcVel.z = -4.8f;

                        pos = pos + calcVel * (this.networkDelay - change_frame / 30);
                        
                        tr.position = Vector3.LerpUnclamped(delayedPosition, pos, 1); 
                        this.isPositionUpdate = false;
                    }
                    else
                    {
                        pos = tr.position + this.m_Vel * change_frame / 30;

                        if(change_frame <= 5){
                            Vector3 calcVel = new Vector3(((firstVel.x + firstVel.x * change_frame) * change_frame / 2) / change_frame, 0, ((firstVel.z + firstVel.z * change_frame) * change_frame / 2) / change_frame);
                        }
                        else
                        {
                            Vector3 calcVel = new Vector3((firstVel.x + firstVel.x * change_frame) * change_frame / 2, 0, (firstVel.z + firstVel.z * change_frame) * change_frame / 2);
                            calcVel = (calcVel + firstVel*(change_frame - 6)) / change_frame;
                        }

                        if(calcVel.x > 4.8) calcVel.x = 4.8f;
                        else if(calcVel.x < -4.8) calcVel.x = -4.8f;

                        if(calcVel.z > 4.8) calcVel.z = 4.8f;
                        else if(calcVel.z < -4.8) calcVel.z = -4.8f;

                        pos = pos + calcVel * (this.networkDelay - change_frame / 30);
                        // Debug.Log(pos);
                        tr.position = Vector3.LerpUnclamped(tr.position, pos, 1); 
                        // Debug.Log(tr.position);
                    }
                }

                commUDPnotMine.callback = false;
            }
            else
            {
                if(this.isPositionUpdate)
                {
                    pos = delayedPosition + this.m_Vel * this.networkDelay;
                    tr.position = Vector3.LerpUnclamped(delayedPosition, pos, 1); 
                    this.isPositionUpdate = false;
                }
                else
                {
                    pos = tr.position + this.m_Vel * Time.deltaTime;
                    // Debug.Log(pos);
                    tr.position = Vector3.LerpUnclamped(tr.position, pos, 1); 
                    // Debug.Log(tr.position);
                }
            }

            // syncroplayercontroller
            if(canShot){
                // my bullet position x 2.265  player length 0.6
                if(this.m_Vel.x > 0){
                    if(1.965 - this.m_Vel.x * reachfiredtime < tr.position.x && tr.position.x < 2.565 - this.m_Vel.x * reachfiredtime && canShot){
                    // if(1.865 < positionX && positionX < 1.965 && GameState.canShoot){
                        Shoot.instance.Shot();
                        BulletControllerCopy.instance.shoot();
                        canShot = false;
                    }
                }
                else if(this.m_Vel.x < 0){
                    if(1.965 - this.m_Vel.x * reachfiredtime < tr.position.x && tr.position.x < 2.565 - this.m_Vel.x * reachfiredtime && canShot){
                    // if(2.565 < positionX && positionX < 2.665 && GameState.canShoot){
                        Shoot.instance.Shot();
                        BulletControllerCopy.instance.shoot();
                        canShot = false;
                    }
                }
            }
            else{
                if(tr.position.x < -3 || 8 < tr.position.x){
                    canShot = true;
                }
            }
            
            tr.rotation = Quaternion.RotateTowards(tr.rotation, this.m_NetworkRotation, this.m_Angle * Time.deltaTime *  PhotonNetwork.SerializationRate);
            this.m_StoredAccel = this.m_Accel;
            
            if(m_Vel.x > 0){
                if(m_Vel.z == 0){
                    // Rayの作成
                    ray = new Ray(transform.position, Vector3.right);
                }
                else if (m_Vel.z > 0){
                    ray = new Ray(transform.position, new Vector3 (1, 0, 1));
                }
                else{
                    ray = new Ray(transform.position, new Vector3 (1, 0, -1));
                }
                
            }
            else if(m_Vel.x == 0)
            {
                if(m_Vel.z > 0){
                    ray = new Ray(transform.position, new Vector3 (0, 0, 1));
                }
                else if (m_Vel.z < 0){
                    ray = new Ray(transform.position, new Vector3 (0, 0, -1));
                }
                else{
                    ray = new Ray(transform.position, new Vector3 (1, 0, 0));
                }
            }
            else
            {
                if(m_Vel.z == 0){
                    // Rayの作成
                    ray = new Ray(transform.position, Vector3.left);
                }
                else if (m_Vel.z > 0){
                    ray = new Ray(transform.position, new Vector3 (-1, 0, 1));
                }
                else{
                    ray = new Ray(transform.position, new Vector3 (-1, 0, -1));
                }
            }
            // Debug.DrawRay(ray.origin, ray.direction * 10, Color.red, 5, false);

            if (Physics.Raycast(ray, out hit)) // もしRayを投射して何らかのコライダーに衝突したら
            {
                // string name = hit.collider.gameObject.name; // 衝突した相手オブジェクトの名前を取得
                distance = hit.distance;
                // Debug.Log(name); // コンソールに表示
                // Debug.Log(distance);
            }

            position_x = delayedPosition.x.ToString("F6");
            // position_y = delayedPosition.y.ToString("F6");
            position_z = delayedPosition.z.ToString("F6");
            time = delayedTime.ToString("F6");

            velocity_x = this.m_Vel.x.ToString("F6");
            // velocity_y = this.m_Vel.y.ToString("F6");
            velocity_z = this.m_Vel.z.ToString("F6");
            // lagging = this.lag.ToString("F6");
            targetDistance = distance.ToString("F6");

            // data = "D" + "," + time + "," + position_x + "," + position_y + "," + position_z + "," + velocity_x + "," + velocity_y + "," + velocity_z + "," + lagging + "," + targetDistance + "," + networkDelay.ToString("F6") + "," + commUDPnotMine.rcvTime.ToString("F6") + "," + "true";

            // data = time + "," + this.sendTime.ToString("F6") + "," + commUDPnotMine.rcvTime.ToString("F6") + "," + position_x + "," + position_y + "," + position_z + "," + velocity_x + "," + velocity_y + "," + velocity_z + "," + lagging + "," + networkDelay.ToString("F6") + "," + targetDistance;

            // data = time + "," + this.sendTime.ToString("F6") + "," + position_x + "," + position_z + "," + velocity_x + "," + velocity_z + "," + networkDelay.ToString("F6") + "," + targetDistance;

            data = time + "," + position_x + "," + position_z + "," + velocity_x + "," + velocity_z + "," + targetDistance;                  

            commUDPnotMine.send(data);
        }

        else
        {
            // Debug.Log(this.rcvRpcLag);

            // dt = DateTime.Now;
            // milSec = dt.Millisecond / 1000f;
            // nowTime = (dt.Minute * 60) + dt.Second + milSec;

            // position_x = tr.position.x.ToString("F6");
            // // position_y = tr.position.y.ToString("F6");
            // position_z = tr.position.z.ToString("F6");
            // time = nowTime.ToString("F6");

            // velocity_x = this.m_Vel.x.ToString("F6");
            // // velocity_y = this.m_Vel.y.ToString("F6");
            // velocity_z = this.m_Vel.z.ToString("F6");

            // // data = time + "," + position_x + "," + position_y + "," + position_z + "," + velocity_x + "," + velocity_y + "," + velocity_z;
            // data = time + "," + position_x + "," + position_z + "," + velocity_x + "," + velocity_z;
    
            // commUDPisMine.send(data);

        }

    }

    public void OnPhotonSerializeView(PhotonStream stream, PhotonMessageInfo info)
    {
        var tr = transform;

        // Write
        if (stream.IsWriting)
        {
            if (this.m_SynchronizePosition)
            {
                if (m_UseLocal)
                {
                    dt = DateTime.Now;
                    milSec = dt.Millisecond / 1000f;
                    this.sendTime = (dt.Minute * 60) + dt.Second + milSec;
                    
                    this.m_StoredPosition2 = this.m_StoredPosition1;
                    this.m_StoredPosition1 = tr.position;
                    elapsedTime = this.sendTime - lastTime;

                    // this.m_Direction = tr.localPosition - this.m_StoredPosition;
                    this.m_StoredPosition = tr.localPosition;
                    this.m_Vel = (this.m_StoredPosition1 - this.m_StoredPosition2) / elapsedTime;
                    this.m_Accel = (this.m_Vel - this.m_StoredVel) / elapsedTime;

                    stream.SendNext(tr.localPosition);
                    // stream.SendNext(this.m_Direction);
                    stream.SendNext(this.m_Vel);
                    stream.SendNext(this.m_Accel);
                    stream.SendNext(this.RpcLag);

                    lastTime = this.sendTime;

                }
                else
                {
                    dt = DateTime.Now;
                    milSec = dt.Millisecond / 1000f;
                    this.sendTime = (dt.Minute * 60) + dt.Second + milSec;

                    this.m_StoredPosition2 = this.m_StoredPosition1;
                    this.m_StoredPosition1 = tr.position;
                    elapsedTime = this.sendTime - lastTime;

                    this.m_StoredPosition = tr.position;
                    // this.m_Direction = tr.position - this.m_StoredPosition;
                    this.m_Vel = (this.m_StoredPosition1 - this.m_StoredPosition2) / elapsedTime;
                    this.m_Accel = (this.m_Vel - this.m_StoredVel) / elapsedTime;

                    stream.SendNext(tr.position);
                    // stream.SendNext(this.m_Direction);
                    stream.SendNext(this.m_Vel);
                    stream.SendNext(this.m_Accel);
                    stream.SendNext(this.sendTime);
                    stream.SendNext(this.RpcLag);
                    
                    lastTime = this.sendTime;
                }
            }

            if (this.m_SynchronizeRotation)
            {
                if (m_UseLocal)
                {
                    stream.SendNext(tr.localRotation);
                }
                else
                {
                    stream.SendNext(tr.rotation);
                }
            }

            if (this.m_SynchronizeScale)
            {
                stream.SendNext(tr.localScale);
            }
        }
        // Read
        else
        {
            if (this.m_SynchronizePosition)
            {
                // this.lag = Mathf.Abs((float) (PhotonNetwork.Time - info.timestamp));

                this.delayedPosition = (Vector3)stream.ReceiveNext();
                // this.m_Direction = (Vector3)stream.ReceiveNext();
                this.m_Vel = (Vector3)stream.ReceiveNext();
                this.m_Accel = (Vector3)stream.ReceiveNext();
                this.sendTime = (float)stream.ReceiveNext();

                this.rcvRpcLag = (float)stream.ReceiveNext();

                this.isPositionUpdate = true;

                // if (m_firstTake)
                // {
                //     if (m_UseLocal)
                //         tr.localPosition = this.m_NetworkPosition;
                //     else
                //         tr.position = this.m_NetworkPosition;

                //     this.m_Distance = 0f;
                // }
                // else
                // {
                //     this.lag = Mathf.Abs((float)(PhotonNetwork.Time - info.SentServerTime));
                //     // Debug.Log("lag: " + this.lag); //addition

                //     this.m_NetworkPosition = this.delayedPosition + this.m_Direction * this.lag;
                //     if (m_UseLocal)
                //     {
                //         this.m_Distance = Vector3.Distance(tr.localPosition, this.m_NetworkPosition);
                //     }
                //     else
                //     {
                //         this.m_Distance = Vector3.Distance(tr.position, this.m_NetworkPosition);
                //     }
                // }

            }

            if (this.m_SynchronizeRotation)
            {
                this.m_NetworkRotation = (Quaternion)stream.ReceiveNext();

                if (m_firstTake)
                {
                    this.m_Angle = 0f;

                    if (m_UseLocal)
                    {
                        tr.localRotation = this.m_NetworkRotation;
                    }
                    else
                    {
                        tr.rotation = this.m_NetworkRotation;
                    }
                }
                else
                {
                    if (m_UseLocal)
                    {
                        this.m_Angle = Quaternion.Angle(tr.localRotation, this.m_NetworkRotation);
                    }
                    else
                    {
                        this.m_Angle = Quaternion.Angle(tr.rotation, this.m_NetworkRotation);
                    }
                }
            }

            if (this.m_SynchronizeScale)
            {
                tr.localScale = (Vector3)stream.ReceiveNext();
            }

            if (m_firstTake)
            {
                m_firstTake = false;
            }
        }
    }
}