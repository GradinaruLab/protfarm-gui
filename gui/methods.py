methods = {
	'Perfect match': {
		'short':'PM',
		'parameters': {
				'Mismatch Quality Threshold': {
					'type':'Entry',
					'name':'mismatch_quality_threshold'
				},
				'Variant Quality Threshold': {
					'type':'Entry',
					'name':'variant_sequence_quality_threshold'
				}
			}
		},
	'BowTie': {
		'short':'BT',
		'parameters': {
				'BowTie param 1': {
					'type':'Checkbutton',
					'name':'bt1'
				},
				'BowTie param 2': {
					'type':'Checkbutton',
					'name':'bt2'
				},
				'Number of mistakes': {
					'type':'Entry',
					'name':'bt3'
				},
				'Allow insertions/deletions': {
					'type':'Checkbutton',
					'name':'bt4'
				}
			}
		},
	'Mosaik': {
		'short':'MS',
		'parameters': {
				'Number of errors': {
					'type':'Entry',
					'name':'ms1'
				},
				'Mosaik param 2': {
					'type':'Checkbutton',
					'name':'ms2'
				},
				'Mosaik param 3': {
					'type':'Entry',
					'name':'ms3'
				},
				'Mosaik param 4': {
					'type':'Checkbutton',
					'name':'ms4'
				}
			}
		}
	}
# Perfect match = PM[1-9][0-9]*
# BowTie = BT[1-9][0-9]*
# Mosaik = MS[1-9][0-9]*