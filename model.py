import pandas as pd
import os
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report, confusion_matrix
from getFilesFromGD import getFilesFromGD


def model():
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

#clean csv
    df = pd.read_csv('combined.csv') #change to the combined file
    df = df.dropna()
    df[df.iloc[:, 0] != 'error'] #I add errors to the dataset so I know what errors occur. remove these for training
#REMOVE later
    df.columns = ['time', 'direction','isweekend','after 10','12am-6am','passenger count','stop # of next stop on route','late','feelslike(f)', 'visibility(mi)','windgust(mph)','precip(in)','uv','humidity', 'conditions']

    encoded_cols = pd.get_dummies(df['conditions'])
    encoded_cols.reset_index(drop=True, inplace=True)

    X = df[["direction", "isweekend","after 10","12am-6am","passenger count","stop # of next stop on route", "feelslike(f)", "visibility(mi)", "windgust(mph)", "precip(in)", "uv", "humidity"]] #no time (index) and conditions (one-hot encoded)
    X.reset_index(drop=True, inplace=True)
    X = pd.concat([X, encoded_cols], axis=1)
    X.replace({True: 1, False: 0}, inplace=True)


    y = df["late"]
    y.reset_index(drop=True, inplace=True)

    print(X,y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Create an SVM classifier
    clf = svm.SVC(kernel='linear')

    # Train the SVM classifier
    clf.fit(X_train, y_train)

    # Make predictions on the testing set
    y_pred = clf.predict(X_test)

    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)

                    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                    # model = DecisionTreeClassifier()

                    # model.fit(X_train, y_train)

                    # y_pred = model.predict(X_test)

                    # # Evaluate the model
                    # print("Accuracy:", accuracy_score(y_test, y_pred))
                    # print("\nClassification Report:\n", classification_report(y_test, y_pred))
                    # print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))


                # mse = mean_squared_error(y_test, y_pred)
                # r2 = r2_score(y_test, y_pred)

                # acc = accuracy_score(y_test, y_pred)

                # print(f'Mean Squared Error: {mse}')
                # print(f'R-squared: {r2}')
                # print(f'Accuracy: {acc}')
                # print('Coefficients:', model.coef_)
                # print('Intercept:', model.intercept_)
    


    os.remove("combined.csv") #prevents clutter, esp since this is a big file

model()