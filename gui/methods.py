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
                        'name':'is_local'
                },
                # 'Reference Name': {
    #                     'type':'Entry',
    #                 'datatype':'str',
                #         'name':'reference_name'
                # },
                'Total Quality Score Threshold': {
                        'type':'Entry',
                    'datatype':'float',
                        'name':'quality_threshold'
                },
                'Allow insertions/deletions': {
                        'type':'Checkbutton',
                        'name':'allow_insertions_deletions'
                },
                'Alignment approach':{
                        'type':'Radiobutton',
                        'name':'approach',
                     'options':{
                         'Eliminate NNK from template':'elimination',
                         'Mismatch Strategy':'mismatch'
                     }
                }
            }
        }
    }


# ,
#     'Mosaik': {
#         'short':'MS',
#         'parameters': {
#                 'Number of errors': {
#                     'type':'Entry',
#                     'datatype':'int',
#                     'name':'ms1'
#                 },
#                 'Mosaik param 2': {
#                     'type':'Checkbutton',
#                     'name':'ms2'
#                 },
#                 'Mosaik param 3': {
#                     'type':'Entry',
#                     'datatype':'int',
#                     'name':'ms3'
#                 },
#                 'Mosaik param 4': {
#                     'type':'Checkbutton',
#                     'name':'ms4'
#                 }
#             }
#         }