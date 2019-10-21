import pandas as pd
import os

## cleaning the salaries first.

salaries = pd.read_csv('salaries.csv')
inflation = pd.read_csv('Inflation.csv')
batters = pd.read_csv('batters_bbr_full_TOTs_removed.csv')

salaries = salaries.drop(['age', 'signing_bonus',
                            'incentives', 'payroll_perc',
                            'active', 'lux_tax', 'team',], axis=1)

#include the cpi to the dataframe to get total_salary in dollars of 2018.

salaries = pd.merge(salaries,inflation, left_on = ['year'], right_on= ['year'] )
salaries['cpi'] = salaries['cpi'].astype(float)

for col in ['base_salary', 'total_salary', 'adjusted_salary']:

    salaries.drop(salaries[salaries[col]=='-'].index, inplace=True)
    salaries[col] = salaries[col].str.replace('$', '')
    salaries[col] = salaries[col].str.replace(',', '')
    salaries[col] = salaries[col].astype(int)
    salaries['real_' + col ] = salaries[col] * salaries['cpi']

#cleaning the batters dataframe (merged with salaries)

batters_sal = pd.merge(batters,salaries, left_on = ['key', 'Year'], right_on= ['key','year'] )
batters_sal = batters_sal.drop(['Salary'], axis=1)
batters_sal.Tm2.fillna(batters_sal.Tm, inplace=True)
batters_sal.Tm3.fillna(batters_sal.Tm2, inplace=True)
batters_sal.Awards.fillna('no_award', inplace=True)
batters_sal.dropna(inplace=True)


cwd = os.getcwd().replace('data_cleaning', 'modelling').replace('\\', '/')

batters_sal.to_csv(cwd + '/batters_stats_and_salary.csv')
