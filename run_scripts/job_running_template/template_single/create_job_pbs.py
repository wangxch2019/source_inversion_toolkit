#!/usr/bin/env python

import os
import glob
import math
import re

nevents_per_job = 3
nnodes_per_job = 3840 * nevents_per_job
walltime = "1:00:00" 
eventlist_file = "./XEVENTID"
job_template = "job_solver_bundle.bash"


def read_txt_to_list(filename):
    with open(filename, 'r') as f:
        content = f.readlines()
        return [ line.rstrip('\n') for line in content ] 


def write_list_to_txt(vlist, filename):
    with open(filename, 'w') as f:
        for value in vlist:
            f.write("%s\n" % value)


def modify_job_sbatch_file(inputfile, outputfile, eventfile, start_idx):
    fi = open(inputfile, "r")
    fo = open(outputfile, "w")

    content = fi.readlines()

    for line in content:
        line = re.sub(r"^#PBS -l nodes=.*", "#PBS -l nodes=%d" % nnodes_per_job, line)
        line = re.sub(r"^#PBS -l walltime=.*", "#PBS -l walltime=%s" % walltime, line)
        line = re.sub(r"^eventfile=.*", "eventfile=\"%s\"" % eventfile, line)
        line = re.sub(r"^event_index=.*", "event_index=%d" % (start_idx+1), line)

        # turn of waiting mode
        #line = re.sub(r"./bin/xspecfem3D .*", "./bin/xspecfem3D &", line)
        line = re.sub(r"^#wait", "wait", line)

        fo.write(line) 


if __name__ == "__main__":

    sub_eventfile_prefix = "XEVENTID_"
    sub_sbatch_prefix = "job_solver_bundle.pbs."

    # remove old files 
    filelist = glob.glob(sub_eventfile_prefix+"*")
    for fn in filelist:
        os.remove(fn)
    filelist = glob.glob(sub_sbatch_prefix+"*")
    for fn in filelist:
        os.remove(fn)

    eventlist = read_txt_to_list(eventlist_file)
    nevents = len(eventlist)
    njobs = int(math.ceil( float(nevents) / nevents_per_job))
    print "Number of events:", nevents 
    print "Number of jobs:", njobs

    for ijob in range(njobs):

        # create sub-eventlist file
        start_idx = ijob * nevents_per_job 
        end_idx = (ijob + 1) * nevents_per_job
        if ijob == njobs-1:
            end_idx = nevents

        eventfile = "%s%d" %(sub_eventfile_prefix, ijob+1)
        write_list_to_txt(eventlist[start_idx:end_idx], eventfile)

        # create job pbs script
        outputfn = "%s%d" %(sub_sbatch_prefix, ijob+1)
        modify_job_sbatch_file(job_template, outputfn, eventfile, start_idx)

