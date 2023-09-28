from os.path import join
from os import path as osp

import mitsuba as mi
mi.set_variant("scalar_rgb")

from tactile_optical_simulation.scene_cfg_loading_utils import load_render_cfg
from tactile_optical_simulation.folder_utils import create_folder

# from ipdb import set_trace

cdir = osp.dirname(osp.abspath(__file__))

model_fn = join("models", "flatgel_with_mesh.xml")	
render_params_fn = join(cdir, "render_cfgs", "full_sensor_resolution.cfg")
_outdir = join("results", "new_mesh")

## filepath of new mesh. Absolute path is preferred
new_mesh_fn = join("models", "meshes", "gelpad_tri0s.obj")
##

bname = osp.basename(new_mesh_fn)
mesh_bname, ext = osp.splitext(bname)

if ext != '.obj':
	print("Currently only obj mesh file format is supported")
	exit(1)

mesh_dname = osp.dirname(new_mesh_fn)
mi.Thread.thread().file_resolver().append(mesh_dname)

dname = osp.dirname(model_fn)
mi.Thread.thread().file_resolver().append(dname)
render_params = load_render_cfg(render_params_fn)
params = {
	"hfName" : mesh_bname
}

del render_params["model_folder"], render_params["reduce_fac"], render_params["full"]
scene = mi.load_file(model_fn, **render_params, **params)
create_folder(_outdir)
outFn = join(_outdir, "outfile.exr")
image = mi.render(scene, spp=render_params["num_samples"])
mi.util.write_bitmap(outFn, image)