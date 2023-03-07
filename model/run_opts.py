from datetime import datetime

tag = datetime.now().strftime("_%Y-%m-%d_%H-%M")
config_runtime = {
    'run_name': 'set2'+tag,
    'seed': 142,
    'device': 'cuda',
    'train_frac': 0.87,
    'num_epochs': 250,
    'batch_size': 128,
    'learning_rate': 1e-3,
    'hidden_size': 512,
    'log_step': 512
}
