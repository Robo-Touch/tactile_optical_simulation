import os
from os import path as osp

def create_folder(project_name, overwrite = False):
  try:
    os.mkdir(osp.join('results', project_name))
  except FileExistsError:
    if(not overwrite):
      tmp = input("Dir exists. Do you want to overwrite(Y/n)?")
      if(tmp == 'n'):
        exit(1)