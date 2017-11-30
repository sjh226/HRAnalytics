import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

def overtime(vaca=False):
	ot_df = pd.read_csv('data/overtime.csv')
	ot_df.columns = [col.lower().replace(' ', '_') for col in ot_df.columns]

	def over_50(hours):
		if hours > 10:
			return hours - 10
		else:
			return 0

	ot_df['over_50'] = ot_df['number_of_hours'].apply(over_50)

	total_hours = ot_df.groupby(['full_name', 'empl./appl.name', 'global_id'], as_index=False).sum()
	total_hours = total_hours[['full_name', 'global_id', 'number_of_hours', 'over_50']]

	emp_df = pd.read_csv('data/headcount.csv')
	emp_df['o_unit'] = emp_df['Organizational Unit']
	emp_df.columns = [col.lower().replace(' ', '_') for col in emp_df.columns]
	emp_df['global_id'] = emp_df['gpid']

	overtime_df = pd.merge(emp_df, total_hours, on='global_id', how='outer')

	if vaca == True:
		vacation_df = vacation()
		vacation_df['personnel_number'] = vacation_df['employee_id']

		df = pd.merge(overtime_df, vacation_df, on='personnel_number', how='outer')
	else:
		df = overtime_df

	return df

def vacation():
	vaca_df = pd.read_csv('data/vacation.csv')
	vaca_df.columns = [col.lower().replace(' ', '_') for col in vaca_df.columns]

	vaca_df['perc_remaining'] = vaca_df['remainder'] / vaca_df['entitlement']

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
				 (df['primary_bu'].str.contains('OPERATIONS'))]['remainder'].mean()
		if avg > 0:
			y_dic[bu] = avg

	ind = np.arange(len(y_dic.keys()))
	width = 0.35

	p1 = ax1.bar(ind, y_dic.values(), width, color='#db4b32')
	ax1.set_ylabel('Average Remaining Vacation Time (Hours)')
	ax1.set_xlabel('BU')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')

	plt.title('Average Remaining Vacation Time of Non-Exempt Employees by BU')
	plt.tight_layout()

	plt.savefig('images/bu_vaca_nonexempt_avg.png')

def percent_vaca(df):
	plt.close()

	fig, ax1 = plt.subplots(1, 1, figsize=(17, 15))
	matplotlib.rcParams.update({'font.size': 18})

	df['primary_bu'] = df['primary_bu'].str.lstrip('L48 - ')

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
	for bu in sorted(ops['bu'].unique()):
		y_dic[bu] = ops[ops['bu'] == bu]['number_of_hours'].mean()

	ind = np.arange(len(ops['bu'].unique()))
	width = 0.35

	p1 = ax1.bar(ind, y_dic.values(), width, color='#db4b32')
	ax1.set_ylabel('Average Overtime Hours')
	ax1.set_xlabel('Business Unit')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')

	plt.title('Average Overtime Hours by BU')
	plt.tight_layout()

	plt.savefig('images/bu_overtime_avg.png')

def org_ot(df):
	plt.close()

	fig, ax1 = plt.subplots(1, 1, figsize=(17, 15))
	matplotlib.rcParams.update({'font.size': 18})

	units = []
	north = {}
	east = {}
	west = {}
	mid = {}
	y_dic = {}
	for unit in sorted(df[(df['o_unit'].str.contains('Ops')) & \
					 	  ~(df['o_unit'].str.contains('VP'))]['o_unit'].unique()):
		avg_hours = df[df['o_unit'] == unit]['number_of_hours'].mean()
		if avg_hours > 0:
			if 'north' in unit.lower():
				north[unit] = avg_hours
			elif 'east' in unit.lower():
				east[unit] =avg_hours
			elif 'west' in unit.lower():
				west[unit] = avg_hours
			elif 'mid' in unit.lower():
				mid[unit] = avg_hours

	for bu in [east, mid, north, west]:
		for unit in sorted(bu, key=bu.__getitem__):
			y_dic[unit] = bu[unit]

	ind = np.arange(len(y_dic.keys()))
	# Attempting to label BUs on graph
	# bu_labels = ind[[0, len(east) - 1, len(east) + len(mid) - 1, \
	# 				 len(east) + len(mid) + len(north) - 1, \
	# 				 len(east) + len(mid) + len(north) + len(west) - 1]]
	width = 0.35

	p1 = ax1.bar(ind, y_dic.values(), width, color='#db4b32')
	ax1.set_ylabel('Average Overtime Hours')
	ax1.set_xlabel('Organizational Unit')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')
	# ax1.set_xticks(bu_labels, minor=True)

	plt.title('Average Overtime Hours by Organizational Unit')
	plt.tight_layout()

	plt.savefig('images/o_unit_overtime_avg1.png', dpi=2000)

def bu_ot_50(df):
	plt.close()

	fig, ax1 = plt.subplots(1, 1, figsize=(17, 15))

	df['bu'] = df['bu'].str.lstrip('L48 - ')

	ops = df[df['bu'].str.contains('Operations')]

	y_dic = {}
	for bu in sorted(ops['bu'].unique()):
		y_dic[bu] = ops[ops['bu'] == bu]['over_50'].mean()

	ind = np.arange(len(ops['bu'].unique()))
	width = 0.35

	p1 = ax1.bar(ind, y_dic.values(), width, color='#db4b32')
	ax1.set_ylabel('Average Overtime Hours Over 50/week')
	ax1.set_xlabel('Business Unit')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')

	plt.title('Average Overtime Hours by BU')
	plt.tight_layout()

	plt.savefig('images/bu_overtime_50_avg.png')

def ot_nonexempt(df):
	plt.close()

	fig, ax1 = plt.subplots(1, 1, figsize=(17, 15))
	matplotlib.rcParams.update({'font.size': 18})

	df['primary_bu'] = df['primary_bu'].str.lstrip('L48 - ')

	y_dic = {}
	for bu in sorted(df['primary_bu'].astype(str).unique()):
		avg = df[(df['primary_bu'] == bu) & \
				 (df['employee_subgroup'].str.contains('Non')) & \
				 (df['primary_bu'].str.contains('OPERATIONS'))]['number_of_hours'].mean()
		if avg > 0:
			y_dic[bu] = avg

	ind = np.arange(len(y_dic.keys()))
	width = 0.35

	p1 = ax1.bar(ind, y_dic.values(), width, color='#db4b32')
	ax1.set_ylabel('Average Overtime (Hours)')
	ax1.set_xlabel('BU')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')

	plt.title('Average Overtime of Non-Exempt Employees by BU')
	plt.tight_layout()

	plt.savefig('images/bu_ot_nonexempt_avg.png')

if __name__ == '__main__':
	ot_df = overtime()
	# bu_ot(ot_df)
	org_ot(ot_df)
	# bu_ot_50(ot_df)
	# ot_vac_df = overtime(vaca=True)
	# ot_nonexempt(ot_df)

	# vaca_df = vacation()
	# vac_remaining(vaca_df)
	# vac_pos(vaca_df)
	# vac_nonexempt(vaca_df)
	# percent_vaca(vaca_df)
