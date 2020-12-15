from os import path as osp
from configparser import ConfigParser
from skimage.io import imread
from ast import literal_eval


def load_render_cfg(fname="default.cfg"):
  cfg = ConfigParser()
  cfg.optionxform = str 
  cfg.read(fname)
  # for key,val in cfg['DEFAULT'].items():
  #   print(key, (val))
  default_params = {k: literal_eval(v) for k, v in cfg['DEFAULT'].items()}

  default_params['resW'] = default_params['resW']//default_params["reduce_fac"]
  default_params['resH'] = default_params['resH']//default_params["reduce_fac"]
  default_params['cropW'] = default_params['cropW']//default_params["reduce_fac"]
  default_params['cropH'] = default_params['cropH']//default_params["reduce_fac"]

  if default_params["full"]:
    default_params["cropX"] = (default_params["resW"] - default_params["cropW"])//2
    default_params["cropY"] = (default_params["resH"] - default_params["cropH"])//2
  # set_trace()
  return default_params
  
def update_hyperparam(params, default_params):
  model_folder = default_params["model_folder"]
  # mesh and object
  if "mesh_fn" in params:
    params["mesh_fn"] = osp.join(model_folder, "meshes", params["mesh_fn"])
  if "obj_fn" in params:
    params["obj_fn"] = osp.join(model_folder, "objects", params["obj_fn"])
  
  if "u" in params and not default_params["full"]:
    params["cropX"] = params["u"]//default_params['reduce_fac'] - default_params["cropW"]//2
    del params["u"]
  if "v" in params and not default_params["full"]:
    params["cropY"] = params["v"]//default_params['reduce_fac'] - default_params["cropH"]//2
    del params["v"]
  return params

def load_img_with_cfg(train_img_list, default_params):

  # load scene per train_file
  # scene_list = []
  loading_param_list = []
  target_im_list = []

  for img_fn in train_img_list:
    # obtain the param dict
    # assumed img and cfg struct
    # folder
    # -- img
    #   -- img1.exr
    # -- cfg
      # -- img1.py
    # ----------
    # add img
    target_im = imread(img_fn)
    target_im_list.append(target_im.ravel())
    # add scene
    base = osp.splitext(osp.basename(img_fn))[0]
    img_cfg_fn = osp.join(osp.dirname(img_fn), "..", "cfg", "%s.cfg"%base)
    cfg = ConfigParser()
    cfg.optionxform = str
    cfg.read(img_cfg_fn)
    # for key,val in cfg['DEFAULT'].items():
    #   print(key, (val))
    params = {k: literal_eval(v) for k, v in cfg['DEFAULT'].items()}
    params["baseFn"] = base
    update_hyperparam(params, default_params)
    loading_param_list.append(params.copy())

  return loading_param_list, target_im_list

def load_scene_from_params(train_img_list, fname, default_params):
  import mitsuba
  from mitsuba.core.xml import load_file
  
  loading_param_list, target_im_list = load_img_with_cfg(train_img_list, default_params)
  scene_list = []
  for params in loading_param_list:
    scene = load_file(fname, **default_params, **params)
    scene_list.append(scene) 
  return scene_list, target_im_list
