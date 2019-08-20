import pandas as pd

## cleaning the salaries first.

salaries = pd.read_csv('salaries.csv')
inflation = pd.read_csv('Inflation.csv')
batters = pd.read_csv('batters_bbr_full_TOTs_removed.csv')

salaries = salaries.drop(['age', 'status', 'base_salary', 'signing_bonus',
                            'incentives','adjusted_salary', 'payroll_perc',
                            'active', 'lux_tax', 'team',], axis=1)

#include the cpi to the dataframe to get total_salary in dollars of 2018.

salaries = pd.merge(salaries,inflation, left_on = ['year'], right_on= ['year'] )

salaries.drop(salaries[salaries['total_salary']=='-'].index, inplace=True)
salaries['total_salary'] = salaries['total_salary'].str.replace('$', '')
salaries['total_salary'] = salaries['total_salary'].str.replace(',', '')
salaries['total_salary'] = salaries['total_salary'].astype(int)

salaries['real_total_salary'] = salaries['total_salary'] * salaries['cpi']

batters = pd.merge(batters,salaries, left_on = ['key', 'Year'], right_on= ['key','year'] )

print(batters[['key', 'year','Salary', 'total_salary']].head(50))

## 'Salary' is a column from batters. 'total_salary' is from salaries.
## Which one do we keep?

## next step, reproduce and clean the R script here.
