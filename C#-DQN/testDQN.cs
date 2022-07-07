// type2
public class testDQN
    {
        public class Env
        {
            int n_action;
            int n_expericePool;
            int n_expericeSamples;
            int n_samplesEveryType;

            int NDaction_last = 0;
            List<int> NDallActions;
            
            Dictionary<int, List<double[]>> envActionStates_dict = null;

            public Env(NDarray trainRealData, int SamplesEveryType)
            {
                n_samplesEveryType = SamplesEveryType;
                n_action = 10;
                n_expericePool = 3000;
                n_expericeSamples = 32;
                NDallActions = new List<int>(new int[n_action].IntialZero());

                envActionStates_dict = new Dictionary<int, List<double[]>>(n_action);

                for (int i = 0; i < n_action; i++)
                {

                    List<double[]> stateALLType = new List<double[]>();

                    for (int indexSample = 0; indexSample < SamplesEveryType; indexSample++)
                    {
                        //state[indexSample] = trainRealData[i * SamplesEveryType + indexSample];
                        var tstate = trainRealData[i * SamplesEveryType + indexSample];
                        stateALLType.Add(tstate.GetData<double>());

                    }
                    envActionStates_dict[i] = stateALLType;
                }

            }

            public List<double> reset()
            {
                var s_ = envActionStates_dict[0][0];
                return new List<double>(s_);
            }

            public void step(List<double> listAction, int i_index, double good, double bad, out List<double> s_, out List<double> reward, out bool done)
            {

                done = false;
                int pos = !listAction.Any() ? -1 : listAction.Select((value, index) => new { Value = value, Index = index }).Aggregate((a, b) => (a.Value > b.Value) ? a : b).Index;
                NDallActions[pos] += 1;
                if (pos == NDaction_last)
                    reward = new List<double>(new double[] { good });
                else
                    reward = new List<double>(new double[] { bad });
                int replace_i = (NDallActions[pos]) % n_samplesEveryType;
                s_ = new List<double>(envActionStates_dict[pos][replace_i]);

                if (i_index >= n_samplesEveryType - 1)
                    done = true;

                NDaction_last = pos;
            }

        }
        public class Agent
        {
            public class SmemerySample
            {
                public List<double> s = new List<double>();
                public List<double> a = new List<double>();
                public List<double> r = new List<double>();
                public List<double> s_ = new List<double>();
            }

            public int n_actions = 0;
            public int n_feature = 0;
            double r = 0;
            double gamma = 0;
            double epsion = 0;
            double qlearningRate = 0;
            int n_learn_step_counter = 0;
            int n_replace_target_iter = 0;
            int n_memeryindex = -1;
            public int n_expericePool = 0;
            int n_expericeSamples = 0;
            int[] s_shape_Input;
            int[] a_shape_Input;
            int[] r_shape_Input;

            int[] s_shape_single;
            int[] a_shape_single;
            int[] r_shape_single;


            public BaseModel q_eval_modle;
            public BaseModel q_next_modle;

            public Sequential q_eval_modle1;
            public Sequential q_next_modle2;


            public BaseModel q_oldeval_modle;
            public BaseModel q_oldnext_modle;

            public List<SmemerySample> memeries_list = null;

            public Sequential LoadModel(Sequential model)
            {
                model.Add(new Conv2D(32, kernel_size: (3, 3).ToTuple(),
                                 activation: "relu",
                                 input_shape: new Shape(s_shape_single)));
                model.Add(new Conv2D(64, (3, 3).ToTuple(), activation: "relu"));
                model.Add(new MaxPooling2D(pool_size: (2, 2).ToTuple()));
                model.Add(new Dropout(0.25));
                model.Add(new Flatten());
                model.Add(new Dense(128, activation: "relu"));
                model.Add(new Dropout(0.5));
                model.Add(new Dense(n_actions, activation: "softmax"));

                model.Compile(loss: "categorical_crossentropy",
                optimizer: new Adadelta(), metrics: new string[] { "accuracy" });

                return model;
            }
            public Agent()
            {
                n_actions = 10;
                n_feature = 784;
                r = 200;
                epsion =0.7;
                n_replace_target_iter = 200;
                gamma = 0.001;
                qlearningRate =0.006;
                n_expericePool = 3000;
                n_expericeSamples = 32;
                memeries_list = new List<SmemerySample>(n_expericePool);
                s_shape_Input = new int[] { n_expericeSamples, 28,28, 1 };
                a_shape_Input = new int[] { n_expericeSamples, n_actions };
                r_shape_Input = new int[] { n_expericeSamples, 1 };

                s_shape_single = new int[] { 28, 28, 1 };
                a_shape_single = new int[] { n_actions };
                r_shape_single = new int[] { 1 };

          
                q_eval_modle1 = new Sequential();
                q_eval_modle = LoadModel(q_eval_modle1);

                q_next_modle2 = new Sequential();
                q_next_modle = LoadModel(q_next_modle2);
              

            }
            public void store_transition(List<double> s, List<double> a, List<double> r, List<double> s_)
            {

                SmemerySample smemerySample = new SmemerySample();
                smemerySample.s = s;
                smemerySample.a = a;
                smemerySample.r = r;
                smemerySample.s_ = s_;

                ++n_memeryindex;
                if (memeries_list.Count < n_expericePool)
                {
                    memeries_list.Add(smemerySample);
                }
                else
                {
                    memeries_list[n_memeryindex % n_expericePool] = smemerySample;
                }

            }

            public void choose_action(List<double> observation, out List<double> action)
            {

                var Ndobservation = np.array(observation.ToArray()).reshape(s_shape_single);
                NDarray Ndaction = null;

                Random random = new Random();
                double r = random.NextDouble();
                if (r < epsion)
                {
                    int randomAction = random.Next(n_actions);
                    Console.WriteLine("随机动作{0}", randomAction);
                    action = new List<double>(new double[n_actions].IntialZero());
                    action[randomAction] = 1;
                }
                else
                {
                    Ndobservation = Ndobservation[np.newaxis];
                    action = new List<double>(q_eval_modle.Predict(x: Ndobservation, verbose: 0).GetData<double>());
                }
            }
            public void learning()
            {
                if (n_learn_step_counter % n_replace_target_iter == 0)
                {
                    q_next_modle.SetWeights(q_eval_modle.GetWeights());
                    Console.WriteLine("已更新目标量网络参数");
                }

                //get the random samples
                List<SmemerySample> batch_memory_list = new List<SmemerySample>(n_expericeSamples);
                List<int> listRandom = new List<int>(n_expericeSamples);
                Random random = new Random();
                int randomNum = random.Next(0, n_expericePool);
                while (listRandom.Count != n_expericeSamples)
                {
                    if (!listRandom.Contains(randomNum))
                        listRandom.Add(randomNum);
                    randomNum = random.Next(0, n_expericePool);
                }

                foreach (var item in listRandom)
                {
                    batch_memory_list.Add(memeries_list[item]);
                }


                NDarray Nds_array = np.zeros(s_shape_Input);
                NDarray Nda_array = np.zeros(a_shape_Input);
                NDarray Ndr_array = np.zeros(r_shape_Input);
                NDarray Ndnext_s_array = np.zeros(s_shape_Input);
                NDarray Ndq_next;
                NDarray Ndq_eval;
                NDarray Ndq_target;
                NDarray Ndbatch_index;
                NDarray Ndeval_act_index;
                NDarray Ndselected_q_next;
                NDarray Nddelt_act_max;
                Keras.Callbacks.History Ndhistory;
                NDarray NdcostArray;
                NDarray Ndcost;

                int i = 0;
                foreach (var item in batch_memory_list)
                {
                    Nds_array[i] = np.array(item.s.ToArray()).reshape(s_shape_single);
                    Nda_array[i] = np.array(item.a.ToArray()).reshape(a_shape_single);
                    Ndr_array[i] = np.array(item.r.ToArray()).reshape(r_shape_single);
                    Ndnext_s_array[i] = np.array(item.s_.ToArray()).reshape(s_shape_single);
                    i++;
                }

                Ndq_next = q_next_modle.Predict(x: Ndnext_s_array);
                Ndq_eval = q_eval_modle.Predict(x: Ndnext_s_array);
                Ndq_target = Ndq_eval.copy();

                Ndbatch_index = np.arange(n_expericeSamples, dtype: np.int32);

                Ndeval_act_index = np.argmax(Nda_array, axis: 1).astype(np.int32);

                Ndselected_q_next = np.max(Ndq_next, axis: new int[] { 1 });


                Nddelt_act_max = (1 - qlearningRate) * Ndq_eval[Ndbatch_index, Ndeval_act_index];
                Ndq_target[Ndbatch_index, Ndeval_act_index] = Nddelt_act_max + r * (np.squeeze(Ndr_array) + gamma * Ndselected_q_next);



                Ndhistory = q_eval_modle.Fit(x: Nds_array, y: Ndq_target, verbose: 0);

                NdcostArray = np.array(Ndhistory.HistoryLogs["loss"]);
                Ndcost = np.around(NdcostArray[-1], 4);


                n_learn_step_counter += 1;
            }
        }

        public void RunDQN()
        {
            Agent agent = new Agent();

            // input image dimensions
            int img_rows = 28, img_cols = 28;

            // Declare the input shape for the network
            Shape input_shape = null;

            // Load the MNIST dataset into Numpy array
            var ((x_train, y_train), (x_test, y_test)) = MNIST.LoadData();

            //Check if its channel fist or last and rearrange the dataset accordingly
            if (Backend.ImageDataFormat() == "channels_first")
            {
                x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols);
                x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols);
                input_shape = (1, img_rows, img_cols);
            }
            else
            {
                x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1);
                x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1);
                input_shape = (img_rows, img_cols, 1);
            }

            //Normalize the input data
            x_train = x_train.astype(np.float32);
            x_test = x_test.astype(np.float32);
            x_train /= 255;
            x_test /= 255;
            Console.WriteLine("x_train shape: " + x_train.shape);
            Console.WriteLine(x_train.shape[0] + " train samples");
            Console.WriteLine(x_test.shape[0] + " test samples");

            // Convert class vectors to binary class matrices
            //y_train = Util.ToCategorical(y_train, 10);
            //y_test = Util.ToCategorical(y_test, 10);


            //模型构建
           
            int trainN = x_test.shape[0] / agent.n_actions;
            Env env = new Env(x_train, trainN);

            List<double> epochMeanWared_list = new List<double>();
            List<int> epoches_list = new List<int>();
            List<double> epoches_trainAccList = new List<double>();
            List<double> epoches_validAccList = new List<double>();
            List<double> observation_ = new List<double>();

            int t_steps = 0;
            for (int epoch_i = 0; epoch_i < 1500; epoch_i++)
            {
                Console.WriteLine("########################");
                Console.WriteLine("#########new epoch#########");
                Console.WriteLine("########################");

                List<double> observation = env.reset();
                bool done = false;

                List<double> allReward = new List<double>();

                while (!done)
                {
                    List<double> action = new List<double>(agent.n_actions);
                    List<double> reward = new List<double>(1);

                    agent.choose_action(observation, out action);


                    env.step(action, t_steps % trainN, 200,0, out observation_, out reward, out done);

                    agent.store_transition(observation, action, reward, observation_);
                    allReward.Add(reward[0]);

                    if (agent.memeries_list.Count < agent.n_expericePool)
                        Console.WriteLine("已有{0}经验样本", agent.memeries_list.Count);

                    if (agent.memeries_list.Count >= agent.n_expericePool)
                    {
                        agent.learning();
                    }

                    observation = observation_;
                    ++t_steps;
                }

                if (agent.memeries_list.Count >= agent.n_expericePool)
                {
                    epochMeanWared_list.Add(allReward.Average());
                    epoches_list.Add(epoch_i);


                   // var trainlossAcc = agent.q_eval_modle.Evaluate(x_test, y_test);
         
                }
                GC.Collect();

            }

            string tempFile = Path.Combine(Directory.GetCurrentDirectory(), "tempFile");
            if (!Directory.Exists(tempFile))
                Directory.CreateDirectory(tempFile);
        }

    }
    
    //run like this
    testDQN testDQN = new testDQN();
    testDQN.RunDQN();