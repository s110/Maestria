  import numpy as np
  import pandas as pd
  import matplotlib.pyplot as plt
  from mpl_toolkits.mplot3d import Axes3D
  import math

  from sklearn.preprocessing import MinMaxScaler

  # create training  dataset.
  x_vals = np.arange(0,2*np.pi,0.1)
  y_vals =  [ np.sin(e + np.random.normal(0,0.2) ) for e  in x_vals]
  data = pd.DataFrame({"x_train":x_vals, "y_train":y_vals})
  print(data)
  plt.plot(x_vals, y_vals,'*',)
  X = x_vals
  Y = y_vals

  X  = (X - min(X))/(max(X) - min(X))
  Y  = (Y - min(Y))/(max(Y) - min(Y))

  plt.plot(X,Y,"*")


  def h(X, W):
    return np.polyval(W,X)

  def Error(X, W, Y,lam):
    y_pred=h(X,W)
    print(y_pred)
    loss=np.mean((Y-h(X,W))**2)+lam*np.sum(W**2)
    return loss

  def derivada(X, W, Y, lam):
    # write your code here
    # Return a (k+1)x1 vector. This vector contains the derivatives from Loss function
    # respect to all variable w_j
    length = len(W)
    error = Y - h(W, X)
    dw = np.sum(error ** 2) * (-1 * X) /length  +2 * lam * np.sum(W)

    return dw

  def update(W,  dW, alpha):
    # write your code here
    W=W-alpha*dW
    return W

  def train(X, Y, epochs, alfa, lam):
    np.random.seed(2001)
    W = np.array([np.random.rand() for i in range(X.shape[1])])
    L = Error(X, W, Y, lam)
    loss = []
    for i in range(epochs):
      dW = derivada(X, W, Y, lam)
      W = update(W, dW, alfa)
      L = Error(X, W, Y, lam)
      loss.append(L)
      if i % 100000 == 0:
        print(L)
    return W, loss

  #Plotear la ecuación
  def conver_matrix(X, p):
    potencia = [i for i in range(p)]
    XX = [ [ e**i for e in X ] for i in potencia]
    return np.array(XX).T



  XX = conver_matrix(X,6)
  w , loss = train(XX,Y, 10000, 0.9,0.2) #train(XX,Y, 10000, 0.9, 0)
  plt.plot(X,Y,"*")
  y_aprox = h(XX,w)

  plt.plot(X,y_aprox,"*")