import pandas as pd

df1 = pd.DataFrame({
    'atable':     ['Users', 'Users', 'Domains', 'Domains', 'Locks'],
    'column':     ['col_1', 'col_2', 'col_a', 'col_b', 'col'],
    'column_type':['varchar', 'varchar', 'int', 'varchar', 'varchar'],
    'is_null':    ['No', 'No', 'Yes', 'No', 'Yes'],
})

df1_grouped = df1.groupby('atable')

# iterate over each group
for group_name, df_group in df1_grouped:
    print('\nCREATE TABLE {}('.format(group_name))

    for row_index, row in df_group.iterrows():
        col = row['column']
        column_type = row['column_type']
        is_null = 'NOT NULL' if row['is_null'] == 'NO' else ''
        print('\t{} {} {},'.format(col, column_type, is_null))

    print(");")
