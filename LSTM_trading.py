import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import pandas_ta as ta

data = yf.download(tickers = '^GSPC', start = '2012-03-11',end = '2022-12-13')
data.head(10)

#indicator selection panel
data['RSI']=ta.rsi(data.Close, length=14) 
data['EMAF']=ta.ema(data.Close, length=20)
data['EMAM']=ta.ema(data.Close, length=100)
data['EMAS']=ta.ema(data.Close, length=150)


#closing price of next day
data['TargetNextClose'] = data['Adj Close'].shift(-1) 

data.dropna(inplace=True)
data.reset_index(inplace = True)

#non needed column in database
data.drop(['Volume', 'Close', 'Date'], axis=1, inplace=True)

data_set = data.iloc[:, 0:11]
pd.set_option('display.max_columns', None)

data_set.head(20)

from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range=(0,1)) 
data_set_scaled = sc.fit_transform(data_set)
# print(data_set_scaled)


X = []

backcandles = 35 #sees last 30 days data to predict next close price
print(data_set_scaled.shape[0])

#appending data of the 8 colmns we need to feed as input
for j in range(8):
    X.append([])
    for i in range(backcandles, data_set_scaled.shape[0]):
        X[j].append(data_set_scaled[i-backcandles:i, j])


X=np.moveaxis(X, [0], [2])


X, yi = np.array(X), np.array(data_set_scaled[backcandles:,-1])
y = np.reshape(yi,(len(yi),1))

# print(X)
print(X.shape)
# print(y)
print(y.shape)

#finalised the inputs for our network above->
#now implementing networks:

# splitting data to training test sets
splitlimit = int(len(X)*0.8) #using 80% data for training
# print(splitlimit)
X_train, X_test = X[:splitlimit], X[splitlimit:]
y_train, y_test = y[:splitlimit], y[splitlimit:]
print(X_train.shape)
# print(X_test.shape)
# print(y_train.shape)
# print(y_test.shape)
# print(y_train)

from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers import Dense
from keras.layers import TimeDistributed

import tensorflow as tf
import keras
from keras import optimizers
from keras.callbacks import History
from keras.models import Model
from keras.layers import Dense, Dropout, LSTM, Input, Activation, concatenate
import numpy as np
np.random.seed(10)

#2d input shape -> back-candles are rows, 8 are column size of data categorization
lstm_input = Input(shape=(backcandles, 8), name='lstm_input')
inputs = LSTM(250, name='first_layer')(lstm_input)
inputs = Dense(1, name='dense_layer')(inputs)
output = Activation('linear', name='output')(inputs)
model = Model(inputs=lstm_input, outputs=output)
adam = optimizers.Adam()
model.compile(optimizer=adam, loss='mse')
model.fit(x=X_train, y=y_train, batch_size=15, epochs=30, shuffle=True, validation_split = 0.1)

y_pred = model.predict(X_test)

#comparing numberic data -> predicted vs test data
for i in range(10):
    print(y_pred[i], y_test[i])



plt.figure(figsize=(16,8))
plt.plot(y_test, color = 'gray', label = 'Test')
plt.plot(y_pred, color = 'green', label = 'Predicted')
plt.legend()
plt.show()


