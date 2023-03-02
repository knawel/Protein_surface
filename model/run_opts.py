from datetime import datetime

tag = datetime.now().strftime("_%Y-%m-%d_%H-%M")
config_runtime = {
    'run_name': 'dnn'+tag,
    'seed': 142,
    'device': 'cuda',
    'train_frac': 0.85,
    'num_epochs': 128,
    'batch_size': 128,
    'learning_rate': 1e-4,
    'hidden_size': 256,
    'log_step': 1024
}
