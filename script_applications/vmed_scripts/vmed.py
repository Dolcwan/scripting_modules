import subprocess               
import re                       
                                
import strlist as strl
import ioparse as iop 
import mathops as mops
import pinax   as px  
import cmdline as cl
import tcheck as __check__

'''
    --------
    | vmed |
    --------

    Note: 'vmed.py' must be added to the pmod package for 
          vmed scripts to function. 'vmed.py' is not a 
          standard pmod module

    Usage: Aids in scripting nuclear matter potential and EoS 
           programs given by the following fortran functions:

               Nuclear potential: 

                   effn3lo3nf.f 
                   cpot.f 
                     
               Nuclear Matter EoS:

                   n2lo450new.f                
                   n2lo500new.f 
                   n3lo450new.f                
                   n3lo500new.f 
                   n4lo450new.f                
                   n4lo500new.f 
                   matter.f 
                   nnsum_2015.f
               

    A list of relevent functions and constants to optimize working with 
    the effective 3NF nuclear potential pipeline. Optimized for working 
    at the third order of the chiral expansion.

    list of functions:

        jsl_entry : creates a tuple corrosponding to an internally formatted jsl entry

        grab_jsl : allows array of texts to be searched for jsl patterns,
                   corrosponding to an input potential matrix in jsl form.

        get_contribs : gets vmed contribs from a 'contribs.txt' file 
        
        v_lines : returns a list of individual vmed contributions

        v_group : returns a list of vmed contributions grouped by v number 

        gen_table_12_13 :   

    available constants:

        pi   : standard pi [12-digits]
        hc   : nuclear conversion constant [6-digits] 
        vmhc : nuclear potential conversion from (MeV^-2) to (fm) 
        mnuc : standard nucleon mass energy (MeV) [6-digits]
        mneu : neutron mass energy (MeV) [10-digits]
        mprt : proton mass energy (MeV) [13-digits]
        melc : electron mass energy (MeV) [9-digits]
        mmun : muon mass energy (MeV) [12 -digits]           

        Five lists are also available corrosponding to common density-momenta convensions:

        kf_vals_20 : simply a list starting at 0.1 and incrementing by 0.1 : [0.1, 0.2, 0.3 ... 1.9, 2.0]
        qf_vals_20 : kf_vals_20 in MeV instead of fm^{-1}
        pf_vals_20 : integer roundings of qf_vals_20, required for vmed parsing of jsl codes  

        sm_vals_20 : symmetric matter densities (MeV/fm^{3}) corrosponding to fermi momenta in kf_vals_20  
        nm_vals_20 : neutron matter densities (MeV/fm^{3}) corrosponding to fermi momenta in kf_vals_20      
'''


match = '(-?\d\.\d*D.\d{2})'
v_line = re.compile(match)

def jsl_entry(j,p1,p2,t):
    '''
    jsl_entry
     
    j => {0, 1, 2, 3}
    p1, p2 - A python numeric or string corrosponding to a numeric 
    t => {'singlet', triplet', 'V++', 'V--', 'V+-', 'V-+'}
    '''

    entry = (str(j),'('+str(p1)+','+str(p2)+')',str(t))
    return entry


def grab_jsl(file_text, list_jsl_match, round_form, round_length=None):
    
    def __parse_tfile__(file_text):

        j_codes = [0,1,2,3]
        for i in file_text:
            split = i.split()
            try:
                test = int(float([j for j in split if j][0]))
            except:
                test = -1
            if(test in j_codes):
                j = int(float(split[0].replace('D','E')))
                x = int(float(split[1].replace('D','E')))
                y = int(float(split[2].replace('D','E')))
                xy_val = str('('+str(x)+','+str(y)+')')
                j_val  = str(j)
            else:
                temp=v_line.findall(i)
                temp=[k.replace('D','E') for k in temp]
                for k in range(len(temp)):
                    jsl_val = jsl_codes[k]
                    jsl_inst = (j_val,xy_val,jsl_val)
                    yield jsl_inst, float(temp[k])    
        

    jsl_codes = {0:'singlet',1:'triplet',2:'V++',3:'V--',4:'V+-',5:'V-+'}
      
    Total_Out_List = []
    nos_jsl = []    
    finalvals = []
    
    for i in list_jsl_match:
        for j,k in __parse_tfile__(file_text):
#            print str(i)+" --- "+str(j)    # Debug printing
            if(i == j):
                finalvals.append(k)
     
    for i in range(len(finalvals)):
        if(round_form == 1):
            if(round_length == None or round_length < 7):
                sticky = mops.round_scientific(float(finalvals[i]),9,'26')
            else:
                sticky = mops.round_scientific(float(finalvals[i]),round_length,'26')
        else:
            sticky = finalvals[i]
        finalvals[i] = sticky
     
    return finalvals


def get_contribs():

    cmv = cl.path_parse('linux')
    
    # Get path of file storing the contribs
    success, file_path_list = cmv.cmd("dir contribs.txt")

    if(success == False):
        print("[vmed][get_contribs] Error: could not find 'contribs.txt'")
        return False

    file_path_list = file_path_list[0]

    lines_list = iop.flat_file_grab(file_path_list, [], scrub = True)
    return lines_list


def ventry(dictval, vlist):
    fkey = ['number','values']
    vkey = ['force','v','factor','zero','pion','tensor','prop']     
    vval = strl.str_to_list(vlist[0], filtre=True)
                     
    funs = vlist[1:] 
    funlist = []       
    for i in funs:
        funlist.append(strl.str_to_list(i,filtre=True)[-1])
   
    nfuns = len(funs)
    fval = [nfuns, funlist]

    vdict = dict(zip(vkey,vval))
    fdict = dict(zip(fkey,fval))

    if(dictval in vkey):
        return vdict[dictval]  
    elif(dictval in fkey):
        return fdict[dictval]
    elif(dictval == 'entry'):
        return vlist[0]
    elif(dictval == 'funs'):
        return vlist[1:]
    else:
        print("[vmed][ventry] Error: "+str(dictval)+" is not a valid entry")
        return False
      
      


def v_lines():

    vnline = '\D+\s+v\d+\s+-*\d.\s+0.0\s+138.04\s+[0-1]+.\s+-*[0-1]+.'
    vnlinec = re.compile(vnline)

    lines = get_contribs()
    if(lines == False):
        return False
    
    vinst = []
    vlineslist = []
    n = len(lines)
    i = 0
    group = False 
    
    while(i<n):    
        if(len(vnlinec.findall(lines[i])) != 0):
            group = True
            if(len(vinst) > 0):
                vlineslist.append(vinst)
                vinst = []
            vinst.append(vnlinec.findall(lines[i])[0])        
        if(len(vnlinec.findall(lines[i])) == 0):               
            group = False
            vinst.append(lines[i])
        i+=1
        if(i==n):
            vlineslist.append(vinst)    
    
    if(len(vlineslist) <= 0):
        print("[vmed][v_lines] Warning: no V lines could be parsed from 'contribs.txt'")  
    return vlineslist




def v_group():

    # Get contrib lines 

    lines_list = get_contribs()
    if(lines_list == False):
        return False
    
    # Pair up V line with fun. line 
    main = strl.array_nth_index(lines_list, 2)
    comp = strl.array_nth_index(lines_list, 2, True)
    paired = map(lambda x,y: [x,y], main,comp)
        
    ### Group V contribs by number
    ngroup = []
    lngroup = []
    numgroup = []
    setn = -1
    for i in paired:
        get = i[0]
        vn = strl.str_to_list(get,filtre=True)[1]
        num = int(vn[1:])
        if(setn == num):
            lngroup.append(i)
        else:
            numgroup.append(num)
            ngroup.append(lngroup)
            lngroup = []
            lngroup.append(i)
            setn = num        
    ngroup.append(lngroup)
    ngroup = filter(None,ngroup)
    
    for i in range(len(ngroup)):
        ngroup[i] = strl.array_flatten(ngroup[i],safety=False)    

    return numgroup, ngroup


def gen_table_12_13(lines):

    list_12, list_13 = [], []

    lines = strl.array_filter_spaces(lines)
     
    for i in xrange(len(pf_vals_20)):
        try:
            s_vals = grab_jsl(lines, s_jsl(pf_vals_20[i]), round_form = 1)
            p_vals = grab_jsl(lines, p_jsl(pf_vals_20[i]), round_form = 1)
        except: 
            print("[gen_fig_12_13] Error: an error occured while trying to parse jsl values form 'lines' input")
            return False
        if(s_vals != []):
            list_12.append(s_vals)
        if(p_vals != []):
            list_13.append(p_vals)
    
         
    val_table_12 = px.table_trans(list_12)
    val_table_13 = px.table_trans(list_13)
    if(val_table_12 == False or val_table_13 == False):
        print("[gen_fig_12_13] Error: an error occured while trying to transpose jsl tables")
        return False
         
    for i in range(len(val_table_12)):
        val_table_12[i] = [float(j)*vmhc for j in val_table_12[i]]
    for i in range(len(val_table_13)):
        val_table_13[i] = [float(j)*vmhc for j in val_table_13[i]]
    
    val_table_12.insert(0,kf_vals_20)
    val_table_12 = px.table_trans(val_table_12)
    if(val_table_12 == False):
        print("[gen_fig_12_13] Error: an error occured while trying to transpose table 12 after adding kfs")
        return False
    
    val_table_13.insert(0,kf_vals_20)
    val_table_13 = px.table_trans(val_table_13)
    if(val_table_13 == False):
        print("[gen_fig_12_13] Error: an error occured while trying to transpose table 13 after adding kfs")
        return False
    
    for i in range(len(val_table_12)):
        try:
            val_table_12[i] = strl.array_to_str(val_table_12[i], spc = '  ')
        except:
            print("[gen_fig_12_13] Error: entries in table 12 could not be converted to strings")
    for i in range(len(val_table_13)):
        try:
            val_table_13[i] = strl.array_to_str(val_table_13[i], spc = '  ')
        except:
            print("[gen_fig_12_13] Error: entries in table 13 could not be converted to strings")

    return val_table_12, val_table_13

#################################
#   functions for vmed_format   #
#################################

# heading function for vmed_format

def head_construct(self, eflt, latex, nfile):
    
    head_match = '\d\d*'
    head_compile = re.compile(head_match)
    eflt.sort(key = lambda y: int(head_compile.findall(y)[0]))
    sp_7 = '       '
    sp_6 = '      '
    sp_5 = '     '
    sp_4 = '    '
    
    try: 
        if(latex == 1):
            head = 'j & (x,y) & State & '
        else:
            head = 'j    q1  q2    State    '

        count = 0
        for i in eflt:
            head_num = head_compile.findall(i)

            if(latex == 1):  
                if(count<nfile-1):
                    head = head+'Eq.'+str(head_num[0])+' & '
                else:
                    head = head+'Eq.'+str(head_num[0])+'\\\\'
                count += 1
            else:
                if(count<nfile-1):
                    if(int(head_num[0]) < 10):
                        head = head+'Eq.'+str(head_num[0])+sp_7
                    elif(int(head_num[0]) < 100):
                        head = head+'Eq.'+str(head_num[0])+sp_6
                    elif(int(head_num[0]) < 1000):
                        head = head+'Eq.'+str(head_num[0])+sp_5
                    else:
                        head = head+'Eq.'+str(head_num[0])+sp_4
                else:
                    head = head+'Eq.'+str(head_num[0])
                count += 1   
    except:
        head = ''

    return head



# Captures the s (first 4) and p (last 4) waves corrosponding to the ones in the reference paper [*}

def sp_jsl(p): 

    jsl_out = [
        ('0','('+str(p)+','+str(p)+')','singlet'),
        ('1','('+str(p)+','+str(p)+')','V--'),
        ('1','('+str(p)+','+str(p)+')','V++'),
        ('1','('+str(p)+','+str(p)+')','V-+'),
        ('1','('+str(p)+','+str(p)+')','singlet'),
        ('0','('+str(p)+','+str(p)+')','V++'),
        ('1','('+str(p)+','+str(p)+')','triplet'),
        ('2','('+str(p)+','+str(p)+')','V--')
    ]
     
    return jsl_out  


def s_jsl(p):

    jsl_out = [
        ('0','('+str(p)+','+str(p)+')','singlet'),
        ('1','('+str(p)+','+str(p)+')','V--'),
        ('1','('+str(p)+','+str(p)+')','V++'),
        ('1','('+str(p)+','+str(p)+')','V-+'),
    ]
     
    return jsl_out  

def p_jsl(p):

    jsl_out = [
        ('1','('+str(p)+','+str(p)+')','singlet'),
        ('0','('+str(p)+','+str(p)+')','V++'),
        ('1','('+str(p)+','+str(p)+')','triplet'),
        ('2','('+str(p)+','+str(p)+')','V--')
    ]
     
    return jsl_out  


################################
#   functions for nnsum_vmed   #
################################

def partial_eos(file_name = None, lines = None):

    ptline = '\de/a\(mev\)\s*-*\d*\.*\d*\s*-*\d*\.*\d*\s*'
    
    start = '\de/a\(mev\)'
    space = '\s*'
    digit = '-*\d*\.*\d*'
    cgl   = space+digit
    
    line = start+7*cgl
    v_line = re.compile(line)
  
    fail = False

    if(isinstance(file_name,str)):      
        try:
            lines = iop.flat_file_grab(file_name)
        except:
            fail = True 
            print("[partial_eos] Error: could not open file: "+file_name)
    elif(__check__.array_test(lines)):
        for i in range(len(lines)):
            if(not isinstance(lines[i],str)):
                fail = True 
                print("[partial_eos] Error: line number "+str(i)+" is not a string")
    else:
        fail = True 

    if(fail):
        try:
            lines = iop.flat_file_grab('test1.txt')
        except:
            print("[partial_eos] Error: could not parse input or input files") 
            return False
                       
         
    match_lines = []
    for i in lines:
        bg = v_line.findall(i)
        if(len(bg) != 0 ):
            match_lines.append(bg[0])
    
    return match_lines



# Constants
     
pi = 3.141592653589793 # pi - 16 digits 
hc = 197.327           # hc - Standard Nuclear Conversion Constant
pi2 = pi*pi            # pi squared
                       
mnuc = 938.918         # Nucleon Mass-Energy 
mneu = 939.5656328     # Neutron Mass-Energy   
mprt = 938.2720881629  # Proton Mass-Energy  
melc = 0.51099895      # Electron Mass-Energy 
mmun = 105.658375523   # Muon Mass-Energy    
                       
vmhc = pi*hc*mnuc/2.0  # (pi/2) hc [MeV^-2] -> fm Conversion Constant      

kf_vals_20 = [i*0.1 for i in xrange(1,21)]  
qf_vals_20 = [hc*float(i) for i in kf_vals_20]
pf_vals_20 = [int(i) for i in qf_vals_20]

sm_vals_20 = [2.0*i*i*i/(3.0*pi2) for i in kf_vals_20]    
nm_vals_20 = [i*i*i/(3.0*pi2) for i in kf_vals_20]   