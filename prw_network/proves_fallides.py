    
# EM PETA L'ORDINADOR...
def getContactsFromTrajOPT(filename, interac_r, loops, toFile=True):
    ticksPerCicle = loops*ticksPerLoop
    trajDF = pd.read_csv(configs_path+filename)
    # get a contact list from each configuration:
    ids = pd.unique(trajDF['ID'])
    Nbots = len(ids)
    Nconfigs = len(trajDF)/Nbots
    # is there any tick with more than 1 config?
    count = Counter(list(trajDF.loc[trajDF['ID']==0]['ticks']))
    ticks_plus1_configs = []
    for k,v in count.items():
        if v>1:
            ticks_plus1_configs.append(k)
    if(ticks_plus1_configs):
        print(f"There are {len(ticks_plus1_configs)} ticks with more than 1 config, from Nconfigs.")
    # search for contacts in each configuration and build the columns of a future dataframe:
    configID, cicleID, contacts0, contacts1 = [], [], [], []
    cicle = 0
    for i in tqdm(range(int(Nconfigs))):
        dfconfig = trajDF.loc[(i*Nbots):(i*Nbots+Nbots-1)]
        dfconfig.reset_index(drop=True, inplace=True)
        if int(dfconfig['ticks'][0]) > (cicle+1)*ticksPerCicle:
            cicle += 1
        positions = [(x,y) for (x,y) in zip(dfconfig['x_position'], dfconfig['y_position'])]
        contactCounter = 0
        for j,pos in enumerate(positions[:-1]):
            pos = positions[j]
            dists = [dist2D(pos1, pos) for pos1 in positions[j+1:]]
            contactsAgenti = [k+1+j for k,d in enumerate(dists) if d < 70.0]
            contacts0.extend([j]*len(contactsAgenti)), contacts1.extend(contactsAgenti)
            contactCounter += len(contacts0)
        configID.extend([i]*contactCounter)
        cicleID.extend([cicle]*contactCounter)
    # build the dataframe:
    dfconfigs = pd.DataFrame({'configID':configID, 'cicleID':cicleID, 'contacts0':contacts0, 'contacts1':contacts1})
    if toFile:
        call(f'mkdir -p {configs_path}contacts/', shell=True)
        dfconfigs.to_csv(f'{configs_path}contacts/{filename[:-4]}_loops_{loops}_ir_{interac_r}_contacts.csv', index=False)
    return dfconfigs, Nbots
    
# FER SERVIR AIXO? https://stackoverflow.com/questions/61840607/calculate-distance-between-various-points-of-a-dataframe-with-python-in-a-two-d
# segueix sent mes rapid l'original, pel que sembla
def getContactsFromTrajOPT2(filename, interac_r, loops, toFile=True):
    ticksPerCicle = loops*ticksPerLoop
    trajDF = pd.read_csv(configs_path+filename)
    # get a contact list from each configuration:
    ids = pd.unique(trajDF['ID'])
    Nbots = len(ids)
    Nconfigs = len(trajDF)/Nbots
    # is there any tick with more than 1 config?
    count = Counter(list(trajDF.loc[trajDF['ID']==0]['ticks']))
    ticks_plus1_configs = []
    for k,v in count.items():
        if v>1:
            ticks_plus1_configs.append(k)
    if(ticks_plus1_configs):
        print(f"There are {len(ticks_plus1_configs)} ticks with more than 1 config, from Nconfigs.")
    # search for contacts in each configuration and build the columns of a future dataframe:
    configID, cicleID, contacts0, contacts1 = [], [], [], []
    cicle = 0
    for i in tqdm(range(int(Nconfigs))):
        dfconfig = trajDF.loc[(i*Nbots):(i*Nbots+Nbots-1)]
        dfconfig.reset_index(drop=True, inplace=True)
        if int(dfconfig['ticks'][0]) > (cicle+1)*ticksPerCicle:
            cicle += 1
        for j,id0 in enumerate(ids[:-1]):
            contactsAgent0 = []
            pos0 = (dfconfig['x_position'][id0], dfconfig['y_position'][id0])
            distances = np.sqrt(((pos0[0] - dfconfig.x_position)**2 + (pos0[1] - dfconfig.y_position)**2))
            distances = distances[j+1:]
            contactsAgent0.extend([k+1+j for k,d in enumerate(distances) if d < interac_r])
            if contactsAgent0:
                configID.extend([i]*len(contactsAgent0)), cicleID.extend([cicle]*len(contactsAgent0))
                contacts0.extend([id0]*len(contactsAgent0)), contacts1.extend(contactsAgent0)
    # build the dataframe:
    dfconfigs = pd.DataFrame({'configID':configID, 'cicleID':cicleID, 'contacts0':contacts0, 'contacts1':contacts1})
    if toFile:
        call(f'mkdir -p {configs_path}contacts/', shell=True)
        dfconfigs.to_csv(f'{configs_path}contacts/{filename[:-4]}_loops_{loops}_ir_{interac_r}_contacts.csv', index=False)
    return dfconfigs, Nbots

