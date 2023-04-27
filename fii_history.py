import yfinance as yf
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import joblib

def preprocess_data(df):
    # Drop rows with missing values
    df.dropna(inplace=True)

    # Calculate the target variable, next week's closing price
    df['Next_Week_Close'] = df['Close'].shift(-7)

    # Drop the last 7 rows as they have no next week closing price
    df.drop(df.tail(7).index, inplace=True)

    return df

def train_neural_network(df, ticker):
    # Preprocess the data
    df = preprocess_data(df)

    # Check if the DataFrame has enough rows
    if df.shape[0] < 10:
        print(f"Not enough data for {ticker}. Skipping...")
        return

    # Define the features and target variable
    X = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    y = df['Next_Week_Close']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create a pipeline with data preprocessing and the neural network model
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('nn', MLPRegressor())
    ])

    # Define the hyperparameters for grid search
    param_grid = {
        'nn__hidden_layer_sizes': [(50,), (100,), (200,)],
        'nn__activation': ['relu', 'tanh', 'logistic'],
        'nn__alpha': [0.0001, 0.001, 0.01],
        'nn__learning_rate_init': [0.001, 0.01, 0.1]
    }

    # Create the grid search object
    grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='neg_mean_squared_error', n_jobs=-1)

    # Train the model using grid search
    grid_search.fit(X_train, y_train)

    # Evaluate the model on the test set
    y_pred = grid_search.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print("Mean Squared Error: ", mse)

    best_nn_model = grid_search.best_estimator_

    # Save the trained model
    output_path = f"./models/{ticker}_model.pkl"
    joblib.dump(best_nn_model, output_path)
    print(f"Model for {ticker} saved at {output_path}")

def get_fii_history(ticker, start_date="2010-01-01"):
    end_date = datetime.now().strftime('%Y-%m-%d')
    try:
        fii = yf.Ticker(ticker)
        fii_history = fii.history(start=start_date, end=end_date)
        fii_history.to_csv(f"./history/{ticker}.csv")
    except:
        print(f"Error: {ticker}")

if __name__ == "__main__":
    fiis_list= ['QIRI11.SA', 'VINO11.SA', 'MGFF11.SA', 'VILG11.SA', 'XPCM11.SA', 'HABT11.SA', 'BBGO11.SA', 'VGIA11.SA', 'KISU11.SA', 'XPCI11.SA', 'CPTS11.SA', 'EQIR11.SA', 'MCHF11.SA', 'RECR11.SA', 'RBHG11.SA', 'TGAR11.SA', 'HGAG11.SA', 'AAZQ11.SA', 'KNHY11.SA', 'GTWR11.SA', 'CYCR11.SA', 'RZAG11.SA', 'MGCR11.SA', 'XPSF11.SA', 'GAME11.SA', 'BIME11.SA', 'KNCA11.SA', 'VGIR11.SA', 'XPCA11.SA', 'VIUR11.SA', 'TGAR11.SA', 'OURE11.SA']

    dict_current_price = {}
    for fii in fiis_list:
        get_fii_history(fii)

    folder_path = './history/'
    files = os.listdir(folder_path)
    for file in files:
        ticker = file.replace('.csv', '')
        print(f"Training model for {ticker}...")
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)

        # Train and save the neural network model
        train_neural_network(df, ticker)
