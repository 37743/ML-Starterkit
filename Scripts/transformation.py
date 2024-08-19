'''
This script contains the function to perform transformations on the data.
The function takes in the data, the types of transformations to be performed,
and the columns on which the transformations are to be performed.
'''

from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder, LabelEncoder
from numpy import log1p, power
from pandas import DataFrame, concat
from Scripts.Threading.functhreading import thread

@thread
def perform_transformations(data, transformation_types, columns_subset):
    """
    Apply various transformations to the specified columns of the given data.

    Parameters:
    - data (pandas.DataFrame): The input data to be transformed.
    - transformation_types (list): A list of transformation types to be applied. Available options are:
        - 'Standardization': Perform standardization on numeric columns.
        - 'Normalization': Perform normalization on numeric columns.
        - 'One-Hot Encoding': Perform one-hot encoding on categorical columns.
        - 'Label Encoding': Perform label encoding on categorical columns.
        - 'Log Transformation': Perform log transformation on right-skewed numeric columns.
        - 'Polynomial Transformation': Perform polynomial transformation on left-skewed numeric columns.

    - columns_subset (list): A list of column names to be transformed. If empty, all columns will be transformed.

    Returns:
    None
    """
    if transformation_types == []:
        return False
    if columns_subset == []:
        columns_subset = data.columns
    
    # Makes sure to perform standardization/normalization first.
    if 'Standardization' in transformation_types:
        for col in columns_subset:
            if data[col].dtype == 'object':
                continue
            scaler = StandardScaler()
            data[col] = scaler.fit_transform(data[col].values.reshape(-1, 1))
    elif 'Normalization' in transformation_types:
        for col in columns_subset:
            if data[col].dtype == 'object':
                continue
            scaler = MinMaxScaler()
            data[col] = scaler.fit_transform(data[col].values.reshape(-1, 1))

    for label in transformation_types:
        if label == 'One-Hot Encoding':
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
            for col in columns_subset:
                if data[col].dtype == 'object':
                    continue
                if data[col].skew() > 0.3:
                    # Handling negative values
                    data[col] = log1p(data[col] - data[col].min())
        elif label == 'Polynomial Transformation':
            # Works only on left-skewed/negative skew data
            for col in columns_subset:
                if data[col].dtype == 'object':
                    continue
                if data[col].skew() < -0.3:
                    data[col] = power(data[col], 2)
    return True
