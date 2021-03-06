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

		vo_df = pd.merge(overtime_df, vacation_df, on='personnel_number', how='outer')
	else:
		vo_df = overtime_df

	vo_df['emp_name'] = vo_df['first_name'].str.lower() + ' ' + vo_df['last_name'].str.lower()

	# sup_df = pd.read_csv('data/vaca_rej.csv')
	# sup_df.columns = [col.lower().replace(' ', '_') for col in sup_df.columns]
	# sup_df.rename(columns={'manager/approver_name': 'supervisor'}, inplace=True)
    #
	# sup_df['emp_name'] = sup_df['employee_name'].str.lower()
	# sup_df['emp_name'] = sup_df['emp_name'].str.lstrip(' ')
	# sup_df['emp_name'] = sup_df['emp_name'].str.lstrip('miss')
	# sup_df['emp_name'] = sup_df['emp_name'].str.lstrip('ms')
	# sup_df['emp_name'] = sup_df['emp_name'].str.lstrip('mr')
	# sup_df['emp_name'] = sup_df['emp_name'].str.lstrip('mrs')
    #
	# sup_df['super'] = sup_df['manager/approver_name'].str.lower()
	# sup_df['super'] = sup_df['super'].str.lstrip(' ')
	# sup_df['super'] = sup_df['super'].str.lstrip('miss')
	# sup_df['super'] = sup_df['super'].str.lstrip('ms')
	# sup_df['super'] = sup_df['super'].str.lstrip('mr')
	# sup_df['super'] = sup_df['super'].str.lstrip('mrs')

	sup_df = pd.read_csv('data/super_map.csv')
	sup_df.columns = [col.lower().replace(' ', '_') for col in sup_df.columns]
	sup_df.rename(columns={'employee_name': 'emp_name'}, inplace=True)

	def name_format(val):
		return ' '.join(val.split(',')[::-1]).lower().strip()

	for col in ['emp_name', 'supervisor']:
		sup_df.loc[:, col] = sup_df[col].apply(name_format)

	sup_df = sup_df[['emp_name', 'supervisor']].drop_duplicates()
	sup_df.loc[:, 'supervisor'] = sup_df['supervisor'].str.title()

	df = pd.merge(vo_df, sup_df, on='emp_name', how='outer')
	df['number_of_hours'] = df['number_of_hours'].fillna(0)

	return df

def rej_vaca():
	df = pd.read_csv('data/vaca_rej.csv')
	df.columns = [col.lower().replace(' ', '_') for col in df.columns]
	df.rename(columns={'manager/approver_name': 'supervisor'}, inplace=True)
	df = df[(df['leave_request_date'].str.contains('2016')) & (df['note'].isnull())]

	df.loc[:, 'supervisor'] = df['supervisor'].str.lower()
	df.loc[:, 'supervisor'] = df['supervisor'].str.lstrip()
	df.loc[:, 'supervisor'] = df['supervisor'].str.lstrip('miss')
	df.loc[:, 'supervisor'] = df['supervisor'].str.lstrip('ms')
	df.loc[:, 'supervisor'] = df['supervisor'].str.lstrip('mr')
	df.loc[:, 'supervisor'] = df['supervisor'].str.lstrip('mrs')
	df.loc[:, 'supervisor'] = df['supervisor'].str.title()

	sup_df = df[['supervisor', 'absence_hours', 'status']]

	sup_df = sup_df.groupby(['supervisor', 'status'], as_index=False).sum()

	org_df = pd.read_csv('data/headcount.csv')
	org_df.drop(['Organizational unit'], axis=1, inplace=True)
	org_df.columns = [col.lower().replace(' ', '_') for col in org_df.columns]
	org_df.loc[:, 'supervisor'] = org_df['first_name'] + ' ' + org_df['last_name']
	org_df = org_df[['supervisor', 'organizational_unit']]

	sup_df = pd.merge(sup_df, org_df, on='supervisor', how='outer')

	return sup_df, df

def reject_plot(df, full_df, plot_type='total'):
	plt.close()

	fig, ax1 = plt.subplots(1, 1, figsize=(17, 15))

	sup_dic = {}
	total_emp_dic = {}
	for sup in df[(df['status'].str.lower() == 'rejected') & \
				  (df['organizational_unit'].str.contains('Ops'))]['supervisor'].unique():
		sup_dic[sup] = df[(df['status'].str.lower() == 'rejected') & \
						(df['supervisor'] == sup)]['absence_hours'].unique()[0]

	for sup in df[df['status'].str.lower() == 'rejected']['supervisor'].unique():
		total_emp_dic[sup] = df[(df['status'].str.lower() == 'rejected') & \
						(df['supervisor'] == sup)]['absence_hours'].unique()[0] /\
						full_df[full_df['supervisor'] == sup]['employee_name'].shape[0]

	y_dic = {}
	if plot_type == 'total':
		for sup in sorted(sup_dic, key=sup_dic.__getitem__):
			y_dic[sup] = sup_dic[sup]
	elif plot_type == 'average':
		for sup in sorted(total_emp_dic, key=total_emp_dic.__getitem__):
			y_dic[sup] = total_emp_dic[sup]

	ind = np.arange(len(y_dic))
	width = 0.35

	ax1.bar(ind, y_dic.values(), width, color='#db4b32')
	ax1.set_ylabel('{} Declined Vacation Time (Hours)'.format(plot_type.title()))
	ax1.set_xlabel('Supervisor')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')

	plt.title('Declined Vacation Time by Supervisor')
	plt.tight_layout()
	if plot_type == 'total':
		plt.savefig('images/sup_decl_vaca.png')
	elif plot_type == 'average':
		plt.savefig('images/sup_decl_vaca_avg.png')

def west_overtime():
	ot_df = pd.read_csv('data/west_ot.csv', encoding = 'ISO-8859-1')
	ot_df.rename(columns={ot_df.columns[3]: 'bu_primary'}, inplace=True)
	ot_df.columns = [col.lower().replace(' ', '_') for col in ot_df.columns]

	ot_df.groupby(['employee_name', 'personnel_area', 'organizational_unit', \
				   'bu_primary', 'position', 'absence/remuneration_date', \
				   'wage_type', 'supervisor'], as_index=False).sum()

	ot_df.dropna(inplace=True)

	ot_df['remuneration__number'] = pd.to_numeric(ot_df['remuneration__number'])

	return ot_df

def vacation():
	vaca_df = pd.read_csv('data/vacation.csv')
	vaca_df.columns = [col.lower().replace(' ', '_') for col in vaca_df.columns]

	vaca_df['perc_remaining'] = vaca_df['remainder'] / vaca_df['entitlement']

	return vaca_df

def west_sup_plot(df):
	plt.close()

	fig, ax1 = plt.subplots(1, 1, figsize=(17, 15))
	matplotlib.rcParams.update({'font.size': 18})

	sum_dic = {}
	mean_dic = {}
	y_dic = {}
	y2_dic = {}
	for sup in sorted(df['supervisor'].astype(str).unique()):
		sum_dic[sup] = df[df['supervisor'] == sup]['remuneration__number'].sum()
		mean_dic[sup] = df[df['supervisor'] == sup]['remuneration__number'].mean()

	for sup in sorted(sum_dic, key=sum_dic.__getitem__):
		y_dic[sup] = sum_dic[sup]
		y2_dic[sup] = mean_dic[sup]

	ind = np.arange(len(y_dic))
	width = 0.35

	p1 = ax1.bar(ind, y_dic.values(), width, color='#25379b')
	ax1.set_ylabel('Total Overtime Hours')
	ax1.set_xlabel('Supervisor')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')

	ax2 = ax1.twinx()
	p2 = ax2.bar(ind + width, y2_dic.values(), width, color='#649b25')
	ax2.set_ylabel('Average Overtime Hours')

	plt.title('Overtime Hours in West by Supervisor')
	plt.legend((p1[0], p2[0]), ('Total Hours', 'Average Hours'), loc=2)
	plt.tight_layout()

	plt.savefig('images/west_overtime.png')

def approval():
	vaca_df = pd.read_csv('data/vaca_request.csv')
	vaca_df.columns = [col.lower().replace(' ', '_') for col in vaca_df.columns]
	vaca_df = vaca_df[['position', 'pers.no.', 'hrs', 'organizational_unit']]

	total_vaca_df = vaca_df.groupby(['position', 'pers.no.', 'organizational_unit'], as_index=False).sum()
	total_vaca_df.rename(columns={'hrs': 'req_hours', 'pers.no.': 'pers_no'}, inplace=True)

	pto_df = pd.read_csv('data/pto.csv')
	pto_df.columns = [col.lower().replace(' ', '_') for col in pto_df.columns]
	pto_df = pto_df[pto_df['attendance_or_absence_type'].str.lower() == 'vacation']
	pto_df = pto_df[['pers.no.', 'hrs']]

	total_pto_df = pto_df.groupby(['pers.no.'], as_index=False).sum()
	total_pto_df.rename(columns={'hrs': 'actual_hours', 'pers.no.': 'pers_no'}, inplace=True)

	df = pd.merge(total_vaca_df, total_pto_df, on='pers_no', how='outer')
	df = df.groupby(['pers_no', 'position', 'actual_hours'], as_index=False).sum()

	person_df = pd.read_csv('data/personnel.csv', header=None)
	person_df = person_df[[0, 5, 12]]
	person_df.columns = ['pers_no', 'office', 'department']

	df = pd.merge(df, person_df, on='pers_no')

	df['declined_hours'] = df['req_hours'] - df['actual_hours']

	return df

def decline_plot(df):
	plt.close()

	fig, ax1 = plt.subplots(1, 1, figsize=(17, 15))

	y_dic = {}
	for dept in sorted(df[df['department'].str.contains('Ops')]['department'].unique()):
		decl_mean = df[df['department'] == dept]['declined_hours'].mean()
		if decl_mean > 0:
			y_dic[dept] = decl_mean

	ind = np.arange(len(y_dic))
	width = 0.35

	p1 = ax1.bar(ind, y_dic.values(), width, color='#db4b32')
	ax1.set_ylabel('Total Declined Vacation Time (Hours)')
	ax1.set_xlabel('Department')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')

	plt.title('Declined Vacation Time by BU')
	plt.tight_layout()

	plt.savefig('images/bu_decl_vaca.png')

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

	fig, ax = plt.subplots(1, 1, figsize=(17, 15))
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
				north[unit.lstrip('North Ops ')] = avg_hours
			elif 'east' in unit.lower():
				east[unit.lstrip('East Ops ')] =avg_hours
			elif 'west' in unit.lower():
				west[unit.lstrip('West Ops ')] = avg_hours
			elif 'mid' in unit.lower():
				mid[unit.lstrip('Mid Con Ops ')] = avg_hours

	for bu in [east, mid, north, west]:
		for unit in sorted(bu, key=bu.__getitem__):
			y_dic[unit] = bu[unit]

	ind = np.arange(len(y_dic.keys()))
	# Attempting to label BUs on graph
	# bu_labels = ind[[0, len(east) - 1, len(east) + len(mid) - 1, \
	# 				 len(east) + len(mid) + len(north) - 1, \
	# 				 len(east) + len(mid) + len(north) + len(west) - 1]]
	width = 0.35

	east_ind = ind[:len(east)]
	mid_ind = ind[len(east):len(east) + len(mid)]
	north_ind = ind[len(east) + len(mid): len(east) + len(mid) + len(north)]
	west_ind = ind[len(east) + len(mid) + len(north):]

	# p1 = ax1.bar(ind, y_dic.values(), width, color='#db4b32')
	p1 = ax.bar(east_ind, sorted(east.values()), width, color='#db4b32')
	p2 = ax.bar(mid_ind, sorted(mid.values()), width, color='#ad7900')
	p3 = ax.bar(north_ind, sorted(north.values()), width, color='#30c16f')
	p4 = ax.bar(west_ind, sorted(west.values()), width, color='#0772ba')
	ax.set_ylabel('Average Overtime Hours')
	ax.set_xlabel('Operations Unit')
	ax.text(.5, 250, 'East', color='#db4b32', fontsize=24, fontweight='bold')
	ax.text(7, 175, 'Mid Con', color='#ad7900', fontsize=24, fontweight='bold')
	ax.text(18, 275, 'North', color='#30c16f', fontsize=24, fontweight='bold')
	ax.text(35, 200, 'West', color='#0772ba', fontsize=24, fontweight='bold')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')
	# ax1.set_xticks(bu_labels, minor=True)

	# plt.legend((p1[0], p2[0], p3[0], p4[0]), ('East', 'Mid Con', 'North', 'West'), loc=2)
	plt.title('Average Overtime Hours by Operations Organizational Unit')
	plt.tight_layout()

	plt.savefig('images/o_unit_overtime_avg.png')

def sup_ot(df):
	plt.close()

	fig, ax = plt.subplots(1, 1, figsize=(17, 15))
	matplotlib.rcParams.update({'font.size': 18})

	df.dropna(subset=['o_unit'], inplace=True)

	sup_dic = {}
	north = {}
	east = {}
	west = {}
	mid = {}
	for supervisor in df[(df['o_unit'].str.contains('Ops')) & \
					 	 ~(df['o_unit'].str.contains('VP'))]['supervisor'].unique():
		avg_hours = df[df['supervisor'] == supervisor]['number_of_hours'].mean()
		if avg_hours > 0:
			sup_dic[supervisor] = avg_hours
			if 'north' in df[df['supervisor'] == supervisor]['bu'].unique()[0].lower():
				north[supervisor] = avg_hours
			elif 'east' in df[df['supervisor'] == supervisor]['bu'].unique()[0].lower():
				east[supervisor] = avg_hours
			elif 'west' in df[df['supervisor'] == supervisor]['bu'].unique()[0].lower():
				west[supervisor] = avg_hours
			elif 'mid' in df[df['supervisor'] == supervisor]['bu'].unique()[0].lower():
				mid[supervisor] = avg_hours

	y_dic = {}
	for bu in [east, mid, north, west]:
		for sup in sorted(bu, key=bu.__getitem__):
			y_dic[sup] = bu[sup]

	ind = np.arange(len(y_dic.keys()))
	width = 0.35

	east_ind = ind[:len(east)]
	mid_ind = ind[len(east):len(east) + len(mid)]
	north_ind = ind[len(east) + len(mid): len(east) + len(mid) + len(north)]
	west_ind = ind[len(east) + len(mid) + len(north):]

	p1 = ax.bar(east_ind, sorted(east.values()), width, color='#db4b32')
	p2 = ax.bar(mid_ind, sorted(mid.values()), width, color='#ad7900')
	p3 = ax.bar(north_ind, sorted(north.values()), width, color='#30c16f')
	p4 = ax.bar(west_ind, sorted(west.values()), width, color='#0772ba')
	ax.set_ylabel('Average Overtime Hours')
	ax.set_xlabel('Supervisor')
	ax.text(.5, 125, 'East', color='#db4b32', fontsize=24, fontweight='bold')
	ax.text(7, 165, 'Mid Con', color='#ad7900', fontsize=24, fontweight='bold')
	ax.text(18, 205, 'North', color='#30c16f', fontsize=24, fontweight='bold')
	ax.text(33, 130, 'West', color='#0772ba', fontsize=24, fontweight='bold')

	# p1 = ax.bar(ind, y_dic.values(), width, color='#db4b32')
	# ax.set_ylabel('Average Overtime Hours')
	# ax.set_xlabel('Supervisor')
	plt.xticks(ind, y_dic.keys(), rotation='vertical')

	plt.title('Average Overtime Hours by Supervisor')
	plt.tight_layout()

	plt.savefig('images/sup_overtime_avg.png')

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
	# ot_df = overtime()
	# bu_ot(ot_df)
	# org_ot(ot_df)
	# bu_ot_50(ot_df)
	# ot_vac_df = overtime(vaca=True)
	# ot_nonexempt(ot_df)
	# sup_ot(ot_df)

	# vaca_df = vacation()
	# vac_remaining(vaca_df)
	# vac_pos(vaca_df)
	# vac_nonexempt(vaca_df)
	# percent_vaca(vaca_df)

	# app_df = approval()
	# decline_plot(app_df)

	# w_ot_df = west_overtime()
	# west_sup_plot(w_ot_df)

	vaca_df, full_df = rej_vaca()
	reject_plot(vaca_df, full_df, plot_type='average')
