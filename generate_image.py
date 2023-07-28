import mitsuba as mi
# mi.set_variant("llvm_ad_rgb")
mi.set_variant("scalar_rgb")

from os import path as osp
from os.path import join

from tactile_optical_simulation.scene_cfg_loading_utils import load_render_cfg, load_img_with_cfg, load_scene_from_params
from tactile_optical_simulation.folder_utils import create_folder

# Load file list 
from file_list_cfgs.flatgel import fname, img_list, project_name

cdir = osp.dirname(osp.abspath(__file__))

# Register any searchs path needed to load scene resources (optional)
dname = osp.dirname(fname)
mi.Thread.thread().file_resolver().append(join(cdir, dname))

# load render params
render_params = load_render_cfg(join(cdir, "render_cfgs", "focussed.cfg"))
loading_param_list, target_im_list = load_img_with_cfg(img_list, render_params)
# remove model_folder from render_params
del render_params["model_folder"]
del render_params["reduce_fac"]
del render_params["full"]

for scene_id, params in enumerate(loading_param_list):
  baseFn = params["baseFn"]
  del params["baseFn"]
  print(f"Rendering {scene_id}/{len(loading_param_list)} fn:{baseFn}")

  # Load the scene from an XML file
  print(render_params, params)
  scene = mi.load_file(fname, **render_params, **params)

  outFn = f"{baseFn}_sim.png"

  # create output dir
  create_folder(join("results", "flatgel"))
  outFn = join("results", "flatgel", outFn)
  
  image = mi.render(scene, spp=render_params["num_samples"])
  mi.util.write_bitmap(outFn, image)
