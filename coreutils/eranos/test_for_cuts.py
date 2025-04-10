# input: core object
# beta-tests for the axial cuts

# run make_core_object first
# add fixed to the input JSON

dict_ass_cuts = alfred_nea.NE.AxialConfig.cuts
ass = dict_ass_cuts.keys()
trans_ass = ['CR']
for assembly in ass:
    if "trans" in assembly:
        trans_ass.append(assembly)

my_dict = {}

for ass in trans_ass:
    ax_cuts = dict_ass_cuts[ass]
    reg = ax_cuts.reg
    loz = ax_cuts.loz
    upz = ax_cuts.upz
    my_dict[ass] = {'reg':reg,'loz':loz,'upz':upz}

ass = 'CR-1trans'
cuts = alfred_nea.NE.AxialConfig.cuts[ass]
transconfig = {"which": [[6, 37]],"dz": [-10],"fixed": [72]}
dz = transconfig['dz'][0]
fixed_pos = transconfig.get("fixed",[0])[0]

if fixed_pos == 0:
    cuts.upz[0:-1] = [z+dz for z in cuts.upz[0:-1]]
    cuts.loz[1:] = [z+dz for z in cuts.loz[1:]]
else:
    for i in range(len(cuts.upz)-1):
        if cuts.upz[i]<=fixed_pos:
            cuts.upz[i] += 0
            cuts.loz[i] += 0
        else:
            if cuts.loz[i]+dz <= fixed_pos and cuts.upz[i]+dz > fixed_pos:
                cuts.loz[i] = fixed_pos
                cuts.upz[i] += dz
            elif cuts.loz[i]+dz <= fixed_pos and cuts.upz[i]+dz <= fixed_pos:
                cuts.upz[i] = fixed_pos
                cuts.loz[i] = fixed_pos
            else:
                cuts.upz[i] += dz
                cuts.loz[i] += dz
    cuts.loz[-1] += dz

