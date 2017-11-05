#!/bin/env python
# -*- coding: iso-8859-1 -*-

__author__ = "Sebastien Bouche"
__copyright__ = "Copyright(c) 2017"
__version__   = "0.1"


"""Usage: pyocto.py [options] command(s)

Commands are
   setup            : setup a yocto project
"""

################################################################################
# Import of Standard Python Modules
################################################################################
import sys, os, re, glob, time, datetime, logging, ctypes
import os.path as osp

import ConfigParser
from optparse import OptionParser, OptionGroup
import warnings
try:
    # from git import Repo
    import git
    join = osp.join
except ImportError:
    print "try pip install gitpython"
    print "or download from: https://github.com/gitpython-developers/GitPython"
    exit()

try:
    from pushetta import Pushetta
    importpushetta = True
except ImportError:
    print "try pip install Pushetta"
    importpushetta = False

from UserDict import DictMixin

def logo(): 
    """ print the logo
    """
    print "                         _        "
    print "                        | |       "
    print "  _ __  _   _  ___   ___| |_ ___  "
    print " | '_ \| | | |/ _ \ / __| __/ _ \ "
    print " | |_) | |_| | (_) | (__| || (_) |"
    print " | .__/ \__, |\___/ \___|\__\___/ "
    print " | |     __/ |                    "
    print " |_|    |___/                     "
    print " "

#===============================================================================
# Struct
#===============================================================================
class Struct(DictMixin):
    def __init__(self, **entries): self.__dict__.update(entries)
    def __getitem__(self, k): return self.__dict__[k]
    def __setitem__(self, k, v): self.__dict__[k] = v
    def keys(self): return self.__dict__.keys()
    #def iteritems(self): return self.__dict__.__iter__()
    def copy(self): s = Struct(); s.__dict__.update(self.__dict__); return s
    def __repr__(self): return 'Struct(%s)' % ', '.join(["%s=%s" % (k, repr(v)) for (k, v) in vars(self).iteritems()])



#===============================================================================
# Class: Pyocto
#===============================================================================
class pyocto():


    _GlobalConfigDefault = Struct(
        project    = "",
        work       = "v_yocto",
    )

    _YoctoDefault = Struct(
        repo_yocto   = "",
        branch = "",
    )
    _XilinxDefault = Struct(
        repo_xilinx    = "",
        branch = "",
    )
    
    _ZynqberryDefault = Struct(
        repo_zynqberry    = "",
        branch = "",
    )
    
    _NotificationDefault = Struct(
        api_key      = "",
        channel_name = "",
    )
    
    def pyocto_loadconfig(self,inifile, globalconfig,yocto,xilinx,zynqberry,notification):
        """ 
        ## Function name: pyocto_loadconfig                             ##
        ## Inputs list  : inifile, config, yocto, xilinx, notification  ##
        ## Outputs list : config, yocto, xilinx, notification           ##
        ## Description  : * Load ini file and return project data       ##
        """
        globalconfig = globalconfig.copy()
        yocto = yocto.copy()
        xilinx = xilinx.copy()
        notification = notification.copy()
        # Read ini file
        if not os.path.exists(inifile): raise Exception("-E- Configuration settings file (%s) not found" % inifile)
        cp = ConfigParser.ConfigParser()
        cp.optionxform = str
        cp.read(inifile)
        for sec in cp.sections():
            if sec == "globalconfig":
                for opt in cp.options(sec):
                    globalconfig[opt] = cp.get(sec, opt).strip()
            elif sec == "yocto":
                for opt in cp.options(sec):
                    yocto[opt] = cp.get(sec, opt).strip()
            elif sec == "xilinx":
                for opt in cp.options(sec):
                    xilinx[opt] = cp.get(sec, opt).strip()
            elif sec == "zynqberry":
                for opt in cp.options(sec):
                    zynqberry[opt] = cp.get(sec, opt).strip()
            elif sec == "notification":
                for opt in cp.options(sec):
                    notification[opt] = cp.get(sec, opt).strip()
            else:
                raise SyntaxError("Unknown section %s in %s" % (sec, inifile))
        return globalconfig, yocto, xilinx, zynqberry, notification

    def pyocto_git_clone(self, type):
        """ 
        ## Function name: pyocto_git_clone                              ##
        ## Inputs list  : type                                          ##
        ## Outputs list : return status                                 ##
        ## Description  : * Clone the repos denfined by type            ##
        """
        print "-I- Clone the following repo: "+type
        if (type == "yocto"):
            if (os.path.exists("./poky")):
                print "-W- poky exists. Consider using the update switch - skip the clone"
            else:
                self.g.clone(self.yocto.repo_yocto)
                self.checkout = self.yocto.branch
                self.g.checkout(self.checkout)
                print "-.- selected branch for "+type+": "+self.g.branch()

        elif (type == "meta-xilinx"):
            if (os.path.exists("./"+type)):
                print "-W- "+type+" exists. Consider using the update switch - skip the clone"
            else:
                self.g.clone(self.xilinx.repo_xilinx+type)
                self.checkout = self.yocto.branch
                os.chdir(type)
                self.g.checkout(self.checkout)
                print "-.- selected branch for "+type+": "+self.g.branch()
                os.chdir('..')
            
        elif (type == "meta-xilinx-tools"):
            if (os.path.exists("./"+type)):
                print "-W- "+type+" exists. Consider using the update switch - skip the clone"
            else:
                self.g.clone(self.xilinx.repo_xilinx+type)
                self.checkout = self.xilinx.branch
                os.chdir(type)
                self.g.checkout(self.checkout)
                print "-.- selected branch for "+type+": "+self.g.branch()
                os.chdir('..')
            
        elif (type == "meta-xilinx-petalinux"):
            if (os.path.exists("./"+type)):
                print "-W- "+type+" exists. Consider using the update switch - skip the clone"
            else:
                self.g.clone(self.xilinx.repo_xilinx+type)
                self.checkout = self.xilinx.branch
                os.chdir(type)
                self.g.checkout(self.checkout)
                print "-.- selected branch for "+type+": "+self.g.branch()
                os.chdir('..')

        elif (type == "meta-zynqberry"):
            if (os.path.exists("./"+type)):
                print "-W- "+type+" exists. Consider using the update switch - skip the clone"
            else:
                self.g.clone(self.zynqberry.repo_zynqberry+type)
                self.checkout = self.zynqberry.branch
                # print self.checkout
                os.chdir(type)
                self.g.checkout(self.checkout)
                print "-.- selected branch for "+type+": "+self.g.branch()
                os.chdir('..')
            
    def __init__(self, inifile, options): 
        """ Class initialization
        """
        self.globalconfig,self.yocto,self.xilinx,self.zynqberry,self.notification  = self.pyocto_loadconfig(inifile
             , self._GlobalConfigDefault
             , self._YoctoDefault
             , self._XilinxDefault
             , self._ZynqberryDefault
             , self._NotificationDefault
        )
             
        self.inifile = inifile
        
        #cree l'objet gerant les repos git
        self.g = git.Git()

        #Creation of the work directory:
        work_folder=self.globalconfig.work
        if not os.path.exists(work_folder):
            print "-.- setup the work folder"
            os.mkdir(work_folder)

        os.chdir(work_folder)
        print "-.- path is now: "+os.getcwd()
        


################################################################################
################################      Main      ################################
################################################################################
def main():

    parser = OptionParser(usage=__doc__)#, version=__version__)
    parser.set_defaults(gui=True)
    parser.add_option("--ini",
                      action="store", dest="inifile", default="config/config.ini",
                      help="specify pyocto ini file (default: config.ini)")
    parser.add_option("-n", "--notify",
                      action="store_true", dest="push", default=False,
                      help="send push notification when script terminates")
    parser.add_option("--setup",
                      action="store_true", dest="setup", default=False,
                      help="setup a vivado project")
    parser.add_option("--clear",
                      action="store_true", dest="clear", default=False,
                      help="clear a yocto build project")
    parser.add_option("--build",
                      action="store_true", dest="build", default=False,
                      help="build the yocto project")
    parser.add_option("--update",
                      action="store", dest="update",
                      help="update the git repos.")

    # Parse command-line
    global options
    if len(sys.argv) < 2:
        if os.path.exists("pyocto.cmd"):
            argv = list(flatten([a for a in (l.split('#')[0].split() for l in open("pyocto.cmd")) if len(a)]))
        else:
            argv = ["--help"]
    else:
        argv = sys.argv[1:]
    cmdline = ' '.join(argv)
    (options, args) = parser.parse_args(argv)

    inifile = options.inifile

    # Parse options form the configuration file
    v_pyocto = pyocto(inifile, options)
    
    #execute using the selected options
    if options.setup:
        print "-.- clone the yocto repos."
        v_pyocto.pyocto_git_clone("yocto")
        #if (os.path.exists("./poky")):
        #    print "-W- poky exists. Consider using the update switch - skip the clone"
        #else:
        #    g.clone(v_pyocto.yocto.repo_yocto)
        #    # git.Git().clone(v_pyocto.yocto.repo_yocto)
 
        os.chdir('poky')
        print "-.- path is now: "+os.getcwd()
        v_pyocto.pyocto_git_clone("meta-xilinx")
        v_pyocto.pyocto_git_clone("meta-xilinx-tools")
        # v_pyocto.pyocto_git_clone("meta-xilinx-petalinux")
        v_pyocto.pyocto_git_clone("meta-zynqberry")
       
        print "-I- Setup is DONE ----"
        
        notification =  "PYOCTO (setup) is over"
    
    if options.clear:
        print "clear"
        notification =  "PYOCTO (clear) is not supported"
        
        print "---- DONE ----"
        exit()

    if options.build:
        print "build"
        notification =  "PYOCTO (build) is not supported"
        exit()

    if options.update:
        print "update"
        notification =  "PYOCTO (update) is not supported"
        exit()

    if options.push and importpushetta:
        
        print "-.- Send notification"
        
        API_KEY=v_pyocto.notification.api_key
        CHANNEL_NAME=v_pyocto.notification.channel_name
        
        p=Pushetta(API_KEY)
        p.pushMessage(CHANNEL_NAME, notification)
    
    print "-.- done"
    
if __name__ == "__main__":
    logo()
    sys.exit(main())

