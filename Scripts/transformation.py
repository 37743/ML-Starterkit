from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, LabelEncoder
from numpy import log, power
from pandas import DataFrame, concat

def perform_transformations(data, transformation_types, columns_subset):
    if columns_subset == []:
        columns_subset = data.columns

    for label in transformation_types:
        if label == 'Standardization':
            for col in columns_subset:
                scaler = StandardScaler()
                data[col] = scaler.fit_transform(data[col].values.reshape(-1, 1))
        elif label == 'Normalization':
            for col in columns_subset:
                scaler = MinMaxScaler()
                data[col] = scaler.fit_transform(data[col].values.reshape(-1, 1))
        elif label == 'One-Hot Encoding':
            for col in columns_subset:
                encoder = OneHotEncoder()
                if data[col].dtype == 'object':
                    transformed_data = DataFrame(encoder.fit_transform(data[col]).toarray())
                    data = concat([data, transformed_data], axis=1)
        elif label == 'Label Encoding':
            for col in columns_subset:
                encoder = LabelEncoder()
                if data[col].dtype == 'object':
                    data[col] = encoder.fit_transform(data[col])
        elif label == 'Log Transformation':
            # Works only on right-skewed/positive skew data
            if data[col].skew() > 0.3:
                data[col] = log(data[col])
        elif label == 'Polynomial Transformation':
            # Works only on left-skewed/negative skew data
            for col in columns_subset:
                if data[col].skew() < -0.3:
                    data[col] = power(data[col], 2)
    return data
