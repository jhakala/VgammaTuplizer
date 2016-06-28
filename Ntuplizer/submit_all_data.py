#!/usr/bin/env python
"""
This is a small script that submits a config over many datasets
"""
import os
from optparse import OptionParser

def getOptions() :
    """
    Parse and return the arguments provided by the user.
    """
    usage = ('usage: python submit_all.py -c CONFIG -d DIR ')

    parser = OptionParser(usage=usage)    
    parser.add_option("-c", "--config", dest="config",
        help=("The crab script you want to submit "),
        metavar="CONFIG")
    parser.add_option("-d", "--dir", dest="dir",
        help=("The crab directory you want to use "),
        metavar="DIR")
    parser.add_option("-f", "--datasets", dest="datasets",
        help=("File listing datasets to run over"),
        metavar="FILE")
    (options, args) = parser.parse_args()


    if options.config == None or options.dir == None:
        parser.error(usage)
    
    return options
    

def main():

    options = getOptions()

    #from WMCore.Configuration import Configuration
    from CRABClient.UserUtilities import config
    config = config()

    from CRABAPI.RawCommand import crabCommand
    from httplib import HTTPException

    # We want to put all the CRAB project directories from the tasks we submit here into one common directory.
    # That's why we need to set this parameter (here or above in the configuration file, it does not matter, we will not overwrite it).
    config.section_("General")
    config.General.workArea = options.dir
    config.General.transferLogs = True

    config.section_("JobType")
    config.JobType.pluginName = 'Analysis'
    config.JobType.psetName = options.config
    config.JobType.allowUndistributedCMSSW = True
   # config.JobType.pyCfgParams = ['DataProcessing=MC25ns_MiniAODv2','lheLabel=externalLHEProducer']
    config.JobType.inputFiles = [
        './JSON/Cert_271036-274421_13TeV_PromptReco_Collisions16_JSON.txt',
        './JEC/Spring16_25nsV3_DATA_Uncertainty_AK8PFchs.txt',
        './JEC/Spring16_25nsV3_DATA_Uncertainty_AK4PFchs.txt',
        './JEC/Spring16_25nsV3_DATA_L1FastJet_AK8PFchs.txt', 
        './JEC/Spring16_25nsV3_DATA_L2Relative_AK8PFchs.txt',
        './JEC/Spring16_25nsV3_DATA_L3Absolute_AK8PFchs.txt',
        './JEC/Spring16_25nsV3_DATA_L2L3Residual_AK8PFchs.txt',
        './JEC/Spring16_25nsV3_DATA_L2Relative_AK8PFPuppi.txt',
        './JEC/Spring16_25nsV3_DATA_L3Absolute_AK8PFPuppi.txt',
        './JEC/Spring16_25nsV3_DATA_L2L3Residual_AK8PFPuppi.txt',
        './JEC/Spring16_25nsV3_DATA_L1FastJet_AK4PFchs.txt',
        './JEC/Spring16_25nsV3_DATA_L2Relative_AK4PFchs.txt',
        './JEC/Spring16_25nsV3_DATA_L3Absolute_AK4PFchs.txt',
        './JEC/Spring16_25nsV3_DATA_L2L3Residual_AK4PFchs.txt',
        

]


    config.section_("Data")
    config.Data.inputDataset = None
    # config.Data.inputDBS = 'phys03' #to be commented in case of global#
    config.Data.splitting = 'LumiBased'#'LumiBased'#
    config.Data.unitsPerJob = 100
    config.Data.ignoreLocality = False
    config.Data.publication = False    
    config.Data.outLFNDirBase = '/store/user/cgalloni/Ntuple_80_270516'
    config.Data.lumiMask      = '/mnt/t3nfs01/data01/shome/cgalloni/RunII/CMSSW_8_0_7/src/EXOVVNtuplizerRunII/Ntuplizer/JSON/Cert_271036-274421_13TeV_PromptReco_Collisions16_JSON.txt'
    config.section_("Site")
    config.Site.storageSite = 'T3_CH_PSI'


    print 'Using config ' + options.config
    print 'Writing to directory ' + options.dir

    
    def submit(config):
        try:
            crabCommand('submit', config = config)
        except HTTPException, hte:
            print 'Cannot execute command'
            print hte.headers

    #############################################################################################
    ## From now on that's what users should modify: this is the a-la-CRAB2 configuration part. ##
    #############################################################################################

    datasetsFile = open( options.datasets )
    jobsLines = datasetsFile.readlines()
    jobs = []
    for ijob in jobsLines :
        s = ijob.rstrip()
        jobs.append( s )
        print '  --> added ' + s

        
    for ijob, job in enumerate(jobs) :

        ptbin = job.split('/')[1]
        cond = job.split('/')[2]
        
        config.General.requestName = ptbin +'_'+ cond +'_MCjec'
        config.Data.inputDataset = job
        config.Data.outputDatasetTag =  ptbin +'_'+ cond +'_MCjec'
        print "ptbin :%s and cond: %s " %(ptbin, cond)
        print 'Submitting ' + config.General.requestName + ', dataset = ' + job
        print 'Configuration :'
        print config
    
        try :
            from multiprocessing import Process
            p = Process(target=submit, args=(config,))
            p.start()
            p.join()
           # submit(config)
        except :
            print 'Not submitted.'
        





if __name__ == '__main__':
    main()            