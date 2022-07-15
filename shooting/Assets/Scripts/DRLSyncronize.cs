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

    private Vector3 delayedPosition;

    private float lag;

    [Tooltip("Indicates if localPosition and localRotation should be used. Scale ignores this setting, and always uses localScale to avoid issues with lossyScale.")]
    public bool m_UseLocal;

    bool m_firstTake = false;

    private Vector3 m_Vel;
    private float elapsedTime;

    private bool isPositionUpdate = false;

    private int Action, ChangeFrame;
    private int preAction;
    private float ChangeTime;
    private Vector3 pos;
    private Vector3 newVel;
    
    private float v_x, v_y, v_z;

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

    private Vector3 calculateVelocity(int action, int lastAction, Vector3 vel, int frame)
    {
        Vector3 sumVel = Vector3.zero;
        Vector3 predictVel;
        if(frame > 0){
            int count = frame;
            while(count > 0)
            {
                if(action == 0){

                }
                else if(action == 1){
                    if(lastAction == 1 || lastAction == 6 || lastAction == 8)
                    {
                        v_x = vel.x + 0.8828f;
                        if(v_x > 4.88228f){
                            v_x = 4.88228f;
                        }
                        else
                        { }

                        sumVel += new Vector3(v_x, 0, 0);
                    }
                    else
                    {
                        sumVel += new Vector3(0.8828f, 0, 0);
                    }
                    count -= 1;
                }
                else if(action == 2){
                    if(lastAction == 2 || lastAction == 5 || lastAction == 7)
                    {
                        v_x = vel.x - 0.8828f;
                        if(v_x < -4.88228f){
                            v_x = -4.88228f;
                        }
                        else
                        { }

                        sumVel += new Vector3(v_x, 0, 0);
                    }
                    else
                    {
                        sumVel -= new Vector3(0.8828f, 0, 0);
                    }
                    count -= 1;
                }
                else if(action == 3){
                    if(lastAction == 3 || lastAction == 5 || lastAction == 6)
                    {
                        v_z = vel.z + 0.8828f;
                        if(v_z > 4.88228f){
                            v_z = 4.88228f;
                        }
                        else
                        { }

                        sumVel += new Vector3(0, 0, v_z);
                    }
                    else
                    {
                        sumVel += new Vector3(0, 0, 0.8828f);
                    }
                    count -= 1;
                }
                else if(action == 4){
                    if(lastAction == 4 || lastAction == 7 || lastAction == 8)
                    {
                        v_z = vel.z - 0.8828f;
                        if(v_z < -4.88228f){
                            v_z = -4.88228f;
                        }
                        else
                        { }

                        sumVel += new Vector3(0, 0, v_z);
                    }
                    else
                    {
                        sumVel -= new Vector3(0, 0, 0.8828f);
                    }
                    count -= 1;
                }
                // else if(action == 5){
                //     if(lastAction == 5){

                //     }
                //     else if(lastAction == 2 || lastAction == 7)
                //     {
                //         v_z = vel.z + 0.8828f;
                //         if(v_z > 4.88228){
                //             v_z = 4.88228;
                //         }
                //         else
                //         { }

                //         sumVel += Vector3(0, 0, v_z);
                //     }
                //     else
                //     {
                //         sumVel += (0, 0, 0.8828f);
                //     }
                //     count -= 1;
                // }
            }
            predictVel = new Vector3(sumVel.x/frame, sumVel.y/frame, sumVel.z/frame);
        }
        else
        {
            predictVel = vel;
        }
        return predictVel;
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
            
            string data = "D" + "," + time + "," + position_x + "," + position_y + "," + position_z + "," + velocity_x + "," + velocity_y + "," + velocity_z + "," + lagging;
            
            commUDPnotMine.send(data);

            string[] rcvData = commUDPnotMine.rcvMsg.Split(',');
            // Debug.Log(commUDP.rcvMsg);

            if(commUDPnotMine.rcvMsg != "ini"){
                // Debug.Log("Estimating");

                Action = int.Parse(rcvData[0]);
                ChangeFrame = int.Parse(rcvData[1]);

                ChangeTime = ChangeFrame * Time.deltaTime;

                if (m_UseLocal)
                {
                    tr.localPosition = Vector3.MoveTowards(tr.localPosition, this.m_NetworkPosition, this.m_Distance  * Time.deltaTime * PhotonNetwork.SerializationRate);
                    tr.localRotation = Quaternion.RotateTowards(tr.localRotation, this.m_NetworkRotation, this.m_Angle * Time.deltaTime * PhotonNetwork.SerializationRate);
                }
                else
                {
                    if(ChangeTime >= lag)
                    {
                        if(this.isPositionUpdate){
                            tr.position = Vector3.LerpUnclamped(delayedPosition, delayedPosition + this.m_Vel * lag, 1);
                            this.isPositionUpdate = false;
                            // tr.position = Vector3.LerpUnclamped(delayedPosition, delayedPosition + m_Vel * lag, 1);
                        }
                        else
                        {
                            tr.position = Vector3.LerpUnclamped(tr.position, tr.position + this.m_Vel * 1 / PhotonNetwork.SerializationRate, 1);
                            // SerializationRate -> OnPhotonSerializeView が一秒間に何回呼ばれるか
                        }
                    }
                    else
                    {
                        if(this.m_Vel.x == 0 && this.m_Vel.z == 0)
                        {
                            preAction = 0;
                        }
                        else if(this.m_Vel.x > 0 && this.m_Vel.z == 0)
                        {
                            preAction = 1;
                        }
                        else if(this.m_Vel.x < 0 && this.m_Vel.z == 0)
                        {
                            preAction = 2;
                        }
                        else if(this.m_Vel.x == 0 && this.m_Vel.z > 0)
                        {
                            preAction = 3;
                        }
                        else if(this.m_Vel.x == 0 && this.m_Vel.z < 0)
                        {
                            preAction = 4;
                        }
                        else if(this.m_Vel.x < 0 && this.m_Vel.z > 0)
                        {
                            preAction = 5;
                        }
                        else if(this.m_Vel.x > 0 && this.m_Vel.z > 0)
                        {
                            preAction = 6;
                        }
                        else if(this.m_Vel.x < 0 && this.m_Vel.z < 0)
                        {
                            preAction = 7;
                        }
                        else if(this.m_Vel.x > 0 && this.m_Vel.z < 0)
                        {
                            preAction = 8;
                        }

                        if(this.isPositionUpdate){
                            newVel = calculateVelocity(Action, preAction, this.m_Vel, Mathf.CeilToInt((lag-ChangeTime)/Time.deltaTime));

                            pos = delayedPosition + this.m_Vel * ChangeTime + newVel * (lag-ChangeTime);

                            tr.position = Vector3.LerpUnclamped(delayedPosition, pos, 1);
                            this.isPositionUpdate = false;
                        }
                        else
                        {
                            newVel = calculateVelocity(Action, preAction, this.m_Vel, Mathf.CeilToInt((lag-ChangeTime)/Time.deltaTime));

                            pos = tr.position + newVel / PhotonNetwork.SerializationRate;
                            
                            tr.position = Vector3.LerpUnclamped(tr.position, pos, 1);
                            // SerializationRate -> OnPhotonSerializeView が一秒間に何回呼ばれるか
                        }
                    }
                    
                    
                    tr.rotation = Quaternion.RotateTowards(tr.rotation, this.m_NetworkRotation, this.m_Angle * Time.deltaTime *  PhotonNetwork.SerializationRate);
                    // Debug.Log((this.m_NetworkPosition - tr.position) + pos);
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
                    if(this.isPositionUpdate){
                        tr.position = Vector3.LerpUnclamped(delayedPosition, delayedPosition + this.m_Vel * lag, 1);
                        this.isPositionUpdate = false;
                        // tr.position = Vector3.LerpUnclamped(delayedPosition, delayedPosition + m_Vel * lag, 1);
                    }
                    else
                    {
                        tr.position = Vector3.LerpUnclamped(tr.position, tr.position + this.m_Vel * 1 / PhotonNetwork.SerializationRate, 1);
                        // SerializationRate -> OnPhotonSerializeView が一秒間に何回呼ばれるか
                    }
                    tr.rotation = Quaternion.RotateTowards(tr.rotation, this.m_NetworkRotation, this.m_Angle * Time.deltaTime *  PhotonNetwork.SerializationRate);
                }
            }
            dt = DateTime.Now;

            milSec = dt.Millisecond / 1000f;
            nowTime = (dt.Minute * 60) + dt.Second + milSec;

            // string position_x = tr.position.x.ToString("00.000000");
            // string position_y = tr.position.y.ToString("00.000000");
            // string position_z = tr.position.z.ToString("00.000000");
            // string time = Time.time.ToString("0000.0000");
            // string time = nowTime.ToString("F3");

            // string velocity_x = rb.velocity.x.ToString("00.000000");
            // string velocity_y = rb.velocity.y.ToString("00.000000");
            // string velocity_z = rb.velocity.z.ToString("00.000000");
            // Debug.Log(Time.time);
            // string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z + "vx" + velocity_x + "vy" + velocity_y + "vz" + velocity_z;
            // string data = "t" + time + "x" + position_x + "y" + position_y + "z" + position_z;

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
                    this.m_Direction = tr.localPosition - this.m_StoredPosition;
                    this.m_StoredPosition = tr.localPosition;
                    this.m_Vel = (this.m_StoredPosition1 - this.m_StoredPosition2) / elapsedTime;

                    stream.SendNext(tr.localPosition);
                    stream.SendNext(this.m_Direction);
                    stream.SendNext(this.m_Vel);

                    elapsedTime = 0f;
                }
                else
                {
                    this.m_StoredPosition = tr.position;
                    this.m_Direction = tr.position - this.m_StoredPosition;
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