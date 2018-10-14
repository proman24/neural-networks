from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np
import argparse

from data import DataLoader
from train import Trainer

np.random.seed(42)

def parse_args():
    parser = argparse.ArgumentParser(description='Training Configuration')
    parser.add_argument('--epochs', type=int, default=10, dest='epochs',
                        help='Number of iterations for training')
    parser.add_argument('--batch-size', type=int, default=64, dest='batch_size', 
                        help='Batch size for one epoch in training')
    parser.add_argument('--lr', type=float, default=0.001, dest='lr',
                        help='Initial learning rate')
    parser.add_argument('--plot', type=bool, default=False, dest='plot',
                        help='Flag that indicates whether plot the accuracy during training')
    return parser.parse_args()

def main():
    args = parse_args()

    X_train, y_train, X_val, y_val, X_test, y_test = DataLoader.load_dataset(flatten=True)

    input_dim = X_train.shape[1]
    num_classes = 10
    dims = [input_dim, 100, 200, 200, num_classes]

    trainer = Trainer(dims=dims)

    train_log = []
    val_log = []

    for epoch in range(1, args.epochs + 1):
        for x_batch, y_batch in DataLoader.iterate_minibatches(X_train, y_train, batchsize=args.batch_size, shuffle=True):
            trainer.fit(x_batch, y_batch, lr=args.lr)
        
        train_log.append(np.mean(trainer.predict(X_train) == y_train))
        val_log.append(np.mean(trainer.predict(X_val) == y_val))
        
        print("Epoch[{}/{}]  train acc: {:.4f}   -   val acc: {:.4f}".format(epoch, args.epochs, train_log[-1], val_log[-1]))
        if args.plot:
            plt.plot(train_log,label='train accuracy')
            plt.plot(val_log,label='val accuracy')
            plt.legend(loc='best')
            plt.grid()
            plt.show()

    print('\nTesting on {} samples'.format(len(X_test)))
    accuracy = np.mean(trainer.predict(X_test) == y_test) * 100
    print('test acc: {:.4f}'.format(accuracy))

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print('EXIT')