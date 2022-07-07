using UnityEngine;

public class MLP
{
    public Net_DQN(int inputSize, int outputSize, float[,] hiddenLayer, float lastWeigtScale=1.0f)
    {
        w1 = Init(inp, h);
        w2 = Init(h, outp);
        b1 = new float[1, h];
        b2 = new float[1, outp];

        m1 = new float[inp, h];
        v1 = new float[inp, h];
        m2 = new float[h, outp];
        v2 = new float[h, outp];

        mb1 = new float[1, h];
        vb1 = new float[1, h];
        mb2 = new float[1, outp];
        vb2 = new float[1, outp];
    }

}