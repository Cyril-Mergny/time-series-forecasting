# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 16:37:09 2021

@author: Cyril
"""

### IMPORTS

import numpy as np
from tqdm import trange
#from soft_dtw_cuda import SoftDTW
from torch.utils.tensorboard import SummaryWriter
import torch
import torch.nn as nn
from torch import optim


### CLASSES

class Encoder(nn.Module):
    """ Used to encode a sequence of time series """
    
    def __init__(self, input_size, hidden_size, num_layers=1):
        """ Simple LSTM layer"""
        super().__init__()
        # LSTM
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers)
        
    def forward(self, x):
        """ 
        For S, N, H the Source length, Batch size and Hidden size:
            x.shape = (S, N, H) : input
            out.shape = (S, N, H) : hidden states for all times
            hidden.shape = (1, N, H) : hidden state
            cell.shape = (1, N, H) : cell state
        """   
        out, (hidden, cell) = self.lstm(x) # hidden not provided : both h_0 and c_0 default to zero.
        return(out, hidden, cell)

class Decoder(nn.Module):
    """ Use hidden state init by Encoder to make predictions """
    
    def __init__(self, input_size, hidden_size, num_layers=1):
        """Decoder : LSTM layer followed by a linear layer"""
        super().__init__()  
        # LSTM
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers) #initalize
        self.linear = nn.Linear(hidden_size, input_size)
        
    def forward(self, x, hidden, cell):
        """ 
        For S, N, H the Source length, Batch size and Hidden size:
            x.shape = (S, N, H) : input
            out.shape = (S, N, H) : hidden states for all times
            hidden.shape = (1, N, H) : hidden state
            cell.shape = (1, N, H) : cell state
        """  
        out, (hidden, cell) = self.lstm(x, (hidden, cell))
        out = self.linear(out.squeeze(0))
        return(out, hidden, cell)
    
class LSTM_EncoderDecoder(nn.Module):
    """
    Use the two Encoder and Decoder classes to train a LSTM neural network
    Can also make predictions once the NN is trained
    """
    def __init__(self, input_size, hidden_size):
        """ Initialising variables with param and Encoder/Decoder classes"""
        super().__init__()
        self.encoder = Encoder(input_size, hidden_size)
        self.decoder = Decoder(input_size, hidden_size)
        

    def forward(self, x, target_len):
        # Initialise outputs (targetlen, bs, # features)
        outputs = torch.zeros(target_len,  x.shape[1], x.shape[2]).to(x.device)
        # Initialise h,c and call Encoder 
        out_e, hidden_e, cell_e = self.encoder(x)
        # Initialise Decoder
        input_d = x[-1, :, :].unsqueeze(0) # shape(bs, n_features)
        hidden_d, cell_d = hidden_e, cell_e
        
        # Iterate by values to predict
        for t in range(target_len):
            # Call Decoder
            out_d, hidden_d, cell_d = self.decoder(input_d, hidden_d, cell_d)
            outputs[t] = out_d
            input_d = out_d.unsqueeze(0)
        return(outputs)