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
public class SelfSyncronize : MonoBehaviourPun, IPunObservable
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
    private forudpwithCB.UdpWithCallback commUDPnotMine = new forudpwithCB.UdpWithCallback();

    private bool callback = false;

    private DateTime dt;
    private float nowTime;
    private float milSec;
    
    private Rigidbody rb;

    private float pos_x, pos_y, pos_z;
    private Vector3 delayedPosition;

    private Vector3 m_Vel;
    private Vector3 m_StoredVel;
    private Vector3 m_Accel;
    private Vector3 m_StoredAccel;

    private Vector3 pos;

    private float lag;
    private float processingDelay = 0.02f;

    [Tooltip("Indicates if localPosition and localRotation should be used. Scale ignores this setting, and always uses localScale to avoid issues with lossyScale.")]
    public bool m_UseLocal;

    bool m_firstTake = false;

    private float elapsedTime;
    private bool isPositionUpdate = false;

    private float normV;
    private Vector3 crossV;
    private float normcrossV; 
    private float k;
    private Vector3 alpha;

    private int action;
    private float change_second;
    private string data;

    public void Awake()
    {
        Application.targetFrameRate = 30; // 30fpsに設定
        PhotonNetwork.SendRate = 120; // メッセージの送信頻度(回/s)
        PhotonNetwork.SerializationRate = 90; // OnPhotonSerializeView()を一秒間に何度呼ぶか

        m_StoredPosition = transform.localPosition;
        m_NetworkPosition = Vector3.zero;

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
            commUDPnotMine.init(50025, 50026, 50021, callback);
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

            string position_x = delayedPosition.x.ToString("F6");
            string position_y = delayedPosition.y.ToString("F6");
            string position_z = delayedPosition.z.ToString("F6");
            string time = nowTime.ToString("F4");

            string velocity_x = this.m_Vel.x.ToString("F6");
            string velocity_y = this.m_Vel.y.ToString("F6");
            string velocity_z = this.m_Vel.z.ToString("F6");
            string lagging = this.lag.ToString("F6");
            
            // string data = "D" + "," + time + "," + position_x + "," + position_y + "," + position_z + "," + velocity_x + "," + velocity_y + "," + velocity_z + "," + lagging;
            if(isPositionUpdate){
                data = "D" + "," + time + "," + position_x + "," + position_y + "," + position_z + "," + velocity_x + "," + velocity_y + "," + velocity_z + "," + lagging + "," + "true";
            }
            else
            {
                data = "D" + "," + time + "," + position_x + "," + position_y + "," + position_z + "," + velocity_x + "," + velocity_y + "," + velocity_z + "," + lagging + "," + "false";
            }
            
            commUDPnotMine.send(data);

            if(callback)
            {
                string[] position = commUDPnotMine.rcvMsg.Split(',');
                // Debug.Log(commUDP.rcvMsg);

                action = int.Parse(position[0]);
                change_second = float.Parse(position[1]);

                if(this.isPositionUpdate)
                {
                    if(this.m_Accel == Vector3.zero)
                    {
                        pos = delayedPosition + this.m_Vel * change_second;
                    }
                    else if(this.m_Accel == this.m_StoredAccel)
                    {
                        pos = delayedPosition + this.m_Vel * lag + (this.m_Accel * Mathf.Pow(lag, 2) / 2);
                    }
                    else
                    {
                        normV = this.m_Vel.magnitude;
                        crossV =  Vector3.Cross(this.m_Vel, this.m_Accel);
                        normcrossV = crossV.magnitude; 
                        k = normcrossV / Mathf.Pow(normV, 3);
                        if(k == 0f)
                        {
                            pos = delayedPosition + this.m_Vel * lag + (this.m_Accel * Mathf.Pow(lag, 2)/ 2);
                        }
                        else
                        {
                            alpha = k * Mathf.Pow(normV, 2) * this.m_Vel / normV;

                            pos = delayedPosition + this.m_Vel * lag + (alpha * Mathf.Pow(lag, 2) / 2);
                        }
                    }
                    
                    tr.position = Vector3.LerpUnclamped(delayedPosition, pos, 1); 
                    this.isPositionUpdate = false;

                }
                else
                {
                    if(this.m_Accel == Vector3.zero)
                    {
                        pos = tr.position + this.m_Vel / PhotonNetwork.SerializationRate;
                    }
                    else if(this.m_Accel == this.m_StoredAccel)
                    {
                        pos = tr.position + this.m_Vel / PhotonNetwork.SerializationRate + (this.m_Accel * Mathf.Pow(1 / PhotonNetwork.SerializationRate, 2) / 2);
                    }
                    else
                    {
                        normV = this.m_Vel.magnitude;
                        crossV =  Vector3.Cross(this.m_Vel, this.m_Accel);
                        normcrossV = crossV.magnitude; 
                        k = normcrossV / Mathf.Pow(normV, 3);
                        if(k == 0f)
                        {
                            pos = tr.position + this.m_Vel / PhotonNetwork.SerializationRate + (this.m_Accel * Mathf.Pow(1 / PhotonNetwork.SerializationRate, 2) / 2);
                        }
                        else
                        {
                            alpha = k * Mathf.Pow(normV, 2) * this.m_Vel / normV;

                            pos = tr.position + this.m_Vel / PhotonNetwork.SerializationRate + (alpha * Mathf.Pow(1 / PhotonNetwork.SerializationRate, 2) / 2);
                        }
                    }

                    // Debug.Log(pos);
                    tr.position = Vector3.LerpUnclamped(tr.position, pos, 1); 
                    // Debug.Log(tr.position);
                }

                callback = false;
            }
            else
            {
                if(this.isPositionUpdate)
                {
                    if(this.m_Accel == Vector3.zero)
                    {
                        pos = delayedPosition + this.m_Vel * lag;
                    }
                    else if(this.m_Accel == this.m_StoredAccel)
                    {
                        pos = delayedPosition + this.m_Vel * lag + (this.m_Accel * Mathf.Pow(lag, 2) / 2);
                    }
                    else
                    {
                        normV = this.m_Vel.magnitude;
                        crossV =  Vector3.Cross(this.m_Vel, this.m_Accel);
                        normcrossV = crossV.magnitude; 
                        k = normcrossV / Mathf.Pow(normV, 3);
                        if(k == 0f)
                        {
                            pos = delayedPosition + this.m_Vel * lag + (this.m_Accel * Mathf.Pow(lag, 2)/ 2);
                        }
                        else
                        {
                            alpha = k * Mathf.Pow(normV, 2) * this.m_Vel / normV;

                            pos = delayedPosition + this.m_Vel * lag + (alpha * Mathf.Pow(lag, 2) / 2);
                        }
                    }
                    
                    tr.position = Vector3.LerpUnclamped(delayedPosition, pos, 1); 
                    this.isPositionUpdate = false;

                }
                else
                {
                    if(this.m_Accel == Vector3.zero)
                    {
                        pos = tr.position + this.m_Vel / PhotonNetwork.SerializationRate;
                    }
                    else if(this.m_Accel == this.m_StoredAccel)
                    {
                        pos = tr.position + this.m_Vel / PhotonNetwork.SerializationRate + (this.m_Accel * Mathf.Pow(1 / PhotonNetwork.SerializationRate, 2) / 2);
                    }
                    else
                    {
                        normV = this.m_Vel.magnitude;
                        crossV =  Vector3.Cross(this.m_Vel, this.m_Accel);
                        normcrossV = crossV.magnitude; 
                        k = normcrossV / Mathf.Pow(normV, 3);
                        if(k == 0f)
                        {
                            pos = tr.position + this.m_Vel / PhotonNetwork.SerializationRate + (this.m_Accel * Mathf.Pow(1 / PhotonNetwork.SerializationRate, 2) / 2);
                        }
                        else
                        {
                            alpha = k * Mathf.Pow(normV, 2) * this.m_Vel / normV;

                            pos = tr.position + this.m_Vel / PhotonNetwork.SerializationRate + (alpha * Mathf.Pow(1 / PhotonNetwork.SerializationRate, 2) / 2);
                        }
                    }

                    // Debug.Log(pos);
                    tr.position = Vector3.LerpUnclamped(tr.position, pos, 1); 
                    // Debug.Log(tr.position);
                }
            }

            tr.rotation = Quaternion.RotateTowards(tr.rotation, this.m_NetworkRotation, this.m_Angle * Time.deltaTime *  PhotonNetwork.SerializationRate);

            this.m_StoredAccel = this.m_Accel;

            dt = DateTime.Now;

            milSec = dt.Millisecond / 1000f;
            nowTime = (dt.Minute * 60) + dt.Second + milSec;

            position_x = tr.position.x.ToString("00.000000");
            position_y = tr.position.y.ToString("00.000000");
            position_z = tr.position.z.ToString("00.000000");
            time = nowTime.ToString("F4");

            // data = "P" + "t" + time + "x" + position_x + "y" + position_y + "z" + position_z;
            data = "P" + "," + time + "," + position_x + "," + position_y + "," + position_z + "," + pos_x + "," + pos_y + "," + pos_z;

            // commUDPnotMine.send(data);

        }
        else
        {
            dt = DateTime.Now;

            milSec = dt.Millisecond / 1000f;
            nowTime = (dt.Minute * 60) + dt.Second + milSec;

            string position_x = tr.position.x.ToString("00.000000");
            string position_y = tr.position.y.ToString("00.000000");
            string position_z = tr.position.z.ToString("00.000000");
            string time = nowTime.ToString("F4");

            string velocity_x = rb.velocity.x.ToString("00.000000");
            string velocity_y = rb.velocity.y.ToString("00.000000");
            string velocity_z = rb.velocity.z.ToString("00.000000");
            // Debug.Log(Time.time);
            string data = time + "," + position_x + "," + position_y + "," + position_z + "," + velocity_x + "," + velocity_y + "," + velocity_z;

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
                    this.m_Direction = tr.localPosition - this.m_StoredPosition;
                    this.m_StoredPosition = tr.localPosition;
                    this.m_Vel = (this.m_StoredPosition1 - this.m_StoredPosition2) / elapsedTime;
                    this.m_Accel = (this.m_Vel - this.m_StoredVel) / elapsedTime;

                    stream.SendNext(tr.localPosition);
                    stream.SendNext(this.m_Direction);
                    stream.SendNext(this.m_Vel);
                    stream.SendNext(this.m_Accel);

                    elapsedTime = 0f;
                }
                else
                {
                    this.m_StoredPosition = tr.position;
                    this.m_Direction = tr.position - this.m_StoredPosition;
                    this.m_Vel = (this.m_StoredPosition1 - this.m_StoredPosition2) / elapsedTime;
                    this.m_Accel = (this.m_Vel - this.m_StoredVel) / elapsedTime;

                    stream.SendNext(tr.position);
                    stream.SendNext(this.m_Direction);
                    stream.SendNext(this.m_Vel);
                    stream.SendNext(this.m_Accel);

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
                this.m_Accel = (Vector3)stream.ReceiveNext();

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
                    this.lag = Mathf.Abs((float)(PhotonNetwork.Time - info.SentServerTime));
                    // Debug.Log("lag: " + this.lag); //addition

                    this.m_NetworkPosition = this.delayedPosition + this.m_Direction * this.lag;
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