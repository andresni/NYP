# -*- coding: utf-8 -*-

import numpy as np
import scipy.io as sp
import nest_interface as ni
import io_functions as iof
import nest
import auxillary_functions as af
import pandas
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from joblib import Parallel, delayed
import multiprocessing
from scipy import signal

def graphical_output(data,p):
    # Function for creating premade plots. Creates one plot of each type specified in simulation/ouputs.yml, for each recorder.
    # Input: sorted data, input parameters from YML files, path to experiment folder
    
    def make_state_lines(p,dat):
        # Function for creating seperator lines according the states specified in simulation/states.yml
        # Input: input parameters from YML files, sorted data
        # Ouput: line markers, line labels
        
        samples = np.size(dat,1)
        sum_time = np.sum([p["simulation"]["states"][i]["state_length"] for i in p["simulation"]["simulation_params"]["sim_sequence"]])
        res = 1/(samples/(int(sum_time)/1000))
        
        line_labels = np.array(p["simulation"]["simulation_params"]["sim_sequence"])
        lines = np.cumsum([p["simulation"]["states"][i]["state_length"] for i in p["simulation"]["simulation_params"]["sim_sequence"]])
        line_labels = [line_labels[i] for i in range(len(line_labels)) if lines[i] > 0]
        lines = [int(lines[i]/1000/res) for i in range(len(lines)) if lines[i] > 0]
        
        return lines, line_labels
        
    def raster(data,k):
        # Function for creating raster plots. Creates one subplot per recordable
        # Input: sorted data, index
        # Output: figure object
        
        nr_plots = len(data[k].keys())
        spos = 0
        
        fig, ax = plt.subplots(nr_plots,1,sharex=False,sharey=False)
        fig.set_size_inches(12,12)
        fig.suptitle("Rasterplot: "+k)
        
        for i in data[k].keys():
            if not i == "times":
                im=ax[spos].matshow(data[k][i],aspect="auto",cmap="gray",vmin=np.min(data[k][i]),vmax=np.max(data[k][i]))
                cb=plt.colorbar(mappable=im,ax=ax[spos],ticks=[np.min(data[k][i]),np.max(data[k][i])],aspect=10)
                cb.ax.set_title(i,size=8)
                lines, line_labels = make_state_lines(p,data[k][i])
                for x in range(len(lines)):
                    ax[spos].axvline(lines[x],color="k",linestyle="-") if not lines[x] >= np.size(data[k]["times"]) else None
                    ax[spos].axvline(lines[x],color="w",linestyle="--") if not lines[x] >= np.size(data[k]["times"]) else None
                ax[spos].axes.get_xaxis().set_ticks(np.arange(0,np.size(data[k]["times"])+np.size(data[k]["times"])/10,np.size(data[k]["times"])/10))
                ax[spos].set_xticklabels(np.arange(0,np.max(data[k]["times"])+np.max(data[k]["times"])/10,np.max(data[k]["times"])/10))
                ax[spos].tick_params(axis="x",bottom=True,top=False,labelbottom=True,labeltop=False)
                ax[spos].set_ylabel(i)
                spos = spos+1
        ax[spos-2].set_xlabel("Time (ms)")
        
        fig.delaxes(ax[-1])
        
        return fig
    
    def mean_current_lines(data,k):
        # Function for creating average current plots. Whatver timeseries coming here will be averaged. Creates one subplot per recordable
        # Input: sorted data, index
        # Output: figure object
        
        nr_plots = len(data[k].keys())
        spos = 0
        
        fig, ax = plt.subplots(nr_plots,1,sharex=False,sharey=False)
        fig.set_size_inches(12,12)
        fig.suptitle("Current plots: "+k)
        
        for i in data[k].keys():
            if not i == "times":
                im=ax[spos].plot(np.mean(data[k][i],0),'k')
                lines, line_labels = make_state_lines(p,data[k][i])
                for x in range(len(lines)):
                    ax[spos].axvline(lines[x],color="k",linestyle="-") if not lines[x] >= np.size(data[k]["times"]) else None
                    ax[spos].axvline(lines[x],color="w",linestyle="--") if not lines[x] >= np.size(data[k]["times"]) else None
                ax[spos].axes.get_xaxis().set_ticks(np.arange(0,np.size(data[k]["times"])+np.size(data[k]["times"])/10,np.size(data[k]["times"])/10))
                ax[spos].set_ylim([np.min(np.mean(data[k][i],0)),np.max(np.mean(data[k][i],0))])
                ax[spos].set_xticklabels(np.arange(0,np.max(data[k]["times"])+np.max(data[k]["times"])/10,np.max(data[k]["times"])/10))
                ax[spos].tick_params(axis="x",bottom=True,top=False,labelbottom=True,labeltop=False)
                ax[spos].set_ylabel(i)
                spos = spos+1
        ax[spos-2].set_xlabel("Time (ms)")
        
        fig.delaxes(ax[-1])
        
        return fig
    
    for mode in p["simulation"]["output"]["graphical"]:
        if mode == "raster":
            for k in data.keys():
                fig = raster(data,k)
                plt.savefig(p["paths"]["output_path"] + "/Rasters_{}.tif".format(k))
                plt.close(fig)
                
        if mode == "mean_currents":
            for k in data.keys():
                fig = mean_current_lines(data,k)
                plt.savefig(p["paths"]["output_path"] + "/Mean_clines_{}.tif".format(k))
                plt.close(fig)
    
    
def output_data(p,layers,recorders):
    # Functin for sorting data into 2D matrices with neurons at the Y axis, and time on the X axis
    # Input: parameters from YML files, a list of layers, a list of recorders, path to experiment folder
    # Output: sorted data
    
    t = p["simulation"]["output"]["data"]["save"]

    for rec in recorders:
        full_data ={}
        name = rec[1] + "_" + rec[2]
        print("")
        print("Loading data from {}".format(name))
        temp = nest.GetStatus([rec[0][0]])[0]["events"]
        data = {}
        
        if not temp["senders"].any():
            temp = iof.read_data(rec,p)  
            for k in range(len(rec[3])):
                data[rec[3][k]] = temp[k+2]
            temp = {"senders":temp[0],"times":temp[1]}
        else:
            for k in rec[3]:
                data[k] = temp[k]
                
        a,b = int(temp["senders"].min()), int(temp["senders"].max())
        full_data[name] = {"times":temp["times"][temp["senders"] == a]}
    
        for k in rec[3]:
            full_data[name][k] = [data[k][temp["senders"] == i] for i in range(a,b+1)]
        
        
        if ".mat" in t["formats"]:
            sp.savemat("{}/{}.mat".format(p["paths"]["output_path"],name),{"data":full_data})
            
        graphical_output(full_data,p)
    