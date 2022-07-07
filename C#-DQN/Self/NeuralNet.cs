using UnityEngine;

public class NeuralNet
{
    float[,] weight;
    float[,] bias;

    float[,] m1;
    float[,] v1;
    float[,] m2;
    float[,] v2;

    float[,] mb1;
    float[,] vb1;
    float[,] mb2;
    float[,] vb2;

    int t = 0;
    float beta1 = 0.9f;
    float beta2 = 0.999f;
    float eps = 1e-8f;
    float lr = 1e-3f;

    public Linear()
    {

    }

    // ニューラルネットの重みパラメータの初期値設定
    public float[,] Init(float inintialValue, int inputSize, int outputSize)
    {
        float[,] u = new float[inputSize, outputSize];

        for (int i = 0; i < inputSize; i++)
        {
            for (int j = 0; j < outputSize; j++)
            {
                u[i, j] = Random.Range(-inintialValue, inintialValue); //一様分布
            }
        }
        return u;
    }

    public Net(int inputSize, int[,] hiddnLayer, int outputSize, float lr)
    {
        float initial = Mathf.Sqrt(1.0f / inputSize);

        weight[0] = Init(initial, inputSize, hiddnLayer[0]);
        bias[0] = new float[1, hiddnLayer[0]];
        m[0] = new float[inputSize, hiddnLayer[0]];
        v[0] = new float[inputSize, hiddnLayer[0]];
        mb[0] = new float[1, hiddnLayer[0]];
        vb[0] = new float[1, hiddnLayer[0]];
        for(i = 1; i<hiddenLayer[1]; i++)
        {
            weight[i] = Init(initial, hiddnLayer[0], hiddnLayer[0]);
            bias[i] = new float[1, hiddnLayer[0]];
        }
        weight[hiddenLayer[1]] = Init(initial, hiddnLayer[0], outputSize);
        bias[hiddenLayer[1]] = new float[1, outputSize[0]];

        
        
        m2 = new float[h, outp];
        v2 = new float[h, outp];

        
        mb2 = new float[1, outp];
        vb2 = new float[1, outp];

        this.lr = lr;
    }
}