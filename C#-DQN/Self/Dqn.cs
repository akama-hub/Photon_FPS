using UnityEngine;


public class DistributionalFCStateQFunctionWithDiscreteAction
{
    int ndim_obs; // Number of dimensions of observation space.
    int n_actions; // Number of actions in action space.
    int n_atoms; // Number of atoms of return distribution.
    float v_min; // Minimum value this model can approximate.
    float v_max; // Maximum value this model can approximate.
    int n_hidden_channels; // Number of hidden channels.
    int n_hidden_layers; // Number of hidden layers.
    // nonlinearity=F.relu;
    float last_wscale=1.0; // Weight scale of the last layer.

    float[,] z_values;
    float[,] hiddenLayer;

    if(n_atoms < 2){
        Debug.Log("Error");
    }
    else
    {}

    if(v_min > v_max){
        Debug.Log("Error");
    }
    else{}

    z_values = new float getArismeticProgression(v_min, v_max, n_atoms);
    hiddenLayer = new int[n_hidden_channels, n_hidden_layers]
    float[,] NeuralNet = new NeuralNet.Net(ndim_obs, n_actions*n_atoms, hiddenLayer)

    public float[,] getArismeticProgression(float start, float stop, int num){
        float[,] ap = new float[num];
        float diff = (stop - start) / (num - 1);
        for(int i = 0; i < num; i++){
            ap[i] = start + i * diff;
        }
        return ap;
    }
}