logger = setupData["logger"]

import threading 
import os
import json

tlsState = threading.local()

def batch_synth_line_pre(data=None):
    global logger
    global tlsState
    global os
    global json

    path = os.path

    synthLineMidData = []
    synthLinePreEnergyData = []

    linesBatch = data["linesBatch"]

    for request in linesBatch:
        synthLineMidEntry = None
        synthLinePreEnergyEntry = None

        try:
            # sequence = request[0]
            # pitch = request[1]
            # duration = request[2]
            # pace = request[3]
            # tempFileLocation = request[4]
            outPath = request[5]
            # outFolder = request[6]

            (wavDirName,wavFileName) = path.split(outPath)
            baseFileName = path.splitext(path.basename(wavFileName))[0]
            
            possibleOverrideFilePaths = [path.join(wavDirName,"override",baseFileName + ".json"),path.join(wavDirName,"override",baseFileName + ".wav.json")]
            overrideFilePath = None
            for possibleOverrideFilePath in possibleOverrideFilePaths:
                if path.exists(possibleOverrideFilePath):
                    overrideFilePath = possibleOverrideFilePath
                    break

            if overrideFilePath is not None:

                with open(overrideFilePath) as f:
                    overrideData = json.load(f)
                pitches = overrideData["pitchNew"]
                durations = overrideData["dursNew"]
                energies = overrideData["energyNew"]

                synthLineMidEntry = (pitches,durations)
                synthLinePreEnergyEntry = energies
        except Exception as e:
            logger.log(traceback.format_exc())
            
        synthLineMidData.append(synthLineMidEntry)
        synthLinePreEnergyData.append(synthLinePreEnergyEntry)

    tlsState.synthLineMidData = synthLineMidData
    tlsState.synthLinePreEnergyData = synthLinePreEnergyData



def synth_line_mid(data=None):
    global logger
    global tlsState

    synthLineMidData = None
    try:
        synthLineMidData = tlsState.synthLineMidData
    except AttributeError:
        None

    if synthLineMidData is None:
        return
        
    for i, entry in enumerate(synthLineMidData):
        if entry is None:
            continue

        (newPitch,newDuration) = entry

        oldDuration = data["duration"][i]
        oldPitch = data["pitch"][i]

        if len(oldDuration) != len(newDuration):
            logger.log("Override file has not the expected number of duration entries. Expected " + str(len(oldDuration)) + ", got " + str(len(newDuration)))
            return                

        if len(oldPitch) != len(newPitch):
            logger.log("Override file has not the expected number of pitch entries. Expected " + str(len(oldPitch)) + ", got " + str(len(newPitch)))
            return                


        data["duration"][i] = newDuration
        data["pitch"][i] = newPitch
        

def synth_line_pre_energy(data=None):
    global logger
    global tlsState

    synthLinePreEnergyData = None
    try:
        synthLinePreEnergyData = tlsState.synthLinePreEnergyData
    except AttributeError:
        None

    if synthLinePreEnergyData is None:
        return
        
    for i, entry in enumerate(synthLinePreEnergyData):
        if entry is None:
            continue

        newEnergy = entry

        oldEnergy = data["energy"][i]

        if len(oldEnergy) != len(newEnergy):
            logger.log("Override file has not the expected number of energy entries. Expected " + str(len(oldEnergy)) + ", got " + str(len(newEnergy)))
            return                


        data["energy"][i] = newEnergy

            
def batch_synth_line_post(data=None):
    global logger
    global tlsState

    tlsState.synthLineMidData = None
    tlsState.synthLinePreEnergyData = None

    
