import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

def regression(df):
    # Convert the date column to numeric values
    
    df['date_numeric'] = pd.to_numeric(df['date'])

    # Fit a linear regression model
    X = df['date_numeric'].values.reshape(-1, 1)
    y = df['smoothed_revenue'].values.reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, y)

    # Generate predicted values
    X_pred = np.linspace(X.min(), X.max(), num=100).reshape(-1, 1)
    y_pred = model.predict(X_pred)

    # Plot the data and trend line
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['smoothed_revenue'], marker='o', linestyle='-', label='Net Sales')
    plt.plot(pd.to_datetime(X_pred.flatten()), y_pred.flatten(), linestyle='--', color='red', label='Trend Line')
    plt.xlabel('Date')
    plt.ylabel('Revenue (Normalized)')
    plt.title('Revenue Trend')
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True)
    return plt
