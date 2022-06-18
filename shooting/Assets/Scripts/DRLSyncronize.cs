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

public class DRLSyncronize : MonoBehaviourPun, IPunObservable
{
    private float m_Distance;
    private float m_Angle;

    private Vector3 m_Direction;
    private Vector3 m_NetworkPosition;
    private Vector3 m_StoredPosition;

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

    private Vector3 delayedPosition;

    private float lag;

    [Tooltip("Indicates if localPosition and localRotation should be used. Scale ignores this setting, and always uses localScale to avoid issues with lossyScale.")]
    public bool m_UseLocal;

    private int lastAction = 0;

    bool m_firstTake = false;

    private float firstSpeed = 2.6248f;
    private Vector3 m_Vel;

    private float frame_delay = 0;

    public void Awake()
    {
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

            string position_x = delayedPosition.x.ToString("00.000000");
            string position_y = delayedPosition.y.ToString("00.000000");
            string position_z = delayedPosition.z.ToString("00.000000");
            // string time = Time.time.ToString("0000.0000");
            string time = nowTime.ToString("F3");

            string velocity_x = rb.velocity.x.ToString("00.000000");
            string velocity_y = rb.velocity.y.ToString("00.000000");
            string velocity_z = rb.velocity.z.ToString("00.000000");
            string lagging = lag.ToString("0000.0000");
            // Debug.Log(Time.time);
            string data = "D" + "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y + "vz" + velocity_z ;
            // string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y;
            commUDPnotMine.send(data);

            string[] position = commUDPnotMine.rcvMsg.Split(',');
            // Debug.Log(commUDP.rcvMsg);

            if(commUDPnotMine.rcvMsg != "ini"){

                Vector3 pos = delayedPosition;
                
                int action = int.Parse(position[0]);
                float NframesChange = float.Parse(position[1]);

                // Debug.Log(action);
                // Debug.Log(NframesChange);
                
                if (m_UseLocal)
                {
                    tr.localPosition = Vector3.MoveTowards(tr.localPosition, this.m_NetworkPosition, this.m_Distance  * Time.deltaTime * PhotonNetwork.SerializationRate);
                    tr.localRotation = Quaternion.RotateTowards(tr.localRotation, this.m_NetworkRotation, this.m_Angle * Time.deltaTime * PhotonNetwork.SerializationRate);
                }
                else
                {
                    if(Time.deltaTime != 0)
                    {
                        frame_delay = lag / Time.deltaTime;
                    }
                    else
                    {

                    }
                    // Debug.Log(lag);
                    // Debug.Log(Time.deltaTime);
                    // Debug.Log(delayedPosition);
                    // Debug.Log(pos);                

                    if (NframesChange >= frame_delay){
                        pos.x = tr.position.x + this.m_Vel.x * lag;
                        pos.z = tr.position.z + this.m_Vel.z * lag;

                        tr.rotation = Quaternion.RotateTowards(tr.rotation, this.m_NetworkRotation, this.m_Angle * Time.deltaTime *  PhotonNetwork.SerializationRate);
                    }
                    else
                    {
                        if(action == 0)
                        {
                            pos.x = tr.position.x + this.m_Vel.x * NframesChange * Time.deltaTime;
                            pos.z = tr.position.z + this.m_Vel.z * NframesChange * Time.deltaTime;
                        }
                        else if (action == 1)
                        {
                            if(lastAction == 1 || lastAction == 6 || lastAction == 8)
                            {
                                pos.x = tr.position.x + this.m_Vel.x * lag;
                                pos.z = tr.position.z + this.m_Vel.z * NframesChange * Time.deltaTime;
                            }
                            else
                            {
                                pos.x = tr.position.x + this.m_Vel.x * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                                pos.z = tr.position.z + this.m_Vel.z * NframesChange * Time.deltaTime;
                            }
                        }
                        else if (action == 2)
                        {
                            if(lastAction == 2 || lastAction == 5 || lastAction == 7)
                            {
                                pos.x = tr.position.x + this.m_Vel.x * lag;
                                pos.z = tr.position.z + this.m_Vel.z * NframesChange * Time.deltaTime;
                            }
                            else
                            {
                                pos.x = tr.position.x + this.m_Vel.x * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                                pos.z = tr.position.z + this.m_Vel.z * NframesChange * Time.deltaTime;
                            }
                        }
                        else if (action == 3)
                        {
                            if(lastAction == 3 || lastAction == 5 || lastAction == 6)
                            {
                                pos.x = tr.position.x + this.m_Vel.x * NframesChange * Time.deltaTime;
                                pos.z = tr.position.z + this.m_Vel.z * lag;
                            }
                            else
                            {
                                pos.x = tr.position.x + this.m_Vel.x  * NframesChange * Time.deltaTime;
                                pos.z = tr.position.z + this.m_Vel.z * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                            }
                        }
                        else if (action == 4)
                        {
                            if(lastAction == 4 || lastAction == 7 || lastAction == 8)
                            {
                                pos.x = tr.position.x + this.m_Vel.x * NframesChange * Time.deltaTime;
                                pos.z = tr.position.z + this.m_Vel.z * lag;
                            }
                            else
                            {
                                pos.x = tr.position.x + this.m_Vel.x  * NframesChange * Time.deltaTime;
                                pos.z = tr.position.z + this.m_Vel.z * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                            }
                        }
                        else if (action == 5)
                        {
                            if(lastAction == action){
                                pos.x = tr.position.x + this.m_Vel.x * lag;
                                pos.z = tr.position.z + this.m_Vel.z * lag;
                            }
                            else if(lastAction == 2 || lastAction == 7)
                            {
                                pos.x = tr.position.x + this.m_Vel.x * lag;
                                pos.z = tr.position.z + this.m_Vel.z * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                            }
                            else if(lastAction == 3 || lastAction == 6)
                            {
                                pos.x = tr.position.x + this.m_Vel.x * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                                pos.z = tr.position.z + this.m_Vel.z * lag;
                            }
                            else
                            {
                                pos.x = tr.position.x + this.m_Vel.x * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                                pos.z = tr.position.z + this.m_Vel.z * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                            }
                        }
                        else if (action == 6)
                        {
                            if(lastAction == action){
                                pos.x = tr.position.x + this.m_Vel.x * lag;
                                pos.z = tr.position.z + this.m_Vel.z * lag;
                            }
                            else if(lastAction == 1 || lastAction == 8)
                            {
                                pos.x = tr.position.x + this.m_Vel.x * lag;
                                pos.z = tr.position.z + this.m_Vel.z * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                            }
                            else if(lastAction == 3 || lastAction == 5)
                            {
                                pos.x = tr.position.x + this.m_Vel.x * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                                pos.z = tr.position.z + this.m_Vel.z * lag;
                            }
                            else
                            {
                                pos.x = tr.position.x + this.m_Vel.x * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                                pos.z = tr.position.z + this.m_Vel.z * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                            }
                        }
                        else if (action == 7)
                        {
                            if(lastAction == action){
                                pos.x = tr.position.x + this.m_Vel.x * lag;
                                pos.z = tr.position.z + this.m_Vel.z * lag;
                            }
                            else if(lastAction == 2 || lastAction == 5)
                            {
                                pos.x = tr.position.x + this.m_Vel.x * lag;
                                pos.z = tr.position.z + this.m_Vel.z * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                            }
                            else if(lastAction == 4 || lastAction == 8)
                            {
                                pos.x = tr.position.x + this.m_Vel.x * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                                pos.z = tr.position.z + this.m_Vel.z * lag;
                            }
                            else
                            {
                                pos.x = tr.position.x + this.m_Vel.x * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                                pos.z = tr.position.z + this.m_Vel.z * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                            }
                        }
                        else if (action == 8)
                        {
                            if(lastAction == action){
                                pos.x = tr.position.x + this.m_Vel.x * lag;
                                pos.z = tr.position.z + this.m_Vel.z * lag;
                            }
                            else if(lastAction == 1 || lastAction == 6)
                            {
                                pos.x = tr.position.x + this.m_Vel.x * lag;
                                pos.z = tr.position.z + this.m_Vel.z * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                            }
                            else if(lastAction == 4 || lastAction == 7)
                            {
                                pos.x = tr.position.x + this.m_Vel.x * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                                pos.z = tr.position.z + this.m_Vel.z * lag;
                            }
                            else
                            {
                                pos.x = tr.position.x + this.m_Vel.x * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                                pos.z = tr.position.z + this.m_Vel.z * NframesChange * Time.deltaTime + firstSpeed * (lag - NframesChange * Time.deltaTime);
                            }
                        }

                    }
                    lastAction = action;
                    // Debug.Log(pos);
                    if(lag != 0){
                        tr.position = Vector3.LerpUnclamped(delayedPosition, pos, 1 + Time.deltaTime/lag);
                    }
                    else
                    {
                        tr.position = Vector3.MoveTowards(tr.position, this.m_NetworkPosition, this.m_Distance * Time.deltaTime * PhotonNetwork.SerializationRate);
                    }
                }
                
                
            }
            else{
                if (m_UseLocal)
                {
                    tr.localPosition = Vector3.MoveTowards(tr.localPosition, this.m_NetworkPosition, this.m_Distance  * Time.deltaTime * PhotonNetwork.SerializationRate);
                    tr.localRotation = Quaternion.RotateTowards(tr.localRotation, this.m_NetworkRotation, this.m_Angle * Time.deltaTime * PhotonNetwork.SerializationRate);
                }
                else
                {
                    tr.position = Vector3.MoveTowards(tr.position, this.m_NetworkPosition, this.m_Distance * Time.deltaTime * PhotonNetwork.SerializationRate);
                    tr.rotation = Quaternion.RotateTowards(tr.rotation, this.m_NetworkRotation, this.m_Angle * Time.deltaTime *  PhotonNetwork.SerializationRate);
                }
            }

            dt = DateTime.Now;

            milSec = dt.Millisecond / 1000f;
            nowTime = (dt.Minute * 60) + dt.Second + milSec;

            // string position_x = tr.position.x.ToString("00.000000");
            // string position_y = tr.position.y.ToString("00.000000");
            // string position_z = tr.position.z.ToString("00.000000");
            // // string time = Time.time.ToString("0000.0000");
            // string time = nowTime.ToString("F3");

            // string velocity_x = rb.velocity.x.ToString("00.000000");
            // string velocity_y = rb.velocity.y.ToString("00.000000");
            // string velocity_z = rb.velocity.z.ToString("00.000000");
            // // Debug.Log(Time.time);
            // string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y + "vz" + velocity_z;

            position_x = tr.position.x.ToString("00.000000");
            position_y = tr.position.y.ToString("00.000000");
            position_z = tr.position.z.ToString("00.000000");
            time = nowTime.ToString("F3");

            velocity_x = rb.velocity.x.ToString("00.000000");
            velocity_y = rb.velocity.y.ToString("00.000000");
            velocity_z = rb.velocity.z.ToString("00.000000");
            data = "P" + "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y + "vz" + velocity_z + "l" + lagging + "T" + Time.deltaTime.ToString("0.000000");
            // string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y;
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
                    stream.SendNext(tr.localPosition);
                    stream.SendNext(this.m_Direction);
                }
                else
                {
                    this.m_Direction = tr.position - this.m_StoredPosition;
                    this.m_StoredPosition = tr.position;
                    this.m_Vel = (this.m_Direction/Time.deltaTime);
                    stream.SendNext(tr.position);
                    stream.SendNext(this.m_Direction);
                    stream.SendNext(this.m_Vel);
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

            stream.SendNext(rb.velocity);
        }
        // Read
        else
        {
            if (this.m_SynchronizePosition)
            {
                this.m_NetworkPosition = (Vector3)stream.ReceiveNext();
                this.m_Direction = (Vector3)stream.ReceiveNext();
                this.m_Vel = (Vector3)stream.ReceiveNext();

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
                    this.delayedPosition = this.m_NetworkPosition;
                    this.m_NetworkPosition += this.m_Direction * lag;
                    this.m_Distance = Vector3.Distance(tr.position, this.m_NetworkPosition);
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