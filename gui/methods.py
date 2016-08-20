methods = {
	'Perfect_Match_Aligner': {
		'short':'PM',
		'parameters': {
				'Mismatch Quality Threshold': {
					'type':'Entry',
					'datatype':'int',
					'name':'mismatch_quality_threshold'
				},
				'Variant Quality Threshold': {
					'type':'Entry',
					'datatype':'int',
					'name':'variant_sequence_quality_threshold'
				}
			}
		},
	'Bowtie_Aligner': {
		'short':'BT',
		'parameters': {
				'Local alignment': {
					'type':'Checkbutton',
					'name':'bt1'
				},
				'Match using elimination': {
					'type':'Checkbutton',
                    'datatype':'str',
					'name':'bt2'
				},
				'Total Quality Score Threshold': {
					'type':'Entry',
					'datatype':'float',
					'name':'bt3'
				},
				'Allow insertions/deletions': {
					'type':'Checkbutton',
					'name':'bt4'
				}
			}
		}
	}


# ,
# 	'Mosaik': {
# 		'short':'MS',
# 		'parameters': {
# 				'Number of errors': {
# 					'type':'Entry',
# 					'datatype':'int',
# 					'name':'ms1'
# 				},
# 				'Mosaik param 2': {
# 					'type':'Checkbutton',
# 					'name':'ms2'
# 				},
# 				'Mosaik param 3': {
# 					'type':'Entry',
# 					'datatype':'int',
# 					'name':'ms3'
# 				},
# 				'Mosaik param 4': {
# 					'type':'Checkbutton',
# 					'name':'ms4'
# 				}
# 			}
# 		}