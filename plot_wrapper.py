from utils import plot_train_val_loss
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Wrapper script to plot log file')
    parser.add_argument('log_file_dir', help='path to log file to plot')
    args = parser.parse_args()

    log_file = f'{args.log_file_dir}/train.log'
    plot_train_val_loss(log_file)

    