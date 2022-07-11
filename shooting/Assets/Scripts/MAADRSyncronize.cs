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
public class MAADRSyncronize : MonoBehaviourPun, IPunObservable
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
    private Vector3 m_StoredVel;
    private Vector3 m_Accel;
    private Vector3 m_StoredAccel;

    private Vector3 pos;

    private float elapsedTime;
    private bool isPositionUpdate = false;

    private float normV;
    private Vector3 crossV;
    private float normcrossV; 
    private float k;
    private Vector3 alpha;

    [Tooltip("Indicates if localPosition and localRotation should be used. Scale ignores this setting, and always uses localScale to avoid issues with lossyScale.")]
    public bool m_UseLocal;

    bool m_firstTake = false;

    public void Awake()
    {
        m_StoredPosition1 = transform.localPosition;
        m_StoredVel = Vector3.zero;
        m_StoredAccel = Vector3.zero;

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

            string position_x = tr.position.x.ToString("00.000000");
            string position_y = tr.position.y.ToString("00.000000");
            string position_z = tr.position.z.ToString("00.000000");
            // // string time = Time.time.ToString("0000.0000");
            string time = nowTime.ToString("F4");

            // string velocity_x = rb.velocity.x.ToString("00.000000");
            // string velocity_y = rb.velocity.y.ToString("00.000000");
            // string velocity_z = rb.velocity.z.ToString("00.000000");
            // string lagging = lag.ToString("0000.0000");
            // // Debug.Log(Time.time);
            // string data = "D" + "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y + "vz" + velocity_z + "l" + lagging;
            string data = "D" + "t" + time + "x" + position_x + "y" + position_y + "z" + position_z;

            // // string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y;
            // string data = "D" + "l" + lag.ToString("0000.0000");
            commUDPnotMine.send(data);

            string[] position = commUDPnotMine.rcvMsg.Split(',');
            // Debug.Log(commUDP.rcvMsg);

            if(commUDPnotMine.rcvMsg != "ini")
            { }
            else
            {
                if (m_UseLocal)
                {
                    tr.localPosition = Vector3.MoveTowards(tr.localPosition, this.m_NetworkPosition, this.m_Distance  * Time.deltaTime * PhotonNetwork.SerializationRate);

                    tr.localRotation = Quaternion.RotateTowards(tr.localRotation, this.m_NetworkRotation, this.m_Angle * Time.deltaTime * PhotonNetwork.SerializationRate);
                }
                else
                {
                    // Debug.Log(this.isPositionUpdate);
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
                        else{
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
                        // Debug.Log(this.m_Accel);
                        // Debug.Log(this.m_StoredAccel);
                        if(this.m_Accel == Vector3.zero)
                        {
                            pos = tr.position + this.m_Vel / PhotonNetwork.SerializationRate;
                        }
                        else if(this.m_Accel == this.m_StoredAccel)
                        {
                            pos = tr.position + this.m_Vel / PhotonNetwork.SerializationRate + (this.m_Accel * Mathf.Pow(1 / PhotonNetwork.SerializationRate, 2) / 2);
                        }
                        else{
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
                        tr.position = Vector3.Lerp(tr.position, pos, 1); 
                        // Debug.Log(tr.position);
                    }

                    tr.rotation = Quaternion.RotateTowards(tr.rotation, this.m_NetworkRotation, this.m_Angle * Time.deltaTime *  PhotonNetwork.SerializationRate);

                    this.m_StoredAccel = this.m_Accel;
                }
                
            }

            dt = DateTime.Now;

            milSec = dt.Millisecond / 1000f;
            nowTime = (dt.Minute * 60) + dt.Second + milSec;

            // // string position_x = tr.position.x.ToString("00.000000");
            // // string position_y = tr.position.y.ToString("00.000000");
            // // string position_z = tr.position.z.ToString("00.000000");
            // // // string time = Time.time.ToString("0000.0000");
            // // string time = nowTime.ToString("F3");

            // // string velocity_x = rb.velocity.x.ToString("00.000000");
            // // string velocity_y = rb.velocity.y.ToString("00.000000");
            // // string velocity_z = rb.velocity.z.ToString("00.000000");
            // // // Debug.Log(Time.time);
            // // string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y + "vz" + velocity_z;

            position_x = tr.position.x.ToString("00.000000");
            position_y = tr.position.y.ToString("00.000000");
            position_z = tr.position.z.ToString("00.000000");
            time = nowTime.ToString("F3");

            // velocity_x = rb.velocity.x.ToString("00.000000");
            // velocity_y = rb.velocity.y.ToString("00.000000");
            // velocity_z = rb.velocity.z.ToString("00.000000");
            data = "P" + "t" + time + "x" + position_x + "y" + position_y + "z" + position_z;
            // data = "P" + "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y + "vz" + velocity_z + "l" + lagging + "T" + Time.deltaTime.ToString("0.000000");
            // // string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y;
            commUDPnotMine.send(data);

        }
        else
        {
            dt = DateTime.Now;

            milSec = dt.Millisecond / 1000f;
            nowTime = (dt.Minute * 60) + dt.Second + milSec;

            string position_x = tr.position.x.ToString("00.000000");
            string position_y = tr.position.y.ToString("00.000000");
            string position_z = tr.position.z.ToString("00.000000");
            // string time = Time.time.ToString("0000.0000");
            string time = nowTime.ToString("F3");

            string velocity_x = rb.velocity.x.ToString("00.000000");
            string velocity_y = rb.velocity.y.ToString("00.000000");
            string velocity_z = rb.velocity.z.ToString("00.000000");
            // Debug.Log(Time.time);
            string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y + "vz" + velocity_z;
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
                    this.m_StoredVel = this.m_Vel;
                    this.m_Vel = (this.m_StoredPosition1 - this.m_StoredPosition2) / elapsedTime;
                    // Debug.Log(this.m_Vel);

                    this.m_Accel = (this.m_Vel - this.m_StoredVel) / elapsedTime;
                    // Debug.Log(this.m_Accel);


                    stream.SendNext(this.m_Direction);
                    stream.SendNext(tr.localPosition);
                    stream.SendNext(this.m_Vel);
                    stream.SendNext(this.m_Accel);

                    elapsedTime = 0f;
                }
                else
                {
                    this.m_Direction = tr.position - this.m_StoredPosition2;
                    this.m_StoredVel = this.m_Vel;
                    this.m_Vel = (this.m_StoredPosition1 - this.m_StoredPosition2) / elapsedTime;

                    this.m_Accel = (this.m_Vel - this.m_StoredVel) / elapsedTime;
                    // Debug.Log(this.m_Accel);


                    stream.SendNext(this.m_Direction);
                    stream.SendNext(tr.position);
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
                this.m_Direction = (Vector3)stream.ReceiveNext();
                this.delayedPosition = (Vector3)stream.ReceiveNext();
                this.m_Vel = (Vector3)stream.ReceiveNext();
                this.m_Accel = (Vector3)stream.ReceiveNext();
                // Debug.Log(this.m_Accel);

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
                    // Debug.Log("Lag: " + lag); //addition
                    this.m_NetworkPosition = delayedPosition + this.m_Direction * lag;

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