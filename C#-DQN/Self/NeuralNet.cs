using UnityEngine;

public class NeuralNet
{
    float[,] weight;
    float[,] bias;

    float[,] momentum;
    float[,] velocity;

    float[,] mb1;
    float[,] vb1;

    int t = 0;
    float beta1 = 0.9f;
    float beta2 = 0.999f;
    float eps = 1e-8f;
    float lr = 1e-3f;

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

    // hiddenLayer [number of channels, number of layers]
    public Net(int inputSize, int[,] hiddenLayer, int outputSize, float lr)
    {
        float initial = Mathf.Sqrt(1.0f / inputSize);

        weight[0] = Init(initial, inputSize, hiddenLayer[0]);
        bias[0] = new float[1, hiddenLayer[0]];
        momentum[0] = new float[inputSize, hiddenLayer[0]];
        velocity[0] = new float[inputSize, hiddenLayer[0]];
        mb[0] = new float[1, hiddenLayer[0]];
        vb[0] = new float[1, hiddenLayer[0]];
        for(i = 1; i<hiddenLayer[1]; i++)
        {
            weight[i] = Init(initial, hiddenLayer[0], hiddenLayer[0]);
            bias[i] = new float[1, hiddenLayer[0]];
            momentum[i] = new float[inputSize, hiddenLayer[0]];
            velocity[i] = new float[inputSize, hiddenLayer[0]];
            mb[i] = new float[1, hiddenLayer[0]];
            vb[i] = new float[1, hiddenLayer[0]];
        }
        weight[hiddenLayer[1]] = Init(initial, hiddenLayer[0], outputSize);
        bias[hiddenLayer[1]] = new float[1, outputSize];
        momentum[hiddenLayer[1]] = new float[hiddenLayer[0]], outputSize];
        velocity[hiddenLayer[1]] = new float[hiddenLayer[0]], outputSize];
        mb[hiddenLayer[1]] = new float[1, outputSize];
        vb[hiddenLayer[1]] = new float[1, outputSize];

        this.lr = lr;
    }

    public void Adam(float[,] weight, float[,] dweight, float[,] momentum, float[,] velocity, int batch_size)
    {
        for (int i = 0; i < weight.GetLength(0); i++)
        {
            for (int j = 0; j < weight.GetLength(1); j++)
            {
                float d = dweight[i, j] / batch_size;
                momentum[i, j] = momentum[i, j] * beta1 + (1 - beta1) * d;
                velocity[i, j] = velocity[i, j] * beta2 + (1 - beta2) * d * d;
                float mb = momentum[i, j] / (1 - Mathf.Pow(beta1, t));
                float vb = velocity[i, j] / (1 - Mathf.Pow(beta2, t));

                weight[i, j] = weight[i, j] - lr * (mb / (Mathf.Sqrt(vb) + eps));
            }
        }
    }

    // 順伝播
    public float[,] Forward(float[,] inputLayer)
    {
        float[,] z = Add(Dot(inputLayer, weight[0]), bias[0]);
        float[,] h = Relu(z);

        for(i = 1; i < hiddenLayer[1]; i++){
            z = Add(Dot(z, weight[i]), bias[i]);
            float[,] h = Relu(z);
        }

        return Add(Dot(z, weight[hiddenLayer[1]]), bias[hiddenLayer[1]]);
    }

    // 逆伝播
    public float Backward(float[,] inputLayer, int[] action, float[] q_target, float max_grad_norm)
    {
        // q値の計算
        float[,] z = Add(Dot(inputLayer, weight[0]), bias[0]);
        float[,] h = Relu(z);

        for(i = 1; i < hiddenLayer[1]; i++){
            z = Add(Dot(z, weight[i]), bias[i]);
            float[,] h = Relu(z);
        }

        float[,] q = Add(Dot(z, weight[hiddenLayer[1]]), bias[hiddenLayer[1]]);

        // 誤差
        float[,] d = new float[q.GetLength(0), q.GetLength(1)];
        for (int i = 0; i < inputLayer.GetLength(0); i++)
        {
            //　二乗誤差のほうが良い？
            d[i, action[i]] = q[i, action[i]] - q_target[i];
            if (d[i, action[i]] < -1)
                d[i, action[i]] = -1;
            else if (d[i, action[i]] > 1)
                d[i, action[i]] = 1;
        }
        // 逆伝播（連鎖率をつかって考える）
        float[,] out1 = Dot(d, Transpose(w2));
        out1 = DerRelu(out1, z1);

        float[,] dw2 = Dot(Transpose(h1), d);
        float[,] dw1 = Dot(Transpose(inputLayer), out1);
        float[,] db2 = Sum(d);
        float[,] db1 = Sum(out1);

        float total_norm = 0;

        total_norm += Sum_total_norm(w2, b2);
        total_norm += Sum_total_norm(w1, b1);

        total_norm = Mathf.Sqrt(total_norm);
        float clip_coef = (float)(max_grad_norm / (total_norm + 1e-6));
        if (clip_coef < 1)
        {
            dw2 = Mult_clip_coef(dw2, db2, out db2, clip_coef);
            dw1 = Mult_clip_coef(dw1, db1, out db1, clip_coef);
        }

        t++;
            Adam(w1, dw1, m1, v1, inputLayer.GetLength(0));
            Adam(w2, dw2, m2, v2, inputLayer.GetLength(0));
            Adam(b1, db1, mb1, vb1, inputLayer.GetLength(0));
            Adam(b2, db2, mb2, vb2, inputLayer.GetLength(0));
       
        return Sum_total_norm(d, new float[1,d.GetLength(1)]) / inputLayer.GetLength(0);
    }
}