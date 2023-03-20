from datetime import datetime

tag = datetime.now().strftime("_%Y-%m-%d_%H-%M")
config_runtime = {
    'run_name': 'set2'+tag,
    'seed': 45,
    'device': 'cuda',
    'train_frac': 0.74,
    'num_epochs': 75,
    'batch_size': 512,
    'learning_rate': 1e-3,
    'hidden_size': 32,
    'log_step': 512
}
