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

def vacation():
	vaca_df = pd.read_csv('data/vacation.csv')
	vaca_df.columns = [col.lower().replace(' ', '_') for col in vaca_df.columns]

	return vaca_df

def vac_remaining(df):
	plt.close()

	fig, ax1 = plt.subplots(1, 1, figsize=(17, 15))
	matplotlib.rcParams.update({'font.size': 18})

	df['primary_bu'] = df['primary_bu'].str.lstrip('L48 - ')

	y_dic = {}
	for bu in sorted(df['primary_bu'].unique()):
		y_dic[bu] = df[df['primary_bu'] == bu]['remainder'].sum()

	ind = np.arange(len(df['primary_bu'].unique()))
	width = 0.35

	p1 = ax1.bar(ind, y_dic.values(), width, color='#db4b32')
	ax1.set_ylabel('Total Remaining Vacation Time (Hours)')
	ax1.set_xlabel('Business Unit')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')

	plt.title('Remaining Vacation Time by BU')
	plt.tight_layout()

	plt.savefig('images/bu_vaca_r.png')

def vac_pos(df):
	plt.close()

	fig, ax1 = plt.subplots(1, 1, figsize=(17, 15))
	matplotlib.rcParams.update({'font.size': 18})

	df['primary_bu'] = df['primary_bu'].str.lstrip('L48 - ')

	y_dic = {}
	for pos in sorted(df['position'].unique()):
		rem = df[df['position'] == pos]['remainder'].mean()
		if rem > 100:
			y_dic[pos] = rem

	ind = np.arange(len(y_dic.keys()))
	width = 0.35

	p1 = ax1.bar(ind, y_dic.values(), width, color='#db4b32')
	ax1.set_ylabel('Average Remaining Vacation Time (Hours)')
	ax1.set_xlabel('Position')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')

	plt.title('Average Remaining Vacation Time by Position\nLimited to Positions with >100 Hours')
	plt.tight_layout()

	plt.savefig('images/pos_vaca_r.png')

def vac_nonexempt(df):
	plt.close()

	fig, ax1 = plt.subplots(1, 1, figsize=(17, 15))
	matplotlib.rcParams.update({'font.size': 18})

	df['primary_bu'] = df['primary_bu'].str.lstrip('L48 - ')

	y_dic = {}
	for bu in sorted(df['primary_bu'].unique()):
		avg = df[(df['primary_bu'] == bu) & \
				 (df['employee_subgroup'].str.contains('Non')) & \
				 (df['primary_bu'].str.contains('OPERATIONS'))]['remainder'].sum()
		if avg > 0:
			y_dic[bu] = avg

	ind = np.arange(len(y_dic.keys()))
	width = 0.35

	p1 = ax1.bar(ind, y_dic.values(), width, color='#db4b32')
	ax1.set_ylabel('Total Remaining Vacation Time (Hours)')
	ax1.set_xlabel('BU')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')

	plt.title('Total Remaining Vacation Time of Non-Exempt Employees by BU')
	plt.tight_layout()

	plt.savefig('images/bu_vaca_nonexempt_tot.png')

def percent_vaca(df):
	plt.close()

	fig, ax1 = plt.subplots(1, 1, figsize=(17, 15))
	matplotlib.rcParams.update({'font.size': 18})

	df['primary_bu'] = df['primary_bu'].str.lstrip('L48 - ')
	df['perc_remaining'] = df['remainder'] / df['entitlement']

	y_dic = {}
	for bu in sorted(df['primary_bu'].unique()):
		avg = df[(df['primary_bu'] == bu) & \
				 (df['primary_bu'].str.contains('OPERATIONS'))]['perc_remaining'].mean()
		if avg > 0:
			y_dic[bu] = avg

	ind = np.arange(len(y_dic.keys()))
	width = 0.35

	p1 = ax1.bar(ind, y_dic.values(), width, color='#db4b32')
	ax1.set_ylabel('Average Percent Vacation Remaining')
	ax1.set_xlabel('BU')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')

	plt.title('Percent Remaining Vacation by BU')
	plt.tight_layout()

	plt.savefig('images/bu_vaca_perc.png')

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
	# ot_df = overtime()
	# bu_ot(df)
	# org_ot(ot_df)

	vaca_df = vacation()
	# vac_remaining(vaca_df)
	# vac_pos(vaca_df)
	# vac_nonexempt(vaca_df)
	percent_vaca(vaca_df)
