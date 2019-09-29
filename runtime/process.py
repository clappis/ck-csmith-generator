#
# Postprocessing CK template demo
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, 2018, Grigori.Fursin@cTuning.org, http://fursin.net
#

import json
import os
import re
import sys

def ck_postprocess(i):

    ck=i['ck_kernel']
    rt=i['run_time']
    deps=i['deps']

    d={}

    env=i.get('env',{})

    return {'return':0}

# Check output with a reference one (can check numerical stability)

def ck_check_output(i):
    ck=i['ck_kernel']

    env=i.get('env',{})
    text1=None

    file1=i.get('file1','')
    if file1!='':
       r=ck.load_text_file({'text_file':file1})
       if r['return']>0: return r
       text1=r['bin']

    if text1 is None:
       return {'return':1, 'error':'text1 to compare is empty'}

    text2=None
    file2=i.get('file2','')
    if file2!='':
       r=ck.load_text_file({'text_file':file2})
       if r['return']>0: return r
       text2=r['bin']

    if text2 is None:
       return {'return':1, 'error':'text2 to compare is empty'}

    if text1 <> text2:
       return {'return':0, 'failed':True, 'fail_reason':'Outputs differ:\n'+err}

    return {'return':0, 'failed':False}

# Do not add anything here!

# Do not add anything here!
