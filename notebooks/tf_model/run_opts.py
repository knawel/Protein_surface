from datetime import datetime

tag = datetime.now().strftime("_%Y-%m-%d_%H-%M")
config_runtime = {
    'run_name': 'set2'+tag,
    'seed': 10,
    'device': 'cuda',
    'train_frac': 0.9,
    'num_epochs': 45,
    'batch_size': 256,
    'learning_rate': 1e-4,
    'hidden_size': 32,
    'log_step': 512
}
