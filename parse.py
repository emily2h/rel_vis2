import pandas as pd 
import json


def write_json(df, df_alt):
	uniq_c1 = list(pd.unique(df.couple1))
	uniq_c2 = list(pd.unique(df.couple2))
	uniq_alt = list(pd.unique(df_alt.couple1)) + list(pd.unique(df_alt.couple2))
	uniq_nodes = list(set(uniq_c1 + uniq_c2 + uniq_alt))
	nodes = list()
	non_lead_connects = {name:0 for name in uniq_nodes}
	for c in uniq_nodes:
		if c in uniq_c1:
			group = 'lead'
		elif c in uniq_c2:
			group = df[df.couple2 == c].show_season.values[0]

		nodes.append({"id": c, "group": group})

	edges = list()

	for i, rows in df.iterrows():
		if rows.couple1 in non_lead_connects:
			non_lead_connects[rows.couple1] += 1
		if rows.couple2 in non_lead_connects:
			non_lead_connects[rows.couple2] += 1
		edges.append({"source": rows.couple1, "target": rows.couple2, "group": rows.relationship_status})

	for i, rows in df_alt.iterrows():
		if rows.couple1 in non_lead_connects:
			non_lead_connects[rows.couple1] += 1
		if rows.couple2 in non_lead_connects:
			non_lead_connects[rows.couple2] += 1

		edges.append({"source": rows.couple1, "target": rows.couple2, "group": rows.relationship_status})


	df_dict = {"nodes":nodes, "links":edges}
	# print(len(nodes))
	# print(len(edges))
	# print(df.relationship_status.value_counts())
	# print(df_alt.relationship_status.value_counts())
	# print(non_lead_connects)
	# print(sorted(non_lead_connects.items(), key=lambda item: item[1]))
	# for key, item in non_lead_connects.items():
	# 	if item >= 10:
	# 		print(key,item)


	with open("sample.json", "w") as outfile: 
	    json.dump(df_dict, outfile, indent=4)


def main():
	df = pd.read_csv("rel_full.csv")
	df_alt = pd.read_csv("rel_alt.csv")
	write_json(df, df_alt)

if __name__ == '__main__':
	main()