import streamlit as st
import pandas as pd
# import matplotlib.pyplot as pl
import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

funds = ['Cash', 'Default', 'Conservative', 'Moderate', 'Balanced', 'Growth']
fund_returns = {'Cash' : 1,
                'Default' : 2,
                'Conservative' : 3,
                'Moderate' : 4,
                'Balanced' : 5,
                'Growth' : 6
                }

pie_data = pd.DataFrame(columns = funds,
                        index = [
                                'Start Amount',
                                'Employee Contributions',
                                'Employer Contributions',
                                'Government Contributions',
                                'Investment Returns']
                        )
for col in pie_data.columns:
    pie_data[col].values[:] = 0
pie_data['Key'] = pie_data.index.values


# Get user parameters from sidebar.
def user_input_parameters():
    start_amount = int(st.sidebar.text_input("Initial Deposit", 1000))
    employee_contribution = st.sidebar.slider('Contribution', 3, 10, 4)
    employer_contribution = st.sidebar.slider('Employer Match', 3, 10, 4)
    yearly_salary = int(st.sidebar.text_input("Salary (Pre-Tax)", 25000))
    age = int(st.sidebar.text_input("Age", 18))
    fund = st.sidebar.selectbox("Fund", funds)
    compare = st.sidebar.button("Compare Funds")

    # Collate all parameters into a single object
    data = {'start_amount'          : start_amount,
            'employee_contribution' : employee_contribution,
            'employer_contribution' : employer_contribution,
            'yearly_salary'         : yearly_salary,
            'age'                   : age,
            'fund'                  : fund,
            'compare'               : compare
            }
    return data

# Get percentage from single number
def get_percentage(x, increase = False):
    if(increase):
        return (1 + (x / 100))
    else:
        return (x / 100)


# Create and fill the data frame based off input parameters
def create_df(data):
    df = pd.DataFrame(columns=['Year', 'Growth', 'Balanced', 'Moderate', 'Conservative', 'Default', 'Cash'])
    df = df.append([{'Year': datetime.datetime.now().year,
                     'Cash': data['start_amount'],
                     'Default': data['start_amount'],
                     'Conservative': data['start_amount'],
                     'Moderate': data['start_amount'],
                     'Balanced': data['start_amount'],
                     'Growth': data['start_amount']
                     }], ignore_index=True)

    yearly_salary = data['yearly_salary']
    contribution = data['employee_contribution']
    employer_contribution = data['employer_contribution']
    age = data['age']

    for fund in funds:
        pie_data[fund]['Start Amount'] = data['start_amount']

    employee_contribution_percentage = get_percentage(contribution)
    employer_contribution_percentage = get_percentage(employer_contribution)

    employee_contribution = employee_contribution_percentage * yearly_salary
    employer_contribution = employer_contribution_percentage * yearly_salary
    government_contribution = min(521.43, ((contribution / 100) * yearly_salary) / 2)

    for i in range(age + 1, 65):
        df = df.append([{'Year': df['Year'].max() + 1}], ignore_index=True)
        for fund in df.columns[1:]:
            new_amount = df[fund][df.shape[0] - 2]
            new_amount += government_contribution
            new_amount += employee_contribution
            new_amount += employer_contribution
            return_amount = new_amount * get_percentage(fund_returns[fund])
            new_amount += return_amount
            df[fund][df.shape[0] - 1] = new_amount

            pie_data[fund]['Employee Contributions'] = employee_contribution + pie_data[fund]['Employee Contributions']
            pie_data[fund]['Employer Contributions'] = employer_contribution + pie_data[fund]['Employer Contributions']
            pie_data[fund]['Government Contributions'] = government_contribution + pie_data[fund]['Government Contributions']
            pie_data[fund]['Investment Returns'] = return_amount + pie_data[fund]['Investment Returns']

    return df

def create_fund_comparison_chart(df):
    fig = go.Figure()
    colors = [
        '#9467bd',  # muted purple
        '#8c564b',  # chestnut brown
        '#e377c2',  # raspberry yogurt pink
        '#7f7f7f',  # middle gray
        '#bcbd22',  # curry yellow-green
        '#17becf'  # blue-teal
    ]

    for i in range(0, len(df.columns[1:])):
        fund = df.columns[i + 1]
        color = colors[i]
        width = 1
        if (fund == user_data['fund']):
            width = 5
        fig.add_trace(go.Scatter(x=df['Year'], y=df[fund],
                                 line=dict(color=color, width=width),
                                 name=fund))
    return fig

def create_fund_chart(df):
    fig = go.Figure()
    fund = user_data['fund']

    fig.add_trace(go.Scatter(x=df['Year'], y=df[fund],
                             name=fund))
    return fig

def create_pie_chart(data):
    fig = px.pie(data, values = user_data['fund'], names = 'Key')
    return fig

def create_pie_chart_comparison(data):
    fig = make_subplots(rows=3, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}],
                                               [{'type': 'domain'}, {'type': 'domain'}],
                                               [{'type': 'domain'}, {'type': 'domain'}]])
    r = 1
    c = 1
    for fund in data.columns.values[0:6]:
        fig.add_trace(go.Pie(labels = data['Key'], values=data[fund], name=fund), r, c)
        if c == 2:
            c = 1
            r += 1
        else:
            c += 1

    fig.update_traces(hole=.5, hoverinfo="label+percent+name")
    fig.update_layout(autosize = True)
    return fig



st.write("""
# Kiwisaver Calculator
""")

st.sidebar.header('User Input Parameters')

user_data = user_input_parameters()
df = create_df(user_data)

st.write(pie_data)
if(user_data['compare']):
    line_fig = create_fund_comparison_chart(df)
    pie_fig = create_pie_chart_comparison(pie_data)
else:
    line_fig = create_fund_chart(df)
    pie_fig = create_pie_chart(pie_data)


st.plotly_chart(line_fig)
st.plotly_chart(pie_fig)



