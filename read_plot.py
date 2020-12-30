import os
import glob
import matplotlib.cm as cm
import matplotlib.colors as col
import matplotlib.pyplot as plt
import nanonispy as nap
import pandas as pd
import numpy as np
import matplotlib 
matplotlib.use('Qt5Agg')
import addcopyfighandler


filepath = input("Please input the data path:  ").replace( "\"", "")   # replace is important to filename decode

# ------Initial setting------
divider = 100
multi_line_distance_ratio = 0.01 # for folder and lin-cut multi-line plot distance setting
draw_origin = 'upper'    #select draw origin:'lower' or 'upper'
data_channel = "LI Demod 2 X (A)" # Current (A);LI Demod 1 X (A);LI Demod 1 Y (A);LI Demod 2 X (A);LI Demod 2 Y (A)
mapping_Bias_select = 0


#-------WSXM colorbar setting-----   
diy_cmap = plt.cm.bwr


def plot_scan_image():  # plot_setting for mapping image
    global scan_size_x,scan_size_y
    plt.xlabel('');plt.xticks([])
    plt.ylabel('');plt.yticks([])
    #clb = plt.colorbar(show_image, shrink=.8);clb.set_ticks([])
    scan_size_x = scan_size[0]*np.power(10, 9)
    scan_size_y = scan_size[1]*np.power(10, 9)
    date_sxm = raw_data.header['rec_date']+'/'+filepath.split("\\")[-1].rstrip('.sxm').split('_')[-1]+')'
    plt.xlabel('%.2f'%scan_size_x + 'nm × ' + '%.2f'%scan_size_y + 'nm  ('+date_sxm)
    
def plot_mapping_image():  # plot_setting for scan image
    global scan_size_x,scan_size_y
    plt.xlabel('');plt.xticks([])
    plt.ylabel('');plt.yticks([])
    scan_size_x = scan_size[0]*np.power(10, 9)
    scan_size_y = scan_size[1]*np.power(10, 9)
    date_3ds = raw_data.header['start_time'].split(" ")[0]+'/'+filepath.split("\\")[-1].rstrip('.3ds').split('_')[-1]
    plt.xlabel('%.2f'%scan_size_x + 'nm × ' + '%.2f'%scan_size_y + 'nm ('+('%.2f meV) ' % scan_Bias)+date_3ds)

def plot_waterfall():
    global fig_line, ax_line1, ax_line2
    # plot the muti-lines
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['font.family'] = 'Arial'
    fig_line = plt.figure('waterfall')
    ax_line1 = fig_line.add_subplot(1, 2, 1,)
    ax_line1.set_yticks([])
    ax_line1.set_xlabel("Energy (meV)")
    ax_line1.set_ylabel("dI/dV (a.u.)")
    box = ax_line1.get_position()
    ax_line1.set_position([box.x0, box.y0, box.width*0.8, box.height])
    # ax_line2 for line profile image
    plt.rcParams['xtick.direction'] = 'in'  # set before plot show
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['font.family'] = 'Arial'
    ax_line2 = fig_line.add_subplot(1, 2, 2,)
    ax_line2.set_xlabel("Energy (meV)")
    ax_line2.set_ylabel("Distance (nm)")
    # set picture title
    ax_line1.set_title("Date : %s"%date)
    ax_line2.set_title("Path : %s"%name)
    #cursor = Cursor(ax_line2, useblit=True, color='red', linewidth=1,horizOn=True, vertOn=True)

def plot_Spec():
    global ax_spec, STS_color
    fig_spec = plt.figure('STS')
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['font.family'] = 'Arial'
    ax_spec = fig_spec.add_subplot(111)
    ax_spec.set_yticks([])
    ax_spec.set_xlabel("Energy (meV)")
    ax_spec.set_ylabel("dI/dV (a.u.)")
    STS_color = 'b'  # just for single STS plot instead of multi .dat in a folder

# ------line profile setting------
def plot_waterfall_image():
    # width + hight in Grid
    line_distance = (raw_data.header['size_xy'][0])*np.power(10, 9) 
    extent_induced_ratio = (line_distance-0)/(Bias[-1]-Bias[0])
    if (Bias[-1]-Bias[0]) > 0:
        extent_xy = [Bias[0], Bias[-1], 0, line_distance]
        line_mapping = ax_line2.imshow(data[0,:,:], cmap=plt.cm.bwr, interpolation='none', extent=extent_xy,origin='lower')
    else:
        extent_xy = [Bias[-1], Bias[0], 0, line_distance]
        line_mapping = ax_line2.imshow(data[0,:,-1::-1], cmap=plt.cm.bwr, interpolation='none', extent=extent_xy,origin='lower')
    #clb = plt.colorbar(line_mapping, shrink=0.8);clb.set_ticks([])
    #------set line mapping aspect ratio to 2,ratio means single pixel------
    ax_line2.set_aspect(np.abs(2/extent_induced_ratio))
# ------read sigle data file------

def read_file(path):
    if os.path.splitext(path)[1] == '.3ds':
        global raw_data, Bias,data,name,date
        # read grid mapping as well as line spectroscopy data(.3ds)
        raw_data = nap.read.Grid(path)
        data = raw_data.signals[data_channel]
        Bias = raw_data.signals['sweep_signal']*1000/divider
        name = path.split("\\")[-1].rstrip('.3ds')
        date = raw_data.header['start_time'].split(" ")[0]
        # judge the type of file is whether waterfall or not
        if (raw_data.header['dim_px'][0]==1) or (raw_data.header['dim_px'][1]==1):
            distance = np.abs(np.mean(data))
            print(distance)
            count_3ds = 0
            plot_waterfall()  # plot line profile mapping
            for i in range(data.shape[1]):     # cycle single STS in different position
                #data[0,i,:] = data[0,i,:]/np.mean(data[0,i,:]) #normalize 
                data_single_line = data[0,i,:] + count_3ds*multi_line_distance_ratio*distance
                ax_line1.plot(Bias, data_single_line, label=count_3ds,lw=1,
                              color=plt.cm.rainbow(np.linspace(0, 1, data.shape[1])[count_3ds]))
                count_3ds += 1
            plot_waterfall_image()
        else:
        #------print the fixed and experimental parameters------
            for p in range(raw_data.signals['params'].shape[2]):
                if p < len(raw_data.header['fixed_parameters']):
                    print('%s :  '%(raw_data.header['fixed_parameters'][p])+ '%s'%(raw_data.signals['params'][0,0,p]))
                else:
                    g = p-len(raw_data.header['fixed_parameters'])
                    print('%s :  '%(raw_data.header['experimental_parameters'][g]) + '%s'%(raw_data.signals['params'][0,0,p]))
        #------mapping data show------
            global scan_size,scan_Bias
            data_mapping = data[:, :, mapping_Bias_select]
            scan_size = raw_data.header['size_xy']
            scan_Bias = raw_data.signals['sweep_signal'][mapping_Bias_select]*1000/divider
            #------show topography------
            # plt.figure('topography')
            # topography = raw_data.signals['topo']
            # plt.imshow(topography,origin=draw_origin,cmap=diy_cmap,interpolation='none')
            # plt.xticks([]);plt.yticks([])
            #---------------------------
            mapping = plt.figure('Mapping Bias : %.2f meV' % scan_Bias)
            mapping_3ds= mapping.add_subplot(1,1,1,)
            show_image = mapping_3ds.imshow(data_mapping, aspect=1,cmap=plt.cm.bwr, interpolation='none',origin='lower')
            plot_mapping_image()
            mapping_3ds.set_aspect(np.abs((scan_size_y/scan_size_x)/(data_mapping.shape[0]/data_mapping.shape[1])))
    elif os.path.splitext(path)[1] == '.sxm':
        raw_data = nap.read.Scan(path)  # read scan data(.sxm)
        scan_size = raw_data.header['scan_range']
        data = raw_data.signals['Z']["forward"] # Z(m),Current;Coloum header: forward，backward.
        Data_Bias = np.float(raw_data.header['bias>bias (v)'])
        scan = plt.figure('Topography ---- Bias : %.2f meV' % Data_Bias)
        scan_sxm= scan.add_subplot(1,1,1,)
        show_image = scan_sxm.imshow(data, cmap=diy_cmap, interpolation='none',origin = draw_origin,)
        plot_scan_image()
        scan_sxm.set_aspect(np.abs(scan_size_y/scan_size_x))
    elif os.path.splitext(path)[1] == '.dat':
        raw_data = nap.read.Spec(path)  # read Spec data (.dat)
        data = raw_data.signals[data_channel]
        if "PointSpec" in path:
            Bias = raw_data.signals["Bias (V)"]*1000/divider
        else:
            Bias = raw_data.signals["Bias calc (V)"]*1000/divider
        plot_Spec()
        label = raw_data.header['Saved Date'].split(' ')[0]+'/'+path.split("\\")[-1].rstrip('.dat')
        ax_spec.plot(Bias, data, color=STS_color, lw=1,label=label)
        plt.legend(loc='best', frameon=False)
    else:
        print("The type of data is not handleable")

# ------read sigle data folder------
folder_img = []
def read_folder(path):  # to plot multi-line under different experimental environment
    postfix = '*.dat'
    filespath = glob.glob(os.path.join(filepath, postfix))
    #filespath = sorted(filespath,key=lambda x: os.path.getmtime(x))#sort files with record time
    plot_Spec()
    count_dat = 0
    for file in filespath[::]:
        print(file)
        #name = file.split("\\")[-1].rstrip('.dat')
        name = file.split("\\")[-1].rstrip('.dat').split('_')[-2]
        name = file.split("\\")[-1].rstrip('.dat')
        raw_data = nap.read.Spec(file)  # read Spec data (.dat)
        if "PointSpec" in file:
            Bias = raw_data.signals["Bias (V)"]*1000/divider
        else:
            Bias = raw_data.signals["Bias calc (V)"]*1000/divider #is spec extract from linecut
        data = raw_data.signals[data_channel]  # X1 channal data
        data = data/np.abs(np.min(data))# normalize
        folder_img.append(data)
        distance = np.abs(np.max(data))
        data_single_line = data + count_dat*multi_line_distance_ratio*distance
        ax_spec.plot(Bias, data_single_line, label=name,color=[plt.cm.rainbow(i) for i in np.linspace(0, 1, file_num)][count_dat])      
        count_dat += 1
        ax_spec.legend(loc='best', frameon=False, fontsize=7)
    ## show folder image------
    '''
    plt.figure('image from .dat folder')
    if (Bias[-1]-Bias[0]) > 0:
        plt.imshow(np.array(folder_img)[:,:],origin='lower',cmap='bwr',interpolation='none',
                   extent=[Bias[0], Bias[-1], 20, 300],
                   aspect=np.abs(2*(Bias[-1]-Bias[0])/(300-20)))
    else:
        plt.imshow(np.array(folder_img)[:,::-1],origin='lower',cmap='bwr',interpolation='none',
                   extent=[Bias[-1], Bias[0], 20, 300],
                   aspect=np.abs(2*(Bias[-1]-Bias[0])/(300-20)))
    plt.xlabel('Bias(meV)')
    '''
# ------output setting------
if os.path.isfile(filepath):
    read_file(filepath)
elif os.path.isdir(filepath):
    global file_num
    postfix = '*.dat'
    filespath = glob.glob(os.path.join(filepath, postfix))
    list_files = []
    file_num = len([list_files.append(file) for file in filespath])
    read_folder(filepath)
plt.tight_layout()
plt.show()


