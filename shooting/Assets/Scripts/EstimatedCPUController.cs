using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Photon.Pun;

using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

using forudp;


public class EstimatedCPUController : MonoBehaviourPunCallbacks
{
    public static int positionLength = 8;
    private forudp.UDP commUDP = new forudp.UDP();

    private Rigidbody rigidbody;
    
    // Start is called before the first frame update
    void Start()
    {
        commUDP.init(50002, 50000, 50001);
        //UDP受信開始
        commUDP.start_receive();
        rigidbody = this.GetComponent<Rigidbody> ();
    }

    // Update is called once per frame
    void Update()
    {
        string position = commUDP.rcvMsg;
        int pos_x = int.Parse(position.Substring(0, positionLength));
        int pos_y = int.Parse(position.Substring(positionLength, positionLength));
        
        Transform myTransform = this.transform;
        
        Vector3 pos = myTransform.position;
        pos.x = pos_x;
        pos.y = pos_y;

        myTransform.position = pos;
    }

}
