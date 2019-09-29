#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage:
  main.py <ck_path> <repository_name> <amount> 

Created on Fri Sep 27 16:51:11 2019

@author: clappis
"""

from docopt import docopt
import subprocess
import names
import json
import os

TIMEOUT_SEC = 30


def run_script(script, ignore_return=None):    
    proc = subprocess.Popen(['bash', '-c', script],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        stdin=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    if proc.returncode and not ignore_return:
        raise ScriptException(proc.returncode, stdout, stderr, script)
    return stdout, stderr

class ScriptException(Exception):
    def __init__(self, returncode, stdout, stderr, script):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        super(Exception, self).__init__('Error in script: {}'.format(stderr))
        

def create_program(ck_path, repository_name):
    program_name = 'csmith-{}'.format(names.get_last_name().lower())
    
    list_programs = run_script('ck list {}:program:'.format(repository_name))[0]
    while program_name in str(list_programs):
        program_name = 'csmith-{}'.format(names.get_last_name().lower())

    print('Adding the {} program'.format(program_name))
    
    ck_add_string_bash = 'ck add {}:program:{} --template=template-hello-world-c-output-validation'
    run_script(ck_add_string_bash.format(repository_name, program_name))
    ck_program_path = '{}/{}/program/{}/'.format(ck_path, repository_name, program_name)
    rm_hello_world = 'rm {}/{}/program/{}/hello-world.c'.format(ck_path, repository_name, program_name)
    run_script(rm_hello_world)
    copy_lib_command = 'cp -r runtime/* {}'.format(ck_program_path)
    run_script(copy_lib_command)
    
    with open('meta_template.json') as json_file:
        meta = json.load(json_file)    
        
    with open('{}.cm/meta.json'.format(ck_program_path)) as json_file:
        meta_created = json.load(json_file)    
    
    meta['backup_data_uid'] = meta_created['backup_data_uid']
    meta['data_name'] = meta_created['data_name']
    meta['source_files'] = [program_name + '.c']
    
    with open('{}.cm/meta.json'.format(ck_program_path), 'w') as outfile:
        json.dump(meta, outfile, indent=4)
    
    while True:
        csmith_generate_command = './csmith > {}{}'.format(ck_program_path, program_name + '.c')
        run_script(csmith_generate_command)        
        
        compile_program = 'ck compile {}:program:{} --compiler_tags=milepost'.format(repository_name, program_name)
        run_script(compile_program)
    
        run_program = 'timeout {} ck run {}:program:{} --overwrite_reference_output'.format(TIMEOUT_SEC, repository_name, program_name)
        run_script(run_program, True)
            
        stdout_path = '{}tmp/stdout.log'.format(ck_program_path)
        if os.path.exists(stdout_path):
            with open(stdout_path) as stdout:
               if stdout.readline().startswith('checksum'): #default output on csmith programs
                   break
       
        print('Csmith generate a looping program')
        print('We will generate a new one')
    
    share_program_command = 'ck mv program.output:program-uid-{} {}:: --share'.format(meta['backup_data_uid'], repository_name)
    run_script(share_program_command)
    print('Successfully added {} program'.format(program_name))


def main():
    args = docopt(__doc__)
    ck_path = args['<ck_path>']
    repository_name = args['<repository_name>']
    amount = args['<amount>']
    
    [create_program(ck_path, repository_name) for i in range(0, int(amount))]
    

if __name__ == '__main__':
    main()
    

