import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

def overtime():
	ot_df = pd.read_csv('data/overtime.csv')
	ot_df.columns = [col.lower().replace(' ', '_') for col in ot_df.columns]

	total_hours = ot_df.groupby(['full_name', 'empl./appl.name', 'global_id'], as_index=False).sum()
	total_hours = total_hours[['full_name', 'global_id', 'number_of_hours']]

	emp_df = pd.read_csv('data/headcount.csv')
	emp_df['o_unit'] = emp_df['Organizational Unit']
	emp_df.columns = [col.lower().replace(' ', '_') for col in emp_df.columns]
	emp_df['global_id'] = emp_df['gpid']

	df = pd.merge(emp_df, total_hours, on='global_id', how='outer')

	return df

def bu_ot(df):
	plt.close()

	fig, ax1 = plt.subplots(1, 1, figsize=(17, 15))
	matplotlib.rcParams.update({'font.size': 18})

	df['bu'] = df['bu'].str.lstrip('L48 - ')

	ops = df[df['bu'].str.contains('Operations')]

	y_dic = {}
	for bu in ops['bu'].unique():
		y_dic[bu] = ops[ops['bu'] == bu]['number_of_hours'].sum()

	ind = np.arange(len(ops['bu'].unique()))
	width = 0.35

	p1 = ax1.bar(ind, y_dic.values(), width, color='#db4b32')
	ax1.set_ylabel('Total Overtime Hours')
	ax1.set_xlabel('Business Unit')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')

	plt.title('Total Overtime Hours by BU')
	plt.tight_layout()

	plt.savefig('images/bu_overtime.png')

def org_ot(df):
	plt.close()

	fig, ax1 = plt.subplots(1, 1, figsize=(17, 15))
	matplotlib.rcParams.update({'font.size': 18})

	units = []
	y_dic = {}
	for unit in sorted(df['o_unit'].unique()):
		tot_hours = df[df['o_unit'] == unit]['number_of_hours'].sum()
		if tot_hours > 100:
			y_dic[unit] = tot_hours
			units.append(unit)

	ind = np.arange(len(units))
	width = 0.35

	p1 = ax1.bar(ind, y_dic.values(), width, color='#db4b32')
	ax1.set_ylabel('Total Overtime Hours')
	ax1.set_xlabel('Organizational Unit')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')

	plt.title('Total Overtime Hours by Organizational Unit\nLimited to Units with >100 Hours')
	plt.tight_layout()

	plt.savefig('images/o_unit_overtime.png')


if __name__ == '__main__':
	df = overtime()
	# bu_ot(df)
	org_ot(df)
