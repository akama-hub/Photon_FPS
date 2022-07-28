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
public class DRSyncronize : MonoBehaviourPun, IPunObservable
{
    private float m_Distance;
    private float m_Angle;

    private Vector3 m_Direction;
    private Vector3 m_NetworkPosition;
    private Vector3 m_StoredPosition;
    private Vector3 m_StoredPosition1;
    private Vector3 m_StoredPosition2;

    private Quaternion m_NetworkRotation;

    public bool m_SynchronizePosition = true;
    public bool m_SynchronizeRotation = true;
    public bool m_SynchronizeScale = false;

    private forudp.UDP commUDPisMine = new forudp.UDP();
    private forudp.UDP commUDPnotMine = new forudp.UDP();

    private DateTime dt;
    private float nowTime;
    private float milSec;
    
    private Rigidbody rb;

    private float pos_x, pos_y, pos_z;
    private Vector3 delayedPosition;

    private float lag;
    // private float fixedDelay = 0.0364f;
    // private float fixedDelay = 0.046f;
    private float fixedDelay = 0.0974f;

    private Vector3 m_Vel;

    private float elapsedTime;
    private bool isPositionUpdate = false;

    [Tooltip("Indicates if localPosition and localRotation should be used. Scale ignores this setting, and always uses localScale to avoid issues with lossyScale.")]
    public bool m_UseLocal;

    bool m_firstTake = false;
    string check;
    private float rcvTime;
    private float RTT;

    // private Vector3 predictPosition;

    public void Awake()
    {
        Application.targetFrameRate = 30; // 30fpsに設定
        PhotonNetwork.SendRate = 60; // メッセージの送信頻度(回/s)
        PhotonNetwork.SerializationRate = 30; // OnPhotonSerializeView()を一秒間に何度呼ぶか

        m_StoredPosition1 = transform.localPosition;
        m_NetworkPosition = Vector3.zero;

        elapsedTime = 0f;

        m_NetworkRotation = Quaternion.identity;
    }

    void Start()
    {
        rb = this.GetComponent<Rigidbody>();

        if(photonView.IsMine){
            // commUDP.init(int型の送信用ポート番号, int型の送信先ポート番号, int型の受信用ポート番号);
            commUDPisMine.init(50023, 50020, 50024);
        }
        else{
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

    public void Update()
    {
        var tr = transform;

        if (!this.photonView.IsMine)
        {
            dt = DateTime.Now;
            milSec = dt.Millisecond / 1000f;
            nowTime = (dt.Minute * 60) + dt.Second + milSec;

            RTT = nowTime - rcvTime;

            if (m_UseLocal)
            {
                tr.localPosition = Vector3.MoveTowards(tr.localPosition, this.m_NetworkPosition, this.m_Distance  * Time.deltaTime * PhotonNetwork.SerializationRate);

                tr.localRotation = Quaternion.RotateTowards(tr.localRotation, this.m_NetworkRotation, this.m_Angle * Time.deltaTime * PhotonNetwork.SerializationRate);
            }
            else
            {
                if(this.isPositionUpdate){
                    // predictPosition = delayedPosition + this.m_Vel * lag;
                    tr.position = Vector3.LerpUnclamped(delayedPosition, delayedPosition + this.m_Vel * lag, 1);
                    // tr.position = Vector3.LerpUnclamped(delayedPosition, delayedPosition + this.m_Vel * RTT, 1);
                    this.isPositionUpdate = false;
                    // tr.position = Vector3.LerpUnclamped(delayedPosition, delayedPosition + m_Vel * lag, 1);
                    check = "true";
                }
                else
                {
                    // predictPosition = tr.position + this.m_Vel * lag;
                    tr.position = Vector3.LerpUnclamped(tr.position, tr.position + this.m_Vel * 1 / PhotonNetwork.SerializationRate, 1);
                    // SerializationRate -> OnPhotonSerializeView が一秒間に何回呼ばれるか
                    check = "false";
                }
                tr.rotation = Quaternion.RotateTowards(tr.rotation, this.m_NetworkRotation, this.m_Angle * Time.deltaTime *  PhotonNetwork.SerializationRate);
                
            }

            string position_x = tr.position.x.ToString("F6");
            string position_y = tr.position.y.ToString("F6");
            string position_z = tr.position.z.ToString("F6");
            string time = nowTime.ToString("F4");
            string lagging = lag.ToString("F6");
            
            // data = "P" + "," + time + "," + position_x + "," + position_y + "," + position_z;
            // string data = time + "," + position_x + "," + position_y + "," + position_z + "," + lag + "," + RTT + "," + check;
            // Debug.Log(tr.position);
            // Debug.Log(predictPosition);
            string data = time + "," + position_x + "," + position_y + "," + position_z + "," + lag + "," + RTT + "," + delayedPosition.x.ToString("F6")  + "," + delayedPosition.y.ToString("F6") + "," + delayedPosition.z.ToString("F6");
            commUDPnotMine.send(data);
        }
        else
        {
            dt = DateTime.Now;

            milSec = dt.Millisecond / 1000f;
            nowTime = (dt.Minute * 60) + dt.Second + milSec;

            string position_x = tr.position.x.ToString("F6");
            string position_y = tr.position.y.ToString("F6");
            string position_z = tr.position.z.ToString("F6");
            // string time = Time.time.ToString("0000.0000");
            string time = nowTime.ToString("F4");

            // string velocity_x = rb.velocity.x.ToString("F6");
            // string velocity_y = rb.velocity.y.ToString("F6");
            // string velocity_z = rb.velocity.z.ToString("F6");
            // Debug.Log(Time.time);
            string data = time + "," + position_x + "," + position_y + "," + position_z;
            // string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y;
            commUDPisMine.send(data);
            
            this.m_StoredPosition2 = this.m_StoredPosition1;
            this.m_StoredPosition1 = tr.position;
            elapsedTime += Time.deltaTime;
            
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
                    this.m_Direction = tr.localPosition - this.m_StoredPosition2;
                    this.m_Vel = (this.m_StoredPosition1 - this.m_StoredPosition2) / elapsedTime;

                    
                    stream.SendNext(tr.localPosition);
                    stream.SendNext(this.m_Direction);
                    stream.SendNext(this.m_Vel);

                    elapsedTime = 0f;
                }
                else
                {
                    this.m_Direction = tr.position - this.m_StoredPosition2;
                    this.m_Vel = (this.m_StoredPosition1 - this.m_StoredPosition2) / elapsedTime;

                    stream.SendNext(tr.position);
                    stream.SendNext(this.m_Direction);
                    stream.SendNext(this.m_Vel);

                    elapsedTime = 0f;
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
                this.delayedPosition = (Vector3)stream.ReceiveNext();
                this.m_Direction = (Vector3)stream.ReceiveNext();
                this.m_Vel = (Vector3)stream.ReceiveNext();

                this.isPositionUpdate = true;

                if (m_firstTake)
                {
                    if (m_UseLocal)
                        tr.localPosition = this.m_NetworkPosition;
                    else
                        tr.position = this.m_NetworkPosition;

                    this.m_Distance = 0f;
                }
                else
                {
                    lag = Mathf.Abs((float)(PhotonNetwork.Time - info.SentServerTime));
                    
                    dt = DateTime.Now;
                    milSec = dt.Millisecond / 1000f;
                    this.rcvTime = (dt.Minute * 60) + dt.Second + milSec;

                    this.m_NetworkPosition = this.delayedPosition + this.m_Direction * lag;

                    if (m_UseLocal)
                    {
                        this.m_Distance = Vector3.Distance(tr.localPosition, this.m_NetworkPosition);
                    }
                    else
                    {
                        this.m_Distance = Vector3.Distance(tr.position, this.m_NetworkPosition);
                    }
                    
                }

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