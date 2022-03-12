class MD:

    def __init__(self, md):
        self.md = md

    def get(self, key):
        """Return value of the given configuration item

        Searches for the key at top-level, in the experimental configuration common to
        all groups, and in the report configuration
        """
        if key in self.md.keys():
            val = self.md[key]
        elif key in self.md['expt_cfg']['common']:
            val = self.md['expt_cfg']['common'][key]
        elif key in self.md['rpt_cfg']:
            val = self.md['rpt_cfg'][key]
        else:
            raise KeyError(f'key {key} not found in metadata')

        return val

    def group(self, group_id):
        """Return independent variables and their values for the given group id"""
        group_id = 'group ' + str(group_id)
        if group_id in self.md['expt_cfg']:
            val = self.md['expt_cfg'][group_id]
        else:
            raise KeyError(f'group {group_id} not found in metadata')
        return val

    def group_label(self, group_id, label_map=None):
        """Return string describing independent variables and values for a group.

        Variable names are mapped to labels where defined in the label map, with default label map
        used if not specified
        """
        if label_map is None:
            label_map = self.get('default_label_map')
        expt_cond = ' '.join([f'{label_map.get(var, var)}: {val}' for var, val in self.group(group_id).items()])
        return f'group {group_id} - {expt_cond}'

    def default_labels(self, var_labels):
        ecfg = self.md['expt_cfg']
        group_ids = [str(gid) for gid in self.get('groups')]
        labels = {}
        for key, val in ecfg.items():
            if key.startswith('group') and ',' not in key:
                _, group_id = key.split()
                lst = [f'{group_id}:'] + [f'{var_labels.get(pname, pname)} {pval}' for pname, pval in val.items()]
                labels[group_id] = ' '.join(lst)

        # if any of the groups are not "simple" then just use the group id in the label
        if len(labels) != len(group_ids):
            for group_id in group_ids:
                labels[group_id] = f'group {group_id}'

        #     print(f'labels: {labels}')
        return labels
