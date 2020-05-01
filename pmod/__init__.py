import cmdline as cl
#import phelp as ph
import ioparse as iop 
import mathops as mops 
import pinax   as pnx 
import strlist as strl
import tcheck  as check 
import zkparse as zkp

'''

Welcome to the PMOD package, use the 'pmod_help' function for more info on each of the modules 

Class list:
 
    module  | class
    _______ | ___________  
    cmdline | PathParse
    mathops | spline
    zkparse | clock

'''

def pmod_help(string = '', printOption = True):

    __module_list__ = ['help',
                       'cmdline',
                       'ioparse',
                       'mathops',
                       'phelp',
                       'pinax',
                       'strlist',
                       'tcheck',
                       'zkparse']

    __doc_list__ = ["'help' returns a list of the modules in the pmod package. ",

                    "'cmdline' contains the 'PathParse' class which enables shell command line "+
                    "values to be passed to the '.cmd()' function, resulting in pathway and file "+
                    "management functionality, a host of stand-alone functions provided within the "+
                    "PathParse class provide additional pathway parsing and management utilities.",

                    "Contains functions for file input/output, options include reading, "+
                    "writing, appending and modifying the content of text files.",

                    "Contains functions for rounding numerical values as well as the "+
                    "'spline' class for performing spline and calculus operations on 1D functions",

                    "'phelp' contains functions for easy plotting usage of matplotlib",

                    "'pinax' class contains functions for tabulating data",

                    "'strlist' contains miscellaneous functions for parsing"+
                    "strings and arrays(lists and tuples)",

                    "'tcheck' contains functions for 'TypeError' testing and printing",

                    "'zkparse' contains functions for time and calandar functionality, also "+
                    "contains the 'clock' class which improves time and date dependent automation"  

                   ]

    __module_doc_list__ = dict(zip(__module_list__,__doc_list__))

    if(string in __module_list__):
        out_string = __module_doc_list__[string]
    else:
        out_string = "Input string not recognized, input the name of a module in pmod for additional info"
       
    if(printOption):
        print(" ")
        print(out_string+"\n")
        
    return out_string


# Universal Info
__version__ = '1.6'
__author__  = 'Randy Millerson'


