from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import seaborn as sb
from sklearn.linear_model import Lasso, LinearRegression, LogisticRegression, Ridge
from sklearn.metrics import confusion_matrix
from statsmodels.regression.linear_model import RegressionResultsWrapper
from statsmodels.stats.diagnostic import normal_ad
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import plotly.express as px 

colors = ['#FF69B4', '#FFB6C1']  
importance_palette = ['#E093B8', '#E093B8','#E093B8', '#F0A1C6', '#F0A1C6', '#F0A1C6', '#E3B8C6', '#E3B8C6','#E3B8C6', '#E6D1D4', '#E6D1D4', '#E6D1D4']
palette3 = ['#E093B8', '#F0A1C6', '#E3B8C6', "#E6D1D4"] 

def bar_plot(data_frame, variable):
    '''This function creates a bar plot for a given variable in a DataFrame, 
    displaying the count of unique values with labels "No (0)" and "Yes (1)".'''
    data = data_frame[variable]
    values_count = data.value_counts()
    plt.figure(figsize=(10, 5))
    bars = plt.bar(values_count.index, values_count, color=colors)
    plt.xticks(values_count.index, values_count.index.values)
    plt.ylabel("Count")
    plt.title(variable)
    plt.legend([bars[0], bars[1]], ['No (0)', 'Yes (1)'], loc='upper right')
    plt.show()

def bmi_histogram(data_frame):
    '''This function creates a bar plot showing the distribution of BMI categories 
    (Underweight, Healthy Weight, Overweight, Obesity) based on the "BMI" column in a DataFrame.'''
    column = data_frame["BMI"]
    frequency = {
        "Underweight": 0,
        "Healthy Weight": 0,
        "Overweight": 0,
        "Obesity": 0,
    }

    for bmi in column.values:
        if bmi < 18.5:
            frequency["Underweight"] += 1
        elif bmi < 25:
            frequency["Healthy Weight"] += 1
        elif bmi < 30:
            frequency["Overweight"] += 1
        else:
            frequency["Obesity"] += 1

    group_names = list(frequency.keys())
    group_counts = list(frequency.values())
    plt.figure(figsize=(10, 6))
    plt.bar(group_names, group_counts, color=colors[0])
    plt.title('BMI Categories Distribution')
    plt.xlabel('BMI Categories')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

# functions for analysis of model

def check_for_missing_values(df): 
    '''This function checks for missing values in a DataFrame and returns a DataFrame 
    showing the number and percentage of missing values for each column with missing data.'''
    missing_values = df.isna().sum()
    non_zero_missing = missing_values[missing_values != 0]
    non_zero_missing_percentage = (non_zero_missing / len(df)) * 100
    return pd.DataFrame({
        'N missing': non_zero_missing,
        '% missing': non_zero_missing_percentage
    })

def correlation_matrix(data_frame):
    '''This function creates a heatmap of the correlation matrix of a DataFrame, 
    displaying the correlation coefficients between numerical features.'''
    plt.subplots(figsize=(30,10))
    plt.xticks(rotation=45) 
    sb.heatmap(data_frame.corr(), annot=True, fmt = ".2f")
    plt.show()  

def get_lasso_model(features, labels):
    '''This function fits a Lasso regression model to the given features and labels, 
    with a specified regularization strength (alpha=0.01), and returns the trained model.'''
    lasso_model = Lasso(alpha=0.01)
    lasso_model.fit(features, labels)
    return lasso_model

# functions for evulation of model

def get_sse(model, features, labels):
    '''This function calculates the Sum of Squared Errors (SSE) for a given model, features, and labels. 
    It supports linear regression models and requires prediction functionality from the model.'''
    if hasattr(model, 'predict'):  
        if isinstance(model, sm.regression.linear_model.RegressionResultsWrapper):
            features = sm.add_constant(features, has_constant='add')
        y_pred = model.predict(features)
        sse = np.sum((labels - y_pred) ** 2)
        return sse
    raise ValueError("Unsupported model type for SSE calculation.")

def get_rsquared(model, features, labels):
    '''This function calculates the R-squared (R²) value for a given model, features, and labels, 
    indicating the proportion of variance explained by the model.'''
    if hasattr(model, 'predict'):
        if isinstance(model, sm.regression.linear_model.RegressionResultsWrapper):
            features = sm.add_constant(features, has_constant='add')
        y_pred = model.predict(features)
        from sklearn.metrics import r2_score
        r_squared = r2_score(labels, y_pred)
        return r_squared
    raise ValueError("Unsupported model type for R² calculation.")

def evaluate_model(model, name, features, labels):
    '''This function evaluates a model by calculating and printing its SSE, RMSE, R², and adjusted R² for given features and labels.'''
    sse = get_sse(model, features, labels) 
    rmse = get_rmse(model, features, labels)
    rsquared = get_rsquared(model, features, labels)
    rsquared_adj = get_rsquared_adj(model, features, labels)

    print(f"{name} Model:")
    print(f"SSE: {sse}")
    print(f"RMSE: {rmse}")
    print(f"R²: {rsquared}")
    print(f"R² adj : {rsquared_adj}\n")

# fuctions fo checking assumptions of the model

def calculate_residuals(model, features, labels):
    '''This function calculates the residuals (difference between actual and predicted values) 
    for a given model and returns them in a DataFrame along with actual and predicted values.'''
    y_pred = model.predict(features)
    df_results = pd.DataFrame({'Actual': labels, 'Predicted': y_pred})
    df_results['Residuals'] = abs(df_results['Actual']) - abs(df_results['Predicted'])
    return df_results

def linear_assumption(model: LinearRegression | RegressionResultsWrapper, features: np.ndarray | pd.DataFrame, labels: pd.Series, p_value_thresh=0.05, plot=True):
    '''This function checks the linearity assumption for a linear regression model, 
    and optionally plots the predicted vs. actual values, along with the line of perfect predictions.'''
    df_results = calculate_residuals(model, features, labels)
    y_pred = df_results['Predicted']
    
    if plot:
        plt.figure(figsize=(6,6))
        plt.scatter(labels, y_pred, alpha=.5)
        line_coords = np.linspace(np.concatenate([labels, y_pred]).min(), np.concatenate([labels, y_pred]).max())
        plt.plot(line_coords, line_coords, color='darkorange', linestyle='--')
        plt.title('Linear assumption')
        plt.xlabel('Actual')
        plt.ylabel('Predicted')
        plt.show()

    if isinstance(model, RegressionResultsWrapper):
        p_value = model.f_pvalue
        is_linearity_found = p_value < p_value_thresh
        return is_linearity_found, p_value
    else:
        return True, None

def normality_of_errors_assumption(model, features, label, p_value_thresh=0.05, plot=True):
    '''This function checks the normality of errors assumption by testing the residuals 
    for normality and optionally plotting the distribution of residuals.'''
    df_results = calculate_residuals(model, features, label)
    
    if plot:
        plt.title('Distribution of residuals')
        sb.histplot(df_results['Residuals'], kde=True, kde_kws={'cut': 3})
        plt.show()
    
    p_value = normal_ad(df_results['Residuals'])[1]
    dist_type = 'normal' if p_value >= p_value_thresh else 'non-normal'
    return dist_type, p_value

def perfect_collinearity_assumption(features: pd.DataFrame, plot=True):
    '''This function checks for perfect collinearity in the feature set by calculating the correlation matrix, 
    and optionally plotting the heatmap of correlations.'''
    correlation_matrix = features.corr()
    
    if plot:
        sb.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.1)
        plt.title('Correlation Matrix')
        plt.show()
    
    np.fill_diagonal(correlation_matrix.values, np.nan)
    pos_perfect_collinearity = (correlation_matrix > 0.999).any().any()
    neg_perfect_collinearity = (correlation_matrix < -0.999).any().any()
    has_perfect_collinearity = pos_perfect_collinearity or neg_perfect_collinearity
    
    return has_perfect_collinearity

def calculate_vif(x_train):
    '''This function calculates the Variance Inflation Factor (VIF) for each feature in the dataset.'''
    x_train_with_const = sm.add_constant(x_train, has_constant='add')
    vif_data = pd.DataFrame()
    vif_data["Variable"] = x_train_with_const.columns
    vif_data["VIF"] = [variance_inflation_factor(x_train_with_const.values, i) 
                       for i in range(x_train_with_const.shape[1])]
    
    return vif_data

def are_assumptions_satisfied_linear(model, features, labels, p_value_thresh=0.05):
    '''This function checks if the assumptions for linear regression are satisfied:
    Linearity, Independence of errors (no autocorrelation), Normality of errors, 
    Equal variance (homoscedasticity), and no Perfect collinearity.'''
    x_with_const = sm.add_constant(features)
    is_linearity_found, p_value = linear_assumption(model, x_with_const, labels, p_value_thresh, plot=False)
    autocorrelation, dw_value = independence_of_errors_assumption(model, x_with_const, labels, plot=False)
    n_dist_type, p_value = normality_of_errors_assumption(model, x_with_const, labels, p_value_thresh, plot=False)
    e_dist_type, p_value = equal_variance_assumption(model, x_with_const, labels, p_value_thresh, plot=False)
    has_perfect_collinearity = perfect_collinearity_assumption(features, plot=False)
    
    if not is_linearity_found:
        return "Linearity assumption is not satisfied."
    elif autocorrelation is not None:
        return "Independence of errors (no autocorrelation) assumption is not satisfied."
    elif n_dist_type != 'normal':
        return f"Normality of errors assumption is not satisfied. Distribution type: {n_dist_type}"
    elif e_dist_type != 'equal':
        return f"Equal variance (homoscedasticity) assumption is not satisfied. Distribution type: {e_dist_type}"
    elif has_perfect_collinearity:
        return "Perfect collinearity assumption is not satisfied."
    else:
        return True
    
def check_model_assumptions(model, features, labels, p_value_thresh=0.05):
    '''This function checks the assumptions for different models: LinearRegression, Ridge, Lasso, and LogisticRegression.'''
    if isinstance(model, (LinearRegression, RegressionResultsWrapper)):
        return are_assumptions_satisfied_linear(model, features, labels, p_value_thresh)
    if isinstance(model, (Ridge, Lasso)):
        return are_assumptions_satisfied_ridge_lasso(model, features, labels, p_value_thresh)
    elif isinstance(model, LogisticRegression):
        return are_assumptions_satisfied_logistic(model, features, labels, p_value_thresh)
    else:
        return "Model type not supported for assumption checks."
    
# functions for visualization

def plot_comparison(data_frame, feature, label):
    '''The function displays a linear regression plot (lmplot) for the given feature and label, comparing data based on PCOS status.'''
    figure= sb.lmplot(data=data_frame, x=feature, y=label, hue="PCOS(Y/N)", palette= colors)
    plt.show()

def plot_logistic_confusion_matrix(model, x_test, y_test):
    ''' Function to generate and plot a confusion matrix for a logistic regression model.'''
    predictions = model.predict(x_test)
    cm = confusion_matrix(y_test, predictions)
    palette3 = ['#F2BED1', '#FDCEDF', '#F8E8EE', "#F9F5F6"]
    cmap = ListedColormap(palette3)
    plt.figure(figsize=(8, 6))
    sb.heatmap(cm, annot=True, fmt='d', cmap=cmap, cbar=False, 
               vmin=0, vmax=cm.max(),
               xticklabels=["Not Pcos", "Pcos"], yticklabels=["Not Pcos", "Pcos"])
    plt.title("Confusion Matrix for Logistic Regression Model", fontsize=16)
    plt.xlabel("Predicted Label", fontsize=14)
    plt.ylabel("True Label", fontsize=14)
    plt.show()

def plot_pairplot(data_frame):
    '''Creates a pairplot for visualizing relationships between features and label'''
    features = ["Age(yrs)", "BMI", "Cycle length(days)"]
    label = ["PCOS(Y/N)"]
    selected_columns = features + label
    sb.pairplot(data_frame[selected_columns], diag_kind='kde', corner=True, hue='PCOS(Y/N)', palette=colors)
    plt.suptitle('Pairplot of Features and Targets', y=1.02)
    plt.show()

def pcos_visualization(data_frame, logistic_model, x_test, y_test):
    '''The function displays visualization of data frame'''
    features = ["Age(yrs)","Weight(kg)", "BMI", "Hb(g/dl)", "Cycle length(days)","Endometrium(mm)",
                 "Follicle No.(L)","Follicle No.(R)"]
    plot_pcos_swarmbox(data_frame, features)

    features = ["Age(yrs)","Age(yrs)", "Age(yrs)","Follicle No.(R)","Avg. F size(L)(mm)"]
    labels = ["Cycle length(days)", "BMI", "Cycle(R/I)", "Follicle No.(L)", "Avg. F size(R)(mm)"]
    for i in range(len(features)):
        plot_comparison(data_frame, features[i], labels[i])

    plot_logistic_confusion_matrix(logistic_model, x_test, y_test)
    visualize_feature_importance(logistic_model, x_test)

    plot_pairplot(data_frame)
    plot_3d_scatter(data_frame)