# To allow for proper module importing and file referencing, please reset the pwd 
# by cd to 'Senior_Thesis_Code/' on command line.

import time, itertools, sys, warnings, os, json, argparse
warnings.simplefilter(action='ignore', category=FutureWarning)
from os import path
import pandas as pd

from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn import tree
from Ch3_optimal.tree import optimalDecisionTreeClassifier
import Ch2_framework.dataset as dataset

parser = argparse.ArgumentParser()
parser.add_argument('--a', type=float, required=True, 
                    help='alpha, tree regularization param')
parser.add_argument('--d', type=int, required=True, help='depth of the tree')
parser.add_argument('--s', type=int, required=True, help='random seed value')
parser.add_argument('--hidden_dim', type=int, required=True)
# the following three are optional arguments
parser.add_argument('--min_samples_split', type=int, default=2, 
                    help='leaf node minimum value')
parser.add_argument('--timelimit', type=int, default=13800) # Gurobi timeout limit (3.8hr)
parser.add_argument('--data', type=str, default='CTG_width') # name of the dataset

args = parser.parse_args()
a, d, s, hidden_dim, min_samples_split, data, timelimit = args.a, args.d, args.s, \
    args.hidden_dim, args.min_samples_split, args.data, args.timelimit

'''
alpha = [0.001, 0.01, 0.1]
depth = [4,6,8]
hidden_dims = [20, 40, 60, 80, 100, 120]
seeds = [37, 42, 53] # use of specified random states for experiment reproducibility
'''

train_ratio = 0.6
val_ratio = 0.2
test_ratio = 0.2
MIPGAP_TOLERANCE = 0.1 # minimum bar to stop retraining model
CSV_FILEPATH = 'res/oct_vary_width.csv'
COLUMNS= ['instance', 'hidden_dim', 'depth', 'alpha', 'seed', 'train_acc', 'val_acc', 
        'test_acc', 'train_time', 'gap']

# create or load previously computed results
if path.isfile(CSV_FILEPATH):
    res_oct = pd.read_csv(CSV_FILEPATH)
else:
    res_oct = pd.DataFrame(columns=COLUMNS)

# load data
x, y = dataset.loadData(data, hidden_dim)
# data splitting
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=1-train_ratio, random_state=s)
x_val, x_test, y_val, y_test = train_test_split(x_test, y_test, 
                                                test_size=test_ratio/(test_ratio+val_ratio), random_state=s)

# oct
row = res_oct[(res_oct['instance'] == data) & (res_oct['depth'] == d) & 
            (res_oct['alpha'] == a) & (res_oct['seed'] == s) & 
            (res_oct['gap'] <= MIPGAP_TOLERANCE) & (res_oct['hidden_dim'] == hidden_dim)]
if len(row): # if the specific oct is already trained and optimized up to a degree, we directly print the previously recorded results
    msg = {'instance':data, 'hidden_dim':hidden_dim, 'depth':d, 'min_leaf':min_samples_split, 'alpha':a, 'seed':s, 'train_acc':row['train_acc'].values[0], 
    'val_acc':row['val_acc'].values[0], 'test_acc':row['test_acc'].values[0], 'train_time':row['train_acc'].values[0], 'gap':row['gap'].values[0]}
    print(json.dumps(msg, indent = 4))

else: # tree has not been trained, so train
    octree = optimalDecisionTreeClassifier(max_depth=d, min_samples_split=min_samples_split, alpha=a, warmstart=True,
                                                timelimit=timelimit, output=True)
    filepath = f'synthetic_tests/CTG_width/gurobi_logs/oct_dim_{hidden_dim}_a_{a}_d_{d}_l{min_samples_split}_s_{s}.txt'
    
    orig_stdout = sys.stdout
    with open(filepath, 'w') as f: # redirect the Gurobi logs to a different file
        sys.stdout = f
        tick = time.time()
        octree.fit(x_train, y_train)
        tock = time.time()
        train_time = tock - tick
    sys.stdout = orig_stdout

    train_acc = accuracy_score(y_train, octree.predict(x_train))
    val_acc = accuracy_score(y_val, octree.predict(x_val))
    test_acc = accuracy_score(y_test, octree.predict(x_test))
    row = {'instance':data, 'hidden_dim':hidden_dim, 'depth':d, 'min_leaf': min_samples_split, 'alpha':a, 'seed':s, 'train_acc':train_acc, 'val_acc':val_acc,
        'test_acc':test_acc, 'train_time':train_time, 'gap':octree.optgap}
    print(json.dumps(row, indent = 4))