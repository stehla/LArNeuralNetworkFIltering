import os
import numpy as np
from keras import backend as K
from keras.callbacks import TensorBoard
from .training_data import TrainingData
from .weight_mask import WeightMask
from .pruning_callback import PruningCallback


# Limit number of threads to one master-thread and one worker-thread
tf_config = K.tf.ConfigProto(intra_op_parallelism_threads=1,
                             inter_op_parallelism_threads=1)
K.set_session(K.tf.Session(config=tf_config))


class RunSingleModel:

    def __init__(self, model, runs, epochs, params, training_data, comments):
        '''
        Construct and initialize a model including all parameters required:
        Parameters include:
        'model' - a compilable Keras Model
        'epochs' - number of training epochs
        'params' - additional parameters for the Model
        'training_params' - paramaters required for processing training data
        'comments' - info to be passed into the foldernames of output-data
        '''
        self.name = str(model.__name__)
        self.model = model
        self.epochs = epochs
        self.params = params
        self.training_data = training_data
        self.comments = comments

        # create a title including model name and parameters
        # for output files
        self.sim_title = self.name + '-' + str(params)

        # The highest energy measured in the hit samples is stored
        # to be able to scale the data for being smaller or equal to 1
        # in the neural network processing and to be rescaled afterwards
        self.scale = 0

        # create empty file list for training data files
        self.file_list = []

        # Number of Runs
        self.runs = runs

        # create empty value_loss history array with an entry for each epoch
        # self.value_loss = np.zeros((1, epochs))

    def run(self):
        """carry out one or multiple runs of training"""
        # create overall path for trained model and Tensorboard Graphs
        if self.comments == '':
            model_path = './saved_models/' + self.name + '/'

        # create a subdirectory if comments are passed
        else:
            model_path = './saved_models/' + self.name + '/' \
                + self.comments + '/'
        os.makedirs(model_path, exist_ok=True)
        print(self.sim_title)

        # create training and testing data
        train, test = self.training_data

        # Since Multiple runs should be in a new directory each:
        # run numbers are generated taking into account
        # previous directories created for runs
        runs_completed = 0
        total_run_number = 1


        # iterate until the number of runs specified have been carried out,
        # regardless of how many runs have been carried out previousky
        while runs_completed<self.runs:
            log_dir = model_path + 'Graph/' + self.sim_title \
                                + '/run' + str(total_run_number) + '/'

        # Check whether a run number still exists
            if not os.path.isdir(log_dir):
                print('run number: ' + str(runs_completed + 1))
                self.run_model(train, test, log_dir)
                runs_completed += 1

        # Otherwise increment run number until a free one is found
            total_run_number += 1

    def run_model(self, train, test, log_dir):
        """one training run isolated two save memory"""

        # instantiate Neural Network model with parameters
        current_model = self.model(*self.params)

        # Enable TensorBoard analytic files
        tbCallBack = TensorBoard(log_dir=log_dir, histogram_freq=0, write_images=True,
                                 write_graph=True)
        # Training
        current_model.fit(*train, validation_data=test, epochs=self.epochs, verbose=2,
                  callbacks=[tbCallBack])

        # save models and weights
        current_model.save(log_dir + self.sim_title + ".h5")
        #del current_model

