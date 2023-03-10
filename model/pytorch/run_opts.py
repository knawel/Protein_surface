from datetime import datetime

tag = datetime.now().strftime("_%Y-%m-%d_%H-%M")
config_runtime = {
    'run_name': 'set2'+tag,
    'seed': 142,
    'device': 'cuda',
    'train_frac': 0.87,
    'num_epochs': 30,
    'batch_size': 128,
    'learning_rate': 5e-4,
    'hidden_size': 256,
    'log_step': 512
}
