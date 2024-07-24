
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
from sklearn.utils import resample  # Add this import
from getFilesFromGD import getFilesFromGD
import os

def mainModel():


    #get files
    status, message = getFilesFromGD(all=True) #gets all data files from google drive
    if status == 404:
        print(message)

    #COMBINE FILES 
    if os.path.isfile("combined.csv"): #remove old combined.csv if applicable
        os.remove("combined.csv")


    csv_files = [file for file in os.listdir('.') if file.endswith('.csv')]
    dfs = []
    for file in csv_files:
        df = pd.read_csv(file)
        dfs.append(df)


    combined_df = pd.concat(dfs, ignore_index=True)

    combined_df.to_csv('combined.csv', index=False)

    print("Combined csv files into combined.csv")

    #deletes all csv files except combined.csv to prevent clutter
    csv_files = [file for file in os.listdir('.') if file.endswith('.csv')]
    files_to_delete = [file for file in csv_files if file != 'combined.csv']
    for file in files_to_delete:
        os.remove(file)

    # Read the CSV file
    df = pd.read_csv('combined.csv')
    df = df.dropna()
    df = df[df.iloc[:, 0] != 'error']  # Corrected to reassign df

    # One-hot encode the 'conditions' column
    encoded_cols = pd.get_dummies(df['conditions'])
    encoded_cols.reset_index(drop=True, inplace=True)

    # Extract additional temporal features from 'time'
    df['time'] = pd.to_datetime(df['time'])
    df['hour'] = df['time'].dt.hour
    df['day_of_week'] = df['time'].dt.dayofweek
    df['month'] = df['time'].dt.month

    # Select and prepare the feature columns
    X = df[["direction", "isweekend", "after 10", "12am-6am", "passenger count",
            "stop # of next stop on route", "feelslike(f)", "visibility(mi)", 
            "windgust(mph)", "precip(in)", "uv", "humidity", "hour", "day_of_week", "month"]]
    X.reset_index(drop=True, inplace=True)
    X = pd.concat([X, encoded_cols], axis=1)
    X.replace({True: 1, False: 0}, inplace=True)

    # Select the target column
    y = df["late"]
    y.reset_index(drop=True, inplace=True)

    # Handle imbalanced data by oversampling the minority class
    df_balanced = pd.concat([X, y], axis=1)
    df_minority = df_balanced[df_balanced.late == 1]
    df_majority = df_balanced[df_balanced.late == 0]

    df_minority_upsampled = resample(df_minority, 
                                    replace=True,     # sample with replacement
                                    n_samples=len(df_majority),    # to match majority class
                                    random_state=42) # reproducible results

    df_balanced = pd.concat([df_majority, df_minority_upsampled])

    X_balanced = df_balanced.drop('late', axis=1)
    y_balanced = df_balanced['late']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_balanced, y_balanced, test_size=0.2, random_state=42)

    # Scale the features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Convert the data to PyTorch tensors
    X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
    X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train.values, dtype=torch.float32).view(-1, 1)
    y_test_tensor = torch.tensor(y_test.values, dtype=torch.float32).view(-1, 1)

    # Define the neural network
    class SimpleNN(nn.Module):
        def __init__(self, input_size):
            super(SimpleNN, self).__init__()
            self.fc1 = nn.Linear(input_size, 128)  # First hidden layer
            self.fc2 = nn.Linear(128,256)
            self.fc3 = nn.Linear(256,128)
            self.fc4 = nn.Linear(128, 64)  # Second hidden layer
            self.fc5 = nn.Linear(64, 32)  # Third hidden layer
            self.output = nn.Linear(32, 1)  # Output layer
        
        def forward(self, x):
            x = F.relu(self.fc1(x))
            x = F.relu(self.fc2(x))
            x = F.relu(self.fc3(x))
            x = F.relu(self.fc4(x))
            x = F.relu(self.fc5(x))
            x = torch.sigmoid(self.output(x))  # Sigmoid activation for binary classification
            return x

    # Initialize the model, loss function, and optimizer
    input_size = X_train.shape[1]  # Number of features
    model = SimpleNN(input_size)
    criterion = nn.BCELoss()  # Binary Cross-Entropy Loss
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Train the model
    num_epochs = 10000
    for epoch in range(num_epochs):
        model.train()
        
        optimizer.zero_grad()  # Zero the parameter gradients
        
        outputs = model(X_train_tensor)  # Forward pass
        loss = criterion(outputs, y_train_tensor)  # Compute the loss
        
        loss.backward()  # Backward pass
        optimizer.step()  # Update the weights
        
        if (epoch + 1) % 100 == 0:
            print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}')

    # Evaluate the model
    torch.save(model.state_dict(), 'model.pth')

    model.eval()
    with torch.no_grad():
        predictions = model(X_test_tensor)
        predictions = (predictions >= 0.5).float()  # Apply threshold to get binary outputs

        accuracy = (predictions == y_test_tensor).float().mean()
        # print(f'Accuracy: {accuracy.item():.4f}')
        return accuracy



# Step 1: Read and preprocess the data
def getMostImportantFeatures():
    df = pd.read_csv('combined.csv')
    df = df.dropna()
    df = df[df.iloc[:, 0] != 'error']  # Corrected to reassign df

    # One-hot encode the 'conditions' column
    encoded_cols = pd.get_dummies(df['conditions'])
    encoded_cols.reset_index(drop=True, inplace=True)

    # Extract additional temporal features from 'time'
    df['time'] = pd.to_datetime(df['time'])
    df['hour'] = df['time'].dt.hour
    df['day_of_week'] = df['time'].dt.dayofweek
    df['month'] = df['time'].dt.month

    # Select and prepare the feature columns
    X = df[["direction", "isweekend", "after 10", "12am-6am", "passenger count",
            "stop # of next stop on route", "feelslike(f)", "visibility(mi)", 
            "windgust(mph)", "precip(in)", "uv", "humidity", "hour", "day_of_week", "month"]]
    X.reset_index(drop=True, inplace=True)
    X = pd.concat([X, encoded_cols], axis=1)
    X.replace({True: 1, False: 0}, inplace=True)

    # Select the target column
    y = df["late"]
    y.reset_index(drop=True, inplace=True)

    # Handle imbalanced data by oversampling the minority class
    df_balanced = pd.concat([X, y], axis=1)
    df_minority = df_balanced[df_balanced.late == 1]
    df_majority = df_balanced[df_balanced.late == 0]

    df_minority_upsampled = resample(df_minority, 
                                    replace=True,     # sample with replacement
                                    n_samples=len(df_majority),    # to match majority class
                                    random_state=42) # reproducible results

    df_balanced = pd.concat([df_majority, df_minority_upsampled])

    X_balanced = df_balanced.drop('late', axis=1)
    y_balanced = df_balanced['late']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_balanced, y_balanced, test_size=0.2, random_state=42)

    # Step 2: Fit a Random Forest model to determine feature importance
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    # Step 3: Extract and plot feature importances
    importances = rf.feature_importances_
    indices = np.argsort(importances)[::-1]
    feature_names = X_balanced.columns

    # Print the feature ranking

    ret = {}
    print("Feature ranking:")
    for f in range(X_train.shape[1]):
        print(f"{f + 1}. feature {indices[f]} ({importances[indices[f]]:.4f}) - {feature_names[indices[f]]}")
        ret[feature_names[indices[f]]] = importances[indices[f]]

    return ret

    # # Plot the feature importances
    # plt.figure(figsize=(12, 8))
    # sns.barplot(x=importances[indices], y=[feature_names[i] for i in indices])
    # plt.title("Feature Importances")
    # plt.xlabel("Relative Importance")
    # plt.ylabel("Feature")
    # plt.show()
