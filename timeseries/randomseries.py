# Created on 2020/7/16

# Packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import timeseries.timeseries as ts



### TIME SERIES MODELS ###

# These models describe the evolution of time series.


def AutoRegressive(start_date, end_date, frequency, start_values, cst, order, coeffs, sigma):
    """
    Function generating a time series from the Auto-Regressive (AR) model of an arbitrary order P.
    The model is of the form: x_t = cst + coeffs[0] * x_{t-1} + ... + coeffs[P-1] * x_{t-P} + a_t
    where a_t is the white noise with standard deviation sigma.
    Initial values for {x_0, ..., x_P} are imposed from the values in start_values.
    
    Note: noise is Gaussian here.
    """
    assert(len(coeffs)==order)
    assert(len(start_values)==order)
    P = len(start_values)
    
    # Generating index
    data_index = pd.date_range(start=start_date, end=end_date, freq=frequency)
    T = len(data_index)
    
    # Generating the white noise (Note: p first values are not used)
    a = np.random.normal(loc=0., scale=sigma, size=T)
    
    # Generating the random series
    x = [0.] * T
    for t_ini in range(P):
        x[t_ini] = start_values[t_ini]
    for t in range(P,T,1):
        x[t] = cst + a[t]
        for p in range(P):
            x[t] += coeffs[p] * x[t-p-1]
    
    # Computing theoretical expectation value
    E = cst / (1 - sum(coeffs))
    print("Under stationarity assumption, the expected value for this AR(" + str(P) + ") model is: " + str(E) + "\n")
    
    # Combining them into a time series
    df = pd.DataFrame(index=data_index, data=x)
    rs = ts.timeseries(df)
    return rs
    


def RandomWalk(start_date, end_date, frequency, start_value, sigma):
    """
    Function generating a time series from the Random Walk process, i.e. an AR(1) model with {cst = 0, coeff[0] = 1}.
    The model is of the form: x_t = x_{t-1} + a_t where a_t is the white noise with standard deviation sigma.
    
    Note: noise is Gaussian here.
    """
    # Generating index
    data_index = pd.date_range(start=start_date, end=end_date, freq=frequency)
    T = len(data_index)
    
    # Generating the white noise (Note: first value is not used)
    a = np.random.normal(loc=0., scale=sigma, size=T)
    
    # Generating the random series
    x = [0.] * T
    x[0] = start_value
    for t in range(1,T,1):
        x[t] = x[t-1] + a[t]
    
    # Combining them into a time series
    df = pd.DataFrame(index=data_index, data=x)
    rs = ts.timeseries(df)
    return rs
    

    
def DriftRandomWalk(start_date, end_date, frequency, start_value, drift, sigma):
    """
    Function generating a time series from the Random Walk with Drift process, i.e. an AR(1) model with {cst != 0, coeffs[0] = 1}.
    The model is of the form: x_t = drift + x_{t-1} + a_t where a_t is the white noise with standard deviation sigma.
    
    Note: noise is Gaussian here.
    """
    # Generating index
    data_index = pd.date_range(start=start_date, end=end_date, freq=frequency)
    T = len(data_index)
    
    # Generating the white noise (Note: first value is not used)
    a = np.random.normal(loc=0., scale=sigma, size=T)
    
    # Generating the random series
    x = [0.] * T
    x[0] = start_value
    for t in range(1,T,1):
        x[t] = drift + x[t-1] + a[t]
    
    # Combining them into a time series
    df = pd.DataFrame(index=data_index, data=x)
    rs = ts.timeseries(df)
    return rs
    
    

def MovingAverage(start_date, end_date, frequency, cst, order, coeffs, sigma):
    """
    Function generating a time series from the Moving Average (MA) model of an arbitrary order Q.
    The model is of the form: x_t = cst + a_t + coeffs[0] * a_{t-1} + ... + coeffs[Q-1] * a_{t-Q}
    where {a_t} is the white noise series with standard deviation sigma.
    We don't need to impose any initial values for {x_t} are imposed directly from {a_t}.
    
    Clarification: We thus assume {x_0 = cst + a_0 ; x_1 = cst + a_1 + coeffs[0] * a_0 ;
    x_2 = cst + a_2 + coeffs[0] * a_1 + coeffs[1] * a_0} ; ...
    
    Note: noise is Gaussian here.
    """
    assert(len(coeffs)==order)
    Q = order
    
    # Generating index
    data_index = pd.date_range(start=start_date, end=end_date, freq=frequency)
    T = len(data_index)
    
    # Generating the white noise
    a = np.random.normal(loc=0., scale=sigma, size=T)
    
    # Generating the random series
    x = [0.] * T
    for t in range(T):
        x[t] = cst + a[t]
        for q in range(Q):
            if t-q-1 >= 0:
                x[t] -= coeffs[q] * a[t-q-1]
    
    # Computing theoretical values
    V = 1.
    for q in range(Q):
        V += coeffs[q]**2
    V *= sigma**2
    print("The expected value for this MA(" + str(Q) + ") model is: " + str(cst))
    print("The estimation of the variance for this MA(" + str(Q) + ") model is: " + str(V) + \
          " , i.e. a standard deviation of: " + str(np.sqrt(V)) + "\n")
    
    # Combining them into a time series
    df = pd.DataFrame(index=data_index, data=x)
    rs = ts.timeseries(df)
    return rs



def ARMA(start_date, end_date, frequency, start_values, cst, ARorder, ARcoeffs, MAorder, MAcoeffs, sigma):
    """
    Function generating a time series from the Auto-Regressive Moving Average (ARMA) model of orders (P,Q).
    The model is of the form: x_t = cst + Sum_{i=0}^{P-1} ARcoeffs[i] * a_{t-i} + a_t + Sum_{j=0}^{Q-1} MAcoeffs[j] * a_{t-j}
    where {a_t} is the white noise series with standard deviation sigma.
    Initial values for {x_0, ..., x_P} are imposed from the values in start_values.
    
    Note: noise is Gaussian here.
    """
    assert(len(ARcoeffs)==ARorder)
    assert(len(MAcoeffs)==MAorder)
    assert(len(start_values)==ARorder)
    P = ARorder
    Q = MAorder
    
    # Generating index
    data_index = pd.date_range(start=start_date, end=end_date, freq=frequency)
    T = len(data_index)
    
    # Generating the white noise
    a = np.random.normal(loc=0., scale=sigma, size=T)
    
    # Generating the random series
    x = [0.] * T
    # Taking care of {x_0, x_1, ..., x_P}
    for t_ini in range(P):
        x[t_ini] = start_values[t_ini]
    # Taking care of the rest
    for t in range(P,T,1):
        x[t] = cst + a[t]
        for p in range(P):
            x[t] += ARcoeffs[p] * x[t-p]
        for q in range(Q):
            if t-q-1 >= 0:
                x[t] -= MAcoeffs[q] * x[t-q-1]
    
    # Combining them into a time series
    df = pd.DataFrame(index=data_index, data=x)
    rs = ts.timeseries(df)
    return rs




### HETEROSCEDASTIC MODELS ###

# These models describe the volatility of a time series.

def ARCH(start_date, end_date, frequency, cst, coeffs, order):
    """
    Function generating a volatility series from the Auto-Regressive Conditional Heteroscedastic (ARCH) model of order M.
    """



    
    
    
    
# GARCH = Generalized ARCH
# EGARCH = Exponential GARCH
# CHARMA = Conditional Heterescedastic ARMA
# RCA = Random Coefficient Auto-Regressive
# SV = Stochastic Volatility

