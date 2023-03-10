
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from sklearn.model_selection import train_test_split
import tensorflow as tf
import argparse
# local libs
from src.logger import Logger
from dataset import read_list
from run_opts import config_runtime


# input arguments:
parser = argparse.ArgumentParser(description='Run NN model and save it')
parser.add_argument(
    "pdb_list",
    type=str,
    default='',
    help="A text file that includes a list of PDB codes along with chains, example 1ABC_AB"
    # required=True
)
# arguments
args = parser.parse_args()


n_cls = 3  # number of classes
# conf_dev = config_runtime['device']
train_f = config_runtime['train_frac']
seed = config_runtime['seed']
learning_rate = config_runtime['learning_rate']
batch_size = config_runtime['batch_size']
hid_size = config_runtime['hidden_size']
log_step = config_runtime['log_step']
epochs = config_runtime['num_epochs']
run_name = config_runtime['run_name']

logger = Logger("./", "train")

# store parameters
logger.print("Parameters")
logger.print("-------------------------")
logger.print(f"Train fraction:    {train_f}")
logger.print(f"Learning rate:     {learning_rate}")
logger.print(f"Batch size:        {batch_size}")
logger.print(f"Hidden layer size: {hid_size}")
logger.print(f"Number of epochs:  {epochs}")
logger.print("-------------------------")


# Read list of the proteins
proteins = []
with open(args.pdb_list, 'r') as iFile:
    for i in iFile:
        if i[0] != '#':
            proteins.append(i.strip())



# devide test / train by proteins
train_prots, test_prots = train_test_split(proteins, train_size=train_f, random_state=42)

_, X_train, y_train = read_list(train_prots)
_, X_val, y_val = read_list(test_prots)
n_input = X_train.shape[1]

logger.print("\n")
logger.print("Data")
logger.print("-------------------------")
logger.print(f"Proteins: train {len(train_prots)}   test {len(test_prots)}")
logger.print(f"Proteins in test set: {' '.join(test_prots)}")
logger.print(f"Vertices: train {X_train.shape[0]}   test {X_val.shape[0]}")
logger.print(f"Features: {n_input}")

model = tf.keras.Sequential([
    tf.keras.layers.Dense(n_input, activation='relu'),
    tf.keras.layers.Dense(hid_size, activation='relu'),
    tf.keras.layers.Dropout(0.05),
    tf.keras.layers.Dense(hid_size, activation='relu'),
    tf.keras.layers.Dropout(0.15),
    tf.keras.layers.Dense(hid_size, activation='relu'),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(8, activation='relu'),
    tf.keras.layers.Dense(n_cls)
])

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])
print(model)
checkpoint_path = f"model/model.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)
tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir="model_log", histogram_freq=1)
cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                 save_weights_only=True,
                                                 verbose=1)

model.fit(
         X_train, y_train,
         batch_size=batch_size,
         epochs=epochs,
         validation_data=(X_val, y_val),
         callbacks=[cp_callback, tensorboard_callback])

logger.print("completed")
