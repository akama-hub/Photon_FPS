using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class EstimatedCPUController : MonoBehaviour
{
    private forudp.UDP commUDP = new forudp.UDP();
    
    // Start is called before the first frame update
    void Start()
    {
        // commUDP.init(int型の送信用ポート番号, int型の送信先ポート番号, int型の受信用ポート番号);
        commUDP.init(50002, 50003, 50001);
        //UDP受信開始
        commUDP.start_receive();
    }

    // Update is called once per frame
    void Update()
    {
        string[] position = commUDP.rcvMsg.Split(',');
        // Debug.Log(commUDP.rcvMsg);

        if(commUDP.rcvMsg != "ini"){
            // Debug.Log("Estimating");

            float pos_x = float.Parse(position[0]);
            float pos_y = float.Parse(position[1]);
            float pos_z = float.Parse(position[2]);
            
            // Debug.Log(pos_x);
            // Debug.Log(pos_y);
            // Debug.Log(pos_z);

            Transform myTransform = this.transform;
            
            Vector3 pos = myTransform.position;
            pos.x = pos_x;
            pos.y = pos_y;
            pos.z = pos_z;

            myTransform.position = pos;
        }
        
    }

}
