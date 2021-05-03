# %% Imports and Defining Dataset
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 19:28:56 2021
@author: Cyril
"""
### IMPORTS

%reload_ext autoreload
%autoreload 2
import torch
import numpy as np
import model as lstm
import matplotlib.pyplot as plt
import set_data as setdata
import plot_data as plotdata

### MAIN
# Read and generate dataset
m = 1
ow = 50
data = setdata.ImportData(file_name='Data/airquality',  modes=range(m, m+10))
# overlap ?
#data = setdata.AirQualityData(width=2000)
x_train, y_train, x_valid, y_valid = setdata.PrepareDataset(data, noise=None, in_out_stride=(200, ow, 50))

# %% Create and train model
bs = 4
model = lstm.LSTM_EncoderDecoder(input_size=x_train.shape[2], hidden_size=100).to(x_train.device)
loss = lstm.TrainModel(model, x_train, y_train, n_epochs=300, target_len=ow, batch_size=bs, lr=0.02, wd=1e-9)
plt.plot(np.log10(loss))

# %% Predict&Plot on valid and train data
inlen = -0
p_valid = lstm.Predict(model, x_valid[inlen:, :bs, :], target_len=ow)
plotdata.PlotPredictions(x_valid[inlen:], y_valid, p_valid, batch=0, mode=10)

p_train = lstm.Predict(model, x_train[inlen:, :bs, :], target_len=ow)
plotdata.PlotPredictions(x_train[inlen:], y_train, p_train, batch=0, mode=4)

# %% Saving and loading model
path = 'SavedModels/' + input('model name:')
torch.save(model.state_dict(), path)
#model.load_state_dict(torch.load(path))
#model.eval()

